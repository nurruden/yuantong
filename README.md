# 🏢 远通信息化系统

## 📖 项目概述

远通信息化系统是一个基于Django的企业级应用，集成了企业微信OAuth2认证，为企业提供信息化管理解决方案。

## 🏗️ 系统架构

- **后端框架**: Django 4.x
- **Web服务器**: Nginx
- **应用服务器**: Gunicorn
- **数据库**: SQLite
- **认证系统**: 企业微信OAuth2
- **部署环境**: Linux CentOS/RHEL 8

## 📚 运维文档体系

### 📋 核心文档
1. **[运维手册](OPERATIONS_GUIDE.md)** - 完整的系统运维指南
2. **[故障排查清单](TROUBLESHOOTING_CHECKLIST.md)** - 快速故障诊断和解决方案
3. **[命令速查表](COMMANDS_CHEATSHEET.md)** - 常用运维命令快速参考
4. **[备份指南](BACKUP_GUIDE.md)** - 完整的备份和恢复指南
5. **[SSL证书续期指南](SSL_CERTIFICATE_RENEWAL_GUIDE.md)** - SSL证书过期问题解决方案

### 🛠️ 自动化工具
1. **[快速修复脚本](quick_fix.sh)** - 一键解决常见问题
2. **[健康检查脚本](health_check.sh)** - 系统状态全面检查
3. **[完整备份脚本](backup_yuantong.sh)** - 系统完整备份工具
4. **[系统恢复脚本](restore_yuantong.sh)** - 从备份恢复系统

## 🚀 快速开始

### 系统检查
```bash
# 运行健康检查
./health_check.sh

# 如果发现问题，执行快速修复
sudo ./quick_fix.sh
```

### 服务管理
```bash
# 查看服务状态
sudo systemctl status yuantong-django

# 重启服务
sudo systemctl restart yuantong-django

# 查看实时日志
sudo journalctl -u yuantong-django -f
```

## 🐛 常见问题解决

### 1. 企业微信授权循环
**现象**: 用户登录时一直显示"正在跳转到授权页面"

**快速解决**:
```bash
# 检查配置
grep WECHAT .env

# 重启服务
sudo systemctl restart yuantong-django

# 查看日志
tail -f logs/gunicorn_error.log
```

### 2. 服务无法启动
**快速解决**:
```bash
# 执行一键修复
sudo ./quick_fix.sh

# 如果仍有问题，查看详细错误
sudo journalctl -u yuantong-django --no-pager | tail -20
```

### 3. 权限问题
**快速解决**:
```bash
# 修复文件权限
sudo chown -R deploy:deploy /var/www/yuantong
sudo chmod -R 755 /var/www/yuantong
sudo chmod -R 775 /var/www/yuantong/logs
```

## 📊 系统监控

### 关键指标
- **服务状态**: `systemctl is-active yuantong-django`
- **端口监听**: `netstat -tlnp | grep :8000`
- **进程数量**: `pgrep -f gunicorn | wc -l`
- **响应时间**: `curl -o /dev/null -s -w "%{time_total}" http://127.0.0.1:8000/`

### 日志位置
- **应用错误**: `/var/www/yuantong/logs/gunicorn_error.log`
- **访问日志**: `/var/www/yuantong/logs/gunicorn_access.log`
- **系统日志**: `sudo journalctl -u yuantong-django`

## 🔄 更新部署

### 更新前备份（重要！）
```bash
# 执行完整备份
cd /var/www/yuantong
./backup_yuantong.sh

# 查看备份结果
ls -la /var/backups/yuantong/ | tail -5
```

### 标准更新流程
```bash
# 1. 备份（必须！）
./backup_yuantong.sh

# 2. 更新代码
sudo -u deploy git pull origin main

# 3. 安装依赖
sudo -u deploy pip install -r requirements.txt

# 4. 数据库迁移
sudo -u deploy python manage.py migrate

# 5. 重启服务
sudo systemctl restart yuantong-django

# 6. 验证
./health_check.sh
```

### 如果更新失败
```bash
# 恢复最新备份
./restore_yuantong.sh yuantong_backup_YYYYMMDD_HHMMSS

# 验证恢复结果
curl -I https://jilinyuantong.top/
```

## 🚨 紧急响应

### 紧急情况处理顺序
1. **立即重启**: `sudo systemctl restart yuantong-django`
2. **快速修复**: `sudo ./quick_fix.sh`
3. **查看日志**: `sudo journalctl -u yuantong-django --no-pager | tail -20`
4. **联系支持**: 如果问题仍然存在

### 问题分级
- **🔴 P1 严重**: 服务完全无法访问 → 立即执行快速修复
- **🟡 P2 中等**: 部分功能异常 → 检查日志并重启服务
- **🟢 P3 轻微**: 性能问题 → 清理缓存或重新加载配置

## 📞 技术支持

### 联系方式
- **紧急联系**: [待填写]
- **邮件支持**: [待填写]
- **工作时间**: 9:00-18:00

### 外部依赖
- **企业微信API**: qyapi.weixin.qq.com
- **EAS系统**: [待配置]

## 📝 版本历史

### v1.2 (当前版本)
- ✅ 修复企业微信授权循环问题
- ✅ 优化Redis配置，改用本地缓存
- ✅ 完善运维文档和自动化脚本
- ✅ 添加健康检查和快速修复功能

### v1.1
- ✅ 修复企业微信授权URL问题
- ✅ 改进错误处理和日志记录

### v1.0
- ✅ 初始版本发布
- ✅ 基础功能实现

## 🔐 安全与代码托管（GitHub）

- **切勿将 `.env`、`.env.production` 等含密钥的文件提交到 Git**，已通过 `.gitignore` 排除。
- 首次部署或克隆仓库后：复制 `cp .env.example .env`，在 `.env` 中填入真实配置（数据库、企业微信、SECRET_KEY 等）。
- 仓库中仅保留 `.env.example`（占位说明），无真实密钥。上传到 GitHub 前请确认没有提交任何 `.env` 文件。

## 🔗 相关链接

- [Django官方文档](https://docs.djangoproject.com/)
- [企业微信开发文档](https://developer.work.weixin.qq.com/)
- [Gunicorn配置指南](https://docs.gunicorn.org/)

---

## 📋 快速检查清单

### 每日检查
- [ ] 服务状态正常
- [ ] 日志无异常错误
- [ ] 磁盘空间充足
- [ ] 内存使用正常

### 每周检查
- [ ] 清理过期日志
- [ ] 备份数据库
- [ ] 检查系统更新
- [ ] 性能指标分析

### 每月检查
- [ ] 安全补丁更新
- [ ] 依赖包更新
- [ ] 备份策略验证
- [ ] 灾难恢复演练

---

*最后更新: 2024年1月*
*维护团队: 信息化部门* 