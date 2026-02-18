from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    """公司模型"""
    name = models.CharField(max_length=128, verbose_name="公司名称")
    code = models.CharField(max_length=32, unique=True, verbose_name="公司代码")
    description = models.TextField(blank=True, null=True, verbose_name="公司描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "公司"
        verbose_name_plural = "公司"
        ordering = ['name']

    def __str__(self):
        return self.name

class Role(models.Model):
    """角色模型"""
    name = models.CharField(max_length=64, unique=True, verbose_name="角色名")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"

    def __str__(self):
        return self.name

class Permission(models.Model):
    """权限模型"""
    PERMISSION_TYPE_CHOICES = [
        ('module', '模块权限'),
        ('operation', '操作权限'),
        ('data', '数据权限'),
    ]
    
    code = models.CharField(max_length=64, unique=True, verbose_name="权限代码")
    name = models.CharField(max_length=128, verbose_name="权限名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPE_CHOICES, default='operation', verbose_name="权限类型")
    module = models.CharField(max_length=64, blank=True, null=True, verbose_name="所属模块")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = "权限"

    def __str__(self):
        return self.name

class RolePermission(models.Model):
    """角色权限关联模型"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="权限")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ('role', 'permission')
        verbose_name = "角色权限"
        verbose_name_plural = "角色权限"

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"

class UserRole(models.Model):
    """用户角色关联模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = "用户角色"
        verbose_name_plural = "用户角色"

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

# 组织架构相关模型
class Department(models.Model):
    """部门模型"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="所属公司", null=True, blank=True)
    name = models.CharField(max_length=128, verbose_name="部门名称")
    code = models.CharField(max_length=32, verbose_name="部门代码")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="上级部门")
    level = models.IntegerField(default=1, verbose_name="部门层级")
    description = models.TextField(blank=True, null=True, verbose_name="部门描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"
        ordering = ['company', 'level', 'name']
        unique_together = ('company', 'code')

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    def get_full_path(self):
        """获取完整部门路径"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)

class Position(models.Model):
    """职位模型"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="所属公司", null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属部门")
    name = models.CharField(max_length=128, verbose_name="职位名称")
    code = models.CharField(max_length=32, verbose_name="职位代码")
    level = models.IntegerField(default=1, verbose_name="职位层级")
    description = models.TextField(blank=True, null=True, verbose_name="职位描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "职位"
        verbose_name_plural = "职位"
        ordering = ['company', 'department', 'level', 'name']
        unique_together = ('company', 'code')

    def __str__(self):
        return f"{self.company.name} - {self.department.name} - {self.name}"

class UserProfile(models.Model):
    """用户档案模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户", related_name="system_profile")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="所属公司", null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属部门", null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="职位", null=True, blank=True)
    employee_id = models.CharField(max_length=32, unique=True, verbose_name="员工编号")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="联系电话")
    wechat_id = models.CharField(max_length=64, blank=True, null=True, verbose_name="企业微信ID")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户档案"
        verbose_name_plural = "用户档案"

    def __str__(self):
        return f"{self.user.username} - {self.company.name} - {self.department.name} - {self.position.name}"

class DepartmentPermission(models.Model):
    """部门权限模型"""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="部门")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="权限")
    is_inherited = models.BooleanField(default=False, verbose_name="是否继承上级部门权限")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ('department', 'permission')
        verbose_name = "部门权限"
        verbose_name_plural = "部门权限"

    def __str__(self):
        return f"{self.department.name} - {self.permission.name}"

class PositionPermission(models.Model):
    """职位权限模型"""
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="职位")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="权限")
    is_inherited = models.BooleanField(default=False, verbose_name="是否继承部门权限")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ('position', 'permission')
        verbose_name = "职位权限"
        verbose_name_plural = "职位权限"

    def __str__(self):
        return f"{self.position.name} - {self.permission.name}"

class CompanyPermission(models.Model):
    """公司权限模型"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="公司")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name="权限")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ('company', 'permission')
        verbose_name = "公司权限"
        verbose_name_plural = "公司权限"

    def __str__(self):
        return f"{self.company.name} - {self.permission.name}"
