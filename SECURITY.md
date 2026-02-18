# 安全说明 / Security

## 敏感信息与版本控制

- **不要**将以下内容提交到 Git / GitHub：
  - `.env`、`.env.local`、`.env.production` 等任何含真实密钥的 env 文件
  - `*.key`、`*.pem`、`secrets/`、`credentials/`
  - 数据库备份或含用户数据的文件（除非已脱敏）

- 项目已通过 `.gitignore` 排除上述文件；仅保留 `.env.example` 作为配置项说明模板。

## 上传到 GitHub 前请确认

1. 未提交 `.env` 或 `.env.*`（除 `.env.example` 外）
2. `yuantong/settings.py` 中无硬编码密码、Secret、数据库密码、企业微信密钥
3. 运行 `git status` 和 `git diff` 确认无敏感文件被 add

## 部署时

在服务器或 CI 中通过环境变量或安全的 secrets 管理注入配置，不要依赖提交到仓库的密钥文件。
