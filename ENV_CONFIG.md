# 环境变量配置说明

本项目支持通过环境变量来配置各种接口地址和参数，避免在代码中硬编码敏感信息。

## EAS API 配置

以下环境变量用于配置EAS系统的API接口：

```bash
# EAS API 主机地址
EAS_API_HOST=http://139.9.135.148:8081

# EAS API 路径配置
EAS_API_PATH_ADD=/geteasdata/addManufactureRec      # 添加制造记录
EAS_API_PATH_UPDATE=/geteasdata/upManufactureRec    # 更新制造记录
EAS_API_PATH_DELETE=/geteasdata/delManufactureRec   # 删除制造记录
EAS_API_PATH_GET=/geteasdata/getManufactureRec      # 获取制造记录
```

## 微信企业号配置

```bash
WECHAT_CORP_ID=ww3579e18459d4e719                   # 企业微信Corp ID
WECHAT_APP_SECRET=your_app_secret_here               # 应用Secret
WECHAT_CONTACT_SECRET=your_contact_secret_here       # 通讯录Secret
WECHAT_AGENT_ID=1000016                              # 应用Agent ID
REDIRECT_URI=http://work.local:8000/                 # 重定向URI

# 企业微信消息接收配置（用于接收企业微信推送的消息）
WECHAT_MESSAGE_TOKEN=your_message_token_here         # 接收消息的Token（在企业微信管理后台设置接收消息时配置）
WECHAT_ENCODING_AES_KEY=your_encoding_aes_key_here   # 消息加解密密钥（可选，如果使用加密模式需要配置，长度为43个字符）
```

## 数据库配置

```bash
DB_NAME=yuantong                                     # 数据库名称
DB_USER=root                                         # 数据库用户名
DB_PASSWORD=your_password_here                       # 数据库密码
DB_HOST=localhost                                    # 数据库主机
DB_PORT=3306                                         # 数据库端口
```

## Django配置

```bash
SECRET_KEY=your_secret_key_here                      # Django密钥
DEBUG=True                                           # 调试模式
ALLOWED_HOSTS=work.local,localhost,127.0.0.1        # 允许的主机
```

## 使用方法

1. 在项目根目录创建 `.env` 文件
2. 将上述配置复制到 `.env` 文件中
3. 根据实际情况修改配置值
4. 重启Django应用

## 注意事项

- `.env` 文件不应该提交到版本控制系统中
- 生产环境中应该使用更安全的方式管理环境变量
- 如果不设置环境变量，系统会使用默认值（在settings.py中定义） 