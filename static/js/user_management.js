// 用户管理页面专用JavaScript文件

// 全局变量
let departments = [];
let positions = [];
let users = [];
let currentPage = 1;
let totalPages = 1;
let totalCount = 0;
let pageSize = 10;
let searchParams = {};

// 页面初始化
document.addEventListener('DOMContentLoaded', async function() {
    console.log('用户管理页面初始化开始...');
    
    try {
        // 检查必要的元素是否存在
        const userTableBody = document.getElementById('userTableBody');
        if (!userTableBody) {
            console.error('用户表格元素未找到');
            return;
        }
        
        console.log('开始加载部门和职位数据...');
        
        // 加载部门和职位数据
        await Promise.all([
            loadDepartments(),
            loadPositions()
        ]);
        
        console.log('部门和职位数据加载完成');
        console.log('部门数量:', departments.length);
        console.log('职位数量:', positions.length);
        
        // 加载用户数据
        await loadUsers();
        
        // 绑定搜索表单事件
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                currentPage = 1;
                loadUsers();
            });
        }
        
        console.log('用户管理页面初始化完成');
    } catch (error) {
        console.error('用户管理页面初始化失败:', error);
    }
});

// 加载部门数据
async function loadDepartments() {
    try {
        const response = await fetch('/api/departments/');
        if (response.ok) {
            const data = await response.json();
            departments = data.data || [];
            console.log('部门数据加载完成:', departments.length);
        } else {
            console.error('加载部门数据失败:', response.status);
        }
    } catch (error) {
        console.error('加载部门数据出错:', error);
    }
}

// 加载职位数据
async function loadPositions() {
    try {
        const response = await fetch('/api/positions/');
        if (response.ok) {
            const data = await response.json();
            positions = data.data || [];
            console.log('职位数据加载完成:', positions.length);
        } else {
            console.error('加载职位数据失败:', response.status);
        }
    } catch (error) {
        console.error('加载职位数据出错:', error);
    }
}

// 加载用户数据
async function loadUsers() {
    try {
        console.log('Loading users...');
        
        // 获取搜索参数
        searchParams = getSearchParams();
        
        // 构建查询参数
        const params = new URLSearchParams({
            page: currentPage,
            page_size: pageSize,
            ...searchParams
        });
        
        const response = await fetch(`/api/user-management/?${params.toString()}`);
        if (response.ok) {
            const data = await response.json();
            
            if (data.data && data.data.results) {
                // 分页数据格式
                users = data.data.results;
                totalCount = data.data.count;
                totalPages = data.data.total_pages;
                updatePagination(data.data);
            } else {
                // 兼容旧格式
                users = data.data || [];
                totalCount = users.length;
                totalPages = 1;
                hidePagination();
            }
            
            renderUserTable(users);
            console.log('用户数据加载完成:', users.length);
        } else {
            console.error('加载用户数据失败:', response.status);
        }
    } catch (error) {
        console.error('加载用户数据出错:', error);
    }
}

// 渲染用户表格
function renderUserTable(users) {
    const tbody = document.getElementById('userTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.username}</td>
            <td>${user.first_name || ''} ${user.last_name || ''}</td>
            <td>${user.employee_id || ''}</td>
            <td>${user.department_name || ''}</td>
            <td>${user.position_name || ''}</td>
            <td>${user.email || ''}</td>
            <td>${user.phone || ''}</td>
            <td>${user.wechat_id || ''}</td>
            <td>
                <span class="badge ${user.is_active ? 'bg-success' : 'bg-danger'}">
                    ${user.is_active ? '启用' : '禁用'}
                </span>
            </td>
            <td>${user.date_joined || ''}</td>
            <td>${user.last_login || ''}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editUser(${user.id})">
                    <i class="material-icons" data-icon="edit">edit</i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id})">
                    <i class="material-icons" data-icon="delete">delete</i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 打开添加用户模态框
function openAddUserModal() {
    console.log('打开添加用户模态框');
    
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('userModalLabel');
    const form = document.getElementById('userForm');
    
    if (!modal) {
        console.error('未找到模态框: userModal');
        return;
    }
    
    modalTitle.textContent = '添加用户';
    form.reset();
    document.getElementById('userId').value = '';
    
    // 更新部门和职位选项
    updateDepartmentOptions();
    updatePositionOptions();
    
    console.log('准备显示模态框');
    
    // 显示模态框
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        console.log('使用Bootstrap模态框');
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    } else {
        console.log('使用原生模态框');
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.classList.add('modal-open');
        
        // 添加模态框背景
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
    }
    
    console.log('模态框显示完成');
}

// 编辑用户
function editUser(userId) {
    console.log('编辑用户:', userId);
    const user = users.find(u => u.id === userId);
    if (!user) {
        console.error('未找到用户:', userId);
        return;
    }

    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('userModalLabel');
    const form = document.getElementById('userForm');
    
    if (!modal) {
        console.error('未找到模态框: userModal');
        return;
    }
    
    modalTitle.textContent = '编辑用户';
    
    // 安全地填充表单数据，添加元素存在性检查
    const elements = {
        'userId': user.id,
        'username': user.username,
        'first_name': user.first_name || '',
        'email': user.email || '',
        'phone': user.phone || '',
        'wechat_id': user.wechat_id || '',
        'employee_id': user.employee_id || '',
        'department': user.department_id || '',
        'position': user.position_id || ''
    };
    
    // 逐个设置表单字段值
    Object.keys(elements).forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element) {
            element.value = elements[fieldId];
            console.log(`设置字段 ${fieldId}: ${elements[fieldId]}`);
        } else {
            console.warn(`字段 ${fieldId} 不存在`);
        }
    });
    
    // 修复is_active字段设置 - 使用select元素
    const isActiveSelect = document.getElementById('is_active');
    if (isActiveSelect) {
        isActiveSelect.value = user.is_active ? 'true' : 'false';
        console.log(`设置状态: ${user.is_active ? 'true' : 'false'}`);
    } else {
        console.warn('is_active字段不存在');
    }
    
    // 更新部门和职位选项
    updateDepartmentOptions();
    updatePositionOptions();
    
    // 重新设置部门和职位的选中值（因为update函数会重新生成选项）
    const departmentSelect = document.getElementById('department');
    const positionSelect = document.getElementById('position');
    
    if (departmentSelect && user.department_id) {
        departmentSelect.value = user.department_id;
        console.log(`重新设置部门选中值: ${user.department_id}`);
    }
    
    if (positionSelect && user.position_id) {
        positionSelect.value = user.position_id;
        console.log(`重新设置职位选中值: ${user.position_id}`);
    }
    
    console.log('准备显示模态框');
    
    // 显示模态框
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        console.log('使用Bootstrap模态框');
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    } else {
        console.log('使用原生模态框');
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.classList.add('modal-open');
        
        // 添加模态框背景
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
    }
    
    console.log('模态框显示完成');
}

// 更新部门选项
function updateDepartmentOptions() {
    console.log('更新部门选项开始...');
    const select = document.getElementById('department');
    if (!select) {
        console.error('部门选择框未找到');
        return;
    }
    
    console.log('当前部门数据:', departments);
    
    select.innerHTML = '<option value="">请选择部门</option>';
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        select.appendChild(option);
        console.log(`添加部门选项: ${dept.name} (ID: ${dept.id})`);
    });
    
    console.log('部门选项更新完成');
}

// 更新职位选项
function updatePositionOptions() {
    console.log('更新职位选项开始...');
    const select = document.getElementById('position');
    if (!select) {
        console.error('职位选择框未找到');
        return;
    }
    
    console.log('当前职位数据:', positions);
    
    select.innerHTML = '<option value="">请选择职位</option>';
    positions.forEach(pos => {
        const option = document.createElement('option');
        option.value = pos.id;
        option.textContent = `${pos.name} (${pos.department_name})`;
        select.appendChild(option);
        console.log(`添加职位选项: ${pos.name} (${pos.department_name}) (ID: ${pos.id})`);
    });
    
    console.log('职位选项更新完成');
}

// 保存用户
async function saveUser() {
    const form = document.getElementById('userForm');
    const formData = new FormData(form);
    const userId = document.getElementById('userId').value;
    
    // 安全地获取表单数据
    const data = {
        username: formData.get('username'),
        first_name: formData.get('first_name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        wechat_id: formData.get('wechat_id'),
        employee_id: formData.get('employee_id'),
        department_id: formData.get('department'),
        position_id: formData.get('position')
    };
    
    // 安全地获取is_active值
    const isActiveElement = document.getElementById('is_active');
    if (isActiveElement) {
        data.is_active = isActiveElement.value === 'true';
    } else {
        data.is_active = true; // 默认启用
    }
    
    // 处理密码字段（新增和编辑用户时都需要）
    const password = formData.get('password');
    if (password) {
        data.password = password;
    }
    
    console.log('保存用户数据:', data);
    
    try {
        const url = userId ? `/api/user-management/${userId}/` : '/api/user-management/';
        const method = userId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            alert(result.message || '操作成功');
            closeUserModal();
            await loadUsers();
        } else {
            const error = await response.json();
            alert(error.message || '操作失败');
        }
    } catch (error) {
        console.error('保存用户失败:', error);
        alert('操作失败，请稍后重试');
    }
}

// 删除用户
async function deleteUser(userId) {
    if (!confirm('确定要删除这个用户吗？')) return;
    
    try {
        const response = await fetch(`/api/user-management/${userId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            alert('用户删除成功');
            await loadUsers();
        } else {
            const error = await response.json();
            alert(error.message || '删除失败');
        }
    } catch (error) {
        console.error('删除用户失败:', error);
        alert('删除失败，请稍后重试');
    }
}

// 关闭用户模态框
function closeUserModal() {
    console.log('关闭用户模态框');
    
    const modal = document.getElementById('userModal');
    if (!modal) {
        console.error('未找到模态框: userModal');
        return;
    }
    
    // 隐藏模态框
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        console.log('使用Bootstrap关闭模态框');
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    } else {
        console.log('使用原生方式关闭模态框');
        modal.style.display = 'none';
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
        
        // 移除模态框背景
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
    }
    
    console.log('模态框关闭完成');
}

// 切换密码显示
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const toggleBtn = field.nextElementSibling;
    const icon = toggleBtn.querySelector('i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.textContent = 'visibility_off';
    } else {
        field.type = 'password';
        icon.textContent = 'visibility';
    }
}

// 获取Cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 搜索和分页相关函数

// 获取搜索参数
function getSearchParams() {
    const username = document.getElementById('searchUsername')?.value?.trim() || '';
    const name = document.getElementById('searchName')?.value?.trim() || '';
    const email = document.getElementById('searchEmail')?.value?.trim() || '';
    const status = document.getElementById('searchStatus')?.value || '';
    
    const params = {};
    if (username) params.username = username;
    if (name) params.name = name;
    if (email) params.email = email;
    if (status) params.is_active = status;
    
    return params;
}

// 清除搜索条件
function clearSearch() {
    const searchUsername = document.getElementById('searchUsername');
    const searchName = document.getElementById('searchName');
    const searchEmail = document.getElementById('searchEmail');
    const searchStatus = document.getElementById('searchStatus');
    
    if (searchUsername) searchUsername.value = '';
    if (searchName) searchName.value = '';
    if (searchEmail) searchEmail.value = '';
    if (searchStatus) searchStatus.value = '';
    
    searchParams = {};
    currentPage = 1;
    loadUsers();
}

// 更新分页信息
function updatePagination(data) {
    const paginationContainer = document.getElementById('pagination-container');
    const paginationInfo = document.getElementById('pagination-info');
    const pageNumbers = document.getElementById('page-numbers');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    if (!paginationContainer || !paginationInfo || !pageNumbers || !prevBtn || !nextBtn) {
        console.error('分页元素未找到');
        return;
    }
    
    if (data.count !== undefined) {
        // 分页数据
        totalCount = data.count;
        totalPages = Math.ceil(totalCount / pageSize);
        
        // 显示分页信息
        const start = (currentPage - 1) * pageSize + 1;
        const end = Math.min(currentPage * pageSize, totalCount);
        paginationInfo.textContent = `显示第 ${start}-${end} 条，共 ${totalCount} 条记录`;
        
        // 更新分页按钮
        prevBtn.disabled = currentPage <= 1;
        nextBtn.disabled = currentPage >= totalPages;
        
        // 生成页码按钮
        pageNumbers.innerHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-btn ${i === currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => goToPage(i);
            pageNumbers.appendChild(pageBtn);
        }
        
        paginationContainer.style.display = 'flex';
    } else {
        // 非分页数据，隐藏分页控件
        hidePagination();
    }
}

// 隐藏分页控件
function hidePagination() {
    const paginationContainer = document.getElementById('pagination-container');
    if (paginationContainer) {
        paginationContainer.style.display = 'none';
    }
}

// 切换页面
function changePage(delta) {
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        loadUsers();
    }
}

// 跳转到指定页面
function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        loadUsers();
    }
} 