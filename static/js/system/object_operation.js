// 全局变量
let currentObjectId = null;
let currentUserId = null;

// 初始化扣水率相关功能
async function initObjectOperation() {
    try {
        console.log('开始初始化对象操作功能');
        
        // 获取必要的DOM元素
        const addObjectBtn = document.querySelector('#addObjectBtn');
        if (!addObjectBtn) {
            throw new Error('新增对象按钮 #addObjectBtn 未找到');
        }
        
        const objectForm = document.querySelector('#objectForm');
        if (!objectForm) {
            throw new Error('对象表单 #objectForm 未找到');
        }
        
        const objectModal = document.querySelector('#objectModal');
        if (!objectModal) {
            throw new Error('对象模态框 #objectModal 未找到');
        }
        
        // 加载初始数据
        await Promise.all([
            loadInventoryOrgsForSelect(),
            loadWarehousesForSelect(),
            loadCostCentersForSelect(),
            loadCostObjectsForSelect(),
            loadObjectTable()
        ]);
        
        console.log('对象操作功能初始化完成');
        
    } catch (error) {
        console.error('初始化对象操作功能失败:', error);
        showMessage(error.message || '初始化对象操作功能失败', 'error');
    }
}

// 加载库存组织下拉列表
async function loadInventoryOrgsForSelect() {
    try {
        console.log('开始加载库存组织列表', { currentObjectId });
        
        // 获取选择器
        const select = document.querySelector('#objectForm #inventory_org_id');
        if (!select) {
            throw new Error('库存组织选择器 #inventory_org_id 未找到');
        }
        
        // 获取所有库存组织
        const orgsResponse = await fetch('/api/inventory-org/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!orgsResponse.ok) {
            const errorData = await orgsResponse.json();
            throw new Error(errorData.error || `HTTP error! status: ${orgsResponse.status}`);
        }
        
        // 获取数据
        const orgs = await orgsResponse.json();
        
        console.log('获取到库存组织数据:', orgs);
        
        if (orgs.length === 0) {
            console.log('没有可用的库存组织');
            return;
        }
        
        // 清空并添加默认选项
        select.innerHTML = '<option value="">请选择库存组织</option>';
        
        // 添加所有库存组织
        orgs.forEach(org => {
            const option = document.createElement('option');
            option.value = org.id;
            option.textContent = org.org_name;
            select.appendChild(option);
        });
        
        console.log('库存组织列表加载完成');
        
    } catch (error) {
        console.error('加载库存组织列表失败:', error);
        showMessage(error.message || '加载库存组织列表失败', 'error');
    }
}

// 加载仓库下拉列表
async function loadWarehousesForSelect() {
    try {
        console.log('开始加载仓库列表');
        
        // 获取选择器
        const select = document.querySelector('#objectForm #warehouse_id');
        if (!select) {
            throw new Error('仓库选择器 #warehouse_id 未找到');
        }
        
        // 获取所有仓库
        const warehousesResponse = await fetch('/api/warehouses/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!warehousesResponse.ok) {
            const errorData = await warehousesResponse.json();
            throw new Error(errorData.error || `HTTP error! status: ${warehousesResponse.status}`);
        }
        
        // 获取数据
        const response = await warehousesResponse.json();
        
        console.log('获取到仓库数据:', response);
        
        // 确保我们有一个数组来处理
        const warehouses = Array.isArray(response) ? response : (response.warehouses || response.data || []);
        
        if (warehouses.length === 0) {
            console.log('没有可用的仓库');
            return;
        }
        
        // 清空并添加默认选项
        select.innerHTML = '<option value="">请选择仓库</option>';
        
        // 添加所有仓库
        warehouses.forEach(warehouse => {
            const option = document.createElement('option');
            option.value = warehouse.id;
            option.textContent = warehouse.warehouse_name || warehouse.name;
            select.appendChild(option);
        });
        
        console.log('仓库列表加载完成');
        
    } catch (error) {
        console.error('加载仓库列表失败:', error);
        showMessage(error.message || '加载仓库列表失败', 'error');
    }
}

// 加载成本中心下拉列表
async function loadCostCentersForSelect() {
    try {
        console.log('开始加载成本中心列表');
        
        // 获取选择器
        const select = document.querySelector('#objectForm #cost_center_id');
        if (!select) {
            throw new Error('成本中心选择器 #cost_center_id 未找到');
        }
        
        // 获取所有成本中心
        const costCentersResponse = await fetch('/api/cost-centers/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!costCentersResponse.ok) {
            const errorData = await costCentersResponse.json();
            throw new Error(errorData.error || `HTTP error! status: ${costCentersResponse.status}`);
        }
        
        // 获取数据
        const response = await costCentersResponse.json();
        
        console.log('获取到成本中心数据:', response);
        
        // 确保我们有一个数组来处理
        const costCenters = Array.isArray(response) ? response : (response.cost_centers || response.data || []);
        
        if (costCenters.length === 0) {
            console.log('没有可用的成本中心');
            return;
        }
        
        // 清空并添加默认选项
        select.innerHTML = '<option value="">请选择成本中心</option>';
        
        // 添加所有成本中心
        costCenters.forEach(costCenter => {
            const option = document.createElement('option');
            option.value = costCenter.id;
            option.textContent = costCenter.cost_center_name || costCenter.name;
            select.appendChild(option);
        });
        
        console.log('成本中心列表加载完成');
        
    } catch (error) {
        console.error('加载成本中心列表失败:', error);
        showMessage(error.message || '加载成本中心列表失败', 'error');
    }
}

// 加载成本对象下拉列表
async function loadCostObjectsForSelect() {
    try {
        console.log('开始加载成本对象列表');
        
        // 获取选择器
        const select = document.querySelector('#objectForm #cost_object_id');
        if (!select) {
            throw new Error('成本对象选择器 #cost_object_id 未找到');
        }
        
        // 获取所有成本对象
        const costObjectsResponse = await fetch('/api/cost-objects/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!costObjectsResponse.ok) {
            const errorData = await costObjectsResponse.json();
            throw new Error(errorData.error || `HTTP error! status: ${costObjectsResponse.status}`);
        }
        
        // 获取数据
        const response = await costObjectsResponse.json();
        
        console.log('获取到成本对象数据:', response);
        
        // 确保我们有一个数组来处理
        const costObjects = Array.isArray(response) ? response : (response.cost_objects || response.data || []);
        
        if (costObjects.length === 0) {
            console.log('没有可用的成本对象');
            return;
        }
        
        // 清空并添加默认选项
        select.innerHTML = '<option value="">请选择成本对象</option>';
        
        // 添加所有成本对象
        costObjects.forEach(costObject => {
            const option = document.createElement('option');
            option.value = costObject.id;
            option.textContent = costObject.cost_object_name || costObject.name;
            select.appendChild(option);
        });
        
        console.log('成本对象列表加载完成');
        
    } catch (error) {
        console.error('加载成本对象列表失败:', error);
        showMessage(error.message || '加载成本对象列表失败', 'error');
    }
}

// 加载扣水率列表
async function loadWaterDeductionRates() {
    try {
        console.log('开始加载扣水率列表');
        
        // 发送请求
        const response = await fetch('/api/water-deduction-rates/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        // 获取数据
        const rates = await response.json();
        console.log('获取到扣水率数据:', rates);
        
        // 获取表格主体
        const tbody = document.querySelector('tbody#rateTable');
        if (!tbody) {
            throw new Error('扣水率表格主体 tbody#rateTable 未找到');
        }
        
        // 清空并重新填充表格
        tbody.innerHTML = '';
        
        if (rates.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">暂无扣水率数据</td>
                </tr>
            `;
            return;
        }
        
        // 填充数据
        rates.forEach(rate => {
            try {
                // 转换日期
                const createdAt = new Date(rate.created_at).toLocaleString('zh-CN');
                
                // 确保 rate 是数字
                const rateValue = parseFloat(rate.rate);
                if (isNaN(rateValue)) {
                    console.error('无效的扣水率值:', rate.rate);
                    return;
                }
                
                // 转义组织名称中的单引号
                const escapedOrgName = rate.inventory_org_name.replace(/'/g, "\\'");
                
                tbody.innerHTML += `
                    <tr>
                        <td>${rate.id}</td>
                        <td>${rate.inventory_org_name}</td>
                        <td>${rateValue.toFixed(2)}%</td>
                        <td>${createdAt}</td>
                        <td>
                            <button onclick="editRate(${rate.id}, '${escapedOrgName}', ${rateValue})" 
                                    class="btn btn-primary btn-sm">
                                <span class="material-icons">edit</span>
                                编辑
                            </button>
                            <button onclick="deleteRate(${rate.id})" 
                                    class="btn btn-danger btn-sm">
                                <span class="material-icons">delete</span>
                                删除
                            </button>
                        </td>
                    </tr>
                `;
            } catch (err) {
                console.error('处理扣水率数据项失败:', err, rate);
            }
        });
        
        console.log('扣水率列表加载完成');
        
    } catch (error) {
        console.error('加载扣水率列表失败:', error);
        showMessage(error.message || '加载扣水率列表失败', 'error');
    }
}

// 打开操作对象模态框
window.openObjectModal = async function(isEdit = false) {
    try {
        console.log('开始打开操作对象模态框', { isEdit, currentObjectId });
        
        // 获取模态框元素
        const modal = document.querySelector('#objectModal');
        if (!modal) {
            throw new Error('模态框元素 #objectModal 未找到');
        }
        
        // 获取标题元素
        const modalTitle = modal.querySelector('#objectModalTitle');
        if (!modalTitle) {
            throw new Error('标题元素 #objectModalTitle 未找到');
        }
        
        // 获取表单元素
        const form = modal.querySelector('#objectForm');
        if (!form) {
            throw new Error('表单元素 #objectForm 未找到');
        }
        
        // 获取库存组织选择器
        const orgSelect = form.querySelector('#inventory_org_id');
        if (!orgSelect) {
            throw new Error('库存组织选择器 #inventory_org_id 未找到');
        }
        
        // 获取扣水率输入框
        const rateInput = form.querySelector('#rate');
        if (!rateInput) {
            throw new Error('扣水率输入框 #rate 未找到');
        }
        
        // 设置标题
        modalTitle.textContent = isEdit ? '编辑对象' : '新增对象';
        
        // 加载库存组织、仓库、成本中心和成本对象列表
        try {
            await Promise.all([
                loadInventoryOrgsForSelect(),
                loadWarehousesForSelect(),
                loadCostCentersForSelect(),
                loadCostObjectsForSelect()
            ]);
        } catch (error) {
            console.error('加载列表失败:', error);
            throw error;
        }
        
        // 如果不是编辑模式，才重置表单和状态
        if (!isEdit) {
            form.reset();
            currentObjectId = null;
            // 设置表单状态
            orgSelect.disabled = false;
            orgSelect.value = '';
            rateInput.value = '';
        }
        
        // 显示模态框
        modal.style.display = 'block';
        
        // 聚焦到库存组织选择器
        orgSelect.focus();
        
        console.log(`${isEdit ? '编辑' : '新增'}对象模态框已成功打开，当前编辑对象ID:`, currentObjectId);
        
    } catch (error) {
        console.error('打开操作对象模态框失败:', error);
        showMessage(error.message || '打开操作对象模态框失败', 'error');
    }
}

// 关闭操作对象模态框
function closeObjectModal() {
    try {
        console.log('尝试关闭操作对象模态框');
        
        // 获取模态框元素
        const modal = document.querySelector('#objectModal');
        if (!modal) {
            throw new Error('模态框元素 #objectModal 未找到');
        }
        
        // 获取表单元素
        const form = modal.querySelector('#objectForm');
        if (!form) {
            throw new Error('表单元素 #objectForm 未找到');
        }
        
        // 重置表单
        form.reset();
        
        // 启用库存组织选择器
        const orgSelect = form.querySelector('#inventory_org_id');
        if (orgSelect) {
            orgSelect.disabled = false;
        }
        
        // 关闭模态框
        modal.style.display = 'none';
        
        // 重置编辑状态
        currentObjectId = null;
        
        console.log('操作对象模态框已成功关闭');
        
    } catch (error) {
        console.error('关闭操作对象模态框失败:', error);
        showMessage(error.message || '关闭操作对象模态框失败', 'error');
    }
}

// 提交操作对象表单
async function submitObjectForm(event) {
    try {
        event.preventDefault();
        console.log('开始提交操作对象表单');
        
        // 获取表单元素
        const form = document.querySelector('#objectForm');
        if (!form) {
            throw new Error('表单元素 #objectForm 未找到');
        }
        
        // 获取提交按钮
        const submitBtn = event.submitter;
        if (!submitBtn) {
            throw new Error('提交按钮未找到');
        }
        
        // 禁用提交按钮
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = '保存中...';
        
        try {
            // 获取表单数据
            const user_id = form.querySelector('#user_id')?.value;
            const inventory_org_id = form.querySelector('#inventory_org_id')?.value;
            const warehouse_id = form.querySelector('#warehouse_id')?.value;
            const cost_center_id = form.querySelector('#cost_center_id')?.value;
            const cost_object_id = form.querySelector('#cost_object_id')?.value;
            const rate = form.querySelector('#rate')?.value;
            
            // 验证表单数据
            if (!user_id || !inventory_org_id || !warehouse_id || !cost_center_id || !cost_object_id || !rate) {
                throw new Error('请填写所有必填字段');
            }
            
            // 准备API请求数据
            // 使用表单中的 user_id 值
            currentUserId = user_id;
            const requestData = {
                user_id: user_id,
                inventory_org_id: parseInt(inventory_org_id),
                warehouse_id: parseInt(warehouse_id),
                cost_center_id: parseInt(cost_center_id),
                cost_object_id: parseInt(cost_object_id),
                rate: parseFloat(rate)
            };
            
            // 验证数据类型转换
            if (isNaN(requestData.inventory_org_id) || isNaN(requestData.warehouse_id) || 
                isNaN(requestData.cost_center_id) || isNaN(requestData.cost_object_id) || 
                isNaN(requestData.rate)) {
                throw new Error('请输入有效的数据');
            }
            
            console.log('请求数据:', requestData);
            
            // 检查是否是编辑模式
            console.log('提交前检查编辑状态:', { currentObjectId });
            
            // 准备API请求URL和方法
            let url = '/api/operation-objects/';
            let method = 'POST';
            
            if (currentObjectId) {
                url = `/api/operation-objects/${currentObjectId}/`;
                method = 'PUT';
                console.log('编辑模式 - 使用PUT方法');
            } else {
                console.log('新增模式 - 使用POST方法');
            }
            
            console.log('发送请求:', {
                url,
                method,
                data: requestData
            });
            
            // 发送请求
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            
            if (result.status !== 'success') {
                throw new Error(result.message || '操作失败');
            }
            
            console.log('请求成功:', result);
            
            // 保存操作类型
            const action = currentObjectId ? '编辑' : '新增';
            
            // 关闭模态框
            closeObjectModal();
            
            // 刷新数据并显示成功消息
            await loadObjectTable();
            
            // 显示成功提示
            showMessage(`操作对象${action}成功`, 'success');
            
        } catch (error) {
            console.error('提交对象表单失败:', error);
            showMessage(error.message || '提交对象表单失败', 'error');
            
        } finally {
            // 恢复提交按钮状态
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    } catch (error) {
        console.error('提交对象表单失败:', error);
        showMessage(error.message || '操作失败', 'error');
    }
}

async function editObject(id) {
    try {
        console.log('开始编辑操作对象:', { id });
        
        // 设置当前编辑的ID
        currentObjectId = id;
        console.log('设置当前编辑对象ID:', currentObjectId);
        
        // 获取对象数据
        const response = await fetch(`/api/operation-objects/${id}/`, {
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        if (result.status !== 'success' || !result.data) {
            throw new Error('返回数据格式不正确');
        }
        
        const obj = result.data;
        
        // 打开模态框
        await openObjectModal(true);
        
        // 获取表单元素
        const form = document.querySelector('#objectForm');
        if (!form) {
            throw new Error('表单元素 #objectForm 未找到');
        }
        
        // 设置表单值
        form.querySelector('#user_id').value = obj.user_id;
        form.querySelector('#inventory_org_id').value = obj.inventory_org.id;
        form.querySelector('#warehouse_id').value = obj.warehouse.id;
        form.querySelector('#cost_center_id').value = obj.cost_center.id;
        form.querySelector('#cost_object_id').value = obj.cost_object.id;
        form.querySelector('#rate').value = obj.rate;
        
        // 再次确认编辑状态
        console.log('编辑操作对象表单已准备就绪，当前编辑对象ID:', currentObjectId);
        
    } catch (error) {
        console.error('编辑操作对象失败:', error);
        showMessage(error.message || '编辑操作对象失败', 'error');
        currentObjectId = null; // 发生错误时重置ID
    }
}

// 删除操作对象
async function deleteObject(id) {
    try {
        console.log('尝试删除操作对象', { id });
        
        // 确认删除
        const confirmed = await confirmDialog('确定要删除这条操作对象记录吗？');
        if (!confirmed) {
            console.log('用户取消删除操作对象');
            return;
        }
        
        console.log('发送删除请求:', `/api/operation-objects/${id}/`);
        
        // 发送删除请求
        const response = await fetch(`/api/operation-objects/${id}/`, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        console.log('删除请求成功');
        
        // 刷新数据
        await loadObjectTable();
        
        // 显示成功提示
        showMessage('操作对象删除成功', 'success');
        
    } catch (error) {
        console.error('删除操作对象失败:', error);
        showMessage(error.message || '删除操作对象失败', 'error');
    }
}

// 页面加载完成后初始化
// 加载操作对象列表
async function loadObjectTable() {
    try {
        console.log('开始加载操作对象列表');
        
        // 获取所有操作对象
        const response = await fetch('/api/operation-objects/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('获取到操作对象数据:', result);
        
        if (result.status !== 'success' || !result.data) {
            throw new Error('返回数据格式不正确');
        }
        
        // 获取表格元素
        const tableContainer = document.querySelector('.table-responsive');
        if (!tableContainer) {
            throw new Error('表格容器 .table-responsive 未找到');
        }
        
        const tableBody = document.querySelector('#objectTable');
        if (!tableBody) {
            throw new Error('表格元素 #objectTable 未找到');
        }
        
        // 清空表格
        tableBody.innerHTML = '';
        
        // 添加数据行
        if (result.data.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = '<td colspan="9" class="text-center">暂无数据</td>';
            tableBody.appendChild(emptyRow);
        } else {
            result.data.forEach(obj => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${obj.id}</td>
                    <td>${obj.user_id}</td>
                    <td>${obj.inventory_org.name}</td>
                    <td>${obj.warehouse.name}</td>
                    <td>${obj.cost_center.name}</td>
                    <td>${obj.cost_object.name}</td>
                    <td>${obj.rate}%</td>
                    <td>${obj.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-2" onclick="editObject(${obj.id})">
                            编辑
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteObject(${obj.id})">
                            删除
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
        
        console.log('操作对象列表加载完成');
        
    } catch (error) {
        console.error('加载操作对象列表失败:', error);
        showMessage(error.message || '加载操作对象列表失败', 'error');
    }
}

window.addEventListener('load', function() {
    console.log('开始初始化对象功能...');
    initObjectOperation();
});
