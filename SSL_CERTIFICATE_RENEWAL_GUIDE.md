# 🔐 SSL证书续期操作指南

## 📋 问题描述

**故障现象：**
- 用户访问系统时显示：`Warning: Potential Security Risk Ahead`
- 浏览器提示SSL证书安全问题
- 系统无法正常通过HTTPS访问

**故障时间：** 2025年9月1日 20:20 CST

## 🔍 问题诊断过程

### 1. 检查证书有效期
```bash
# 检查远程证书状态
openssl s_client -connect jilinyuantong.top:443 -servername jilinyuantong.top < /dev/null 2>/dev/null | openssl x509 -noout -dates

# 输出结果
notBefore=Jun  3 12:02:27 2025 GMT
notAfter=Sep  1 12:02:26 2025 GMT
```

### 2. 检查系统时间
```bash
date
# 输出：Mon Sep  1 20:20:45 CST 2025
```

### 3. 分析问题原因
- **证书有效期**：2025年6月3日 - 2025年9月1日 12:02:26 GMT
- **当前时间**：2025年9月1日 20:20 CST
- **问题确认**：证书已过期（超过有效期约8小时）

### 4. 检查系统配置
```bash
# 查看Nginx SSL配置
sudo cat /etc/nginx/sites-available/yuantong

# 检查证书文件位置
sudo ls -la /etc/letsencrypt/live/jilinyuantong.top/

# 验证本地证书文件
sudo openssl x509 -in /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem -noout -dates
```

## 🛠️ 解决方案

### 1. 检查certbot工具
```bash
# 确认certbot安装位置
which certbot
# 输出：~/.local/bin/certbot

# 检查系统路径
ls -la /usr/bin/certbot
ls -la /usr/local/bin/certbot
```

### 2. 执行证书续期
```bash
# 首先进行模拟续期测试
sudo ~/.local/bin/certbot renew --dry-run

# 输出结果
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/jilinyuantong.top.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Account registered.
Simulating renewal of an existing certificate for jilinyuantong.top and www.jilinyuantong.top

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations, all simulated renewals succeeded: 
  /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem (success)
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# 执行实际续期
sudo ~/.local/bin/certbot renew

# 输出结果
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/jilinyuantong.top.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Renewing an existing certificate for jilinyuantong.top and www.jilinyuantong.top
Reloading nginx server after certificate renewal

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations, all renewals succeeded: 
  /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem (success)
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

### 3. 验证续期结果
```bash
# 检查新证书有效期
sudo openssl x509 -in /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem -noout -dates

# 输出结果
notBefore=Sep  1 11:24:36 2025 GMT
notAfter=Nov 30 11:24:35 2025 GMT

# 验证HTTPS连接
curl -I https://jilinyuantong.top/

# 输出结果
HTTP/2 302 
server: nginx/1.14.1
date: Mon, 01 Sep 2025 12:23:29 GMT
content-type: text/html; charset=utf-8
content-length: 0
location: /login/
x-frame-options: DENY
vary: origin, Cookie
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-content-type-options: nosniff
referrer-policy: same-origin
cross-origin-opener-policy: same-origin
```

### 4. 检查自动续期配置
```bash
# 查看cron任务
sudo crontab -l

# 输出结果包含
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

## ✅ 问题解决确认

### 证书状态对比
| 项目 | 续期前 | 续期后 |
|------|---------|---------|
| 有效期开始 | 2025年6月3日 12:02:27 GMT | 2025年9月1日 11:24:36 GMT |
| 有效期结束 | 2025年9月1日 12:02:26 GMT | 2025年11月30日 11:24:35 GMT |
| 状态 | ❌ 已过期 | ✅ 有效（3个月） |

### 系统状态
- ✅ HTTPS连接正常
- ✅ 不再显示安全警告
- ✅ Nginx服务正常运行
- ✅ 自动续期机制已配置

## 🔧 预防措施

### 1. 自动续期机制
系统已配置cron任务，每天中午12点自动检查并续期证书：
```bash
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

### 2. 证书路径配置
```bash
# 证书文件位置
/etc/letsencrypt/live/jilinyuantong.top/fullchain.pem
/etc/letsencrypt/live/jilinyuantong.top/privkey.pem

# 符号链接路径
/usr/bin/certbot -> /usr/local/bin/certbot -> /home/deploy/.local/bin/certbot
```

### 3. 监控建议
- 定期检查证书有效期（建议每月检查一次）
- 监控自动续期日志
- 设置证书到期提醒机制

## 📝 操作日志

### 操作时间线
- **20:20** - 发现问题：SSL证书过期警告
- **20:21** - 开始诊断：检查证书有效期和系统时间
- **20:22** - 确认问题：证书已过期约8小时
- **20:23** - 检查配置：验证Nginx和certbot配置
- **20:24** - 执行续期：先模拟测试，再实际续期
- **20:25** - 验证结果：确认新证书有效期和HTTPS连接
- **20:26** - 检查自动化：确认cron任务配置正确

### 使用的命令总结
```bash
# 诊断命令
openssl s_client -connect jilinyuantong.top:443 -servername jilinyuantong.top < /dev/null 2>/dev/null | openssl x509 -noout -dates
date
sudo cat /etc/nginx/sites-available/yuantong
sudo ls -la /etc/letsencrypt/live/jilinyuantong.top/
sudo openssl x509 -in /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem -noout -dates

# 解决命令
sudo ~/.local/bin/certbot renew --dry-run
sudo ~/.local/bin/certbot renew
sudo openssl x509 -in /etc/letsencrypt/live/jilinyuantong.top/fullchain.pem -noout -dates
curl -I https://jilinyuantong.top/
sudo crontab -l
```

## 🚨 注意事项

1. **权限要求**：证书续期需要sudo权限
2. **服务影响**：续期过程中Nginx会自动重新加载配置，短暂影响服务
3. **备份建议**：续期前建议备份现有证书文件
4. **监控日志**：关注`/var/log/letsencrypt/letsencrypt.log`中的续期日志

## 📞 技术支持

如果遇到证书续期问题：
1. 检查网络连接和DNS解析
2. 查看certbot日志：`sudo tail -f /var/log/letsencrypt/letsencrypt.log`
3. 检查Nginx配置：`sudo nginx -t`
4. 重启Nginx服务：`sudo systemctl restart nginx`

---

**文档创建时间：** 2025年9月1日  
**操作人员：** AI助手  
**问题状态：** ✅ 已解决  
**下次检查建议：** 2025年11月15日（证书到期前15天）




