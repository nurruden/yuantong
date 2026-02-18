// 使用window对象存储变量，避免重复声明
window.currentPackagingId = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadPackagings();
});

// 加载包装物列表
function loadPackagings() {
    fetch('/api/packagings/')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const tbody = document.getElementById('packagingTableBody');
                tbody.innerHTML = '';
                data.data.forEach(packaging => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${packaging.id}</td>
                        <td>${packaging.name}</td>
                        <td>${packaging.created_at}</td>
                        <td>${packaging.updated_at}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="editPackaging(${packaging.id})">
                                <span class="material-icons">edit</span> 编辑
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deletePackaging(${packaging.id})">
                                <span class="material-icons">delete</span> 删除
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                alert('加载包装物列表失败：' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('加载包装物列表失败，请检查网络连接');
        });
}

// 显示新增包装物模态框
function showAddPackagingModal() {
    window.currentPackagingId = null;
    document.getElementById('packagingModalTitle').textContent = '新增包装物';
    document.getElementById('packagingForm').reset();
    document.getElementById('packagingModal').style.display = 'block';
}

// 显示编辑包装物模态框
function editPackaging(id) {
    window.currentPackagingId = id;
    document.getElementById('packagingModalTitle').textContent = '编辑包装物';
    
    fetch(`/api/packagings/${id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('packagingName').value = data.data.name;
                document.getElementById('packagingModal').style.display = 'block';
            } else {
                alert('获取包装物信息失败：' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('获取包装物信息失败，请检查网络连接');
        });
}

// 关闭包装物模态框
function closePackagingModal() {
    document.getElementById('packagingModal').style.display = 'none';
    document.getElementById('packagingForm').reset();
    window.currentPackagingId = null;
}

// 保存包装物
function savePackaging() {
    const name = document.getElementById('packagingName').value.trim();
    if (!name) {
        alert('请输入包装物名称');
        return;
    }

    const data = {
        name: name
    };

    const url = window.currentPackagingId ? 
        `/api/packagings/${window.currentPackagingId}/` : 
        '/api/packagings/';
    
    const method = window.currentPackagingId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            closePackagingModal();
            loadPackagings();
            alert(window.currentPackagingId ? '包装物更新成功' : '包装物创建成功');
        } else {
            alert((window.currentPackagingId ? '更新' : '创建') + '包装物失败：' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert((window.currentPackagingId ? '更新' : '创建') + '包装物失败，请检查网络连接');
    });
}

// 删除包装物
function deletePackaging(id) {
    if (!confirm('确定要删除这个包装物吗？')) {
        return;
    }

    fetch(`/api/packagings/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadPackagings();
            alert('包装物删除成功');
        } else {
            alert('删除包装物失败：' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('删除包装物失败，请检查网络连接');
    });
} 