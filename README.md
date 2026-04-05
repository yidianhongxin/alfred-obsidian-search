# Alfred · Obsidian Search

在 Alfred（需 Powerpack）中按关键字搜索本地 Obsidian 库（文件名、正文、`#标签`、YAML `tags`），回车用 Obsidian 打开；支持 Shift 预览。

**作者**：121个黑梦（见 Workflow 内 Created By）

## 更新日志

- **v1.0.2**：`obsidian://` 参数整段百分号编码（含 `+`、`/` 等）并做路径 NFC 归一化，减少「未找到文件」；README 补充 `obs` 后须加空格、库根与 Obsidian 一致、`USE_PATH_URI=0` 备选等说明。
- **v1.0.1**：关键字恢复为 `obs`；空查询列出最近修改笔记；修复 Configuration Builder 与 Environment Variables 中 `VAULT_PATH` 不一致导致库路径错误的问题（发布包内两处默认已对齐为占位路径，导入后请改为你本机路径）。

## 安装

1. 下载或在本仓库根目录取得 **`Obsidian Search.alfredworkflow`**（ZIP 包），双击导入 Alfred。  
2. 在 Workflow 环境变量中将 **`VAULT_PATH`** 设为你**本机** Obsidian 库根目录（不要使用仓库里的示例路径）。  
3. 更详细的依赖、预览（QLMarkdown / pandoc）、故障排除见 **[README.txt](README.txt)**。

## 从源码打包

```bash
./package-workflow.sh
```

会在当前目录生成/更新 `Obsidian Search.alfredworkflow`。

## 隐私与安全

- 本仓库中的路径、库名均为**占位示例**，使用前请在 Alfred 中改为自己的配置。  
- 请勿在 Issue、讨论或 PR 中粘贴真实库路径、笔记内容、账号等个人信息。

## 发布到你自己的 GitHub

本机已 `git init` 并完成首次提交，仓库目录：  
`/Users/DRLer/Desktop/ob搜索plan/alfred-obsidian-search`

1. 安装并登录 GitHub CLI（仅需一次）：

   ```bash
   brew install gh   # 若尚未安装
   gh auth login
   ```

2. 在**该目录下**创建公开仓库并推送（仓库名可按需修改；将创建在当前 `gh` 登录账号下）：

   ```bash
   cd /Users/DRLer/Desktop/ob搜索plan/alfred-obsidian-search
   gh repo create alfred-obsidian-search --public --source=. --remote=origin --push
   ```

   若你已在网页上新建空仓库，则：

   ```bash
   cd /Users/DRLer/Desktop/ob搜索plan/alfred-obsidian-search
   git remote add origin git@github.com:你的GitHub用户名/alfred-obsidian-search.git
   git push -u origin main
   ```

## 许可

见 [LICENSE](LICENSE)。
