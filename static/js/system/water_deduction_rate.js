// 全局变量
let currentRateId = null;

// 初始化扣水率相关功能
async function initWaterDeductionRate() {
    try {
        console.log('开始初始化扣水率功能');
        
        // 获取必要的DOM元素
        const addRateBtn = document.querySelector('#addRateBtn');
        if (!addRateBtn) {
            throw new Error('新增扣水率按钮 #addRateBtn 未找到');
        }
        
        const rateForm = document.querySelector('#rateForm');
        if (!rateForm) {
            throw new Error('扣水率表单 #rateForm 未找到');
        }
        
        const rateModal = document.querySelector('#rateModal');
        if (!rateModal) {
            throw new Error('扣水率模态框 #rateModal 未找到');
        }
        
        // 加载初始数据
        await Promise.all([
            loadInventoryOrgsForWaterDeduction(),
            loadWaterDeductionRates()
        ]);
        
        console.log('扣水率功能初始化完成');
        
    } catch (error) {
        console.error('初始化扣水率功能失败:', error);
        showMessage(error.message || '初始化扣水率功能失败', 'error');
    }
}

// 加载库存组织下拉列表（扣水率专用）
async function loadInventoryOrgsForWaterDeduction() {
    try {
        console.log('开始加载库存组织列表', { currentRateId });
        
        // 获取选择器
        const select = document.querySelector('#rateForm #inventory_org_id');
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
        
        // 获取已有扣水率的组织
        const ratesResponse = await fetch('/api/water-deduction-rates/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!ratesResponse.ok) {
            const errorData = await ratesResponse.json();
            throw new Error(errorData.error || `HTTP error! status: ${ratesResponse.status}`);
        }
        
        // 获取数据
        const orgs = await orgsResponse.json();
        const rates = await ratesResponse.json();
        
        console.log('获取到库存组织数据:', orgs);
        console.log('获取到扣水率数据:', rates);
        console.log('库存组织数量:', orgs.length);
        console.log('扣水率数量:', rates.length);
        
        if (orgs.length === 0) {
            console.log('没有可用的库存组织');
            return;
        }
        
        // 创建已有扣水率的组织ID集合
        const existingOrgIds = new Set(rates.map(rate => rate.inventory_org_id));
        console.log('已有扣水率的组织ID集合:', existingOrgIds);
        console.log('集合大小:', existingOrgIds.size);
        
        // 如果不是编辑模式，清空并添加默认选项
        if (!currentRateId) {
            select.innerHTML = '<option value="">请选择库存组织</option>';
            console.log('新增模式，开始添加库存组织选项...');
            
            // 只添加未设置扣水率的组织
            let addedCount = 0;
            orgs.forEach(org => {
                const shouldInclude = !existingOrgIds.has(org.id);
                console.log(`检查组织 ${org.org_name} (ID: ${org.id}): ${shouldInclude ? '应该包含' : '应该排除'}`);
                
                if (shouldInclude) {
                    const option = document.createElement('option');
                    option.value = org.id;
                    option.textContent = org.org_name;
                    select.appendChild(option);
                    addedCount++;
                }
            });
            console.log(`最终添加了 ${addedCount} 个库存组织选项`);
        } else {
            // 编辑模式，添加所有库存组织
            select.innerHTML = '';
            console.log('编辑模式，添加所有库存组织...');
            orgs.forEach(org => {
                const option = document.createElement('option');
                option.value = org.id;
                option.textContent = org.org_name;
                select.appendChild(option);
            });
        }
        
        console.log('库存组织列表加载完成');
        
    } catch (error) {
        console.error('加载库存组织列表失败:', error);
        showMessage(error.message || '加载库存组织列表失败', 'error');
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

// 打开新增扣水率模态框
async function openRateModal() {
    try {
        console.log('开始打开新增扣水率模态框');
        
        // 获取模态框元素
        const modal = document.querySelector('#rateModal');
        if (!modal) {
            throw new Error('模态框元素 #rateModal 未找到');
        }
        
        // 获取标题元素
        const modalTitle = modal.querySelector('#rateModalTitle');
        if (!modalTitle) {
            throw new Error('标题元素 #rateModalTitle 未找到');
        }
        
        // 获取表单元素
        const form = modal.querySelector('#rateForm');
        if (!form) {
            throw new Error('表单元素 #rateForm 未找到');
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
        modalTitle.textContent = '新增扣水率';
        
        // 重置表单和状态
        form.reset();
        currentRateId = null;
        
        // 加载库存组织列表
        try {
            await loadInventoryOrgsForWaterDeduction();
        } catch (error) {
            console.error('加载库存组织列表失败:', error);
            throw error;
        }
        
        // 设置表单状态
        orgSelect.disabled = false;
        orgSelect.value = '';
        rateInput.value = '';
        
        // 显示模态框
        modal.style.display = 'block';
        
        // 聚焦到库存组织选择器
        orgSelect.focus();
        
        console.log('新增扣水率模态框已成功打开');
        
    } catch (error) {
        console.error('打开新增扣水率模态框失败:', error);
        showMessage(error.message || '打开新增扣水率模态框失败', 'error');
    }
}

// 关闭扣水率模态框
function closeRateModal() {
    try {
        console.log('尝试关闭扣水率模态框');
        
        // 获取模态框元素
        const modal = document.querySelector('#rateModal');
        if (!modal) {
            throw new Error('模态框元素 #rateModal 未找到');
        }
        
        // 获取表单元素
        const form = modal.querySelector('#rateForm');
        if (!form) {
            throw new Error('表单元素 #rateForm 未找到');
        }
        
        // 重置表单和状态
        form.reset();
        currentRateId = null;
        
        // 启用库存组织选择器
        const orgSelect = form.querySelector('#inventory_org_id');
        if (orgSelect) {
            orgSelect.disabled = false;
        }
        
        // 关闭模态框
        modal.style.display = 'none';
        
        console.log('扣水率模态框已成功关闭');
        
    } catch (error) {
        console.error('关闭扣水率模态框失败:', error);
        showMessage(error.message || '关闭扣水率模态框失败', 'error');
    }
}

// 提交扣水率表单
async function submitRateForm(event) {
    try {
        event.preventDefault();
        console.log('开始提交扣水率表单');
        
        // 获取表单元素
        const form = document.querySelector('#rateForm');
        if (!form) {
            throw new Error('表单元素 #rateForm 未找到');
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
            const inventory_org_id = form.querySelector('#inventory_org_id')?.value;
            const rate = parseFloat(form.querySelector('#rate')?.value);
            
            // 验证表单数据
            if (!inventory_org_id || isNaN(rate)) {
                throw new Error('请填写有效的扣水率信息');
            }
            
            // 验证扣水率数值
            const rateNum = parseFloat(rate);
            if (isNaN(rateNum) || rateNum < 0 || rateNum > 100) {
                throw new Error('扣水率必须是0到100之间的数字');
            }
            // 准备API请求数据
            const requestData = {
                rate: rateNum
            };
            
            // 如果是新增操作，添加库存组织ID
            if (!currentRateId) {
                requestData.inventory_org_id = inventory_org_id;
            }
            
            // 准备API请求URL和方法
            const url = currentRateId ? 
                `/api/water-deduction-rates/${currentRateId}/` : 
                '/api/water-deduction-rates/';
            
            const method = currentRateId ? 'PUT' : 'POST';
            
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
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('请求成功:', result);
            
            // 先关闭模态框
            closeRateModal();
            
            // 刷新数据并显示成功消息
            await loadWaterDeductionRates();
            showMessage('扣水率' + (currentRateId ? '更新' : '添加') + '成功', 'success');
            
            // 刷新库存组织下拉列表
            if (!currentRateId) {
                await loadInventoryOrgsForWaterDeduction();
            }
            
            // 显示成功提示
            const action = currentRateId ? '编辑' : '新增';
            showMessage(`扣水率${action}成功`, 'success');
            
        } catch (error) {
            console.error('提交扣水率表单失败:', error);
            showMessage(error.message || '提交扣水率表单失败', 'error');
            
        } finally {
            // 恢复提交按钮状态
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    } catch (error) {
        console.error('提交扣水率表单失败:', error);
        showMessage(error.message || '操作失败', 'error');
    }
}

async function editRate(id, orgName, rate) {
    try {
        console.log('开始编辑扣水率:', { id, orgName, rate });
        
        // 设置当前编辑的ID
        currentRateId = id;
        
        // 获取模态框元素
        const modal = document.querySelector('#rateModal');
        if (!modal) {
            throw new Error('模态框元素 #rateModal 未找到');
        }
        
        // 获取标题元素
        const modalTitle = modal.querySelector('#rateModalTitle');
        if (!modalTitle) {
            throw new Error('标题元素 #rateModalTitle 未找到');
        }
        
        // 获取表单元素
        const form = modal.querySelector('#rateForm');
        if (!form) {
            throw new Error('表单元素 #rateForm 未找到');
        }
        
        // 获取库存组织选择器和扣水率输入框
        const orgSelect = form.querySelector('#inventory_org_id');
        const rateInput = form.querySelector('#rate');
        
        if (!orgSelect || !rateInput) {
            throw new Error('表单元素未找到');
        }
        
        // 设置标题
        modalTitle.textContent = '编辑扣水率';
        
        // 重置表单
        form.reset();
        
        // 创建库存组织选项
        const option = document.createElement('option');
        option.value = id;
        option.textContent = orgName;
        
        // 清空并设置库存组织
        orgSelect.innerHTML = '';
        orgSelect.appendChild(option);
        orgSelect.value = id;
        orgSelect.disabled = true;
        
        // 设置扣水率
        rateInput.value = rate;
        rateInput.disabled = false;
        rateInput.focus();
        
        // 打开模态框
        modal.style.display = 'block';
        
        console.log('编辑扣水率表单已准备就绪');
        
    } catch (error) {
        console.error('编辑扣水率失败:', error);
        showMessage(error.message || '编辑扣水率失败', 'error');
    }
}

// 删除扣水率
async function deleteRate(id) {
    try {
        console.log('尝试删除扣水率', { id });
        
        // 确认删除
        const confirmed = await confirmDialog('确定要删除这条扣水率记录吗？');
        if (!confirmed) {
            console.log('用户取消删除扣水率');
            return;
        }
        
        console.log('发送删除请求:', `/api/water-deduction-rates/${id}/`);
        
        // 发送删除请求
        const response = await fetch(`/api/water-deduction-rates/${id}/`, {
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
        await loadWaterDeductionRates();
        
        // 显示成功提示
        showMessage('扣水率删除成功', 'success');
        
    } catch (error) {
        console.error('删除扣水率失败:', error);
        showMessage(error.message || '删除扣水率失败', 'error');
    }
}

// 页面加载完成后初始化
window.addEventListener('load', function() {
    console.log('开始初始化扣水率功能...');
    initWaterDeductionRate();
});
