document.addEventListener('DOMContentLoaded', function() {
    // 判断是否为历史页面
    if (window.location.pathname.includes('/dayuan_report/history/')) {
        // 绑定过滤表单提交事件
        const filterForm = document.getElementById('filterForm');
        if (filterForm) {
            filterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                console.log('🔍 大塬报表 - 过滤表单提交事件触发');
                console.log('📝 表单数据:', new FormData(filterForm));
                // 表单提交时加载第一页数据
                loadDayuanHistoryData(1);
            });
            console.log('✅ 大塬报表 - 过滤表单事件绑定成功');
        } else {
            console.error('❌ 大塬报表 - 未找到过滤表单元素');
        }
        
        // 页面初次加载时自动加载第一页数据
        setTimeout(() => {
            loadDayuanHistoryData(1);
        }, 100);
        
        // 延迟初始化历史页面的日期时间选择器，确保DOM完全渲染
        setTimeout(() => {
            console.log('🔧 大塬报表 - 开始初始化历史页面日期时间选择器');
            initHistoryDateTimePickers();
        }, 200);
    } else {
        // 非历史页面，使用通用初始化
        initDateTimePickers();
    }
    
    const form = document.getElementById('qcForm');
    if (form) {
    // 初始化日期选择器
    flatpickr("#date", {
        dateFormat: "Y-m-d",
        locale: "zh",
        defaultDate: "today",
        maxDate: "today"
    });

    // 初始化时间选择器
    flatpickr("#time", {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true,
        locale: "zh",
        defaultHour: new Date().getHours(),
        defaultMinute: new Date().getMinutes()
    });

    // 表单提交处理
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const formData = new FormData(form);
            const data = {};
            
            // 处理表单数据
            for (let [key, value] of formData.entries()) {
                // 跳过空值
                if (value === '') continue;
                
                // 处理数值类型
                if (['moisture_after_drying', 'alkali_content', 'permeability', 
                     'permeability_long', 'wet_cake_density', 'brightness', 'swirl', 
                     'conductance', 'ph', 'moisture', 'bags', 'tons', 'sieving_14m', 
                     'sieving_30m', 'sieving_40m', 'sieving_150m', 'sieving_200m', 
                     'sieving_325m', 'fe_ion', 'ca_ion', 'al_ion', 'oil_absorption', 
                     'water_absorption'].includes(key)) {
                    // 尝试转换为数字
                    const numValue = parseFloat(value);
                    if (!isNaN(numValue)) {
                        data[key] = numValue;
                    }
                } else {
                    data[key] = value;
                }
            }

            console.log('Sending data:', data);  // 调试日志

            const response = await fetch('/api/dayuan-reports/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || '保存失败，请重试');
            }

            const result = await response.json();
            console.log('Response:', result);  // 调试日志

            // 成功提示
            alert('数据保存成功！');
            // 重置表单
            form.reset();
            // 刷新日期和时间选择器
            document.querySelector("#date")._flatpickr.setDate('today');
            document.querySelector("#time")._flatpickr.setDate(new Date());
            
        } catch (error) {
            console.error('Error:', error);
            alert(error.message || '提交失败，请检查网络连接后重试');
        }
    });
    }
}); 

// 历史数据加载和渲染（大塬专用）
let currentPageSize = 10;


async function loadDayuanHistoryData(page = 1, pageSize = 10) {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) return;
    const params = new URLSearchParams();
    params.append('page', page);
    params.append('page_size', pageSize);
    const formData = new FormData(filterForm);
    
    // 添加调试日志
    console.log('🔍 大塬报表 - 开始加载历史数据');
    console.log('📄 当前页码:', page, '每页大小:', pageSize);
    
    for (const [key, value] of formData.entries()) {
        if (key !== 'csrfmiddlewaretoken') {
            // 对于日期和时间字段，允许空字符串（即用户清空后不传递参数）
            if (['start_date','end_date','start_time','end_time'].includes(key)) {
                if (value.trim() !== '') {
                    params.append(key, value);
                    console.log(`📅 过滤条件 [${key}]:`, value);
                }
            } else {
                // 对于其他字段（包括班组），即使为空也要传递，让后端处理
                params.append(key, value);
                console.log(`🔍 过滤条件 [${key}]:`, value);
            }
        }
    }
    
    const apiUrl = `/api/dayuan-report/?${params.toString()}`;
    console.log('🌐 API请求URL:', apiUrl);
    
    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'success') {
                console.log(`✅ 数据加载成功，共 ${result.data.length} 条记录`);
                displayDayuanHistoryData(result.data);
                
                // 记录查看操作日志（仅在第一次加载或页面变化时记录）
                if (page === 1) {
                    logViewOperation();
                }
                
                // 标准分页渲染
                updateDayuanPagination(
                    result.current_page || 1,
                    result.total_pages || 1,
                    result.total_count || 0,
                    function(page, pageSize) {
                        loadDayuanHistoryData(page, pageSize);
                    },
                    pageSize
                );
            } else {
                console.error('❌ 数据加载失败:', result.message);
                alert('数据加载失败：' + (result.message || '未知错误'));
            }
        } else {
            console.error('❌ 请求失败，状态码:', response.status);
            alert('请求失败，状态码：' + response.status);
        }
    } catch (error) {
        console.error('❌ 数据加载异常:', error);
        alert('数据加载异常：' + error.message);
    }
}

function displayDayuanHistoryData(data) {
    const tbody = document.querySelector('#reportTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="37" style="text-align: center; padding: 40px; color: #666;">暂无数据</td></tr>';
        return;
    }
    // 大塬字段顺序
    const dayuanFields = [
        'username', 'date', 'time', 'moisture_after_drying', 'alkali_content', 'flux', 'product_name',
        'permeability', 'permeability_long', 'wet_cake_density', 'bulk_density',
        'sieving_14m', 'sieving_30m', 'sieving_40m', 'sieving_80m', 'sieving_100m', 'sieving_150m',
        'sieving_200m', 'sieving_325m', 'fe_ion', 'ca_ion', 'al_ion', 'brightness',
        'swirl', 'odor', 'conductance', 'ph', 'oil_absorption', 'water_absorption',
        'moisture', 'bags', 'packaging', 'tons', 'batch_number', 'remarks', 'shift'
    ];
    data.forEach(item => {
        const row = document.createElement('tr');
        let tds = '';
        dayuanFields.forEach(field => {
            tds += `<td>${item[field] !== undefined && item[field] !== null && item[field] !== '' ? item[field] : '-'}</td>`;
        });
        // 操作列
        const canEdit = item.can_edit || false;
        const canDelete = item.can_delete || false;
        const permissionReason = item.permission_reason || '';
        tds += `<td><div class="action-buttons-cell">`;
        if (canEdit) {
            tds += `<button class="btn btn-sm btn-primary" onclick="editDayuanRecord(${item.id})" title="编辑记录"><span class="material-icons" data-icon="edit">edit</span> 编辑</button>`;
        } else {
            tds += `<button class="btn btn-sm btn-secondary" disabled title="${permissionReason}"><span class="material-icons" data-icon="lock">lock</span> 已锁定</button>`;
        }
        if (canDelete) {
            tds += `<button class="btn btn-sm btn-danger" onclick="deleteDayuanRecord(${item.id})" title="删除记录"><span class="material-icons" data-icon="delete">delete</span> 删除</button>`;
        } else {
            tds += `<button class="btn btn-sm btn-secondary" disabled title="${permissionReason}"><span class="material-icons" data-icon="lock">lock</span> 无权限</button>`;
        }
        tds += `</div></td>`;
        row.innerHTML = tds;
        tbody.appendChild(row);
    });
}

function updateDayuanPagination(currentPage, totalPages, totalCount) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;
    if (totalPages <= 1 && totalCount <= currentPageSize) {
        paginationContainer.innerHTML = '';
        return;
    }
    let paginationHTML = `<div style="margin-bottom: 10px; text-align: center; color: #666;">共 ${totalCount} 条记录，第 ${currentPage} / ${totalPages} 页`;
    paginationHTML += ` &nbsp; 每页 <select id="pageSizeSelect">`;
    [5, 10, 20, 50, 100].forEach(size => {
        paginationHTML += `<option value="${size}"${size === currentPageSize ? ' selected' : ''}>${size}</option>`;
    });
    paginationHTML += `</select> 条`;
    paginationHTML += ` &nbsp; 跳转到 <input id="gotoPageInput" type="number" min="1" max="${totalPages}" value="${currentPage}" style="width: 50px;"> 页 <button id="gotoPageBtn">Go</button>`;
    paginationHTML += `</div><div style="display: flex; justify-content: center; gap: 5px; flex-wrap: wrap;">`;
    if (currentPage > 1) {
        paginationHTML += `<button onclick="loadDayuanHistoryData(${currentPage - 1}, ${currentPageSize})">上一页</button>`;
    }
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    if (startPage > 1) {
        paginationHTML += `<button onclick="loadDayuanHistoryData(1, ${currentPageSize})">1</button>`;
        if (startPage > 2) {
            paginationHTML += `<span style="padding: 8px;">...</span>`;
        }
    }
    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            paginationHTML += `<button class="current-page">${i}</button>`;
        } else {
            paginationHTML += `<button onclick="loadDayuanHistoryData(${i}, ${currentPageSize})">${i}</button>`;
        }
    }
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<span style="padding: 8px;">...</span>`;
        }
        paginationHTML += `<button onclick="loadDayuanHistoryData(${totalPages}, ${currentPageSize})">${totalPages}</button>`;
    }
    if (currentPage < totalPages) {
        paginationHTML += `<button onclick="loadDayuanHistoryData(${currentPage + 1}, ${currentPageSize})">下一页</button>`;
    }
    paginationHTML += '</div>';
    paginationContainer.innerHTML = paginationHTML;
    // 事件绑定
    document.getElementById('pageSizeSelect').addEventListener('change', function() {
        currentPageSize = parseInt(this.value);
        loadDayuanHistoryData(1, currentPageSize);
    });
    document.getElementById('gotoPageBtn').addEventListener('click', function() {
        const page = parseInt(document.getElementById('gotoPageInput').value);
        if (page >= 1 && page <= totalPages) {
            loadDayuanHistoryData(page, currentPageSize);
        }
    });
    // 支持回车跳页
    document.getElementById('gotoPageInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const page = parseInt(this.value);
            if (page >= 1 && page <= totalPages) {
                loadDayuanHistoryData(page, currentPageSize);
            }
        }
    });
}


function editDayuanRecord(id) {
    window.location.href = `/dayuan-report-edit/${id}/`;
}

async function deleteDayuanRecord(id) {
    if (!confirm('确定要删除这条记录吗？此操作不可恢复。')) return;
    const apiUrl = `/api/dayuan-report/${id}/`;
    try {
        const response = await fetch(apiUrl, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        if (response.ok) {
            alert('删除成功');
            loadDayuanHistoryData(1);
        } else {
            alert('删除失败，状态码：' + response.status);
        }
    } catch (error) {
        alert('删除异常：' + error.message);
    }
}

// 通用flatpickr日期和时间初始化函数
function initDateTimePickers(options = {}) {
    if (typeof flatpickr === 'undefined') return;
    
    // 日期
    if (document.getElementById('date')) {
        flatpickr('#date', {
            dateFormat: 'Y-m-d',
            locale: 'zh',
            defaultDate: options.dateDefault || new Date()
        });
    }
    
    // 时间
    if (document.getElementById('time')) {
        flatpickr('#time', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            locale: 'zh',
            defaultDate: options.timeDefault || getNearest5MinuteTime()
        });
    }
    
    // 历史页筛选
    if (document.getElementById('startDate')) {
        flatpickr('#startDate', {
            dateFormat: 'Y-m-d',
            locale: 'zh'
        });
    }
    if (document.getElementById('endDate')) {
        flatpickr('#endDate', {
            dateFormat: 'Y-m-d',
            locale: 'zh'
        });
    }
    if (document.getElementById('startTime')) {
        flatpickr('#startTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            locale: 'zh'
        });
    }
    if (document.getElementById('endTime')) {
        flatpickr('#endTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            locale: 'zh'
        });
    }
}

// 初始化历史页面的日期时间选择器
function initHistoryDateTimePickers() {
    console.log('🔧 大塬报表 - 开始初始化历史页面日期时间选择器');
    
    if (typeof flatpickr === 'undefined') {
        console.error('❌ flatpickr库未加载');
        return;
    }
    
    console.log('✅ flatpickr库已加载');
    
    // 开始日期
    const startDateEl = document.getElementById('startDate');
    if (startDateEl) {
        console.log('🔧 初始化开始日期选择器');
        flatpickr('#startDate', {
            dateFormat: 'Y-m-d',
            locale: 'zh',
            clickOpens: true,
            allowInput: true
        });
        console.log('✅ 开始日期选择器初始化完成');
    } else {
        console.error('❌ 未找到开始日期元素');
    }
    
    // 结束日期
    const endDateEl = document.getElementById('endDate');
    if (endDateEl) {
        console.log('🔧 初始化结束日期选择器');
        flatpickr('#endDate', {
            dateFormat: 'Y-m-d',
            locale: 'zh',
            clickOpens: true,
            allowInput: true
        });
        console.log('✅ 结束日期选择器初始化完成');
    } else {
        console.error('❌ 未找到结束日期元素');
    }
    
    // 开始时间
    const startTimeEl = document.getElementById('startTime');
    if (startTimeEl) {
        console.log('🔧 初始化开始时间选择器');
        flatpickr('#startTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            locale: 'zh',
            clickOpens: true,
            allowInput: true
        });
        console.log('✅ 开始时间选择器初始化完成');
    } else {
        console.error('❌ 未找到开始时间元素');
    }
    
    // 结束时间
    const endTimeEl = document.getElementById('endTime');
    if (endTimeEl) {
        console.log('🔧 初始化结束时间选择器');
        flatpickr('#endTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            locale: 'zh',
            clickOpens: true,
            allowInput: true
        });
        console.log('✅ 结束时间选择器初始化完成');
    } else {
        console.error('❌ 未找到结束时间元素');
    }
    
    console.log('🎉 大塬报表历史页面日期时间选择器初始化完成');
}

// 获取当前时间最近的5分钟倍数（如14:03->14:05, 14:07->14:05, 14:12->14:10）
function getNearest5MinuteTime() {
    const now = new Date();
    const minutes = now.getMinutes();
    const nearest = Math.round(minutes / 5) * 5;
    now.setMinutes(nearest);
    now.setSeconds(0);
    now.setMilliseconds(0);
    return now;
}

// 昨日产量统计功能
async function calculateYesterdayProduction() {
    try {
        // 显示加载提示
        const loadingMsg = '正在统计昨日产量数据...';
        console.log(loadingMsg);
        
        // 调用API获取昨日产量统计
        const response = await fetch('/api/dayuan-report/?action=yesterday_production', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'success') {
                displayYesterdayProductionResult(result);
            } else {
                alert('统计失败：' + (result.message || '未知错误'));
            }
        } else {
            alert('请求失败，状态码：' + response.status);
        }
    } catch (error) {
        console.error('统计异常：', error);
        alert('统计异常：' + error.message);
    }
}

// 显示昨日产量统计结果
function displayYesterdayProductionResult(result) {
    const { data, date, total_groups } = result;
    
    if (!data || data.length === 0) {
        alert(`${date} 没有找到产量数据`);
        return;
    }
    
    // 创建统计结果HTML
    let html = `
        <div style="max-width: 800px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h2 style="color: #1976d2; margin-bottom: 20px; text-align: center;">
                <span class="material-icons" style="vertical-align: middle; margin-right: 8px;">analytics</span>
                ${date} 昨日产量统计
            </h2>
            <p style="color: #666; margin-bottom: 20px; text-align: center;">
                共找到 ${total_groups} 个班组产品组合
            </p>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <thead>
                        <tr style="background: #f5f5f5;">
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600;">班组</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600;">产品型号</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600;">包装类型</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600;">批号</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600;">备注</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600;">总吨数</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    // 计算总吨数
    let totalTons = 0;
    
    data.forEach(item => {
        const tons = parseFloat(item.total_tons) || 0;
        totalTons += tons;
        
        html += `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${item.shift}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${item.product_name}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${item.packaging}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${item.batch_number}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${item.remarks || '未设置'}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600; color: #1976d2;">${tons.toFixed(2)}</td>
            </tr>
        `;
    });
    
    // 添加总计行
    html += `
                        <tr style="background: #e3f2fd; font-weight: 600;">
                            <td colspan="5" style="padding: 12px; border: 1px solid #ddd; text-align: center;">总计</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #1976d2; font-size: 16px;">${totalTons.toFixed(2)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="closeProductionModal()" style="padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    关闭
                </button>
            </div>
        </div>
    `;
    
    // 创建模态框显示结果
    const modal = document.createElement('div');
    modal.id = 'productionModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    modal.innerHTML = html;
    
    // 添加到页面
    document.body.appendChild(modal);
}

// 关闭产量统计模态框
function closeProductionModal() {
    const modal = document.getElementById('productionModal');
    if (modal) {
        modal.remove();
    }
}

// 大塬报表专用的导出Excel函数
function exportDayuanReportToExcel() {
    console.log('🔍 大塬报表专用导出函数被调用');
    
    try {
        // 获取当前筛选条件
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) {
            console.error('❌ 未找到过滤表单');
            alert('未找到过滤表单，请刷新页面重试');
            return;
        }
        
        const params = new URLSearchParams();
        const formData = new FormData(filterForm);
        
        console.log('🔍 开始收集过滤表单数据...');
        
        for (const [key, value] of formData.entries()) {
            if (key !== 'csrfmiddlewaretoken') {
                // 对于日期和时间字段，允许空字符串（即用户清空后不传递参数）
                if (['start_date','end_date','start_time','end_time'].includes(key)) {
                    if (value.trim() !== '') {
                        params.append(key, value);
                        console.log(`📅 过滤条件 [${key}]:`, value);
                    }
                } else {
                    // 对于其他字段（包括班组），即使为空也要传递，让后端处理
                    params.append(key, value);
                    console.log(`🔍 过滤条件 [${key}]:`, value);
                }
            }
        }
        
        // 构建导出URL
        const exportUrl = `/dayuan_report/export_excel/?${params.toString()}`;
        console.log('🌐 构建的导出URL:', exportUrl);
        
        // 检测企业微信环境
        const userAgent = navigator.userAgent;
        const isWxwork = /wxwork/i.test(userAgent);
        const isMobileDevice = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        const isWeChatMobile = isWxwork && isMobileDevice;
        
        console.log('大塬报表导出环境检测:', {
            isWxwork: isWxwork,
            isMobileDevice: isMobileDevice,
            isWeChatMobile: isWeChatMobile
        });
        
        // 如果是企业微信手机端，使用专用导出函数
        if (isWeChatMobile) {
            console.log('✅ 企业微信手机端，使用专用导出函数');
            if (typeof performWeChatMobileExport === 'function') {
                performWeChatMobileExport(exportUrl, '大塬QC报表');
            } else {
                performDirectExport(exportUrl);
            }
        } else if (typeof exportToExcel === 'function') {
            console.log('✅ 使用通用导出函数');
            // 调用通用导出函数，但传递我们构建的URL
            exportToExcel(exportUrl, 'filterForm', 'export', '大塬QC报表');
        } else {
            console.log('⚠️ 通用导出函数不可用，使用直接导出');
            // 直接执行导出
            performDirectExport(exportUrl);
        }
        
    } catch (error) {
        console.error('❌ 大塬报表导出失败:', error);
        alert('导出失败：' + error.message);
    }
}

// 直接导出函数（作为回退）
function performDirectExport(exportUrl) {
    console.log('🔍 执行直接导出:', exportUrl);
    
    try {
        // 检测环境
        const userAgent = navigator.userAgent;
        const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        
        if (isMobile) {
            // 移动端使用window.open
            console.log('📱 移动端，使用window.open');
            window.open(exportUrl, '_blank');
        } else {
            // PC端使用link.click
            console.log('💻 PC端，使用link.click');
            const link = document.createElement('a');
            link.href = exportUrl;
            link.style.display = 'none';
            link.download = '大塬QC报表.xlsx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        console.log('✅ 直接导出完成');
        alert('Excel导出已开始，请稍候...');
        
    } catch (error) {
        console.error('❌ 直接导出失败:', error);
        alert('导出失败，请重试');
    }
}

// 记录查看操作日志
async function logViewOperation() {
    try {
        const response = await fetch('/api/log-view-operation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                report_type: 'dayuan',
                operation_type: 'VIEW',
                operation_detail: '查看大塬QC报表历史记录',
                request_path: window.location.pathname
            })
        });
        
        if (response.ok) {
            console.log('✅ 查看操作日志记录成功');
        } else {
            console.warn('⚠️ 查看操作日志记录失败:', response.status);
        }
    } catch (error) {
        console.warn('⚠️ 查看操作日志记录异常:', error);
    }
}