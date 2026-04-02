Obsidian 搜索（Alfred）
========================

安装
----
1. 双击「Obsidian Search.alfredworkflow」导入 Alfred。
   （该文件为 ZIP 压缩包，是 Alfred 官方可识别的格式；若你本地曾出现「只是一个文件夹」
   的情况，请使用本仓库根目录下由 package-workflow.sh 生成的同名文件。）
2. 修改脚本或 plist 后，可在项目根目录执行：
     ./package-workflow.sh
   会同步 search.py 到 alfred-workflow-source/ 并重新打包。
3. 在 Workflow 编辑界面右上角 [𝒙] → Environment Variables 中检查：
   - VAULT_PATH：库根目录（请改为本机路径，勿使用他人示例路径）
   - VAULT_NAME：（可选）Obsidian 左侧显示的库名称。留空则用 VAULT_PATH 的文件夹名。
   - USE_PATH_URI：默认已等价于开启（用 path= 绝对路径打开，避免「Vault not found」）。
     若你坚持用 vault+file 形式，请设为 0 或 vault，并保证 VAULT_NAME 与 Obsidian 左侧库名完全一致。
   - MAX_RESULTS：最多显示条数，默认 50。
4. 关键字默认 obs（可在 Script Filter 里改）。

源码与打包
----------
- alfred-workflow-source/：info.plist、icon.png、preview.css；search.py 由 ./package-workflow.sh 从根目录复制
- 根目录 search.py：日常改这里后运行 ./package-workflow.sh 即可更新 .alfredworkflow

依赖
----
- macOS 自带 Python 3（/usr/bin/python3）
- 建议安装 ripgrep 以加快全文搜索：brew install ripgrep
  未安装时会自动改用 grep，库很大时会较慢。

预览（Quick Look）
------------------
- 默认 quicklookurl 指向本地 .md（file://），按 Shift 预览时由 **macOS Quick Look** 决定长什么样。
- **无法做到与 Obsidian 里「完全一致」**：Alfred 预览不会调用 Obsidian 引擎，主题、插件、[[双链]] 解析、Callout 等与 Obsidian 不同。

接近「渲染后」效果的两种做法（可同时用）：

1) **QLMarkdown（推荐，省事）**  
   安装后，系统对 Markdown 的 Quick Look 会变成渲染后的网页样式（仍非 Obsidian 专属效果）。  
   常见安装：`brew install --cask qlmarkdown`（或选用你信任的 QLMarkdown 发行版）。  
   安装后 Workflow **无需改环境变量**（保持 PREVIEW_HTML=md 即可）。

2) **PREVIEW_HTML=pandoc（可选）**  
   在 Workflow 环境变量中设置 `PREVIEW_HTML=pandoc`，并安装：`brew install pandoc`  
   会用 pandoc 把笔记转成 **缓存的 HTML** 再预览（更接近通用「排版后的网页」，支持 YAML frontmatter；首次命中某篇笔记时会稍慢）。  
   未安装 pandoc 时会自动退回为直接预览 .md。

搜索范围
--------
- 文件名与相对路径（不区分大小写）
- 正文全文（含 #标签 与 YAML frontmatter 中的 tags，因同属文件内容）

打开笔记
--------
默认：obsidian://open?path=笔记绝对路径（不依赖库在 Obsidian 里的显示名）。
备选：将 USE_PATH_URI 设为 0，使用 obsidian://open?vault=…&file=…（需 VAULT_NAME 与 Obsidian 中库名一字不差）。

本地使用
--------
克隆或解压本仓库到本机任意目录即可；路径因人而异，请勿将个人路径写入公开仓库。
