// 当前编辑的产品型号ID
window.currentProductModelId = null;



// 加载产品型号列表
function loadProductModels() {
    fetch('/api/product-models/')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const tbody = document.getElementById('productModelTableBody');
                tbody.innerHTML = '';
                data.data.forEach(model => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${model.id}</td>
                        <td>${model.name}</td>
                        <td>${model.created_at}</td>
                        <td>${model.updated_at}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="showEditProductModelModal(${model.id}, '${model.name}')">
                                <span class="material-icons">edit</span>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteProductModel(${model.id})">
                                <span class="material-icons">delete</span>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            }
        })
        .catch(error => console.error('Error:', error));
}

// 显示新增产品型号模态框
function showAddProductModelModal() {
    window.currentProductModelId = null;
    document.getElementById('productModelModalTitle').textContent = '新增产品型号';
    document.getElementById('productModelName').value = '';
    document.getElementById('productModelModal').style.display = 'block';
}

// 显示编辑产品型号模态框
function showEditProductModelModal(id, name) {
    window.currentProductModelId = id;
    document.getElementById('productModelModalTitle').textContent = '编辑产品型号';
    document.getElementById('productModelName').value = name;
    document.getElementById('productModelModal').style.display = 'block';
}

// 关闭产品型号模态框
function closeProductModelModal() {
    document.getElementById('productModelModal').style.display = 'none';
}

// 保存产品型号
function saveProductModel() {
    const name = document.getElementById('productModelName').value;
    if (!name) {
        alert('请输入产品型号名称');
        return;
    }

    const url = window.currentProductModelId 
        ? `/api/product-models/${window.currentProductModelId}/`
        : '/api/product-models/';
    
    const method = window.currentProductModelId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            closeProductModelModal();
            loadProductModels();
            alert(data.message);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('操作失败');
    });
}

// 删除产品型号
function deleteProductModel(id) {
    if (!confirm('确定要删除这个产品型号吗？')) {
        return;
    }

    fetch(`/api/product-models/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadProductModels();
            alert(data.message);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('删除失败');
    });
}

// 页面加载时加载产品型号数据
document.addEventListener('DOMContentLoaded', function() {
    loadProductModels();
}); 