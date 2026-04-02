# Alfred · Obsidian Search

在 Alfred（需 Powerpack）中按关键字搜索本地 Obsidian 库（文件名、正文、`#标签`、YAML `tags`），回车用 Obsidian 打开；支持 Shift 预览。

**作者**：121个黑梦（见 Workflow 内 Created By）

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

## 许可

见 [LICENSE](LICENSE)。
