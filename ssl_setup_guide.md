# 🔐 jilinyuantong.top SSL证书申请指南

## 🎯 推荐方案：Let's Encrypt（免费且自动续期）

Let's Encrypt是最简单、最可靠的免费SSL证书解决方案。

### 📋 前提条件

1. ✅ 域名 `jilinyuantong.top` 已解析到你的华为云服务器IP
2. ✅ 服务器已安装Nginx
3. ✅ 防火墙已开放80和443端口

### 🚀 一键申请SSL证书

#### 步骤1：安装Certbot

**Ubuntu/Debian系统：**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

**CentOS/RHEL系统：**
```bash
sudo yum install epel-release -y
sudo yum install certbot python3-certbot-nginx -y
```

#### 步骤2：申请证书（一条命令搞定）

```bash
# 为jilinyuantong.top申请SSL证书
sudo certbot --nginx -d jilinyuantong.top -d www.jilinyuantong.top --email your-email@example.com --agree-tos --no-eff-email
```

**命令说明：**
- `-d jilinyuantong.top`：为主域名申请证书
- `-d www.jilinyuantong.top`：同时为www子域名申请证书
- `--email`：你的邮箱地址（用于证书到期提醒）
- `--agree-tos`：同意服务条款
- `--no-eff-email`：不接收EFF的邮件

#### 步骤3：设置自动续期

```bash
# 测试自动续期功能
sudo certbot renew --dry-run

# 如果测试成功，添加定时任务
sudo crontab -e

# 在打开的编辑器中添加以下行（每天中午12点检查续期）
0 12 * * * /usr/bin/certbot renew --quiet
```

### ✅ 验证SSL证书

申请成功后，可以通过以下方式验证：

1. **浏览器访问**：https://jilinyuantong.top
2. **命令行检查**：
   ```bash
   curl -I https://jilinyuantong.top
   ```

## 🔄 备选方案：华为云免费SSL证书

如果Let's Encrypt遇到问题，可以使用华为云的免费证书：

### 步骤1：登录华为云控制台

1. 访问：https://console.huaweicloud.com/
2. 搜索"SSL证书管理"

### 步骤2：申请免费证书

1. 点击"购买证书"
2. 选择"DV域名型" → "免费版"
3. 填写域名：`jilinyuantong.top`
4. 选择验证方式（推荐DNS验证）
5. 完成域名验证
6. 下载证书文件

### 步骤3：配置证书到Nginx

下载证书后，将文件上传到服务器：

```bash
# 创建证书目录
sudo mkdir -p /etc/nginx/ssl

# 上传证书文件（替换为实际文件名）
sudo cp jilinyuantong.top.crt /etc/nginx/ssl/
sudo cp jilinyuantong.top.key /etc/nginx/ssl/

# 设置权限
sudo chmod 600 /etc/nginx/ssl/jilinyuantong.top.key
sudo chmod 644 /etc/nginx/ssl/jilinyuantong.top.crt
```

然后修改Nginx配置中的证书路径：
```nginx
ssl_certificate /etc/nginx/ssl/jilinyuantong.top.crt;
ssl_certificate_key /etc/nginx/ssl/jilinyuantong.top.key;
```

## 🛠️ 常见问题解决

### 问题1：域名解析未生效

```bash
# 检查域名解析
nslookup jilinyuantong.top
dig jilinyuantong.top

# 如果解析不正确，需要在域名注册商处设置A记录
```

### 问题2：防火墙阻止

```bash
# 检查防火墙状态
sudo ufw status

# 开放必要端口
sudo ufw allow 80
sudo ufw allow 443
sudo ufw reload
```

### 问题3：Nginx配置错误

```bash
# 测试Nginx配置
sudo nginx -t

# 如果有错误，检查配置文件语法
sudo nano /etc/nginx/sites-available/yuantong
```

## 🎉 完成后的效果

成功配置SSL证书后，你的网站将：

- ✅ 通过 https://jilinyuantong.top 安全访问
- ✅ 浏览器显示绿色锁图标
- ✅ 自动将HTTP请求重定向到HTTPS
- ✅ 获得A+级SSL安全评级

## 📞 需要帮助？

如果在申请过程中遇到问题，可以：

1. 检查域名解析是否正确
2. 确认防火墙设置
3. 查看Nginx错误日志：`sudo tail -f /var/log/nginx/error.log`
4. 查看Certbot日志：`sudo tail -f /var/log/letsencrypt/letsencrypt.log`

记住：Let's Encrypt证书有效期90天，但设置了自动续期后无需手动操作！ 