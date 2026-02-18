window.API_BASE_URL = window.API_BASE_URL || window.location.origin;
window.currentOrgId = window.currentOrgId || null;
window.currentMaterialId = window.currentMaterialId || null;
window.currentWarehouseId = window.currentWarehouseId || null;
window.currentCostCenterId = window.currentCostCenterId || null;
window.currentCostObjectId = window.currentCostObjectId || null;

// RBAC管理页面分页和搜索变量
window.roleCurrentPage = 1;
window.roleTotalPages = 1;
window.roleTotalCount = 0;
window.rolePageSize = 10;
window.roleSearchParams = {};

window.permissionCurrentPage = 1;
window.permissionTotalPages = 1;
window.permissionTotalCount = 0;
window.permissionPageSize = 10;
window.permissionSearchParams = {};

window.userRoleCurrentPage = 1;
window.userRoleTotalPages = 1;
window.userRoleTotalCount = 0;
window.userRolePageSize = 10;
window.userRoleSearchParams = {};

// 获取 Cookie
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

// 页面初始化
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Admin.js 初始化开始...');
    
    try {
        const currentPath = window.location.pathname;
        
        // 检查是否是用户管理页面，如果是则跳过admin.js的初始化
        if (currentPath.includes('/system/user-management/')) {
            console.log('用户管理页面，跳过admin.js初始化');
            return;
        } else if (currentPath.includes('/system/organization/')) {
            
        } else if (currentPath.includes('/system/rbac-management/')) {
            // RBAC管理页面 - 初始化搜索和分页功能
            console.log('RBAC管理页面，初始化搜索和分页功能');
            initRBACSearchAndPagination();
            // 延迟加载初始数据，确保页面完全加载
            setTimeout(async () => {
                await loadRBACData();
            }, 100);
        } else {
            // 其他管理页面 - 初始化相关功能
            const initPromises = [];
            
            // 检查页面是否包含库存组织相关元素
            if (document.getElementById('addOrgBtn') || document.getElementById('orgForm') || document.getElementById('orgModal')) {
                initPromises.push(initInventoryOrg());
            }
            
            // 检查页面是否包含物料映射相关元素
            if (document.getElementById('addMaterialBtn') || document.getElementById('materialForm') || document.getElementById('materialModal')) {
                initPromises.push(initMaterialMapping());
            }
            
            // 检查页面是否包含仓库映射相关元素
            if (document.getElementById('addWarehouseBtn') || document.getElementById('warehouseForm') || document.getElementById('warehouseModal')) {
                initPromises.push(initWarehouseMapping());
            }
            
            // 检查页面是否包含成本中心相关元素
            if (document.getElementById('addCostCenterBtn') || document.getElementById('costCenterForm') || document.getElementById('costCenterModal')) {
                initPromises.push(initCostCenterMapping());
            }
            
            // 检查页面是否包含成本对象相关元素
            if (document.getElementById('addCostObjectBtn') || document.getElementById('costObjectForm') || document.getElementById('costObjectModal')) {
                initPromises.push(initCostObjectMapping());
            }
            
            if (initPromises.length > 0) {
                await Promise.all(initPromises);
            }
        }
        
        console.log('Admin.js 页面初始化完成');
    } catch (error) {
        console.error('Admin.js 页面初始化失败:', error);
    }
});


// 初始化库存组织相关功能
async function initInventoryOrg() {
    console.log('开始初始化库存组织功能');

    const addOrgBtn = document.getElementById('addOrgBtn');
    const orgForm = document.getElementById('orgForm');
    const orgModal = document.getElementById('orgModal');

    if (!addOrgBtn || !orgForm || !orgModal) {
        console.log('库存组织元素未找到，跳过初始化');
        return;
    }

    console.log('库存组织元素已找到');

    addOrgBtn.addEventListener('click', function() {
        openOrgModal();
    });

    orgModal.addEventListener('click', function(event) {
        if (event.target === orgModal) {
            closeOrgModal();
        }
    });

    orgForm.addEventListener('submit', function(event) {
        event.preventDefault();
        submitOrgForm(event);
    });

    try {
        console.log('开始加载库存组织数据');
        await loadInventoryOrgs();
        console.log('库存组织数据加载完成');
    } catch (error) {
        console.error('库存组织数据加载失败:', error);
    }
}

// 初始化物料映射相关功能
async function initMaterialMapping() {
    console.log('开始初始化物料映射功能');

    const addMaterialBtn = document.getElementById('addMaterialBtn');
    const materialForm = document.getElementById('materialForm');
    const materialModal = document.getElementById('materialModal');

    if (!addMaterialBtn || !materialForm || !materialModal) {
        console.log('物料映射元素未找到，跳过初始化');
        return;
    }

    console.log('物料映射元素已找到');

    addMaterialBtn.addEventListener('click', function() {
        openMaterialModal();
    });

    materialModal.addEventListener('click', function(event) {
        if (event.target === materialModal) {
            closeMaterialModal();
        }
    });

    materialForm.addEventListener('submit', function(event) {
        event.preventDefault();
        submitMaterialForm(event);
    });

    try {
        console.log('开始加载物料数据');
        await loadInventoryMaterials();
        console.log('物料数据加载完成');
    } catch (error) {
        console.error('物料数据加载失败:', error);
    }
}

async function initWarehouseMapping() {
    console.log('开始初始化仓库映射功能');

    const addWarehouseBtn = document.getElementById('addWarehouseBtn');
    const warehouseForm = document.getElementById('warehouseForm');
    const warehouseModal = document.getElementById('warehouseModal');

    if (!addWarehouseBtn || !warehouseForm || !warehouseModal) {
        console.log('仓库映射元素未找到，跳过初始化');
        return;
    }

    console.log('仓库映射元素已找到');

    addWarehouseBtn.addEventListener('click', function() {
        openWarehouseModal();
    });

    warehouseModal.addEventListener('click', function(event) {
        if (event.target === warehouseModal) {
            closeWarehouseModal();
        }
    });

    warehouseForm.addEventListener('submit', function(event) {
        event.preventDefault();
        submitWarehouseForm(event);
    });

    try {
        console.log('开始加载仓库数据');
        await loadInventoryWarehouses();
        console.log('仓库数据加载完成');
    } catch (error) {
        console.error('仓库数据加载失败:', error);
    }
}

async function initCostCenterMapping() {
    console.log('开始初始化成本中心映射功能');

    const addCostCenterBtn = document.getElementById('addCostCenterBtn');
    const costCenterForm = document.getElementById('costCenterForm');
    const costCenterModal = document.getElementById('costCenterModal');

    if (!addCostCenterBtn || !costCenterForm || !costCenterModal) {
        console.log('成本中心映射元素未找到，跳过初始化');
        return;
    }

    console.log('成本中心映射元素已找到');

    addCostCenterBtn.addEventListener('click', function() {
        openCostCenterModal();
    });

    costCenterModal.addEventListener('click', function(event) {
        if (event.target === costCenterModal) {
            closeCostCenterModal();
        }
    });

    costCenterForm.addEventListener('submit', function(event) {
        event.preventDefault();
        submitCostCenterForm(event);
    });

    try {
        console.log('开始加载成本中心数据');
        await loadCostCenters();
        console.log('成本中心数据加载完成');
    } catch (error) {
        console.error('成本中心数据加载失败:', error);
    }
}

async function initCostObjectMapping() {
    console.log('开始初始化成本对象映射功能');

    const addCostObjectBtn = document.getElementById('addCostObjectBtn');
    console.log('addCostObjectBtn:', addCostObjectBtn); // 添加调试信息

    const costObjectForm = document.getElementById('costObjectForm');
    const costObjectModal = document.getElementById('costObjectModal');

    if (!addCostObjectBtn || !costObjectForm || !costObjectModal) {
        console.log('成本对象映射元素未找到，跳过初始化');
        return;
    }

    console.log('成本对象映射元素已找到');

    addCostObjectBtn.addEventListener('click', function() {
        console.log('新增成本对象按钮被点击'); // 添加调试信息
        openCostObjectModal();
    });

    costObjectModal.addEventListener('click', function(event) {
        if (event.target === costObjectModal) {
            closeCostObjectModal();
        }
    });

    costObjectForm.addEventListener('submit', function(event) {
        event.preventDefault();
        submitCostObjectForm(event);
    });

    try {
        console.log('开始加载成本对象数据');
        await loadCostObjects();
        console.log('成本对象数据加载完成');
    } catch (error) {
        console.error('成本对象数据加载失败:', error);
    }
}
//库存组织动作
function openOrgModal(isEdit = false) {
    const modal = document.getElementById('orgModal');
    const modalTitle = document.getElementById('modalTitle');
    const orgForm = document.getElementById('orgForm');

    modalTitle.textContent = isEdit ? '编辑库存组织' : '新增库存组织';
    if (!isEdit) {
        currentOrgId = null;
        orgForm.reset();
    }

    modal.style.display = 'block';
    modal.classList.add('show');

    const inputs = modal.querySelectorAll('input[type="text"]');
    if (inputs.length > 0) {
        inputs[0].focus();
    }
}

function closeOrgModal() {
    const modal = document.getElementById('orgModal');
    modal.classList.remove('show');
    modal.style.display = 'none';
}

async function submitOrgForm(event) {
    event.preventDefault();

    const submitBtn = event.submitter;
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '保存中...';

    try {
        const orgName = document.getElementById('orgName').value;
        const orgCode = document.getElementById('orgCode').value;

        const url = currentOrgId
            ? `${API_BASE_URL}/api/inventory-org/${currentOrgId}/`
            : `${API_BASE_URL}/api/inventory-org/`;

        const response = await fetch(url, {
            method: currentOrgId ? 'PUT' : 'POST',
            credentials: 'include',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                org_name: orgName,
                org_code: orgCode
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '保存失败');
        }

        closeOrgModal();
        await loadInventoryOrgs();
    } catch (error) {
        console.error('Error submitting organization:', error);
        alert(error.message || (currentOrgId ? '更新库存组织失败' : '创建库存组织失败'));
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}


//物料动作
function openMaterialModal(isEdit = false) {
    const modal = document.getElementById('materialModal');
    const modalTitle = document.getElementById('materialModalTitle');
    const materialForm = document.getElementById('materialForm');

    modalTitle.textContent = isEdit ? '编辑物料映射' : '新增物料映射';
    if (!isEdit) {
        currentMaterialId = null;
        materialForm.reset();
    }

    modal.style.display = 'block';
    modal.classList.add('show');

    const inputs = modal.querySelectorAll('input[type="text"]');
    if (inputs.length > 0) {
        inputs[0].focus();
    }
}

function closeMaterialModal() {
    const modal = document.getElementById('materialModal');
    modal.classList.remove('show');
    modal.style.display = 'none';
}

async function submitMaterialForm(event) {
    event.preventDefault();

    const submitBtn = event.submitter;
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '保存中...';

    try {
        const materialCode = document.getElementById('materialCode').value;
        const materialName = document.getElementById('materialName').value;

        const url = currentMaterialId
            ? `${API_BASE_URL}/api/materials/${currentMaterialId}/`
            : `${API_BASE_URL}/api/materials/`;

        const response = await fetch(url, {
            method: currentMaterialId ? 'PUT' : 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                material_code: materialCode,
                material_name: materialName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '保存失败');
        }

        closeMaterialModal();
        await loadInventoryMaterials();
    } catch (error) {
        console.error('Error submitting material:', error);
        alert(error.message || (currentMaterialId ? '更新物料失败' : '创建物料失败'));
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// 仓库动作
function openWarehouseModal(isEdit = false) {
    const modal = document.getElementById('warehouseModal');
    const modalTitle = document.getElementById('warehouseModalTitle');
    const warehouseForm = document.getElementById('warehouseForm');

    modalTitle.textContent = isEdit ? '编辑仓库映射' : '新增仓库映射';
    if (!isEdit) {
        currentWarehouseId = null;
        warehouseForm.reset();
    }

    modal.style.display = 'block';
    modal.classList.add('show');

    const inputs = modal.querySelectorAll('input[type="text"]');
    if (inputs.length > 0) {
        inputs[0].focus();
    }
}

function closeWarehouseModal() {
    const modal = document.getElementById('warehouseModal');
    modal.classList.remove('show');
    modal.style.display = 'none';
}

async function submitWarehouseForm(event) {
    event.preventDefault();

    const submitBtn = event.submitter;
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '保存中...';



    try {
        const warehouseCode = document.getElementById('warehouseCode').value;
        const warehouseName = document.getElementById('warehouseName').value;

        const url = currentWarehouseId
            ? `${API_BASE_URL}/api/warehouses/${currentWarehouseId}/`
            : `${API_BASE_URL}/api/warehouses/`;

        const response = await fetch(url, {
            method: currentWarehouseId ? 'PUT' : 'POST',
            credentials: 'include',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                warehouse_code: warehouseCode,
                warehouse_name: warehouseName
            })
        });
        console.log('收到响应:', response);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '保存失败');
        }

        closeWarehouseModal();
        await loadInventoryWarehouses();
    } catch (error) {
        console.error('Error submitting warehouse:', error);
        alert(error.message || (currentWarehouseId ? '更新仓库失败' : '创建仓库失败'));
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}


async function loadInventoryOrgs() {
    const orgTable = document.getElementById('orgTable');
    try {
        orgTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">加载中...</td></tr>';

        const response = await fetch(`${API_BASE_URL}/api/inventory-org/`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('加载失败');
        }

        const orgs = await response.json();

        if (orgs.length === 0) {
            orgTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">暂无数据</td></tr>';
            return;
        }

        orgTable.innerHTML = orgs.map(org => `
            <tr>
                <td>${org.id}</td>
                <td>${org.org_name}</td>
                <td>${org.org_code}</td>
                <td>${org.created_at}</td>
                <td>
                    <button onclick="editOrg(${org.id}, '${org.org_name}', '${org.org_code}')" class="btn btn-primary">编辑</button>
                    <button onclick="deleteOrg(${org.id})" class="btn btn-danger">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading inventory organizations:', error);
        orgTable.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">加载失败，请刷新页面重试</td></tr>';
    }
}

async function loadInventoryMaterials() {
    const materialTable = document.getElementById('materialTable');
    try {
        materialTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">加载中...</td></tr>';

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`${API_BASE_URL}/api/materials/`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        let result;
        try {
            result = await response.json();
        } catch (e) {
            console.error('解析响应JSON失败:', e);
            throw new Error('服务器响应格式错误');
        }

        if (!response.ok || result.status !== 'success') {
            throw new Error(result.message || '加载失败');
        }

        const materials = result.data;

        if (!Array.isArray(materials)) {
            console.error('非预期的数据格式:', result);
            throw new Error('数据格式错误');
        }

        if (materials.length === 0) {
            materialTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">暂无数据</td></tr>';
            return;
        }

        materialTable.innerHTML = materials.map(material => {
            // 使用HTML转义来防止XSS攻击
            const escapedCode = material.material_code.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);
            const escapedName = material.material_name.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);

            return `
                <tr>
                    <td>${material.id}</td>
                    <td>${escapedCode}</td>
                    <td>${escapedName}</td>
                    <td>${material.created_at}</td>
                    <td>
                        <button onclick="editMaterial(${material.id}, '${escapedCode}', '${escapedName}')" class="btn btn-primary">编辑</button>
                        <button onclick="deleteMaterial(${material.id})" class="btn btn-danger">删除</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading materials:', error);
        materialTable.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">加载失败: ${error.message}</td></tr>`;
    }
}

async function loadInventoryWarehouses() {
    const warehouseTable = document.getElementById('warehouseTable');
    try {
        warehouseTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">加载中...</td></tr>';

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`${API_BASE_URL}/api/warehouses/`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        let result;
        try {
            result = await response.json();
        } catch (e) {
            console.error('解析响应JSON失败:', e);
            throw new Error('服务器响应格式错误');
        }

        if (!response.ok || result.status !== 'success') {
            throw new Error(result.message || '加载失败');
        }

        const warehouses = result.data;

        if (!Array.isArray(warehouses)) {
            console.error('非预期的数据格式:', result);
            throw new Error('数据格式错误');
        }

        if (warehouses.length === 0) {
            warehouseTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">暂无数据</td></tr>';
            return;
        }

        warehouseTable.innerHTML = warehouses.map(warehouse => {
            // 使用HTML转义来防止XSS攻击
            const escapedCode = warehouse.warehouse_code.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);
            const escapedName = warehouse.warehouse_name.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);

            return `
                <tr>
                    <td>${warehouse.id}</td>
                    <td>${escapedCode}</td>
                    <td>${escapedName}</td>
                    <td>${warehouse.created_at}</td>
                    <td>
                        <button onclick="editWarehouse(${warehouse.id}, '${escapedCode}', '${escapedName}')" class="btn btn-primary">编辑</button>
                        <button onclick="deleteWarehouse(${warehouse.id})" class="btn btn-danger">删除</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading warehouses:', error);
        warehouseTable.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">加载失败: ${error.message}</td></tr>`;
    }
}

async function loadCostCenters() {
    const costCenterTable = document.getElementById('costCenterTable');
    try {
        costCenterTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">加载中...</td></tr>';

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`${API_BASE_URL}/api/cost-centers/`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        console.log('收到响应:', response);  // 添加调试信息

        if (response.headers.get('Content-Type') !== 'application/json') {
            const text = await response.text();
            console.error('非 JSON 响应:', text);
            throw new Error('服务器响应格式错误');
        }

        let result;
        try {
            result = await response.json();
        } catch (e) {
            console.error('解析响应JSON失败:', e);
            const text = await response.text();  // 获取原始文本
            console.error('原始响应文本:', text);  // 输出原始响应文本
            throw new Error('服务器响应格式错误');
        }

        if (!response.ok || result.status !== 'success') {
            throw new Error(result.message || '加载失败');
        }

        const costCenters = result.data;

        if (!Array.isArray(costCenters)) {
            console.error('非预期的数据格式:', result);
            throw new Error('数据格式错误');
        }

        if (costCenters.length === 0) {
            costCenterTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">暂无数据</td></tr>';
            return;
        }

        costCenterTable.innerHTML = costCenters.map(costCenter => {
            const escapedCode = costCenter.cost_center_code.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);
            const escapedName = costCenter.cost_center_name.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);

            return `
                <tr>
                    <td>${costCenter.id}</td>
                    <td>${escapedCode}</td>
                    <td>${escapedName}</td>
                    <td>${costCenter.created_at}</td>
                    <td>
                        <button onclick="editCostCenter(${costCenter.id}, '${escapedCode}', '${escapedName}')" class="btn btn-primary">编辑</button>
                        <button onclick="deleteCostCenter(${costCenter.id})" class="btn btn-danger">删除</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading cost centers:', error);
        costCenterTable.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">加载失败: ${error.message}</td></tr>`;
    }
}

async function loadCostObjects() {
    const costObjectTable = document.getElementById('costObjectTable');
    try {
        costObjectTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">加载中...</td></tr>';

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`${API_BASE_URL}/api/cost-objects/`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        console.log('收到响应:', response);  // 添加调试信息

        if (response.headers.get('Content-Type') !== 'application/json') {
            const text = await response.text();
            console.error('非 JSON 响应:', text);
            throw new Error('服务器响应格式错误');
        }

        let result;
        try {
            result = await response.json();
        } catch (e) {
            console.error('解析响应JSON失败:', e);
            const text = await response.text();  // 获取原始文本
            console.error('原始响应文本:', text);  // 输出原始响应文本
            throw new Error('服务器响应格式错误');
        }

        if (!response.ok || result.status !== 'success') {
            throw new Error(result.message || '加载失败');
        }

        const costObjects = result.data;

        if (!Array.isArray(costObjects)) {
            console.error('非预期的数据格式:', result);
            throw new Error('数据格式错误');
        }

        if (costObjects.length === 0) {
            costObjectTable.innerHTML = '<tr><td colspan="5" style="text-align: center;">暂无数据</td></tr>';
            return;
        }

        costObjectTable.innerHTML = costObjects.map(costObject => {
            const escapedCode = costObject.cost_object_code.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);
            const escapedName = costObject.cost_object_name.replace(/["'&<>]/g, char => ({
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            })[char]);

            return `
                <tr>
                    <td>${costObject.id}</td>
                    <td>${escapedCode}</td>
                    <td>${escapedName}</td>
                    <td>${costObject.created_at}</td>
                    <td>
                        <button onclick="editCostObject(${costObject.id}, '${escapedCode}', '${escapedName}')" class="btn btn-primary">编辑</button>
                        <button onclick="deleteCostObject(${costObject.id})" class="btn btn-danger">删除</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading cost objects:', error);
        costObjectTable.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">加载失败: ${error.message}</td></tr>`;
    }
}

//成本中心动作
function openCostCenterModal(isEdit = false) {
    const modal = document.getElementById('costCenterModal');
    const modalTitle = document.getElementById('costCenterModalTitle');
    const costCenterForm = document.getElementById('costCenterForm');

    modalTitle.textContent = isEdit ? '编辑成本中心映射' : '新增成本中心映射';
    if (!isEdit) {
        currentCostCenterId = null;
        costCenterForm.reset();  // 重置表单
    } else {
        console.log(`Opening modal for editing - ID: ${currentCostCenterId}`);  // 添加调试信息
    }

    modal.style.display = 'block';
    modal.classList.add('show');

    const inputs = modal.querySelectorAll('input[type="text"]');
    if (inputs.length > 0) {
        inputs[0].focus();
    }
}

function closeCostCenterModal() {
    const modal = document.getElementById('costCenterModal');
    modal.classList.remove('show');
    modal.style.display = 'none';
}

async function submitCostCenterForm(event) {
    event.preventDefault();

    const submitBtn = event.submitter;
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '保存中...';



    try {
        const costCenterCode = document.getElementById('costCenterCode').value;
        const costCenterName = document.getElementById('costCenterName').value;

        const url = currentCostCenterId
            ? `${API_BASE_URL}/api/cost-centers/${currentCostCenterId}/`
            : `${API_BASE_URL}/api/cost-centers/`;

        const response = await fetch(url, {
            method: currentCostCenterId ? 'PUT' : 'POST',
            credentials: 'include',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cost_center_code: costCenterCode,
                cost_center_name: costCenterName
            })
        });
        console.log('收到响应:', response);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '保存失败');
        }

        closeCostCenterModal();
        await loadCostCenters();
    } catch (error) {
        console.error('Error submitting cost center:', error);
        alert(error.message || (currentCostCenterId ? '更新成本中心失败' : '创建成本中心失败'));
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}
//成本对象动作
function openCostObjectModal(isEdit = false) {
    console.log('打开成本对象模态框'); // 添加调试信息
    const modal = document.getElementById('costObjectModal');
    const modalTitle = document.getElementById('costObjectModalTitle');
    const costObjectForm = document.getElementById('costObjectForm');

    modalTitle.textContent = isEdit ? '编辑成本对象' : '新增成本对象';
    if (!isEdit) {
        currentCostObjectId = null;
        costObjectForm.reset();  // 重置表单
    }

    modal.style.display = 'block';
    modal.classList.add('show');

    const inputs = modal.querySelectorAll('input[type="text"]');
    if (inputs.length > 0) {
        inputs[0].focus();
    }
}

// 关闭成本对象模态框
function closeCostObjectModal() {
    const modal = document.getElementById('costObjectModal');
    modal.classList.remove('show');
    modal.style.display = 'none';
}

// 提交成本对象表单
async function submitCostObjectForm(event) {
    event.preventDefault();

    const submitBtn = event.submitter;
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '保存中...';

    try {
        const costObjectCode = document.getElementById('costObjectCode').value;
        const costObjectName = document.getElementById('costObjectName').value;

        const url = currentCostObjectId
            ? `${API_BASE_URL}/api/cost-objects/${currentCostObjectId}/`
            : `${API_BASE_URL}/api/cost-objects/`;

        const response = await fetch(url, {
            method: currentCostObjectId ? 'PUT' : 'POST',
            credentials: 'include',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cost_object_code: costObjectCode,
                cost_object_name: costObjectName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || '保存失败');
        }

        closeCostObjectModal();
        await loadCostObjects();
    } catch (error) {
        console.error('Error submitting cost object:', error);
        alert(error.message || (currentCostObjectId ? '更新成本对象失败' : '创建成本对象失败'));
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// RBAC搜索和分页功能

// 初始化RBAC搜索和分页
function initRBACSearchAndPagination() {
    console.log('初始化RBAC搜索和分页功能');
    
    // 绑定角色搜索表单事件
    const roleSearchForm = document.getElementById('roleSearchForm');
    if (roleSearchForm) {
        roleSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            window.roleCurrentPage = 1;
            loadRoles();
        });
    }
    
    // 绑定权限搜索表单事件
    const permissionSearchForm = document.getElementById('permissionSearchForm');
    if (permissionSearchForm) {
        permissionSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            window.permissionCurrentPage = 1;
            loadPermissions();
        });
    }
    
    // 绑定用户角色搜索表单事件
    const userRoleSearchForm = document.getElementById('userRoleSearchForm');
    if (userRoleSearchForm) {
        userRoleSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            window.userRoleCurrentPage = 1;
            loadUserRoles();
        });
    }
}

// 角色相关函数
function getRoleSearchParams() {
    const roleName = document.getElementById('searchRoleName')?.value?.trim() || '';
    const roleDescription = document.getElementById('searchRoleDescription')?.value?.trim() || '';
    
    const params = {};
    if (roleName) params.role_name = roleName;
    if (roleDescription) params.description = roleDescription;
    
    return params;
}

function clearRoleSearch() {
    const searchRoleName = document.getElementById('searchRoleName');
    const searchRoleDescription = document.getElementById('searchRoleDescription');
    
    if (searchRoleName) searchRoleName.value = '';
    if (searchRoleDescription) searchRoleDescription.value = '';
    
    window.roleSearchParams = {};
    window.roleCurrentPage = 1;
    loadRoles();
}

function updateRolePagination(data) {
    const paginationContainer = document.getElementById('role-pagination-container');
    const paginationInfo = document.getElementById('role-pagination-info');
    const pageNumbers = document.getElementById('role-page-numbers');
    const prevBtn = document.getElementById('role-prev-page');
    const nextBtn = document.getElementById('role-next-page');
    
    if (!paginationContainer || !paginationInfo || !pageNumbers || !prevBtn || !nextBtn) {
        console.error('角色分页元素未找到');
        return;
    }
    
    if (data.count !== undefined) {
        window.roleTotalCount = data.count;
        window.roleTotalPages = Math.ceil(window.roleTotalCount / window.rolePageSize);
        
        const start = (window.roleCurrentPage - 1) * window.rolePageSize + 1;
        const end = Math.min(window.roleCurrentPage * window.rolePageSize, window.roleTotalCount);
        paginationInfo.textContent = `显示第 ${start}-${end} 条，共 ${window.roleTotalCount} 条记录`;
        
        prevBtn.disabled = window.roleCurrentPage <= 1;
        nextBtn.disabled = window.roleCurrentPage >= window.roleTotalPages;
        
        pageNumbers.innerHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, window.roleCurrentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(window.roleTotalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-btn ${i === window.roleCurrentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => goToRolePage(i);
            pageNumbers.appendChild(pageBtn);
        }
        
        paginationContainer.style.display = 'flex';
    } else {
        paginationContainer.style.display = 'none';
    }
}

function changeRolePage(delta) {
    const newPage = window.roleCurrentPage + delta;
    if (newPage >= 1 && newPage <= window.roleTotalPages) {
        window.roleCurrentPage = newPage;
        loadRoles();
    }
}

function goToRolePage(page) {
    if (page >= 1 && page <= window.roleTotalPages) {
        window.roleCurrentPage = page;
        loadRoles();
    }
}

// 权限相关函数
function getPermissionSearchParams() {
    const permissionCode = document.getElementById('searchPermissionCode')?.value?.trim() || '';
    const permissionName = document.getElementById('searchPermissionName')?.value?.trim() || '';
    const permissionType = document.getElementById('searchPermissionType')?.value || '';
    const permissionModule = document.getElementById('searchPermissionModule')?.value?.trim() || '';
    
    const params = {};
    if (permissionCode) params.permission_code = permissionCode;
    if (permissionName) params.permission_name = permissionName;
    if (permissionType) params.permission_type = permissionType;
    if (permissionModule) params.module = permissionModule;
    
    return params;
}

function clearPermissionSearch() {
    const searchPermissionCode = document.getElementById('searchPermissionCode');
    const searchPermissionName = document.getElementById('searchPermissionName');
    const searchPermissionType = document.getElementById('searchPermissionType');
    const searchPermissionModule = document.getElementById('searchPermissionModule');
    
    if (searchPermissionCode) searchPermissionCode.value = '';
    if (searchPermissionName) searchPermissionName.value = '';
    if (searchPermissionType) searchPermissionType.value = '';
    if (searchPermissionModule) searchPermissionModule.value = '';
    
    window.permissionSearchParams = {};
    window.permissionCurrentPage = 1;
    loadPermissions();
}

function updatePermissionPagination(data) {
    const paginationContainer = document.getElementById('permission-pagination-container');
    const paginationInfo = document.getElementById('permission-pagination-info');
    const pageNumbers = document.getElementById('permission-page-numbers');
    const prevBtn = document.getElementById('permission-prev-page');
    const nextBtn = document.getElementById('permission-next-page');
    
    if (!paginationContainer || !paginationInfo || !pageNumbers || !prevBtn || !nextBtn) {
        console.error('权限分页元素未找到');
        return;
    }
    
    if (data.count !== undefined) {
        window.permissionTotalCount = data.count;
        window.permissionTotalPages = Math.ceil(window.permissionTotalCount / window.permissionPageSize);
        
        const start = (window.permissionCurrentPage - 1) * window.permissionPageSize + 1;
        const end = Math.min(window.permissionCurrentPage * window.permissionPageSize, window.permissionTotalCount);
        paginationInfo.textContent = `显示第 ${start}-${end} 条，共 ${window.permissionTotalCount} 条记录`;
        
        prevBtn.disabled = window.permissionCurrentPage <= 1;
        nextBtn.disabled = window.permissionCurrentPage >= window.permissionTotalPages;
        
        pageNumbers.innerHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, window.permissionCurrentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(window.permissionTotalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-btn ${i === window.permissionCurrentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => goToPermissionPage(i);
            pageNumbers.appendChild(pageBtn);
        }
        
        paginationContainer.style.display = 'flex';
    } else {
        paginationContainer.style.display = 'none';
    }
}

function changePermissionPage(delta) {
    const newPage = window.permissionCurrentPage + delta;
    if (newPage >= 1 && newPage <= window.permissionTotalPages) {
        window.permissionCurrentPage = newPage;
        loadPermissions();
    }
}

function goToPermissionPage(page) {
    if (page >= 1 && page <= window.permissionTotalPages) {
        window.permissionCurrentPage = page;
        loadPermissions();
    }
}

// 用户角色相关函数
function getUserRoleSearchParams() {
    const username = document.getElementById('searchUserRoleUsername')?.value?.trim() || '';
    const name = document.getElementById('searchUserRoleName')?.value?.trim() || '';
    const role = document.getElementById('searchUserRoleRole')?.value || '';
    
    const params = {};
    if (username) params.username = username;
    if (name) params.name = name;
    if (role) params.role = role;
    
    return params;
}

function clearUserRoleSearch() {
    const searchUserRoleUsername = document.getElementById('searchUserRoleUsername');
    const searchUserRoleName = document.getElementById('searchUserRoleName');
    const searchUserRoleRole = document.getElementById('searchUserRoleRole');
    
    if (searchUserRoleUsername) searchUserRoleUsername.value = '';
    if (searchUserRoleName) searchUserRoleName.value = '';
    if (searchUserRoleRole) searchUserRoleRole.value = '';
    
    window.userRoleSearchParams = {};
    window.userRoleCurrentPage = 1;
    loadUserRoles();
}

function updateUserRolePagination(data) {
    const paginationContainer = document.getElementById('userRole-pagination-container');
    const paginationInfo = document.getElementById('userRole-pagination-info');
    const pageNumbers = document.getElementById('userRole-page-numbers');
    const prevBtn = document.getElementById('userRole-prev-page');
    const nextBtn = document.getElementById('userRole-next-page');
    
    if (!paginationContainer || !paginationInfo || !pageNumbers || !prevBtn || !nextBtn) {
        console.error('用户角色分页元素未找到');
        return;
    }
    
    if (data.count !== undefined) {
        window.userRoleTotalCount = data.count;
        window.userRoleTotalPages = Math.ceil(window.userRoleTotalCount / window.userRolePageSize);
        
        const start = (window.userRoleCurrentPage - 1) * window.userRolePageSize + 1;
        const end = Math.min(window.userRoleCurrentPage * window.userRolePageSize, window.userRoleTotalCount);
        paginationInfo.textContent = `显示第 ${start}-${end} 条，共 ${window.userRoleTotalCount} 条记录`;
        
        prevBtn.disabled = window.userRoleCurrentPage <= 1;
        nextBtn.disabled = window.userRoleCurrentPage >= window.userRoleTotalPages;
        
        pageNumbers.innerHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, window.userRoleCurrentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(window.userRoleTotalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-btn ${i === window.userRoleCurrentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => goToUserRolePage(i);
            pageNumbers.appendChild(pageBtn);
        }
        
        paginationContainer.style.display = 'flex';
    } else {
        paginationContainer.style.display = 'none';
    }
}

function changeUserRolePage(delta) {
    const newPage = window.userRoleCurrentPage + delta;
    if (newPage >= 1 && newPage <= window.userRoleTotalPages) {
        window.userRoleCurrentPage = newPage;
        loadUserRoles();
    }
}

function goToUserRolePage(page) {
    if (page >= 1 && page <= window.userRoleTotalPages) {
        window.userRoleCurrentPage = page;
        loadUserRoles();
    }
}

// 加载RBAC数据
async function loadRBACData() {
    console.log('开始加载RBAC数据');
    
    try {
        // 加载角色数据
        await loadRoles();
        console.log('角色数据加载完成');
        
        // 加载权限数据
        await loadPermissions();
        console.log('权限数据加载完成');
        
        // 加载用户角色数据
        await loadUserRoles();
        console.log('用户角色数据加载完成');
        
        console.log('RBAC数据加载完成');
    } catch (error) {
        console.error('RBAC数据加载失败:', error);
    }
}

// 加载角色数据
async function loadRoles() {
    try {
        console.log('Loading roles...');
        
        // 获取搜索参数
        const searchParams = getRoleSearchParams();
        console.log('角色搜索参数:', searchParams);
        
        // 构建查询参数
        const params = new URLSearchParams({
            page: window.roleCurrentPage,
            page_size: window.rolePageSize,
            ...searchParams
        });
        
        const url = `/api/rbac/roles/?${params.toString()}`;
        console.log('请求URL:', url);
        
        const response = await fetch(url);
        console.log('角色API响应状态:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('角色API响应数据:', data);
            
            if (data.data && data.data.results) {
                // 分页数据格式
                const roles = data.data.results;
                window.roleTotalCount = data.data.count;
                window.roleTotalPages = data.data.total_pages;
                updateRolePagination(data.data);
                renderRoleTable(roles);
                console.log('角色数据加载完成 (分页格式):', roles.length);
            } else {
                // 兼容旧格式
                const roles = data.data || [];
                window.roleTotalCount = roles.length;
                window.roleTotalPages = 1;
                renderRoleTable(roles);
                console.log('角色数据加载完成 (旧格式):', roles.length);
            }
        } else {
            console.error('加载角色数据失败:', response.status);
            const errorData = await response.text();
            console.error('错误详情:', errorData);
        }
    } catch (error) {
        console.error('加载角色数据出错:', error);
    }
}

// 加载权限数据
async function loadPermissions() {
    try {
        console.log('Loading permissions...');
        
        // 获取搜索参数
        const searchParams = getPermissionSearchParams();
        console.log('权限搜索参数:', searchParams);
        
        // 构建查询参数
        const params = new URLSearchParams({
            page: window.permissionCurrentPage,
            page_size: window.permissionPageSize,
            ...searchParams
        });
        
        const url = `/api/rbac/permissions/?${params.toString()}`;
        console.log('请求URL:', url);
        
        const response = await fetch(url);
        console.log('权限API响应状态:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('权限API响应数据:', data);
            
            if (data.data && data.data.results) {
                // 分页数据格式
                const permissions = data.data.results;
                window.permissionTotalCount = data.data.count;
                window.permissionTotalPages = data.data.total_pages;
                updatePermissionPagination(data.data);
                renderPermissionTable(permissions);
                console.log('权限数据加载完成 (分页格式):', permissions.length);
            } else {
                // 兼容旧格式
                const permissions = data.data || [];
                window.permissionTotalCount = permissions.length;
                window.permissionTotalPages = 1;
                renderPermissionTable(permissions);
                console.log('权限数据加载完成 (旧格式):', permissions.length);
            }
        } else {
            console.error('加载权限数据失败:', response.status);
            const errorData = await response.text();
            console.error('错误详情:', errorData);
        }
    } catch (error) {
        console.error('加载权限数据出错:', error);
    }
}

// 加载用户角色数据
async function loadUserRoles() {
    try {
        console.log('Loading user roles...');
        
        // 获取搜索参数
        const searchParams = getUserRoleSearchParams();
        console.log('用户角色搜索参数:', searchParams);
        
        // 构建查询参数
        const params = new URLSearchParams({
            page: window.userRoleCurrentPage,
            page_size: window.userRolePageSize,
            ...searchParams
        });
        
        const url = `/api/rbac/user-roles/?${params.toString()}`;
        console.log('请求URL:', url);
        
        const response = await fetch(url);
        console.log('用户角色API响应状态:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('用户角色API响应数据:', data);
            
            if (data.data && data.data.results) {
                // 分页数据格式
                const userRoles = data.data.results;
                window.userRoleTotalCount = data.data.count;
                window.userRoleTotalPages = data.data.total_pages;
                updateUserRolePagination(data.data);
                renderUserRoleTable(userRoles);
                console.log('用户角色数据加载完成 (分页格式):', userRoles.length);
            } else {
                // 兼容旧格式
                const userRoles = data.data || [];
                window.userRoleTotalCount = userRoles.length;
                window.userRoleTotalPages = 1;
                renderUserRoleTable(userRoles);
                console.log('用户角色数据加载完成 (旧格式):', userRoles.length);
            }
        } else {
            console.error('加载用户角色数据失败:', response.status);
            const errorData = await response.text();
            console.error('错误详情:', errorData);
        }
    } catch (error) {
        console.error('加载用户角色数据出错:', error);
    }
}

// 渲染角色表格
function renderRoleTable(roles) {
    const tbody = document.getElementById('roleTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (roles.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">暂无数据</td></tr>';
        return;
    }
    
    roles.forEach(role => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${role.id}</td>
            <td>${role.name}</td>
            <td>${role.description || '-'}</td>
            <td>${role.user_count || 0}</td>
            <td>${role.permission_count || 0}</td>
            <td>${role.created_at}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="editRole(${role.id})" title="编辑角色">
                        <i class="material-icons" data-icon="edit">edit</i> 编辑
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="manageRolePermissions(${role.id})" title="管理权限">
                        <i class="material-icons" data-icon="security">security</i> 权限
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteRole(${role.id})" title="删除角色">
                        <i class="material-icons" data-icon="delete">delete</i> 删除
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // 调试信息
    console.log('角色表格渲染完成，角色数量:', roles.length);
    console.log('表格行数:', tbody.children.length);
    
    // 检查按钮是否正确渲染
    const permissionButtons = tbody.querySelectorAll('button[onclick*="manageRolePermissions"]');
    console.log('权限按钮数量:', permissionButtons.length);
    
    if (permissionButtons.length === 0) {
        console.error('❌ 没有找到权限按钮！');
    } else {
        console.log('✅ 权限按钮渲染正常');
    }
}

// 渲染权限表格
function renderPermissionTable(permissions) {
    const tbody = document.getElementById('permissionTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (permissions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">暂无数据</td></tr>';
        return;
    }
    
    permissions.forEach(permission => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${permission.code}</td>
            <td>${permission.name}</td>
            <td>${permission.permission_type}</td>
            <td>${permission.module || '-'}</td>
            <td>${permission.description || '-'}</td>
            <td>${permission.role_count || 0}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="editPermission(${permission.id})">
                        <i class="material-icons" data-icon="edit">edit</i>
                        编辑
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deletePermission(${permission.id})">
                        <i class="material-icons" data-icon="delete">delete</i>
                        删除
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 渲染用户角色表格
function renderUserRoleTable(userRoles) {
    const tbody = document.getElementById('userRoleTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    
    if (userRoles.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">暂无数据</td></tr>';
        return;
    }
    
    userRoles.forEach(userRole => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${userRole.user.id}</td>
            <td>${userRole.user.username}</td>
            <td>${userRole.user.first_name} ${userRole.user.last_name || ''}</td>
            <td>${userRole.role.name}</td>
            <td>${userRole.created_at}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-danger" onclick="deleteUserRole(${userRole.id})">
                        <i class="material-icons" data-icon="delete">delete</i>
                        删除
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}
