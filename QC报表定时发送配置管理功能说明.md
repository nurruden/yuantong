# QC报表定时发送配置管理功能说明

## 📋 功能概述

本功能提供了一个完整的QC报表定时发送配置管理系统，支持所有类型的QC报表（大塬、东泰、长富、兴辉、兴辉二线、远通、远通二线）的定时发送配置，包括发送时间、接收人、发送内容等设置。

## 🎯 核心功能

### 1. 配置管理
- **报表类型**: 支持7种QC报表类型
- **发送时间**: 可配置小时和分钟（24小时制）
- **接收人**: 支持企业微信用户ID和显示名称
- **发送内容**: 可选择发送Excel文件、文本消息或两者
- **消息模板**: 支持自定义文本消息模板
- **启用状态**: 可随时启用或禁用配置

### 2. 定时任务
- **自动同步**: 配置变更自动同步到Celery Beat
- **动态调度**: 支持动态添加、修改、删除定时任务
- **任务监控**: 提供任务执行日志和状态监控

### 3. 发送功能
- **Excel格式**: 与历史记录页面完全一致的Excel格式
- **文本消息**: 支持自定义模板的文本消息
- **企业微信**: 通过企业微信API发送文件和消息

## 🏗️ 技术架构

### 数据模型
```python
class QCReportSchedule(models.Model):
    report_type = models.CharField('报表类型', max_length=20, choices=REPORT_TYPES)
    is_enabled = models.BooleanField('是否启用', default=True)
    send_hour = models.IntegerField('发送小时', default=8)
    send_minute = models.IntegerField('发送分钟', default=0)
    recipient_userid = models.CharField('接收人UserID', max_length=100)
    recipient_name = models.CharField('接收人姓名', max_length=100)
    send_excel = models.BooleanField('发送Excel文件', default=True)
    send_text = models.BooleanField('发送文本消息', default=True)
    text_template = models.TextField('文本消息模板', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

### 支持的报表类型
- `dayuan` - 大塬QC报表
- `dongtai` - 东泰QC报表
- `changfu` - 长富QC报表
- `xinghui` - 兴辉QC报表
- `xinghui2` - 兴辉二线QC报表
- `yuantong` - 远通QC报表
- `yuantong2` - 远通二线QC报表

## 🚀 功能特性

### 1. Web管理界面
- **配置列表**: 以卡片形式展示所有配置
- **实时状态**: 显示配置的启用状态和基本信息
- **快速操作**: 支持编辑、启用/禁用、删除操作
- **响应式设计**: 适配不同屏幕尺寸

### 2. 配置管理功能
- **添加配置**: 支持添加新的报表类型配置
- **编辑配置**: 修改现有配置的所有参数
- **批量操作**: 支持批量启用/禁用配置
- **配置验证**: 自动验证配置参数的有效性

### 3. 定时任务同步
- **自动同步**: 配置变更自动同步到Celery Beat
- **任务管理**: 自动创建、更新、删除对应的定时任务
- **状态同步**: 配置状态与任务状态保持同步

## 📊 使用说明

### 1. 访问配置管理页面
```
URL: /tasks/qc-schedule/
权限: 需要登录
```

### 2. 配置参数说明

#### 基本信息
- **报表类型**: 选择要配置的QC报表类型
- **接收人姓名**: 显示名称，用于界面显示
- **接收人UserID**: 企业微信用户ID，用于实际发送

#### 发送时间
- **发送小时**: 0-23，24小时制
- **发送分钟**: 0-59

#### 发送内容
- **发送Excel文件**: 是否发送Excel格式的报表
- **发送文本消息**: 是否发送文本消息
- **文本消息模板**: 自定义消息模板（可选）

### 3. 默认配置
系统会自动创建以下默认配置：
- 大塬QC报表: 08:00
- 东泰QC报表: 08:05
- 长富QC报表: 08:10
- 兴辉QC报表: 08:15
- 兴辉二线QC报表: 08:20
- 远通QC报表: 08:25
- 远通二线QC报表: 08:30

## 🛠️ 管理命令

### 1. 同步定时任务配置
```bash
python manage.py sync_qc_schedules
```
将数据库中的配置同步到Celery Beat定时任务。

### 2. 手动触发报表发送
```bash
python manage.py test_dayuan_report
```
手动触发大塬QC报表发送（用于测试）。

## 📝 配置示例

### 1. 创建新配置
```json
{
    "report_type": "dayuan",
    "is_enabled": true,
    "send_hour": 8,
    "send_minute": 0,
    "recipient_userid": "GaoBieKeLe",
    "recipient_name": "GaoBieKeLe",
    "send_excel": true,
    "send_text": true,
    "text_template": "自定义消息模板"
}
```

### 2. 更新配置
```json
{
    "id": 1,
    "send_hour": 9,
    "send_minute": 30,
    "is_enabled": false
}
```

## 🔧 技术实现

### 1. 定时任务实现
```python
@shared_task(bind=True)
def send_qc_report_by_schedule(self, report_type):
    """根据配置发送指定类型的QC报表"""
    # 获取配置
    schedule = QCReportSchedule.objects.get(report_type=report_type, is_enabled=True)
    
    # 获取昨日数据
    yesterday = date.today() - timedelta(days=1)
    reports = model_class.objects.filter(date=yesterday)
    
    # 发送文本消息
    if schedule.send_text:
        text_message = format_qc_report_data(reports, yesterday, schedule.get_report_type_display())
        send_wechat_message(text_message, yesterday, schedule.recipient_userid)
    
    # 发送Excel文件
    if schedule.send_excel:
        excel_file_path = generate_qc_excel_report(reports, yesterday, schedule.get_report_type_display())
        send_wechat_message_with_file(excel_file_path, yesterday, schedule.recipient_userid)
```

### 2. Excel格式生成
- 使用与历史记录页面完全相同的字段映射
- 支持空值字段自动过滤
- 保持与历史记录页面一致的样式和格式

### 3. 企业微信集成
- 支持文本消息发送
- 支持Excel文件上传和发送
- 完善的错误处理和重试机制

## 📊 监控和维护

### 1. 任务日志
- 通过Django管理界面查看任务执行日志
- 记录任务执行状态、时间、错误信息
- 支持按状态、任务名称筛选

### 2. 配置监控
- 实时显示配置状态
- 支持批量操作
- 配置变更历史记录

### 3. 故障排查
- 检查Celery服务状态
- 查看任务执行日志
- 验证企业微信配置
- 检查数据源可用性

## 🚨 注意事项

1. **权限要求**: 需要登录才能访问配置管理页面
2. **数据依赖**: 功能依赖QC报表数据，确保数据录入及时
3. **服务依赖**: 需要Celery Beat服务正常运行
4. **网络要求**: 需要稳定的网络连接访问企业微信API
5. **配置同步**: 修改配置后需要运行同步命令更新定时任务

## 🆘 故障排除

### 常见问题
1. **配置不生效**: 运行 `python manage.py sync_qc_schedules`
2. **任务不执行**: 检查Celery Beat服务状态
3. **发送失败**: 检查企业微信配置和网络连接
4. **数据为空**: 确认昨日是否有对应的QC报表数据

### 日志位置
- **Celery Worker**: `/var/www/yuantong/logs/celery_worker.log`
- **Celery Beat**: `/var/www/yuantong/logs/celery_beat.log`
- **Django日志**: 通过管理界面查看

---

**功能实现完成时间**: 2024年10月20日  
**实现状态**: ✅ 已完成并测试通过  
**支持报表类型**: 7种QC报表类型  
**维护团队**: 信息化部门
