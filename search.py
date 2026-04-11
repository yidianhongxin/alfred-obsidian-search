#!/usr/bin/env python3
"""
Alfred Script Filter: search Obsidian vault by filename/path and note contents (incl. #tags & YAML tags).
Reads VAULT_PATH, VAULT_NAME, USE_PATH_URI, MAX_RESULTS, PREVIEW_HTML from environment.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import unicodedata
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# 仅为占位示例；请在 Alfred 环境变量 VAULT_PATH 中改为你的库路径
DEFAULT_VAULT = "~/Obsidian_250614"
MAX_DEFAULT = 50
RECENT_EMPTY_QUERY = 25


def _vault_path() -> Path:
    raw = (os.environ.get("VAULT_PATH") or DEFAULT_VAULT).strip() or DEFAULT_VAULT
    return Path(os.path.expanduser(raw)).resolve()


def _vault_name(vp: Path) -> str:
    env = (os.environ.get("VAULT_NAME") or "").strip()
    if env:
        return env
    return vp.name


def _max_results() -> int:
    try:
        v = int(os.environ.get("MAX_RESULTS", str(MAX_DEFAULT)))
        return max(1, min(v, 200))
    except ValueError:
        return MAX_DEFAULT


def _use_path_uri() -> bool:
    """默认用 path= 绝对路径打开，避免 vault 显示名/中文名与 URI 不一致导致 Vault not found。"""
    raw = os.environ.get("USE_PATH_URI", "1").strip().lower()
    return raw not in ("0", "false", "no", "vault")


def _parse_query_tags(query: str) -> tuple[str, list[str]]:
    """Split user input into (title, [#tags]).

    E.g. '123  #实验 #测试' → ('123', ['#实验', '#测试'])
    """
    tags = re.findall(r'#[\w\-/]+', query)
    title = query
    for tag in tags:
        title = title.replace(tag, '', 1)
    title = re.sub(r'\s+', ' ', title).strip()
    return title, tags


def _uri_component(s: str) -> str:
    """Obsidian URI 查询参数：整段百分号编码（含 / 与 +），避免 + 被当作空格或解析截断。"""
    t = unicodedata.normalize("NFC", s)
    return urllib.parse.quote(t, safe="", encoding="utf-8")


def build_obsidian_arg(vp: Path, note: Path) -> str:
    vp_r = vp.resolve()
    note_r = note.resolve()
    rel = note_r.relative_to(vp_r).as_posix()
    if _use_path_uri():
        # 使用绝对路径；不依赖 Obsidian 里登记的 vault 名称
        return f"obsidian://open?path={_uri_component(str(note_r))}"
    vn = _vault_name(vp_r)
    return f"obsidian://open?vault={_uri_component(vn)}&file={_uri_component(rel)}"


def _preview_mode() -> str:
    """md = 系统 Quick Look 直接预览 .md；pandoc = 用 pandoc 生成缓存 HTML（需 brew install pandoc）。"""
    return os.environ.get("PREVIEW_HTML", "md").strip().lower()


def _pandoc_html_cache(note: Path) -> Path | None:
    if not shutil.which("pandoc"):
        return None
    note = note.resolve()
    try:
        st = note.stat()
    except OSError:
        return None
    cache_root = Path(tempfile.gettempdir()) / "alfred_obsidian_ql_html"
    try:
        cache_root.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    key_src = f"{note}:{st.st_mtime_ns}"
    key = hashlib.sha256(key_src.encode()).hexdigest()[:24]
    out = cache_root / f"{key}.html"
    try:
        if out.exists() and out.stat().st_mtime >= st.st_mtime:
            return out
    except OSError:
        pass
    css = SCRIPT_DIR / "preview.css"
    cmd = [
        "pandoc",
        str(note),
        "-f",
        "markdown+yaml_metadata_block",
        "-t",
        "html5",
        "-s",
        "-o",
        str(out),
    ]
    if css.is_file():
        cmd.extend(["--embed-resources", "-c", str(css)])
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=45,
        )
        return out
    except subprocess.CalledProcessError:
        try:
            out.unlink(missing_ok=True)
        except OSError:
            pass
        if css.is_file():
            cmd2 = [
                "pandoc",
                str(note),
                "-f",
                "markdown+yaml_metadata_block",
                "-t",
                "html5",
                "-s",
                "-c",
                str(css),
                "-o",
                str(out),
            ]
            try:
                subprocess.run(
                    cmd2,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
                return out
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
                try:
                    out.unlink(missing_ok=True)
                except OSError:
                    pass
    except (subprocess.TimeoutExpired, OSError):
        try:
            out.unlink(missing_ok=True)
        except OSError:
            pass
    return None


def quicklook_url(note: Path) -> str:
    if _preview_mode() in ("pandoc", "html"):
        html = _pandoc_html_cache(note)
        if html is not None:
            return html.as_uri()
    return note.resolve().as_uri()


def iter_markdown(vp: Path):
    for p in vp.rglob("*.md"):
        if ".obsidian" in p.parts:
            continue
        yield p


def filename_matches(vp: Path, q_lower: str) -> list[Path]:
    out: list[Path] = []
    for p in iter_markdown(vp):
        rel = p.relative_to(vp).as_posix()
        if q_lower in rel.lower() or q_lower in p.name.lower():
            out.append(p)
    return out


def content_search_rg(vp: Path, query: str) -> list[Path]:
    try:
        r = subprocess.run(
            [
                "rg",
                "-l",
                "-i",
                "-F",
                "--glob",
                "*.md",
                "--glob",
                "!**/.obsidian/**",
                "--",
                query,
                str(vp),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if r.returncode not in (0, 1):
        return []
    if not r.stdout.strip():
        return []
    return [Path(line.strip()) for line in r.stdout.splitlines() if line.strip()]


def content_search_grep(vp: Path, query: str) -> list[Path]:
    try:
        r = subprocess.run(
            [
                "grep",
                "-RIl",
                "--include=*.md",
                "--exclude-dir=.obsidian",
                "-F",
                query,
                str(vp),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return []
    if r.returncode not in (0, 1):
        return []
    if not r.stdout.strip():
        return []
    return [Path(line.strip()) for line in r.stdout.splitlines() if line.strip()]


def content_search(vp: Path, query: str) -> list[Path]:
    if shutil.which("rg"):
        return content_search_rg(vp, query)
    return content_search_grep(vp, query)


def recent_notes(vp: Path, limit: int) -> list[Path]:
    files = list(iter_markdown(vp))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def merge_results(
    vp: Path,
    by_name: list[Path],
    by_content: list[Path],
    cap: int,
) -> list[tuple[Path, int, float]]:
    # priority: 0 = filename hit, 1 = content only
    seen: dict[str, tuple[int, float]] = {}
    for p in by_name:
        try:
            rel = p.resolve().relative_to(vp)
        except ValueError:
            continue
        key = str(rel)
        mtime = p.stat().st_mtime
        prev = seen.get(key)
        if prev is None or prev[0] > 0:
            seen[key] = (0, mtime)
    for p in by_content:
        try:
            rel = p.resolve().relative_to(vp)
        except ValueError:
            continue
        key = str(rel)
        mtime = p.stat().st_mtime
        if key not in seen:
            seen[key] = (1, mtime)
    ranked = [(vp / Path(k), pr, mt) for k, (pr, mt) in seen.items()]
    ranked.sort(key=lambda t: (t[1], -t[2], t[0].as_posix().lower()))
    return ranked[:cap]


def _friendly_mtime(p: Path) -> str:
    try:
        mt = p.stat().st_mtime
    except OSError:
        return ""
    dt = datetime.datetime.fromtimestamp(mt)
    now = datetime.datetime.now()
    diff = now - dt
    if diff.days == 0:
        return f"今天 {dt.strftime('%H:%M')}"
    if diff.days == 1:
        return f"昨天 {dt.strftime('%H:%M')}"
    if diff.days < 7:
        return f"{diff.days}天前"
    return dt.strftime("%Y-%m-%d")


def build_create_arg(vp: Path, name: str, tags: list[str] | None = None) -> str:
    """Build obsidian://new URI to create a note in the vault root.
    Tags are placed after 3 blank lines in the note body."""
    if _use_path_uri():
        new_path = vp / f"{name}.md"
        uri = f"obsidian://new?path={_uri_component(str(new_path))}"
    else:
        vn = _vault_name(vp)
        uri = f"obsidian://new?vault={_uri_component(vn)}&name={_uri_component(name)}"
    if tags:
        content = "\n\n\n" + " ".join(tags) + "\n"
        uri += f"&content={_uri_component(content)}"
    return uri


def item_for_create(vp: Path, name: str, tags: list[str] | None = None) -> dict:
    tag_hint = f"  标签：{' '.join(tags)}" if tags else ""
    return {
        "title": f'Create "{name}"',
        "subtitle": f"在库根目录新建 {name}.md{tag_hint}",
        "arg": build_create_arg(vp, name, tags),
        "uid": "__create__",
        "icon": {"type": "fileicon", "path": "/Applications/Obsidian.app"},
    }


def _exact_name_exists(vp: Path, name: str) -> bool:
    """Check if a note with the exact stem already exists anywhere in the vault."""
    target = name.lower()
    for p in iter_markdown(vp):
        if p.stem.lower() == target:
            return True
    return False


def item_for_note(vp: Path, note: Path, hint: str, show_mtime: bool = False) -> dict:
    rel = note.relative_to(vp).as_posix()
    resolved = note.resolve()
    subtitle = f"{hint} · {rel}"
    if show_mtime:
        subtitle = f"{_friendly_mtime(note)} · {rel}"
    return {
        "title": note.stem,
        "subtitle": subtitle,
        "arg": build_obsidian_arg(vp, note),
        "quicklookurl": quicklook_url(note),
        "uid": str(resolved),
        "type": "file",
        "icon": {"type": "fileicon", "path": str(resolved)},
    }


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    query = query.strip()
    vp = _vault_path()
    cap = _max_results()

    if not vp.is_dir():
        print(
            json.dumps(
                {
                    "items": [
                        {
                            "title": "库目录不存在",
                            "subtitle": str(vp),
                            "valid": False,
                        }
                    ]
                },
                ensure_ascii=False,
            )
        )
        return

    if not query:
        recent = recent_notes(vp, RECENT_EMPTY_QUERY)
        items = [
            item_for_note(vp, p, "最近编辑", show_mtime=True)
            for p in recent
        ]
        if not items:
            print(
                json.dumps(
                    {
                        "items": [
                            {
                                "title": "未找到 Markdown 笔记",
                                "subtitle": str(vp),
                                "valid": False,
                            }
                        ]
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(json.dumps({"items": items}, ensure_ascii=False))
        return

    title, tags = _parse_query_tags(query)
    search_term = title if title else query

    q_lower = search_term.lower()
    name_hits = filename_matches(vp, q_lower)
    content_hits = content_search(vp, search_term)
    merged = merge_results(vp, name_hits, content_hits, cap)

    items = []
    for note, pri, _mt in merged:
        hint = "文件名/路径" if pri == 0 else "正文/标签"
        items.append(item_for_note(vp, note, hint))

    create_name = title if title else query
    if create_name and not _exact_name_exists(vp, create_name):
        create_item = item_for_create(vp, create_name, tags or None)
        if items:
            items.insert(1, create_item)
        else:
            items.append(create_item)

    if not items:
        print(
            json.dumps(
                {
                    "items": [
                        {
                            "title": "无匹配结果",
                            "subtitle": f"查询：{query}",
                            "valid": False,
                        }
                    ]
                },
                ensure_ascii=False,
            )
        )
    else:
        print(json.dumps({"items": items}, ensure_ascii=False))


if __name__ == "__main__":
    main()
