console.log('加载 parameter_config.js - ' + new Date().toISOString());

// 确保 jQuery 已加载
if (typeof jQuery === 'undefined') {
    console.error('jQuery未加载！');
} else {
    console.log('jQuery版本:', jQuery.fn.jquery);
}

// 编辑库存组织
window.editOrg= function(id, code, name) {
    console.log('编辑库存组织:', { id, code, name });
    window.currentOrgId = id;

    const codeInput = document.getElementById('orgCode');
    const nameInput = document.getElementById('orgName');

    if (codeInput && nameInput) {
        codeInput.value = code;
        nameInput.value = name;
        openOrgModal(true);
    }
}
//删除库存组织
window.deleteOrg = async function(id) {
    console.log('尝试删除库存组织:', id);
    if (!confirm('确定要删除这个库存组织吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/inventory-org/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json'
            }
        });

        const result = await response.json();
        console.log('删除库存组织响应:', result);

        if (result.status === 'success') {
            loadInventoryOrgs();
        } else {
            console.error('删除库存组织失败:', result.message);
            alert('删除失败: ' + result.message);
        }
    } catch (error) {
        console.error('删除库存组织出错:', error);
        alert('删除失败: ' + error.message);
    }
}


// 编辑仓库映射
window.editWarehouse = function(id, code, name) {
    console.log('编辑仓库:', { id, code, name });
    window.currentWarehouseId = id;
    
    const codeInput = document.getElementById('warehouseCode');
    const nameInput = document.getElementById('warehouseName');
    
    if (codeInput && nameInput) {
        codeInput.value = code;
        nameInput.value = name;
        openWarehouseModal(true);
    }
}
//删除仓库映射
window.deleteWarehouse = async function(id) {
    console.log('尝试删除仓库:', id);
    if (!confirm('确定要删除这个仓库映射吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/warehouses/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json'
            }
        });

        const result = await response.json();
        console.log('删除仓库响应:', result);
        
        if (result.status === 'success') {
            loadInventoryWarehouses();
        } else {
            console.error('删除仓库失败:', result.message);
            alert('删除失败: ' + result.message);
        }
    } catch (error) {
        console.error('删除仓库出错:', error);
        alert('删除失败: ' + error.message);
    }
}



//编辑物料映射
window.editMaterial = function(id, code, name) {
    console.log('编辑物料映射:', id);
    currentMaterialId = id;

    const codeInput = document.getElementById('materialCode');
    const nameInput = document.getElementById('materialName');

    if (codeInput && nameInput) {
        codeInput.value = code;
        nameInput.value = name;
        openMaterialModal(true);
    }
}

//删除物料映射
window.deleteMaterial = async function(id) {
    if (!confirm('确定要删除这个物料映射吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/materials/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json'
            }
        });

        let result;
        try {
            result = await response.json();
        } catch (e) {
            console.error('解析响应JSON失败:', e);
            throw new Error('服务器响应格式错误');
        }

        if (!response.ok) {
            console.error('删除API响应错误:', response.status, result);
            throw new Error(result.message || `删除失败: ${response.status}`);
        }

        if (result.status !== 'success') {
            console.error('删除API返回错误:', result);
            throw new Error(result.message || '删除失败');
        }

        // 先显示成功消息
        if (result.message) {
            alert(result.message);
        } else {
            alert('删除成功');
        }

        // 然后刷新列表
        await loadInventoryMaterials();
    } catch (error) {
        console.error('删除出错:', error);
        alert(`删除失败: ${error.message}`);
        // 刷新列表以确保显示最新状态
        try {
            await loadMaterials();
        } catch (e) {
            console.error('重新加载失败:', e);
        }
    }
}


//编辑成本中心映射
window.editCostCenter = function(id, code, name) {
    console.log('编辑成本中心:', id);
    currentCostCenterId = id;

    const codeInput = document.getElementById('costCenterCode');
    const nameInput = document.getElementById('costCenterName');

    if (codeInput && nameInput) {
        codeInput.value = code;
        nameInput.value = name;
        openCostCenterModal(true);
    }
}

//删除成本中心映射
window.deleteCostCenter = async function(id) {
    if (!confirm('确定要删除这个成本中心吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/cost-centers/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json'
            }
        });

        let result;
        try {
            result = await response.json();
        } catch (e) {
            console.error('解析响应JSON失败:', e);
            throw new Error('服务器响应格式错误');
        }

        if (!response.ok) {
            console.error('删除API响应错误:', response.status, result);
            throw new Error(result.message || `删除失败: ${response.status}`);
        }

        if (result.status !== 'success') {
            console.error('删除API返回错误:', result);
            throw new Error(result.message || '删除失败');
        }

        // 先显示成功消息
        if (result.message) {
            alert(result.message);
        } else {
            alert('删除成功');
        }

        // 然后刷新列表
        await loadCostCenters();
    } catch (error) {
        console.error('删除出错:', error);
        alert(`删除失败: ${error.message}`);
        // 刷新列表以确保显示最新状态
        try {
            await loadCostCenters();
        } catch (e) {
            console.error('重新加载失败:', e);
        }
    }
}


// 编辑成本对象映射
window.editCostObject = function(id, code, name) {
    console.log('编辑成本对象:', { id, code, name });
    window.currentCostObjectId = id;
    
    const codeInput = document.getElementById('costObjectCode');
    const nameInput = document.getElementById('costObjectName');
    
    if (codeInput && nameInput) {
        codeInput.value = code;
        nameInput.value = name;
        openCostObjectModal(true);
    }
}

// 删除成本对象映射
window.deleteCostObject = async function(id) {
    console.log('尝试删除成本对象:', id);
    if (!confirm('确定要删除这个成本对象映射吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/cost-objects/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json'
            }
        });

        const result = await response.json();
        console.log('删除成本对象响应:', result);
        
        if (result.status === 'success') {
            loadCostObjects();
        } else {
            console.error('删除成本对象失败:', result.message);
            alert('删除失败: ' + result.message);
        }
    } catch (error) {
        console.error('删除成本对象出错:', error);
        alert('删除失败: ' + error.message);
    }
}

// 保存报表参数
window.saveParameter = async function(parameterName) {
    const value = document.getElementById(parameterName).value;
    
    try {
        const response = await fetch('/api/parameters/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                id: parameterName,
                value: value
            })
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            alert('参数保存成功');
        } else {
            console.error('保存参数失败:', result.message);
            alert('保存失败: ' + result.message);
        }
    } catch (error) {
        console.error('保存参数出错:', error);
        alert('保存失败: ' + error.message);
    }
}

// 加载参数
async function loadParameter(paramId, defaultValue = '') {
    try {
        const response = await fetch(`/api/parameters/${paramId}/`);
        const result = await response.json();
        
        if (result.status === 'success') {
            const input = document.getElementById(paramId);
            if (input) {
                input.value = result.data.value;
            }
        } else {
            // 如果参数不存在，设置默认值
            const input = document.getElementById(paramId);
            if (input) {
                input.value = defaultValue;
            }
        }
    } catch (error) {
        console.error(`加载参数 ${paramId} 出错:`, error);
        // 设置默认值
        const input = document.getElementById(paramId);
        if (input) {
            input.value = defaultValue;
        }
    }
}

// 加载所有参数
async function loadParameters() {
    // 加载报表参数
    await loadParameter('report_edit_limit', '7');
    
    // 加载渗透率系数参数
    await loadParameter('yuantong_permeability_coefficient', '6.4');
    await loadParameter('dongtai_permeability_coefficient', '6.4');
    await loadParameter('yuantong_sample_weight', '10.0');
    await loadParameter('dongtai_sample_weight', '10.0');
    await loadParameter('yuantong_filter_area', '28.3');
    await loadParameter('dongtai_filter_area', '28.3');
    
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    loadParameters();
});



