// 长富报表专用的导出Excel函数
function exportChangfuReportToExcel() {
    console.log('🔍 长富报表专用导出函数被调用');
    
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
        
        console.log('🔍 开始收集长富报表过滤表单数据...');
        
        for (const [key, value] of formData.entries()) {
            if (key !== 'csrfmiddlewaretoken') {
                // 对于日期和时间字段，允许空字符串（即用户清空后不传递参数）
                if (['start_date','end_date','start_time','end_time'].includes(key)) {
                    if (value.trim() !== '') {
                        params.append(key, value);
                        console.log(`📅 长富报表过滤条件 [${key}]:`, value);
                    } else {
                        console.log(`⚠️ 跳过空的长富报表日期时间字段 [${key}]:`, value);
                    }
                } else {
                    // 对于其他字段（包括班组），即使为空也要传递，让后端处理
                    params.append(key, value);
                    console.log(`🔍 长富报表过滤条件 [${key}]:`, value);
                }
            }
        }
        
        // 构建导出URL
        const exportUrl = `/changfu_report/export_excel/?${params.toString()}`;
        console.log('🌐 长富报表构建的导出URL:', exportUrl);
        
        // 检测环境
        const userAgent = navigator.userAgent;
        const isWxwork = /wxwork/i.test(userAgent);
        const isNotMobile = !/mobile/i.test(userAgent);
        const isPC = /windows|macintosh|linux/i.test(userAgent);
        const isWeChatPC = isWxwork && isNotMobile && isPC;
        
        console.log('环境检测结果:', {
            userAgent: userAgent,
            isWxwork: isWxwork,
            isNotMobile: isNotMobile,
            isPC: isPC,
            isWeChatPC: isWeChatPC
        });
        
        // 如果是企业微信PC端，使用特殊处理
        if (isWeChatPC) {
            console.log('企业微信PC端，使用特殊导出处理');
            performWeChatWorkExport(exportUrl, 'export', '长富QC报表历史记录');
        } else {
            // 使用增强版导出功能
            if (typeof window.exportToExcel === 'function') {
                console.log('使用增强版导出功能');
                window.exportToExcel(exportUrl, 'filterForm', 'export', '长富QC报表历史记录');
            } else {
                console.log('增强版导出功能不可用，使用回退方式');
                performLegacyExport(exportUrl);
            }
        }
        
    } catch (error) {
        console.error('导出长富报表失败:', error);
        alert('导出失败：' + error.message);
    }
}

// 企业微信PC端特殊导出处理
function performWeChatWorkExport(exportUrl, actionType, reportName) {
    console.log('开始企业微信PC端特殊导出处理:', { exportUrl, actionType, reportName });
    
    try {
        // 调用qc_report_common.js中的增强版企业微信导出功能
        if (typeof window.performWeChatWorkExport === 'function' && window.performWeChatWorkExport !== performWeChatWorkExport) {
            console.log('使用qc_report_common.js中的增强版企业微信导出功能');
            window.performWeChatWorkExport(exportUrl, actionType, reportName);
        } else {
            console.log('使用本地企业微信导出功能');
            // 显示企业微信专用提示
            showWeChatWorkExportPrompt(exportUrl, reportName);
            
            // 延迟执行实际导出
            setTimeout(() => {
                console.log('执行企业微信导出...');
                performWeChatWorkActualExport(exportUrl, reportName);
            }, 1000);
        }
        
    } catch (error) {
        console.error('企业微信导出处理失败:', error);
        // 回退到简单导出
        performSimpleExportForWeChat(exportUrl, reportName);
    }
}

// 显示企业微信导出提示
function showWeChatWorkExportPrompt(exportUrl, reportName) {
    const modalHTML = `
        <div id="wechatExportModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 90%;
                width: 500px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #2196F3, #1976D2);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    📱
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">企业微信PC端导出</h3>
                
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>🔍 检测结果：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>当前环境：企业微信PC端</li>
                        <li>导出类型：${reportName}</li>
                        <li>处理方式：企业微信专用导出</li>
                    </ul>
                    
                    <p style="margin: 0;"><strong>💡 说明：</strong>系统将使用企业微信专用的导出方式，确保文件能正常下载。</p>
                </div>
                
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                ">
                    <button onclick="closeWeChatExportModal()" style="
                        padding: 12px 24px;
                        background: #6c757d;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                    " onmouseover="this.style.background='#5a6268'" onmouseout="this.style.background='#6c757d'">
                        取消导出
                    </button>
                    
                    <button onclick="startWeChatWorkExport()" style="
                        padding: 12px 24px;
                        background: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 600;
                        transition: background-color 0.2s;
                    " onmouseover="this.style.background='#1976D2'" onmouseout="this.style.background='#2196F3'">
                        🚀 开始导出
                    </button>
                </div>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：点击"开始导出"后，系统将自动处理企业微信环境下的文件下载。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 存储导出信息
    window.wechatExportInfo = { exportUrl, reportName };
}

// 关闭企业微信导出提示
function closeWeChatExportModal() {
    const modal = document.getElementById('wechatExportModal');
    if (modal) modal.remove();
}

// 开始企业微信导出
function startWeChatWorkExport() {
    if (window.wechatExportInfo) {
        const { exportUrl, reportName } = window.wechatExportInfo;
        closeWeChatExportModal();
        performWeChatWorkActualExport(exportUrl, reportName);
    }
}

// 执行企业微信实际导出
function performWeChatWorkActualExport(exportUrl, reportName) {
    console.log('执行企业微信实际导出:', exportUrl);
    
    try {
        // 方法1：尝试使用fetch下载
        fetch(exportUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.blob();
            })
            .then(blob => {
                console.log('文件下载成功，大小:', blob.size, '字节');
                
                // 创建下载链接
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${reportName}_${new Date().toISOString().split('T')[0]}.xlsx`;
                link.style.display = 'none';
                
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // 清理URL
                window.URL.revokeObjectURL(url);
                
                // 显示成功提示
                showWeChatWorkExportSuccess();
                
            })
            .catch(error => {
                console.error('fetch下载失败:', error);
                // 回退到传统方法
                performSimpleExportForWeChat(exportUrl, reportName);
            });
            
    } catch (error) {
        console.error('企业微信导出失败:', error);
        // 回退到简单导出
        performSimpleExportForWeChat(exportUrl, reportName);
    }
}

// 企业微信简单导出（回退）
function performSimpleExportForWeChat(exportUrl, reportName) {
    console.log('使用企业微信简单导出方式');
    
    try {
        const fileName = `${reportName}_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // 创建下载链接
        const link = document.createElement('a');
        link.href = exportUrl;
        link.style.display = 'none';
        link.download = fileName;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 显示成功提示
        showWeChatWorkExportSuccess();
        
    } catch (error) {
        console.error('企业微信简单导出失败:', error);
        alert('导出失败：' + error.message);
    }
}

// 显示企业微信导出成功提示
function showWeChatWorkExportSuccess() {
    const modalHTML = `
        <div id="wechatExportSuccessModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 90%;
                width: 400px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
                position: relative;
            ">
                <!-- 右上角关闭按钮 -->
                <button onclick="closeWeChatExportSuccessModal()" style="
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    width: 30px;
                    height: 30px;
                    background: #f5f5f5;
                    border: 1px solid #e0e0e0;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    color: #666;
                    transition: all 0.2s;
                " onmouseover="this.style.background='#e0e0e0'; this.style.color='#333'" onmouseout="this.style.background='#f5f5f5'; this.style.color='#666'">
                    ×
                </button>
                
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    ✅
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">导出成功</h3>
                
                <div style="
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #2e7d32;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>🎉 导出完成：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>文件已成功下载</li>
                        <li>请检查您的下载文件夹</li>
                        <li>文件名包含当前日期</li>
                    </ul>
                    
                    <p style="margin: 0;"><strong>💡 提示：</strong>如果文件没有自动下载，请检查浏览器的下载设置。</p>
                </div>
                
                <button onclick="closeWeChatExportSuccessModal()" style="
                    padding: 12px 24px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: background-color 0.2s;
                " onmouseover="this.style.background='#45a049'" onmouseout="this.style.background='#4CAF50'">
                    确定
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭企业微信导出成功模态框
function closeWeChatExportSuccessModal() {
    const modal = document.getElementById('wechatExportSuccessModal');
    if (modal) {
        modal.remove();
    }
}

// 传统导出方式（回退）
function performLegacyExport(exportUrl) {
    console.log('使用传统导出方式');
    
    try {
        // 创建下载链接
        const link = document.createElement('a');
        link.href = exportUrl;
        link.style.display = 'none';
        link.download = `长富QC报表历史记录_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ 传统导出完成');
        
    } catch (error) {
        console.error('传统导出失败:', error);
        alert('导出失败：' + error.message);
    }
}

// 重置筛选条件
function resetFilters() {
    console.log('🔧 长富报表重置筛选条件被调用');
    
    try {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) {
            console.error('❌ 未找到过滤表单');
            return;
        }
        
        // 重置所有input
        filterForm.reset();
        console.log('✅ 表单已重置');
        
        // 清空flatpickr日期/时间选择器
        const dateTimeFields = ['startDate', 'endDate', 'startTime', 'endTime'];
        dateTimeFields.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                // 如果有flatpickr实例，使用clear方法
                if (el._flatpickr) {
                    el._flatpickr.clear();
                    console.log(`✅ 已清空flatpickr字段: ${id}`);
                } else {
                    // 如果没有flatpickr实例，直接清空值
                    el.value = '';
                    console.log(`✅ 已清空普通字段: ${id}`);
                }
                
                // 触发change事件，确保UI更新
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        // 清空其他输入框
        const otherFields = ['product_name', 'packaging', 'squad'];
        otherFields.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.value = '';
                console.log(`✅ 已清空其他字段: ${id}`);
                // 触发change事件
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        // 重新加载第一页数据（显示所有数据）
        console.log('🔄 重新加载数据...');
        if (typeof loadChangfuHistoryData === 'function') {
            loadChangfuHistoryData(1);
        } else {
            console.warn('⚠️ loadChangfuHistoryData函数不可用');
        }
        
        console.log('✅ 长富报表筛选条件重置完成');
        
    } catch (error) {
        console.error('❌ 重置筛选条件失败:', error);
        alert('重置失败：' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 判断是否为历史页面
    if (window.location.pathname.includes('/changfu_report/history/')) {
        // 延迟初始化历史页面的日期时间选择器，确保DOM完全渲染
        setTimeout(() => {
            console.log('🔧 长富报表 - 开始初始化历史页面日期时间选择器');
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

                const response = await fetch('/api/changfu-reports/', {
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

// 历史数据加载和渲染（长富专用）
let currentPageSize = 10;


async function loadChangfuHistoryData(page = 1, pageSize = 10) {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) return;
    const params = new URLSearchParams();
    params.append('page', page);
    params.append('page_size', pageSize);
    const formData = new FormData(filterForm);
    
    // 添加调试日志
    console.log('🔍 长富报表 - 开始加载历史数据');
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
    
    const apiUrl = `/api/changfu-report/?${params.toString()}`;
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
                displayChangfuHistoryData(result.data);
                
                // 记录查看操作日志（仅在第一次加载或页面变化时记录）
                if (page === 1) {
                    logViewOperation();
                }
                
                // 标准分页渲染
                updateChangfuPagination(
                    result.current_page || 1,
                    result.total_pages || 1,
                    result.total_count || 0,
                    function(page, pageSize) {
                        loadChangfuHistoryData(page, pageSize);
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
                report_type: 'changfu',
                operation_type: 'VIEW',
                operation_detail: '查看长富QC报表历史记录',
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

function displayChangfuHistoryData(data) {
    const tbody = document.querySelector('#reportTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="36" style="text-align: center; padding: 40px; color: #666;">暂无数据</td></tr>';
        return;
    }
    // 长富字段顺序
    const changfuFields = [
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
        changfuFields.forEach(field => {
            tds += `<td>${item[field] !== undefined && item[field] !== null && item[field] !== '' ? item[field] : '-'}</td>`;
        });
        // 操作列
        const canEdit = item.can_edit || false;
        const canDelete = item.can_delete || false;
        const permissionReason = item.permission_reason || '';
        tds += `<td><div class="action-buttons-cell">`;
        if (canEdit) {
            tds += `<button class="btn btn-sm btn-primary" onclick="editChangfuRecord(${item.id})" title="编辑记录"><span class="material-icons" data-icon="edit">edit</span> 编辑</button>`;
        } else {
            tds += `<button class="btn btn-sm btn-secondary" disabled title="${permissionReason}"><span class="material-icons" data-icon="lock">lock</span> 已锁定</button>`;
        }
        if (canDelete) {
            tds += `<button class="btn btn-sm btn-danger" onclick="deleteChangfuRecord(${item.id})" title="删除记录"><span class="material-icons" data-icon="delete">delete</span> 删除</button>`;
        } else {
            tds += `<button class="btn btn-sm btn-secondary" disabled title="${permissionReason}"><span class="material-icons" data-icon="lock">lock</span> 无权限</button>`;
        }
        tds += `</div></td>`;
        row.innerHTML = tds;
        tbody.appendChild(row);
    });
}

function updateChangfuPagination(currentPage, totalPages, totalCount) {
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
        paginationHTML += `<button onclick="loadChangfuHistoryData(${currentPage - 1}, ${currentPageSize})">上一页</button>`;
    }
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    if (startPage > 1) {
        paginationHTML += `<button onclick="loadChangfuHistoryData(1, ${currentPageSize})">1</button>`;
        if (startPage > 2) {
            paginationHTML += `<span style="padding: 8px;">...</span>`;
        }
    }
    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            paginationHTML += `<button class="current-page">${i}</button>`;
        } else {
            paginationHTML += `<button onclick="loadChangfuHistoryData(${i}, ${currentPageSize})">${i}</button>`;
        }
    }
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<span style="padding: 8px;">...</span>`;
        }
        paginationHTML += `<button onclick="loadChangfuHistoryData(${totalPages}, ${currentPageSize})">${totalPages}</button>`;
    }
    if (currentPage < totalPages) {
        paginationHTML += `<button onclick="loadChangfuHistoryData(${currentPage + 1}, ${currentPageSize})">下一页</button>`;
    }
    paginationHTML += '</div>';
    paginationContainer.innerHTML = paginationHTML;
    // 事件绑定
    document.getElementById('pageSizeSelect').addEventListener('change', function() {
        currentPageSize = parseInt(this.value);
        loadChangfuHistoryData(1, currentPageSize);
    });
    document.getElementById('gotoPageBtn').addEventListener('click', function() {
        const page = parseInt(document.getElementById('gotoPageInput').value);
        if (page >= 1 && page <= totalPages) {
            loadChangfuHistoryData(page, currentPageSize);
        }
    });
    // 支持回车跳页
    document.getElementById('gotoPageInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const page = parseInt(this.value);
            if (page >= 1 && page <= totalPages) {
                loadChangfuHistoryData(page, currentPageSize);
            }
        }
    });
}


function editChangfuRecord(id) {
    window.location.href = `/changfu-report-edit/${id}/`;
}

async function deleteChangfuRecord(id) {
    if (!confirm('确定要删除这条记录吗？此操作不可恢复。')) return;
    const apiUrl = `/api/changfu-report/${id}/`;
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
            loadChangfuHistoryData(1);
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
    console.log('🔧 长富报表 - 开始初始化历史页面日期时间选择器');
    
    if (typeof flatpickr === 'undefined') {
        console.error('❌ flatpickr库未加载');
        return;
    }
    
    console.log('✅ flatpickr库已加载');
    
    // 检测是否为企业微信PC端
    const userAgent = navigator.userAgent;
    const isWxwork = /wxwork/i.test(userAgent);
    const isNotMobile = !/mobile/i.test(userAgent);
    const isPC = /windows|macintosh|linux/i.test(userAgent);
    const isWeChatPC = isWxwork && isNotMobile && isPC;
    
    if (isWeChatPC) {
        console.log('🔧 检测到企业微信PC端，使用兼容性修复');
        // 使用企业微信PC端兼容性修复
        if (window.wxWorkPCCompatibility && typeof window.wxWorkPCCompatibility.fixDateTimePickers === 'function') {
            // 先强制清空所有字段
            if (typeof window.wxWorkPCCompatibility.forceClearAllDateTimeFields === 'function') {
                window.wxWorkPCCompatibility.forceClearAllDateTimeFields();
            }
            window.wxWorkPCCompatibility.fixDateTimePickers();
        } else {
            console.warn('⚠️ 企业微信PC端兼容性修复不可用，使用标准初始化');
            initStandardDateTimePickers();
        }
    } else {
        console.log('🔧 标准浏览器环境，使用标准初始化');
        initStandardDateTimePickers();
    }
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

// 标准日期时间选择器初始化
function initStandardDateTimePickers() {
    if (typeof flatpickr === 'undefined') {
        console.warn('⚠️ flatpickr库未加载，跳过日期时间选择器初始化');
        return;
    }
    
    // 开始日期
    const startDateEl = document.getElementById('startDate');
    if (startDateEl) {
        console.log('🔧 长富报表 - 初始化开始日期选择器');
        flatpickr('#startDate', {
            dateFormat: 'Y-m-d',
            locale: 'zh',
            clickOpens: true,
            allowInput: true,
            defaultDate: null
        });
        console.log('✅ 长富报表 - 开始日期选择器初始化完成');
    } else {
        console.error('❌ 长富报表 - 未找到开始日期元素');
    }
    
    // 结束日期
    const endDateEl = document.getElementById('endDate');
    if (endDateEl) {
        console.log('🔧 长富报表 - 初始化结束日期选择器');
        flatpickr('#endDate', {
            dateFormat: 'Y-m-d',
            locale: 'zh',
            clickOpens: true,
            allowInput: true,
            defaultDate: null
        });
        console.log('✅ 长富报表 - 结束日期选择器初始化完成');
    } else {
        console.error('❌ 长富报表 - 未找到结束日期元素');
    }
    
    // 开始时间
    const startTimeEl = document.getElementById('startTime');
    if (startTimeEl) {
        console.log('🔧 长富报表 - 初始化开始时间选择器');
        flatpickr('#startTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            locale: 'zh',
            clickOpens: true,
            allowInput: true,
            defaultDate: null
        });
        console.log('✅ 长富报表 - 开始时间选择器初始化完成');
    } else {
        console.error('❌ 长富报表 - 未找到开始时间元素');
    }
    
    // 结束时间
    const endTimeEl = document.getElementById('endTime');
    if (endTimeEl) {
        console.log('🔧 长富报表 - 初始化结束时间选择器');
        flatpickr('#endTime', {
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true,
            locale: 'zh',
            clickOpens: true,
            allowInput: true,
            defaultDate: null
        });
        console.log('✅ 长富报表 - 结束时间选择器初始化完成');
    } else {
        console.error('❌ 长富报表 - 未找到结束时间元素');
    }
    
    console.log('✅ 标准日期时间选择器初始化完成');
}

// 昨日产量统计功能
async function calculateYesterdayProduction() {
    try {
        // 显示加载提示
        const loadingMsg = '正在统计昨日产量数据...';
        console.log(loadingMsg);

        // 调用API获取昨日产量统计
        const response = await fetch('/api/changfu-report/?action=yesterday_production', {
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

// 关闭产量统计模态框
function closeProductionModal() {
    const modal = document.getElementById('productionModal');
    if (modal) {
        modal.remove();
    }
}

// 显示错误信息
function showError(message) {
    if (typeof showQuickMessage === 'function') {
        showQuickMessage(message, 'error');
    } else {
        alert(message);
    }
}

// 今日产量统计功能
async function calculateTodayProduction() {
    try {
        // 显示加载提示
        const loadingMsg = '正在统计今日产量数据...';
        console.log(loadingMsg);

        // 调用API获取今日产量统计
        const response = await fetch('/api/changfu-report/?action=today_production', {
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
                displayTodayProductionResult(result);
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

// 显示今日产量统计结果
function displayTodayProductionResult(result) {
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
                ${date} 今日产量统计
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
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600; color: #1976d2;">${tons.toFixed(4)}</td>
            </tr>
        `;
    });

    // 添加总计行
    html += `
                        <tr style="background: #e3f2fd; font-weight: 600;">
                            <td colspan="4" style="padding: 12px; border: 1px solid #ddd; text-align: center;">总计</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #1976d2; font-size: 16px;">${totalTons.toFixed(4)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="exportTodayProductionToExcel()" style="padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">
                    <span class="material-icons" style="font-size: 16px; vertical-align: middle; margin-right: 4px;">download</span>
                    导出Excel
                </button>
                <button onclick="closeProductionModal()" style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    <span class="material-icons" style="font-size: 16px; vertical-align: middle; margin-right: 4px;">close</span>
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

// 修改昨日产量统计结果显示，添加导出Excel按钮
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
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600; color: #1976d2;">${tons.toFixed(4)}</td>
            </tr>
        `;
    });

    // 添加总计行
    html += `
                        <tr style="background: #e3f2fd; font-weight: 600;">
                            <td colspan="4" style="padding: 12px; border: 1px solid #ddd; text-align: center;">总计</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #1976d2; font-size: 16px;">${totalTons.toFixed(4)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="exportYesterdayProductionToExcel()" style="padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">
                    <span class="material-icons" style="font-size: 16px; vertical-align: middle; margin-right: 4px;">download</span>
                    导出Excel
                </button>
                <button onclick="closeProductionModal()" style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    <span class="material-icons" style="font-size: 16px; vertical-align: middle; margin-right: 4px;">close</span>
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

// 导出昨日产量统计到Excel（完全参考远通QC报表的做法）
async function exportYesterdayProductionToExcel() {
    try {
        console.log('开始导出长富昨日产量Excel...');
        const exportUrl = '/changfu_report/export_yesterday_production/';
        
        // 检测环境
        const userAgent = navigator.userAgent;
        const isWxwork = /wxwork/i.test(userAgent);
        const isNotMobile = !/mobile/i.test(userAgent);
        const isPC = /windows|macintosh|linux/i.test(userAgent);
        const isWeChatPC = isWxwork && isNotMobile && isPC;
        
        console.log('环境检测结果:', {
            userAgent: userAgent,
            isWxwork: isWxwork,
            isNotMobile: isNotMobile,
            isPC: isPC,
            isWeChatPC: isWeChatPC
        });
        
        // 如果是企业微信PC端，使用特殊处理
        if (isWeChatPC) {
            console.log('企业微信PC端，使用特殊导出处理');
            performWeChatWorkExport(exportUrl, 'export', '长富昨日产量统计');
        } else {
            // 使用增强版导出功能
            if (typeof window.exportToExcel === 'function') {
                console.log('使用增强版导出功能');
                window.exportToExcel(exportUrl, 'filterForm', 'export', '长富昨日产量统计');
            } else {
                console.log('增强版导出功能不可用，使用回退方式');
                performLegacyExport(exportUrl);
            }
        }
        
    } catch (error) {
        console.error('导出昨日产量失败:', error);
        alert('导出失败：' + error.message);
    }
}

// 导出今日产量统计到Excel（完全参考远通QC报表的做法）
async function exportTodayProductionToExcel() {
    try {
        console.log('开始导出长富今日产量Excel...');
        const exportUrl = '/changfu_report/export_today_production/';
        
        // 检测环境
        const userAgent = navigator.userAgent;
        const isWxwork = /wxwork/i.test(userAgent);
        const isNotMobile = !/mobile/i.test(userAgent);
        const isPC = /windows|macintosh|linux/i.test(userAgent);
        const isWeChatPC = isWxwork && isNotMobile && isPC;
        
        console.log('环境检测结果:', {
            userAgent: userAgent,
            isWxwork: isWxwork,
            isNotMobile: isNotMobile,
            isPC: isPC,
            isWeChatPC: isWeChatPC
        });
        
        // 如果是企业微信PC端，使用特殊处理
        if (isWeChatPC) {
            console.log('企业微信PC端，使用特殊导出处理');
            performWeChatWorkExport(exportUrl, 'export', '长富今日产量统计');
        } else {
            // 使用增强版导出功能
            if (typeof window.exportToExcel === 'function') {
                console.log('使用增强版导出功能');
                window.exportToExcel(exportUrl, 'filterForm', 'export', '长富今日产量统计');
            } else {
                console.log('增强版导出功能不可用，使用回退方式');
                performLegacyExport(exportUrl);
            }
        }
        
    } catch (error) {
        console.error('导出今日产量失败:', error);
        alert('导出失败：' + error.message);
    }
}
