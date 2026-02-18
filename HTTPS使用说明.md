# 🔐 HTTPS快速使用说明

## 🎯 目标
为你的网站 `jilinyuantong.top` 配置免费的HTTPS证书

## 📋 前提条件
1. ✅ 域名已解析到服务器IP
2. ✅ 服务器已安装Django项目
3. ✅ 有root权限

## 🚀 一键配置（推荐）

### 方法1：快速设置（最简单）
```bash
# 运行快速设置脚本
sudo ./quick_https_setup.sh
```

### 方法2：完整部署
```bash
# 运行完整部署脚本
sudo ./deploy_https.sh
```

## 📝 配置过程
脚本会自动完成：
1. 安装Nginx和Certbot
2. 配置防火墙
3. 申请Let's Encrypt SSL证书
4. 配置Nginx HTTPS
5. 设置证书自动续期

## ✅ 配置完成后
- 🌐 访问：https://jilinyuantong.top
- 🔒 浏览器显示安全锁图标
- 🔄 HTTP自动重定向到HTTPS
- ⏰ 证书90天自动续期

## 🔧 常用管理命令
```bash
# 查看证书状态
sudo certbot certificates

# 手动续期证书
sudo certbot renew

# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx状态
sudo systemctl status nginx
```

## 🚨 如果遇到问题
1. **域名解析问题**：确保域名指向服务器IP
2. **防火墙问题**：确保开放80和443端口
3. **Nginx问题**：运行 `sudo nginx -t` 检查配置

## 💡 小贴士
- SSL证书完全免费
- 自动续期，无需手动操作
- 支持HTTP/2，网站更快
- 提升SEO排名和用户信任度

## 📞 需要帮助？
如果配置过程中遇到问题，可以：
1. 查看脚本输出的错误信息
2. 检查域名解析是否正确
3. 确认防火墙设置
4. 查看详细的 `HTTPS_部署指南.md`

---
🎉 享受你的HTTPS网站吧！ 