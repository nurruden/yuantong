/**
 * QC报表通用JavaScript功能
 * 支持大塬和东泰两种报表类型的历史记录管理
 */

// 全局变量
let currentPage = 1;
// let pageSize = 10;
// let totalPages = 0;
// let currentReportType = '';
// let reportEditLimit = 7; // 默认7天编辑限制

// 检测是否为企业微信PC端
function isWeChatWorkPC() {
    const userAgent = navigator.userAgent;
    const isWxwork = /wxwork/i.test(userAgent);
    const isNotMobile = !/mobile/i.test(userAgent);
    const isPC = /windows|macintosh|linux/i.test(userAgent);
    
    console.log('企业微信PC端检测:', {
        userAgent: userAgent,
        isWxwork: isWxwork,
        isNotMobile: isNotMobile,
        isPC: isPC,
        result: isWxwork && isNotMobile && isPC
    });
    
    return isWxwork && isNotMobile && isPC;
}

// 检测是否为移动端
function isMobile() {
    const userAgent = navigator.userAgent;
    const result = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
    
    console.log('移动端检测:', {
        userAgent: userAgent,
        result: result
    });
    
    return result;
}

// 获取CSRF Token
function getCSRFToken() {
    // 首先尝试从隐藏表单字段获取
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenElement) {
        return tokenElement.value;
    }
    
    // 如果没有找到，尝试从cookie获取
    const name = 'csrftoken';
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
    return cookieValue || '';
}

// 显示企业微信PC端文件保存提示
function showWeChatWorkPCSavePrompt(actionType) {
    const actionNames = {
        'export': '导出Excel文件',
        'yesterday': '统计昨日产量',
        'today': '统计今日产量'
    };
    
    const actionName = actionNames[actionType] || '操作';
    
    const modalHTML = `
        <div id="wechatWorkModal" style="
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
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    📁
                </div>
                
                <h3 style="
                    margin: 0 0 15px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">${actionName}</h3>
                
                <div style="
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #495057;
                        font-size: 16px;
                        font-weight: 600;
                    ">💡 企业微信PC端文件保存提示：</h4>
                    
                    <div style="
                        color: #6c757d;
                        font-size: 14px;
                        line-height: 1.6;
                    ">
                        <p style="margin: 0 0 10px 0;"><strong>1. 文件下载位置：</strong></p>
                        <p style="margin: 0 0 10px 0; padding-left: 20px;">• 默认下载到：<code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">下载</code> 文件夹</p>
                        <p style="margin: 0 0 10px 0; padding-left: 20px;">• 或企业微信设置的下载目录</p>
                        
                        <p style="margin: 0 0 10px 0;"><strong>2. 如何更改保存位置：</strong></p>
                        <p style="margin: 0 0 10px 0; padding-left: 20px;">• 点击下载链接时，选择"另存为"</p>
                        <p style="margin: 0 0 10px 0; padding-left: 20px;">• 或在企业微信设置中修改下载路径</p>
                        
                        <p style="margin: 0 0 10px 0;"><strong>3. 文件命名规则：</strong></p>
                        <p style="margin: 0 0 10px 0; padding-left: 20px;">• Excel文件：<code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">东泰QC报表_YYYY-MM-DD.xlsx</code></p>
                        <p style="margin: 0 0 10px 0; padding-left: 20px;">• 统计文件：<code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">产量统计_YYYY-MM-DD.xlsx</code></p>
                    </div>
                </div>
                
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                ">
                    <button onclick="closeWeChatWorkModal()" style="
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
                        我知道了
                    </button>
                    
                    <button onclick="openWeChatWorkSettings()" style="
                        padding: 12px 24px;
                        background: #007bff;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                    " onmouseover="this.style.background='#0056b3'" onmouseout="this.style.background='#007bff'">
                        打开设置
                    </button>
                </div>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    提示：在企业微信PC端，文件会自动下载到默认位置。<br>
                    如需更改保存位置，请在企业微信设置中修改下载路径。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭企业微信PC端提示模态框
function closeWeChatWorkModal() {
    const modal = document.getElementById('weChatWorkModal');
    if (modal) modal.remove();
}

// 打开企业微信设置（提示用户）
function openWeChatWorkSettings() {
    alert('请在企业微信PC端中：\n\n1. 点击右上角设置图标 ⚙️\n2. 选择"设置"\n3. 在"通用"中找到"下载路径"\n4. 修改为您想要的文件夹位置');
}

// 通用筛选表单提交事件绑定
function bindFilterFormSubmit(formId, onSubmit) {
    const filterForm = document.getElementById(formId);
    if (!filterForm) return;
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (typeof onSubmit === 'function') onSubmit(1);
    });
}

// 重置筛选条件
function resetFilters() {
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.reset();
        loadHistoryData(1);
    }
}

// 增强版导出Excel函数 - 支持企业微信PC端提示和路径选择
function exportToExcel(exportUrl, filterFormId = 'filterForm', actionType = 'export', customFileName = '') {
    console.log('exportToExcel被调用:', {
        exportUrl: exportUrl,
        filterFormId: filterFormId,
        actionType: actionType,
        customFileName: customFileName
    });
    
    try {
        // 检测环境
        const isWeChat = isWeChatWorkPC();
        const isMobileDevice = isMobile();
        
        console.log('环境检测结果:', {
            isWeChat: isWeChat,
            isMobileDevice: isMobileDevice,
            userAgent: navigator.userAgent
        });
        
        // 如果是企业微信PC端，先检测环境
        if (isWeChat) {
            console.log('检测到企业微信PC端，开始处理...');
            
            // 先检测是否需要刷新
            detectAndShowWeChatWorkRefresh();
            
            // 显示文件保存提示
        showWeChatWorkPCSavePrompt(actionType);
            
        // 延迟执行导出，让用户先看到提示
        setTimeout(() => {
                console.log('延迟执行导出...');
                performExport(exportUrl, filterFormId, customFileName);
        }, 100);
        return;
    }
    
        // 非企业微信PC端，显示导出选项对话框
        console.log('非企业微信PC端，显示导出选项对话框...');
        showExportOptionsDialog(exportUrl, filterFormId, customFileName);
        
    } catch (error) {
        console.error('exportToExcel执行出错:', error);
        
        // 出错时回退到简单导出
        console.log('回退到简单导出方式...');
        performSimpleExport(exportUrl, customFileName);
    }
}

// 企业微信手机端最稳定的导出函数 - 确保表头不丢失
function performWeChatMobileExportStable(exportUrl, customFileName = '') {
    console.log('🔧 企业微信手机端最稳定导出:', exportUrl);
    console.log('📱 当前User Agent:', navigator.userAgent);
    
    const fileName = customFileName || 'QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx';
    console.log('📄 文件名:', fileName);
    
    // 显示提示
    showQuickMessage('正在准备下载文件，请稍候...', 'info');
    
    // 使用最稳定的方法：直接window.open，但先验证文件
    console.log('🚀 使用最稳定的下载方式：验证后直接下载');
    
    // 先验证文件是否存在且不为空
    fetch(exportUrl, {
        method: 'HEAD',
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('📡 文件验证响应状态:', response.status);
        
        if (!response.ok) {
            throw new Error(`文件不存在或无法访问: ${response.status}`);
        }
        
        const contentLength = response.headers.get('content-length');
        const contentType = response.headers.get('content-type');
        
        console.log('📊 文件信息:', {
            size: contentLength,
            type: contentType
        });
        
        if (contentLength && parseInt(contentLength) === 0) {
            throw new Error('文件为空');
        }
        
        // 文件验证通过，直接下载
        console.log('✅ 文件验证通过，开始下载');
        showQuickMessage('文件验证通过，开始下载...', 'success');
        
        // 使用window.open下载，这是最稳定的方式
        window.open(exportUrl, '_blank');
        
        // 延迟显示完成提示
        setTimeout(() => {
            showQuickMessage('Excel文件下载已开始，请检查下载文件夹', 'success');
        }, 1000);
        
    })
    .catch(error => {
        console.error('❌ 文件验证失败:', error);
        
        // 验证失败，直接尝试下载
        console.log('🔄 文件验证失败，直接尝试下载');
        showQuickMessage('正在尝试下载...', 'warning');
        
        window.open(exportUrl, '_blank');
        
        setTimeout(() => {
            showQuickMessage('Excel导出已开始，请稍候...', 'success');
        }, 1000);
    });
}

// 企业微信手机端导出函数 - 多种回退方法确保表头不丢失
function performWeChatMobileExportWithFallback(exportUrl, customFileName = '') {
    console.log('🔧 企业微信手机端导出（多回退方法）:', exportUrl);
    console.log('📱 当前User Agent:', navigator.userAgent);
    
    const fileName = customFileName || 'QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx';
    console.log('📄 文件名:', fileName);
    
    // 方法1：尝试fetch + blob方式
    console.log('🚀 尝试方法1：fetch + blob');
    performWeChatMobileExport(exportUrl, fileName)
        .then(() => {
            console.log('✅ 方法1成功');
        })
        .catch(error => {
            console.log('❌ 方法1失败，尝试方法2:', error.message);
            
            // 方法2：尝试iframe方式
            console.log('🚀 尝试方法2：iframe下载');
            try {
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = exportUrl;
                document.body.appendChild(iframe);
                
                setTimeout(() => {
                    document.body.removeChild(iframe);
                    console.log('✅ 方法2完成');
                }, 3000);
                
            } catch (error2) {
                console.log('❌ 方法2失败，尝试方法3:', error2.message);
                
                // 方法3：尝试直接window.open
                console.log('🚀 尝试方法3：window.open');
                try {
                    window.open(exportUrl, '_blank');
                    console.log('✅ 方法3完成');
                } catch (error3) {
                    console.log('❌ 方法3失败，尝试方法4:', error3.message);
                    
                    // 方法4：尝试创建隐藏链接
                    console.log('🚀 尝试方法4：隐藏链接');
                    try {
                        const link = document.createElement('a');
                        link.href = exportUrl;
                        link.target = '_blank';
                        link.style.display = 'none';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        console.log('✅ 方法4完成');
                    } catch (error4) {
                        console.log('❌ 所有方法都失败了:', error4.message);
                        alert('导出失败，请重试');
                    }
                }
            }
        });
}

// 企业微信手机端专用导出函数 - 确保表头不丢失
function performWeChatMobileExport(exportUrl, customFileName = '') {
    console.log('🔧 企业微信手机端专用导出:', exportUrl);
    console.log('📱 当前User Agent:', navigator.userAgent);
    
    // 生成文件名
    const fileName = customFileName || 'QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx';
    console.log('📄 文件名:', fileName);
    
    console.log('🚀 企业微信手机端导出 - 使用fetch方式确保文件完整性');
    
    // 显示加载提示
    showQuickMessage('正在准备下载文件...', 'info');
    
    // 返回Promise
    return new Promise((resolve, reject) => {
        // 使用fetch获取文件内容，确保表头不丢失
        fetch(exportUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'  // 确保携带cookies
        })
        .then(response => {
            console.log('📡 响应状态:', response.status);
            console.log('📡 响应头:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // 检查Content-Type
            const contentType = response.headers.get('content-type');
            console.log('📄 文件类型:', contentType);
            
            return response.blob();
        })
        .then(blob => {
            console.log('✅ 企业微信手机端 - 文件下载成功');
            console.log('📊 文件大小:', blob.size, 'bytes');
            console.log('📊 文件类型:', blob.type);
            
            // 验证文件大小
            if (blob.size === 0) {
                throw new Error('下载的文件为空');
            }
            
            // 创建下载链接
            const url = window.URL.createObjectURL(blob);
            console.log('🔗 创建下载链接:', url);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = fileName;
            link.style.display = 'none';
            
            // 添加到页面并触发下载
            document.body.appendChild(link);
            console.log('🖱️ 触发下载...');
            link.click();
            
            // 延迟清理，确保下载开始
            setTimeout(() => {
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                console.log('🧹 清理完成');
            }, 1000);
            
            console.log('✅ 企业微信手机端导出完成');
            
            // 显示成功提示
            showQuickMessage('Excel文件下载已开始，请检查下载文件夹', 'success');
            
            // 延迟显示完成提示
            setTimeout(() => {
                showExportCompletedPrompt(fileName);
            }, 3000);
            
            resolve();
        })
        .catch(error => {
            console.error('❌ 企业微信手机端fetch导出失败:', error);
            console.error('❌ 错误详情:', error.message);
            
            // 显示错误提示
            showQuickMessage('下载失败，尝试备用方式...', 'warning');
            
            reject(error);
        });
    });
}

// 简单导出方式（作为回退）
function performSimpleExport(exportUrl, customFileName = '') {
    console.log('执行简单导出:', exportUrl);
    
    try {
        // 生成文件名
        const fileName = customFileName || 'QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx';
        
        // 检测环境
        const isMobileDevice = isMobile();
        const isWeChat = isWeChatWorkPC();
        
        console.log('简单导出环境检测:', {
            isMobileDevice: isMobileDevice,
            isWeChat: isWeChat
        });
        
        if (isMobileDevice) {
            // 移动端使用window.open，确保文件完整性
            console.log('移动端，使用window.open下载');
            window.open(exportUrl, '_blank');
        } else {
            // PC端使用link.click
            console.log('PC端，使用link.click下载');
            const link = document.createElement('a');
            link.href = exportUrl;
            link.style.display = 'none';
            link.download = fileName;
            
            // 添加到页面并点击
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        console.log('简单导出完成');
        
        // 显示成功提示
        showQuickMessage('Excel导出已开始，请稍候...', 'success');
        
        // 延迟显示完成提示
        setTimeout(() => {
            showExportCompletedPrompt(fileName);
        }, 3000);
        
    } catch (error) {
        console.error('简单导出失败:', error);
        showQuickMessage('导出失败，请重试', 'error');
    }
}

// 显示导出选项对话框
function showExportOptionsDialog(exportUrl, filterFormId = 'filterForm', customFileName = '') {
    // 生成默认文件名
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-');
            const defaultFileName = customFileName || `QC报表_${dateStr}_${timeStr}.xlsx`;
    
    const modalHTML = `
        <div id="exportOptionsModal" style="
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
                width: 700px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
                position: relative;
                max-height: 90vh;
                overflow-y: auto;
            ">
                <!-- 关闭按钮 -->
                <button onclick="closeExportOptionsDialog()" style="
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    width: 30px;
                    height: 30px;
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    color: #666;
                    transition: all 0.2s;
                    z-index: 10001;
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
                    📊
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 22px;
                    font-weight: 600;
                ">Excel导出选项</h3>
                
                <!-- 文件名设置 -->
                <div style="
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #495057;
                        font-size: 16px;
                        font-weight: 600;
                    ">📝 文件设置</h4>
                    
                    <div style="margin-bottom: 15px;">
                        <label for="exportFileName" style="
                            display: block;
                            margin-bottom: 8px;
                            color: #495057;
                            font-weight: 500;
                        ">文件名：</label>
                        <input type="text" id="exportFileName" value="${defaultFileName}" style="
                            width: 100%;
                            padding: 10px;
                            border: 1px solid #ced4da;
                            border-radius: 6px;
                            font-size: 14px;
                            font-family: monospace;
                        " placeholder="请输入文件名">
                    </div>
                    
                    <div style="
                        background: #e8f5e8;
                        padding: 12px;
                        border-radius: 6px;
                        border: 1px solid #4caf50;
                        font-size: 13px;
                        color: #2e7d32;
                    ">
                        💡 <strong>提示：</strong>文件名将自动添加当前日期和时间，确保唯一性
                    </div>
                </div>
                
                <!-- 导出选项 -->
                <div style="
                    background: #fff3e0;
                    border: 1px solid #ff9800;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #e65100;
                        font-size: 16px;
                        font-weight: 600;
                    ">⚙️ 导出选项</h4>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="
                            display: flex;
                            align-items: center;
                            margin-bottom: 10px;
                            cursor: pointer;
                        ">
                            <input type="radio" name="exportFormat" value="xlsx" checked style="margin-right: 8px;">
                            <span>📊 Excel格式 (.xlsx) - 推荐，支持完整格式</span>
                        </label>
                        <label style="
                            display: flex;
                            align-items: center;
                            margin-bottom: 10px;
                            cursor: pointer;
                        ">
                            <input type="radio" name="exportFormat" value="csv" style="margin-right: 8px;">
                            <span>📄 CSV格式 (.csv) - 兼容性好，文件小</span>
                        </label>
                    </div>
                    
                    <div style="
                        background: #e3f2fd;
                        padding: 12px;
                        border-radius: 6px;
                        border: 1px solid #2196f3;
                        font-size: 13px;
                        color: #1976d2;
                    ">
                        🔍 <strong>说明：</strong>选择不同格式会影响文件大小和兼容性
                    </div>
                </div>
                
                <!-- 保存位置选择 -->
                <div style="
                    background: #f3e5f5;
                    border: 1px solid #9c27b0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #7b1fa2;
                        font-size: 16px;
                        font-weight: 600;
                    ">💾 保存位置选择</h4>
                    
                    <div style="
                        color: #6c757d;
                        font-size: 14px;
                        line-height: 1.6;
                    ">
                        <p style="margin: 0 0 15px 0;"><strong>🎯 重要：您可以在下载前选择保存位置！</strong></p>
                        
                        <div style="
                            background: #e8f5e8;
                            padding: 15px;
                            border-radius: 6px;
                            margin: 15px 0;
                            border: 1px solid #4caf50;
                        ">
                            <h5 style="margin: 0 0 10px 0; color: #2e7d32;">🚀 方法一：使用"另存为"选择路径</h5>
                            <ol style="margin: 0 0 10px 0; padding-left: 20px;">
                                <li>点击"开始导出"按钮</li>
                                <li>在浏览器下载提示中选择"另存为"</li>
                                <li>选择您想要的保存位置和文件名</li>
                                <li>点击"保存"完成下载</li>
                            </ol>
                        </div>
                        
                        <div style="
                            background: #fff3e0;
                            padding: 15px;
                            border-radius: 6px;
                            margin: 15px 0;
                            border: 1px solid #ff9800;
                        ">
                            <h5 style="margin: 0 0 10px 0; color: #e65100;">⚙️ 方法二：修改浏览器默认下载位置</h5>
                            <ol style="margin: 0 0 10px 0; padding-left: 20px;">
                                <li><strong>Chrome/Edge：</strong>设置 → 高级 → 下载内容 → 更改下载位置</li>
                                <li><strong>Firefox：</strong>选项 → 常规 → 下载 → 保存文件到</li>
                                <li><strong>Safari：</strong>偏好设置 → 通用 → 文件下载位置</li>
                            </ol>
                        </div>
                        
                        <div style="
                            background: #e3f2fd;
                            padding: 15px;
                            border-radius: 6px;
                            margin: 15px 0;
                            border: 1px solid #2196f3;
                        ">
                            <h5 style="margin: 0 0 10px 0; color: #1976d2;">📱 企业微信PC端特殊说明</h5>
                            <ul style="margin: 0 0 10px 0; padding-left: 20px;">
                                <li>文件会下载到企业微信设置的下载目录</li>
                                <li>可在企业微信设置中修改下载路径</li>
                                <li>建议使用"另存为"方式选择具体位置</li>
                            </ul>
                        </div>
                        
                        <div style="
                            background: #fce4ec;
                            padding: 15px;
                            border-radius: 6px;
                            margin: 15px 0;
                            border: 1px solid #e91e63;
                        ">
                            <h5 style="margin: 0 0 10px 0; color: #c2185b;">💡 推荐操作流程</h5>
                            <ol style="margin: 0 0 10px 0; padding-left: 20px;">
                                <li><strong>设置默认下载位置</strong>：在浏览器设置中设置常用下载文件夹</li>
                                <li><strong>使用"另存为"</strong>：每次下载时选择"另存为"来指定具体位置</li>
                                <li><strong>创建专用文件夹</strong>：为QC报表创建专门的文件夹便于管理</li>
                            </ol>
                        </div>
                    </div>
                </div>
                
                <!-- 默认保存位置信息 -->
                <div style="
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #495057;
                        font-size: 16px;
                        font-weight: 600;
                    ">📁 当前默认保存位置</h4>
                    
                    <div style="
                        background: #e9ecef;
                        padding: 15px;
                        border-radius: 6px;
                        border: 1px solid #6c757d;
                        font-family: monospace;
                        font-size: 13px;
                        color: #495057;
                    ">
                        <div id="currentDownloadPath">正在检测...</div>
                    </div>
                    
                    <p style="margin: 10px 0 0 0; font-size: 13px; color: #6c757d;">
                        💡 这是浏览器当前的默认下载位置，您可以通过上述方法进行修改
                    </p>
                </div>
                
                <!-- 操作按钮 -->
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                    flex-wrap: wrap;
                ">
                    <button onclick="closeExportOptionsDialog()" style="
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
                    
                    <button onclick="openBrowserSettings()" style="
                        padding: 12px 24px;
                        background: #17a2b8;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                    " onmouseover="this.style.background='#138496'" onmouseout="this.style.background='#17a2b8'">
                        ⚙️ 打开浏览器设置
                    </button>
                    
                    <button onclick="startExportWithOptions()" style="
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
                        🚀 开始导出
                    </button>
                </div>
                
                <!-- 导出提示 -->
                <div style="
                    background: #fff8e1;
                    border: 1px solid #ffcc02;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0 0 0;
                    text-align: center;
                ">
                    <p style="margin: 0; font-size: 13px; color: #e65100;">
                        💡 <strong>提示：</strong>点击"开始导出"后，选择"另存为"即可自由选择保存位置！
                    </p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 存储导出信息，供后续使用
    window.exportOptionsInfo = { 
        exportUrl, 
        filterFormId, 
        customFileName: defaultFileName,
        originalFileName: customFileName 
    };
    
    // 检测当前下载路径
    detectCurrentDownloadPath();
}

// 检测当前下载路径
function detectCurrentDownloadPath() {
    const pathElement = document.getElementById('currentDownloadPath');
    if (!pathElement) return;
    
    // 尝试检测操作系统和默认下载路径
    const userAgent = navigator.userAgent;
    let osInfo = '';
    let defaultPath = '';
    
    if (userAgent.includes('Windows')) {
        osInfo = 'Windows';
        defaultPath = 'C:\\Users\\用户名\\Downloads';
    } else if (userAgent.includes('Mac')) {
        osInfo = 'macOS';
        defaultPath = '/Users/用户名/Downloads';
    } else if (userAgent.includes('Linux')) {
        osInfo = 'Linux';
        defaultPath = '/home/用户名/Downloads';
    } else {
        osInfo = '未知系统';
        defaultPath = '默认下载文件夹';
    }
    
    pathElement.innerHTML = `
        <strong>操作系统：</strong>${osInfo}<br>
        <strong>默认路径：</strong>${defaultPath}<br>
        <strong>检测时间：</strong>${new Date().toLocaleString('zh-CN')}
    `;
}

// 打开浏览器设置
function openBrowserSettings() {
    const userAgent = navigator.userAgent;
    let settingsUrl = '';
    let instructions = '';
    
    if (userAgent.includes('Chrome') || userAgent.includes('Edge')) {
        settingsUrl = 'chrome://settings/downloads';
        instructions = 'Chrome/Edge设置页面已打开，请找到"下载内容"部分修改下载位置';
    } else if (userAgent.includes('Firefox')) {
        settingsUrl = 'about:preferences#general';
        instructions = 'Firefox设置页面已打开，请找到"下载"部分修改保存位置';
    } else if (userAgent.includes('Safari')) {
        instructions = 'Safari：请点击菜单栏 → Safari → 偏好设置 → 通用 → 文件下载位置';
    } else {
        instructions = '请手动打开浏览器设置，找到下载相关设置';
    }
    
    if (settingsUrl) {
        try {
            window.open(settingsUrl, '_blank');
        } catch (e) {
            console.log('无法直接打开设置页面');
        }
    }
    
    // 显示指导信息
    showSettingsInstructions(instructions);
}

// 显示设置指导
function showSettingsInstructions(instructions) {
    const modalHTML = `
        <div id="settingsInstructionsModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10002;
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
                    background: linear-gradient(135deg, #17a2b8, #138496);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    ⚙️
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">浏览器设置指导</h3>
                
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                    line-height: 1.6;
                ">
                    ${instructions}
                </div>
                
                <button onclick="closeSettingsInstructions()" style="
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
                    我知道了
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭设置指导
function closeSettingsInstructions() {
    const modal = document.getElementById('settingsInstructionsModal');
    if (modal) modal.remove();
}

// 关闭导出选项对话框
function closeExportOptionsDialog() {
    const modal = document.getElementById('exportOptionsModal');
    if (modal) modal.remove();
    window.exportOptionsInfo = null;
}

// 开始导出（通过选项对话框）
function startExportWithOptions() {
    if (!window.exportOptionsInfo) {
        console.error('导出信息不存在');
        return;
    }
    
    const { exportUrl, filterFormId } = window.exportOptionsInfo;
    
    // 获取用户设置的文件名
    const fileNameInput = document.getElementById('exportFileName');
    const customFileName = fileNameInput ? fileNameInput.value.trim() : '';
    
    // 获取选择的导出格式
    const formatRadios = document.querySelectorAll('input[name="exportFormat"]');
    let selectedFormat = 'xlsx';
    formatRadios.forEach(radio => {
        if (radio.checked) {
            selectedFormat = radio.value;
        }
    });
    
    // 关闭对话框
    closeExportOptionsDialog();
    
    // 显示导出状态
    showExportStatus('正在准备导出...');
    
    // 执行导出
    performExportWithOptions(exportUrl, filterFormId, customFileName, selectedFormat);
}

// 执行带选项的导出
function performExportWithOptions(exportUrl, filterFormId, customFileName, format) {
    console.log('开始导出，格式:', format, '文件名:', customFileName);
    
    // 构建导出URL，添加格式参数
    let finalExportUrl = exportUrl;
    if (format === 'csv') {
        finalExportUrl = exportUrl.replace('/export_excel/', '/export_csv/');
    }
    
    // 执行实际导出
    performExport(finalExportUrl, filterFormId, customFileName);
}

// 显示导出状态
function showExportStatus(message) {
    // 创建状态提示
    const statusDiv = document.createElement('div');
    statusDiv.id = 'exportStatus';
    statusDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10001;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 300px;
        word-wrap: break-word;
    `;
    statusDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 18px;">📊</span>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(statusDiv);
    
    // 3秒后自动隐藏
    setTimeout(() => {
        if (statusDiv.parentNode) {
            statusDiv.parentNode.removeChild(statusDiv);
        }
    }, 3000);
}

// 执行实际的导出操作
function performExport(exportUrl, filterFormId = 'filterForm', customFileName = '') {
    console.log('🔍 performExport被调用:', {
        exportUrl: exportUrl,
        filterFormId: filterFormId,
        customFileName: customFileName
    });
    
    try {
    const filterForm = document.getElementById(filterFormId);
    console.log('🔍 找到过滤表单:', filterForm);
    
    const params = new URLSearchParams();
        
    if (filterForm) {
        const formData = new FormData(filterForm);
        console.log('🔍 过滤表单数据收集开始...');
        
        for (const [key, value] of formData.entries()) {
            console.log(`🔍 表单字段 [${key}]:`, value, '类型:', typeof value);
            if (key !== 'csrfmiddlewaretoken') {
                // 对于日期和时间字段，允许空字符串（即用户清空后不传递参数）
                if (['start_date','end_date','start_time','end_time'].includes(key)) {
                    if (value.trim() !== '') {
                        params.append(key, value);
                        console.log(`📅 添加日期时间过滤条件 [${key}]:`, value);
                    } else {
                        console.log(`⚠️ 跳过空的日期时间字段 [${key}]:`, value);
                    }
                } else {
                    // 对于其他字段（包括班组），即使为空也要传递，让后端处理
                    params.append(key, value);
                    console.log(`🔍 添加过滤条件 [${key}]:`, value);
                }
            } else {
                console.log(`🔒 跳过CSRF Token字段 [${key}]`);
            }
        }
        
        console.log('🔍 所有过滤条件参数:', params.toString());
    } else {
        console.error('❌ 未找到过滤表单元素，ID:', filterFormId);
    }
        
    const url = `${exportUrl}?${params.toString()}`;
        console.log('🌐 构建的导出URL:', url);
        
        // 检测环境
        const isWeChat = isWeChatWorkPC();
        const isMobileDevice = isMobile();
        
        console.log('🔍 performExport环境检测:', {
            isWeChat: isWeChat,
            isMobileDevice: isMobileDevice
        });
    
    // 如果是企业微信环境，使用特殊的导出方式
        if (isWeChat) {
            console.log('企业微信环境，使用特殊导出方式...');
            
            // 企业微信手机端使用特殊下载方式，确保表头不丢失
            if (isMobileDevice) {
                console.log('企业微信手机端，使用特殊下载方式确保表头完整...');
                // 使用最稳定的下载方式
                performWeChatMobileExportStable(url, customFileName);
            } else {
                console.log('企业微信PC端，使用下载管理器...');
                // 尝试多种导出方式
                try {
                    performWeChatWorkExportWithDownloadManager(url);
                } catch (error) {
                    console.error('企业微信特殊导出失败，回退到简单方式:', error);
                    performSimpleExport(url, customFileName);
                }
            }
    } else {
        // 非企业微信PC端，使用原有方式
            console.log('非企业微信PC端，使用原有导出方式...');
            
            if (isMobileDevice) {
                console.log('移动端，使用window.open');
            window.open(url, '_blank');
        } else {
                console.log('PC端，使用link.click');
            const link = document.createElement('a');
            link.href = url;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        }
        
         } catch (error) {
         console.error('performExport执行出错:', error);
         
         // 出错时回退到简单导出
         console.log('回退到简单导出方式...');
         performSimpleExport(exportUrl, customFileName);
    }
}

// 企业微信PC端特殊导出方式
function performWeChatWorkExport(exportUrl, actionType = 'export', customFileName = '') {
    console.log('开始企业微信PC端特殊导出处理:', { exportUrl, actionType, customFileName });
    
    try {
        // 企业微信特殊处理：直接使用优化的导出方式
        if (customFileName) {
            performSimpleExportForWeChatWithFileName(exportUrl, customFileName);
        } else {
            // 生成默认文件名
            const now = new Date();
            const dateStr = now.toISOString().split('T')[0];
            const defaultFileName = `东泰QC报表_${dateStr}.xlsx`;
            performSimpleExportForWeChatWithFileName(exportUrl, defaultFileName);
        }
        
    } catch (error) {
        console.error('企业微信导出处理失败:', error);
        // 回退到简单导出
        performSimpleExportForWeChat(exportUrl, customFileName);
    }
}

// 新的文件下载管理器方法
function performWeChatWorkExportWithDownloadManager(url) {
    // 设置文件名（基于当前时间）
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-');
    const defaultFileName = `东泰QC报表_${dateStr}_${timeStr}.xlsx`;
    
    // 显示文件下载管理器
    showDownloadManager(url, defaultFileName);
}

// 显示文件下载管理器
function showDownloadManager(url, fileName) {
    const modalHTML = `
        <div id="downloadManagerModal" style="
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
                width: 600px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
                position: relative;
            ">
                <!-- 关闭按钮 -->
                <button onclick="closeDownloadManager()" style="
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    width: 30px;
                    height: 30px;
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    color: #666;
                    transition: all 0.2s;
                    z-index: 10001;
                " onmouseover="this.style.background='#e0e0e0'; this.style.color='#333'" onmouseout="this.style.background='#f5f5f5'; this.style.color='#666'">
                    ×
                </button>
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
                    📥
                </div>
                
                <h3 style="
                    margin: 0 0 15px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">文件下载管理器</h3>
                
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #1976d2;
                        font-size: 16px;
                        font-weight: 600;
                    ">📋 即将下载的文件信息：</h4>
                    
                    <div style="
                        background: #f5f5f5;
                        padding: 15px;
                        border-radius: 6px;
                        margin: 10px 0;
                        font-family: monospace;
                        font-size: 13px;
                        color: #333;
                        border: 1px solid #ddd;
                    ">
                        📄 <strong>文件名：</strong>${fileName}<br>
                        📊 <strong>文件类型：</strong>Excel表格 (.xlsx)<br>
                        📅 <strong>导出时间：</strong>${new Date().toLocaleString('zh-CN')}<br>
                        🌐 <strong>下载方式：</strong>浏览器下载
                    </div>
                </div>
                
                <div style="
                    background: #fff3e0;
                    border: 1px solid #ff9800;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #e65100;
                        font-size: 16px;
                        font-weight: 600;
                    ">⚠️ 重要说明：</h4>
                    
                    <div style="
                        color: #6c757d;
                        font-size: 14px;
                        line-height: 1.6;
                    ">
                        <p style="margin: 0 0 15px 0;"><strong>🎉 好消息！现在文件下载后会自动打开，让您立即查看内容：</strong></p>
                        
                        <div style="
                            background: #e8f5e8;
                            padding: 15px;
                            border-radius: 6px;
                            margin: 10px 0;
                            border: 1px solid #4caf50;
                        ">
                            <h5 style="margin: 0 0 10px 0; color: #2e7d32;">🚀 智能文件预览功能：</h5>
                            <ol style="margin: 0 0 10px 0; padding-left: 20px;">
                                <li>点击下方"开始下载"按钮</li>
                                <li>系统会<strong>自动下载文件内容</strong></li>
                                <li>下载完成后<strong>尝试在页面内预览文件</strong></li>
                                <li>如果预览成功，您可以直接查看Excel内容</li>
                                <li>如果预览失败，文件会保存到默认下载位置</li>
                            </ol>
                        </div>
                        
                        <div style="
                            background: #fff8e1;
                            padding: 15px;
                            border-radius: 6px;
                            margin: 10px 0;
                            border: 1px solid #ffcc02;
                        ">
                            <h5 style="margin: 0 0 10px 0; color: #e65100;">💾 文件保存位置：</h5>
                            <ul style="margin: 0 0 10px 0; padding-left: 20px;">
                                <li><strong>企业微信PC端</strong>：企业微信下载目录</li>
                                <li><strong>浏览器</strong>：系统默认下载文件夹</li>
                                <li><strong>Windows</strong>：用户文件夹\下载</li>
                                <li><strong>Mac</strong>：用户文件夹\下载</li>
                            </ul>
                            
                            <h5 style="margin: 0 0 10px 0; color: #e65100;">🔍 如何找到文件：</h5>
                            <ul style="margin: 0 0 10px 0; padding-left: 20px;">
                                <li>文件下载后会自动打开，您可以立即查看</li>
                                <li>如果需要保存到其他位置，可以<strong>另存为</strong></li>
                                <li>或检查上述默认下载位置</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                ">
                    <button onclick="closeDownloadManager()" style="
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
                        取消下载
                    </button>
                    
                    <button onclick="startDownloadWithManager()" style="
                        padding: 12px 24px;
                        background: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                        font-weight: 600;
                    " onmouseover="this.style.background='#1976D2'" onmouseout="this.style.background='#2196F3'">
                        🚀 开始下载
                    </button>
                </div>
                
                <!-- 下载状态显示区域 -->
                <div id="downloadStatus" style="
                    display: none;
                    margin-top: 20px;
                    padding: 15px;
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 6px;
                    color: #2e7d32;
                    font-size: 14px;
                    text-align: center;
                ">
                    <strong>下载状态：</strong><span id="statusText">准备就绪</span>
                </div>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：下载完成后，请按照上述解决方案找到并管理您的文件。<br>
                    如果仍有问题，可以联系技术支持获取帮助。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 存储下载信息，供后续使用
    window.downloadManagerInfo = { url, fileName };
}

// 关闭下载管理器
function closeDownloadManager() {
    const modal = document.getElementById('downloadManagerModal');
    if (modal) modal.remove();
    window.downloadManagerInfo = null;
}

// 开始下载（通过下载管理器）
function startDownloadWithManager() {
    if (!window.downloadManagerInfo) {
        console.error('下载信息不存在');
        return;
    }
    
    const { url, fileName } = window.downloadManagerInfo;
    
    // 关闭下载管理器
    closeDownloadManager();
    
    // 显示下载状态
    showDownloadStatus('正在准备下载...');
    
    // 执行下载
    performSmartDownload(url, fileName);
}

// 智能下载方法
function performSmartDownload(url, fileName) {
    console.log('开始智能下载:', url, fileName);
    
    // 方法1：先下载文件，然后自动打开
    downloadAndAutoOpen(url, fileName);
}

// 下载并自动打开文件
function downloadAndAutoOpen(url, fileName) {
    console.log('开始下载并自动打开文件');
    showDownloadStatus('正在下载文件...');
    
    // 使用fetch下载文件
    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.blob();
        })
        .then(blob => {
            console.log('文件下载完成，大小:', blob.size, '字节');
            showDownloadStatus('文件下载完成，正在准备打开...');
            
            // 自动打开文件
            autoOpenFile(blob, fileName);
        })
        .catch(error => {
            console.error('文件下载失败:', error);
            showDownloadStatus('文件下载失败，尝试直接下载...');
            
            // 如果fetch失败，回退到传统下载方式
            setTimeout(() => {
                fallbackDownload(url, fileName);
            }, 1000);
        });
}

// 自动打开文件
function autoOpenFile(blob, fileName) {
    console.log('准备自动打开文件:', fileName);
    showDownloadStatus('正在准备文件预览...');
    
    try {
        // 创建blob URL
        const blobUrl = window.URL.createObjectURL(blob);
        console.log('创建blob URL:', blobUrl);
        
        // 方法1：尝试在新窗口中打开
        const newWindow = window.open(blobUrl, '_blank');
        
        if (newWindow) {
            console.log('文件已在新窗口中打开');
            showDownloadStatus('文件已在新窗口中打开！');
            
            // 显示导出完成提示
            setTimeout(() => {
                showExportCompletedPrompt(fileName, blob.size);
            }, 2000);
            
            // 清理blob URL
            setTimeout(() => {
                window.URL.revokeObjectURL(blobUrl);
                console.log('已释放blob URL');
            }, 10000); // 给用户足够时间查看文件
            
        } else {
            console.log('无法打开新窗口，尝试其他方法');
            showDownloadStatus('无法打开新窗口，尝试其他方法...');
            
            // 方法2：尝试在当前页面打开
            tryOpenInCurrentPage(blobUrl, fileName);
        }
        
    } catch (error) {
        console.error('自动打开文件失败:', error);
        showDownloadStatus('自动打开失败，使用传统下载...');
        
        // 回退到传统下载
        fallbackDownloadWithBlob(blob, fileName);
    }
}

// 在当前页面尝试打开文件
function tryOpenInCurrentPage(blobUrl, fileName) {
    console.log('尝试在当前页面打开文件');
    
    // 创建文件预览容器
    const previewContainer = document.createElement('div');
    previewContainer.id = 'filePreviewContainer';
    previewContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: white;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    // 创建预览头部
    const previewHeader = document.createElement('div');
    previewHeader.style.cssText = `
        background: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    `;
    
    // 文件信息
    const fileInfo = document.createElement('div');
    fileInfo.innerHTML = `
        <h3 style="margin: 0; color: #333; font-size: 18px;">📄 ${fileName}</h3>
        <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">文件预览模式 - 企业微信PC端优化</p>
    `;
    
    // 操作按钮组
    const buttonGroup = document.createElement('div');
    buttonGroup.style.cssText = `
        display: flex;
        gap: 10px;
        align-items: center;
    `;
    
    // 下载按钮
    const downloadBtn = document.createElement('button');
    downloadBtn.textContent = '💾 下载文件';
    downloadBtn.style.cssText = `
        padding: 8px 16px;
        background: #28a745;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s;
    `;
    downloadBtn.onmouseover = () => downloadBtn.style.background = '#218838';
    downloadBtn.onmouseout = () => downloadBtn.style.background = '#28a745';
    downloadBtn.onclick = () => {
        // 触发文件下载
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = fileName;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 显示下载提示
        showDownloadNotification('文件下载已触发，请检查下载文件夹');
    };
    
    // 关闭按钮
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '❌ 关闭预览';
    closeBtn.style.cssText = `
        padding: 8px 16px;
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s;
    `;
    closeBtn.onmouseover = () => closeBtn.style.background = '#c82333';
    closeBtn.onmouseout = () => closeBtn.style.background = '#dc3545';
    closeBtn.onclick = () => {
        document.body.removeChild(previewContainer);
        // 清理blob URL
        window.URL.revokeObjectURL(blobUrl);
        // 显示导出完成提示
        showExportCompletedPrompt(fileName);
    };
    
    // 组装头部
    buttonGroup.appendChild(downloadBtn);
    buttonGroup.appendChild(closeBtn);
    previewHeader.appendChild(fileInfo);
    previewHeader.appendChild(buttonGroup);
    
    // 创建预览内容区域
    const previewContent = document.createElement('div');
    previewContent.style.cssText = `
        flex: 1;
        padding: 20px;
        overflow: auto;
        background: #f8f9fa;
    `;
    
    // 尝试显示文件内容
    if (fileName.toLowerCase().endsWith('.xlsx') || fileName.toLowerCase().endsWith('.xls')) {
        // Excel文件，显示特殊提示
        previewContent.innerHTML = `
            <div style="
                background: white;
                border-radius: 8px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin: 20px;
            ">
                <div style="
                    width: 80px;
                    height: 80px;
                    background: linear-gradient(135deg, #28a745, #20c997);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 32px;
                ">
                    📊
                </div>
                
                <h3 style="color: #333; margin-bottom: 15px;">Excel文件预览</h3>
                
                <div style="
                    background: #e8f5e8;
                    border: 1px solid #28a745;
                    border-radius: 6px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="color: #155724; margin-bottom: 15px;">📋 文件信息：</h4>
                    <ul style="color: #155724; line-height: 1.6; margin: 0; padding-left: 20px;">
                        <li><strong>文件名：</strong>${fileName}</li>
                        <li><strong>文件类型：</strong>Excel表格</li>
                        <li><strong>预览状态：</strong>已成功加载</li>
                    </ul>
                </div>
                
                <div style="
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    border-radius: 6px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="color: #856404; margin-bottom: 15px;">💡 企业微信PC端说明：</h4>
                    <p style="color: #856404; margin: 0; line-height: 1.6;">
                        由于企业微信的安全限制，无法直接预览Excel文件内容。<br>
                        但您可以：<br>
                        1. <strong>下载文件</strong>到本地查看<br>
                        2. <strong>使用"另存为"</strong>选择保存位置<br>
                        3. 在本地Excel应用中打开文件
                    </p>
                </div>
                
                <div style="
                    background: #d1ecf1;
                    border: 1px solid #17a2b8;
                    border-radius: 6px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="color: #0c5460; margin-bottom: 15px;">🔧 操作建议：</h4>
                    <ol style="color: #0c5460; line-height: 1.6; margin: 0; padding-left: 20px;">
                        <li>点击上方的"💾 下载文件"按钮</li>
                        <li>文件会保存到默认下载位置</li>
                        <li>在文件管理器中找到下载的文件</li>
                        <li>双击文件在Excel中打开</li>
                    </ol>
                </div>
            </div>
        `;
    } else {
        // 其他文件类型
        previewContent.innerHTML = `
            <div style="text-align: center; padding: 50px;">
                <h3>文件预览</h3>
                <p>文件类型：${fileName.split('.').pop()}</p>
                <p>请下载文件后在本地应用中打开</p>
            </div>
        `;
    }
    
    // 组装预览容器
    previewContainer.appendChild(previewHeader);
    previewContainer.appendChild(previewContent);
    
    // 添加到页面
    document.body.appendChild(previewContainer);
    
    console.log('文件预览界面已创建');
    showDownloadStatus('文件预览界面已创建，可以查看文件信息');
}

// 显示下载通知
function showDownloadNotification(message) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10002;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    
    notification.textContent = message;
    
    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.style.animation = 'slideOut 0.3s ease-in';
            notification.style.animationFillMode = 'forwards';
            
            // 添加消失动画
            const disappearStyle = document.createElement('style');
            disappearStyle.textContent = `
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(disappearStyle);
            
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }
    }, 3000);
}

// 回退下载方法（使用blob）
function fallbackDownloadWithBlob(blob, fileName) {
    console.log('使用blob回退下载');
    
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileName;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showDownloadStatus('文件已下载到默认位置');
    
    // 显示导出完成提示
    setTimeout(() => {
        showExportCompletedPrompt(fileName, blob.size);
    }, 2000);
}

// 传统下载回退方法
function fallbackDownload(url, fileName) {
    console.log('使用传统下载方法');
    
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showDownloadStatus('文件已下载到默认位置');
    
    // 显示导出完成提示
    setTimeout(() => {
        showExportCompletedPrompt(fileName);
    }, 2000);
}

// 执行实际下载，强制弹出"另存为"对话框
function performActualDownload(url, fileName) {
    console.log('开始执行下载，URL:', url, '文件名:', fileName);
    
    // 显示下载状态提示
    showDownloadStatus('正在准备下载...');
    
    // 方法1：使用fetch下载文件内容，然后创建blob URL
    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
        .then(response => {
            console.log('Fetch响应状态:', response.status, response.ok);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.blob();
        })
        .then(blob => {
            console.log('获取到blob数据，大小:', blob.size, '字节');
            showDownloadStatus('正在创建下载链接...');
            
            // 创建blob URL
            const blobUrl = window.URL.createObjectURL(blob);
            console.log('创建blob URL:', blobUrl);
            
            // 创建下载链接
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = fileName;
            link.style.display = 'none';
            
            // 添加到页面
            document.body.appendChild(link);
            console.log('下载链接已添加到页面');
            
            // 触发下载
            link.click();
            console.log('已触发下载点击事件');
            
            // 清理
            document.body.removeChild(link);
            
            // 释放blob URL
            setTimeout(() => {
                window.URL.revokeObjectURL(blobUrl);
                console.log('已释放blob URL');
            }, 1000);
            
            showDownloadStatus('下载已触发，请检查浏览器下载状态');
        })
        .catch(error => {
            console.error('下载失败:', error);
            showDownloadStatus('Fetch下载失败，尝试备用方法...');
            
            // 如果fetch失败，回退到直接链接方式
            tryDirectDownload(url, fileName);
        });
}

// 直接下载方法（备用）
function tryDirectDownload(url, fileName) {
    console.log('尝试直接下载方法');
    showDownloadStatus('尝试直接下载...');
    
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.target = '_blank';
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log('直接下载方法已执行');
    showDownloadStatus('直接下载已执行，请检查下载状态');
}

// 显示下载状态
function showDownloadStatus(message) {
    console.log('下载状态:', message);
    
    // 如果存在状态显示元素，更新它
    const statusElement = document.getElementById('downloadStatus');
    const statusTextElement = document.getElementById('statusText');
    
    if (statusElement && statusTextElement) {
        statusTextElement.textContent = message;
        statusElement.style.display = 'block';
    }
}

// 备用下载方法：使用iframe方式强制下载
function performDownloadWithIframe(url, fileName) {
    // 创建隐藏的iframe
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = url;
    
    // 添加到页面
    document.body.appendChild(iframe);
    
    // 设置超时清理
    setTimeout(() => {
        if (document.body.contains(iframe)) {
            document.body.removeChild(iframe);
        }
    }, 5000);
}

// 备用下载方法：使用window.open方式
function performDownloadWithWindowOpen(url, fileName) {
    // 在新窗口中打开下载链接
    const downloadWindow = window.open(url, '_blank');
    
    // 设置超时关闭
    setTimeout(() => {
        if (downloadWindow && !downloadWindow.closed) {
            downloadWindow.close();
        }
    }, 3000);
}

// 显示文件保存位置选择提示
function showFileSaveLocationPrompt(url, fileName, onConfirm) {
    const modalHTML = `
        <div id="fileSaveLocationModal" style="
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
                width: 550px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
                position: relative;
            ">
                <!-- 关闭按钮 -->
                <button onclick="closeFileSaveLocationModal()" style="
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    width: 30px;
                    height: 30px;
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    color: #666;
                    transition: all 0.2s;
                    z-index: 10001;
                " onmouseover="this.style.background='#e0e0e0'; this.style.color='#333'" onmouseout="this.style.background='#f5f5f5'; this.style.color='#666'">
                    ×
                </button>
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #FF9800, #F57C00);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    📁
                </div>
                
                <h3 style="
                    margin: 0 0 15px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">选择文件保存位置</h3>
                
                <div style="
                    background: #fff3e0;
                    border: 1px solid #ffcc02;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #e65100;
                        font-size: 16px;
                        font-weight: 600;
                    ">💡 企业微信PC端文件保存说明：</h4>
                    
                    <div style="
                        color: #6c757d;
                        font-size: 14px;
                        line-height: 1.6;
                    ">
                        <p style="margin: 0 0 15px 0;"><strong>即将导出的文件：</strong></p>
                        <div style="
                            background: #fff8e1;
                            padding: 15px;
                            border-radius: 6px;
                            margin: 10px 0;
                            font-family: monospace;
                            font-size: 13px;
                            color: #e65100;
                            border: 1px solid #ffcc02;
                        ">
                            📄 文件名：<strong>${fileName}</strong><br>
                            📊 文件类型：Excel表格 (.xlsx)<br>
                            📅 导出时间：${new Date().toLocaleString('zh-CN')}
                        </div>
                        
                        <p style="margin: 0 0 15px 0;"><strong>新的文件保存方式：</strong></p>
                        <ol style="margin: 0 0 15px 0; padding-left: 20px;">
                            <li>点击下方"开始导出"按钮</li>
                            <li>系统会<strong>先下载文件内容</strong></li>
                            <li>然后弹出<strong>文件保存位置选择器</strong></li>
                            <li>您可以<strong>自由选择保存位置和文件名</strong></li>
                            <li>选择完成后点击"保存"</li>
                        </ol>
                        
                        <p style="margin: 0 0 15px 0;"><strong>技术特点：</strong></p>
                        <ul style="margin: 0 0 10px 0; padding-left: 20px;">
                            <li>✅ 使用现代文件选择器API</li>
                            <li>✅ 真正让用户选择保存位置</li>
                            <li>✅ 支持任意文件夹和文件名</li>
                            <li>✅ 如果现代API不可用，自动回退到传统方式</li>
                        </ul>
                        
                        <p style="margin: 0 0 10px 0;"><strong>推荐保存位置：</strong></p>
                        <ul style="margin: 0 0 10px 0; padding-left: 20px;">
                            <li>📂 桌面 - 方便查找</li>
                            <li>📂 文档文件夹 - 专业管理</li>
                            <li>📂 自定义文件夹 - 按需组织</li>
                        </ul>
                    </div>
                </div>
                
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                ">
                    <button onclick="closeFileSaveLocationModal()" style="
                        padding: 12px 24px;
                        background: #6c757d;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                    " onmouseover="this.style.background='#6c757d'" onmouseout="this.style.background='#6c757d'">
                        取消导出
                    </button>
                    
                    <button onclick="startWeChatWorkExport()" style="
                        padding: 12px 24px;
                        background: #FF9800;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                        font-weight: 600;
                    " onmouseover="this.style.background='#F57C00'" onmouseout="this.style.background='#FF9800'">
                        🚀 开始导出
                    </button>
                </div>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：点击"开始导出"后，您将看到"另存为"对话框，<br>
                    可以自由选择文件保存位置和修改文件名。
                </p>
                
                <!-- 下载状态显示区域 -->
                <div id="downloadStatus" style="
                    display: none;
                    margin-top: 20px;
                    padding: 15px;
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 6px;
                    color: #1976d2;
                    font-size: 14px;
                    text-align: center;
                ">
                    <strong>下载状态：</strong><span id="statusText">准备就绪</span>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 存储回调函数，供后续使用
    window.weChatWorkExportCallback = onConfirm;
}

// 关闭文件保存位置选择提示
function closeFileSaveLocationModal() {
    const modal = document.getElementById('fileSaveLocationModal');
    if (modal) modal.remove();
    window.weChatWorkExportCallback = null;
}

// 开始企业微信PC端导出
function startWeChatWorkExport() {
    // 关闭提示模态框
    closeFileSaveLocationModal();
    
    // 执行导出回调
    if (window.weChatWorkExportCallback) {
        window.weChatWorkExportCallback();
        window.weChatWorkExportCallback = null;
    }
}

// 显示导出完成提示
function showExportCompletedPrompt(fileName = '', fileSize = null) {
    // 检测操作系统和默认下载路径
    const { osInfo, defaultPath, downloadFolderName } = detectOSAndDownloadPath();
    
    // 检测是否为移动端
    const isMobileDevice = isMobile();
    
    // 检测是否为企业微信环境
    const isWeChatEnv = isWeChatWorkPC();
    
    const modalHTML = `
        <div id="exportCompletedModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10004;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 90%;
                width: 600px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
                max-height: 90vh;
                overflow-y: auto;
            ">
                <!-- 关闭按钮 -->
                <button onclick="closeExportCompletedModal()" style="
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    width: 30px;
                    height: 30px;
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    color: #666;
                    transition: all 0.2s;
                    z-index: 10001;
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
                    font-size: 22px;
                    font-weight: 600;
                ">Excel导出完成！</h3>
                
                <!-- 文件信息 -->
                <div style="
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #2e7d32;
                        font-size: 16px;
                        font-weight: 600;
                    ">📄 文件信息</h4>
                    
                    <div style="
                        background: #f5f5f5;
                        padding: 15px;
                        border-radius: 6px;
                        border: 1px solid #ddd;
                        font-family: monospace;
                        font-size: 13px;
                        color: #333;
                    ">
                        <div><strong>文件名：</strong>${fileName || 'QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx'}</div>
                        ${fileSize ? `<div><strong>文件大小：</strong>${formatFileSize(fileSize)}</div>` : ''}
                        <div><strong>导出时间：</strong>${new Date().toLocaleString('zh-CN')}</div>
                        <div><strong>文件格式：</strong>${fileName.endsWith('.xlsx') ? 'Excel (.xlsx)' : 'CSV (.csv)'}</div>
                    </div>
                </div>
                
                <!-- 保存位置信息 -->
                        <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #1976d2;
                        font-size: 16px;
                        font-weight: 600;
                    ">💾 保存位置</h4>
                    
                    <div style="
                        background: #f8f9fa;
                            padding: 15px;
                            border-radius: 6px;
                        border: 1px solid #dee2e6;
                            font-family: monospace;
                            font-size: 13px;
                            color: #495057;
                        ">
                        <div><strong>操作系统：</strong>${osInfo}</div>
                        <div><strong>完整路径：</strong>${defaultPath}</div>
                        <div><strong>文件夹名：</strong>${downloadFolderName}</div>
                        ${isWeChatEnv ? '<div><strong>环境说明：</strong>企业微信PC端下载目录</div>' : ''}
                        <div style="margin-top: 10px; padding: 10px; background: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px;">
                            <strong>📂 完整文件路径：</strong><br>
                            <span style="color: #2e7d32; font-weight: bold;">${defaultPath}${osInfo === 'Windows' ? '\\\\' : '/'}${fileName || 'QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx'}</span>
                        </div>
                        </div>
                        
                    <p style="margin: 15px 0 0 0; font-size: 13px; color: #6c757d;">
                        💡 文件已保存到上述位置，您可以通过以下方式快速访问
                    </p>
                </div>
                
                <!-- 快速访问选项 -->
                <div style="
                    background: #fff3e0;
                    border: 1px solid #ff9800;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <h4 style="
                        margin: 0 0 15px 0;
                        color: #e65100;
                        font-size: 16px;
                        font-weight: 600;
                    ">🚀 快速访问</h4>
                    
                    <div style="
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                        margin-bottom: 15px;
                    ">
                        <button onclick="showFileLocationGuide()" style="
                            padding: 12px 16px;
                            background: #17a2b8;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 500;
                            transition: background-color 0.2s;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            gap: 8px;
                        " onmouseover="this.style.background='#138496'" onmouseout="this.style.background='#17a2b8'">
                            🔍 查看位置指导
                        </button>
                        
                        <button onclick="copyFilePath('${defaultPath}${osInfo === 'Windows' ? '\\\\' : '/'}${fileName || 'QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx'}')" style="
                            padding: 12px 16px;
                            background: #28a745;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 500;
                            transition: background-color 0.2s;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            gap: 8px;
                        " onmouseover="this.style.background='#218838'" onmouseout="this.style.background='#28a745'">
                            📋 复制路径
                        </button>
                    </div>
                    
                    ${isMobileDevice ? `
                        <div style="
                            background: #fce4ec;
                            padding: 12px;
                            border-radius: 6px;
                            border: 1px solid #e91e63;
                            font-size: 13px;
                            color: #c2185b;
                        ">
                            📱 <strong>移动端提示：</strong>文件已下载到设备下载文件夹，您可以通过文件管理器查看
                        </div>
                    ` : ''}
                </div>
                
                <!-- 操作按钮 -->
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                    flex-wrap: wrap;
                ">
                    <button onclick="closeExportCompletedModal()" style="
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
                        ✕ 关闭
                    </button>
                    
                    <button onclick="exportAnotherFile()" style="
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
                        📊 继续导出
                    </button>
                </div>
                
                <!-- 提示信息 -->
                <div style="
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0 0 0;
                    text-align: center;
                ">
                    <p style="margin: 0; font-size: 12px; color: #6c757d;">
                        💡 提示：如果找不到文件，请检查浏览器的下载设置或联系技术支持
                </p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 检测操作系统和下载路径
function detectOSAndDownloadPath() {
    const userAgent = navigator.userAgent;
    let osInfo = '';
    let defaultPath = '';
    let downloadFolderName = '';
    
    if (userAgent.includes('Windows')) {
        osInfo = 'Windows';
        defaultPath = 'C:\\Users\\用户名\\Downloads';
        downloadFolderName = '下载';
    } else if (userAgent.includes('Mac')) {
        osInfo = 'macOS';
        defaultPath = '/Users/用户名/Downloads';
        downloadFolderName = 'Downloads';
    } else if (userAgent.includes('Linux')) {
        osInfo = 'Linux';
        defaultPath = '/home/用户名/Downloads';
        downloadFolderName = 'Downloads';
    } else if (userAgent.includes('Android')) {
        osInfo = 'Android';
        defaultPath = '内部存储/Download';
        downloadFolderName = 'Download';
    } else if (userAgent.includes('iPhone') || userAgent.includes('iPad')) {
        osInfo = 'iOS';
        defaultPath = '文件/下载';
        downloadFolderName = '下载';
    } else {
        osInfo = '未知系统';
        defaultPath = '默认下载文件夹';
        downloadFolderName = '下载';
    }
    
    return { osInfo, defaultPath, downloadFolderName };
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '未知大小';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 打开下载文件夹
function openDownloadFolder() {
    try {
        // 尝试使用系统命令打开文件夹
        if (navigator.platform.includes('Win')) {
            // Windows
            window.open('file:///C:/Users/' + (process.env.USERNAME || '用户名') + '/Downloads');
        } else if (navigator.platform.includes('Mac')) {
            // macOS
            window.open('file:///Users/' + (process.env.USER || '用户名') + '/Downloads');
        } else if (navigator.platform.includes('Linux')) {
            // Linux
            window.open('file:///home/' + (process.env.USER || '用户名') + '/Downloads');
        } else {
            // 其他系统，尝试通用方法
            window.open('file:///Downloads');
        }
        
        showQuickMessage('正在尝试打开下载文件夹...', 'info');
        
    } catch (error) {
        console.error('打开下载文件夹失败:', error);
        showQuickMessage('无法自动打开文件夹，请手动导航到下载文件夹', 'warning');
    }
}

// 显示文件位置指导
function showFileLocationGuide() {
    const { osInfo } = detectOSAndDownloadPath();
    
    let guideContent = '';
    
    if (osInfo === 'Windows') {
        guideContent = `
            <h4>Windows系统查找方法：</h4>
            <ol>
                <li>按 <strong>Win + E</strong> 打开文件资源管理器</li>
                <li>在左侧导航栏找到 <strong>"下载"</strong> 文件夹</li>
                <li>或直接访问：<strong>C:\\Users\\用户名\\Downloads</strong></li>
                <li>在地址栏输入：<strong>%USERPROFILE%\\Downloads</strong></li>
            </ol>
        `;
    } else if (osInfo === 'macOS') {
        guideContent = `
            <h4>macOS系统查找方法：</h4>
            <ol>
                <li>按 <strong>Cmd + Space</strong> 打开Spotlight搜索</li>
                <li>输入 <strong>"Downloads"</strong> 或 <strong>"下载"</strong></li>
                <li>或打开Finder，在左侧边栏找到 <strong>"下载"</strong></li>
                <li>或直接访问：<strong>/Users/用户名/Downloads</strong></li>
            </ol>
        `;
    } else if (osInfo === 'Linux') {
        guideContent = `
            <h4>Linux系统查找方法：</h4>
            <ol>
                <li>打开文件管理器</li>
                <li>在左侧导航栏找到 <strong>"Downloads"</strong> 文件夹</li>
                <li>或直接访问：<strong>/home/用户名/Downloads</strong></li>
                <li>在终端中输入：<strong>xdg-open ~/Downloads</strong></li>
            </ol>
        `;
    } else {
        guideContent = `
            <h4>通用查找方法：</h4>
            <ol>
                <li>打开文件管理器或资源管理器</li>
                <li>查找名为 <strong>"下载"</strong> 或 <strong>"Downloads"</strong> 的文件夹</li>
                <li>通常在用户主目录下</li>
                <li>或检查浏览器的下载设置</li>
            </ol>
        `;
    }
    
    const modalHTML = `
        <div id="fileLocationGuideModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10005;
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
                    background: linear-gradient(135deg, #17a2b8, #138496);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    🔍
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">文件位置查找指导</h3>
                
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                    line-height: 1.6;
                ">
                    ${guideContent}
                </div>
                
                <button onclick="closeFileLocationGuideModal()" style="
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
                    我知道了
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭文件位置指导
function closeFileLocationGuideModal() {
    const modal = document.getElementById('fileLocationGuideModal');
    if (modal) modal.remove();
}

// 关闭导出完成提示
function closeExportCompletedModal() {
    const modal = document.getElementById('exportCompletedModal');
    if (modal) modal.remove();
}

// 复制文件路径到剪贴板
function copyFilePath(filePath) {
    try {
        // 尝试使用现代剪贴板API
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(filePath).then(() => {
                showQuickMessage('文件路径已复制到剪贴板！', 'success');
            }).catch(error => {
                console.error('复制失败:', error);
                fallbackCopyMethod(filePath);
            });
        } else {
            // 回退到传统方法
            fallbackCopyMethod(filePath);
        }
    } catch (error) {
        console.error('复制路径时出错:', error);
        showQuickMessage('复制失败，请手动复制路径', 'error');
    }
}

// 传统复制方法
function fallbackCopyMethod(text) {
    try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
            showQuickMessage('文件路径已复制到剪贴板！', 'success');
        } else {
            showQuickMessage('复制失败，请手动选择并复制路径', 'warning');
        }
    } catch (error) {
        console.error('传统复制方法失败:', error);
        showQuickMessage('复制失败，请手动复制路径', 'error');
    }
}

// 继续导出文件
function exportAnotherFile() {
    closeExportCompletedModal();
    
    // 延迟一下，让用户看到关闭动画
    setTimeout(() => {
        // 重新显示导出选项对话框
        if (window.exportOptionsInfo) {
            const { exportUrl, filterFormId, customFileName } = window.exportOptionsInfo;
            showExportOptionsDialog(exportUrl, filterFormId, customFileName);
        }
    }, 300);
}

// 显示快速消息
function showQuickMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'info' ? '#2196F3' : type === 'warning' ? '#ff9800' : '#4CAF50'};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10006;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 300px;
        word-wrap: break-word;
    `;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // 3秒后自动隐藏
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 3000);
}

// 企业微信PC端特殊导出处理
function performWeChatWorkExport(exportUrl, actionType = 'export', customFileName = '') {
    console.log('开始企业微信PC端特殊导出处理:', { exportUrl, actionType, customFileName });
    
    try {
        // 显示企业微信专用导出选项对话框
        showWeChatWorkExportOptionsDialog(exportUrl, actionType, customFileName);
        
    } catch (error) {
        console.error('企业微信导出处理失败:', error);
        // 回退到简单导出
        performSimpleExportForWeChat(exportUrl, customFileName);
    }
}

// 显示企业微信导出选项对话框
function showWeChatWorkExportOptionsDialog(exportUrl, actionType, customFileName) {
    const actionNames = {
        'export': '远通QC报表',
        'yesterday': '昨日产量统计',
        'today': '今日产量统计'
    };
    
    const actionName = actionNames[actionType] || '报表';
    const defaultFileName = customFileName || `${actionName}_${new Date().toISOString().split('T')[0]}.xlsx`;
    
    const modalHTML = `
        <div id="wechatExportOptionsModal" style="
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
                width: 600px;
                max-height: 90vh;
                overflow-y: auto;
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
                    📊
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">企业微信PC端导出设置</h3>
                
                <!-- 导出信息 -->
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>📋 导出信息：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>导出类型：${actionName}</li>
                        <li>文件格式：Excel (.xlsx)</li>
                        <li>当前时间：${new Date().toLocaleString('zh-CN')}</li>
                    </ul>
                </div>
                
                <!-- 文件名设置 -->
                <div style="
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                ">
                    <label for="wechatFileName" style="
                        display: block;
                        margin-bottom: 10px;
                        font-weight: 600;
                        color: #333;
                    ">📝 自定义文件名：</label>
                    <input type="text" id="wechatFileName" value="${defaultFileName}" style="
                        width: 100%;
                        padding: 12px;
                        border: 2px solid #e0e0e0;
                        border-radius: 6px;
                        font-size: 14px;
                        transition: border-color 0.2s;
                    " onfocus="this.style.borderColor='#2196F3'" onblur="this.style.borderColor='#e0e0e0'">
                    <p style="
                        margin: 10px 0 0 0;
                        font-size: 12px;
                        color: #666;
                    ">💡 提示：可以修改文件名，系统会自动添加.xlsx扩展名</p>
                </div>
                
                <!-- 保存位置指导 -->
                    <div style="
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #856404;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>💾 保存位置设置：</strong></p>
                        <div style="
                        background: #e8f5e8;
                        border: 1px solid #4caf50;
                        border-radius: 6px;
                            padding: 15px;
                        margin: 10px 0;
                        color: #2e7d32;
                    ">
                        <p style="margin: 0 0 10px 0;"><strong>🎯 推荐方法（推荐）：</strong></p>
                        <ol style="margin: 0 0 10px 0; padding-left: 20px;">
                            <li>点击"开始导出"按钮</li>
                            <li>在浏览器弹出的"另存为"对话框中</li>
                            <li>选择您想要的保存位置和文件夹</li>
                            <li>点击"保存"完成导出</li>
                        </ol>
                    </div>
                    
                    <div style="
                        background: #e3f2fd;
                        border: 1px solid #2196f3;
                            border-radius: 6px;
                        padding: 15px;
                            margin: 10px 0;
                            color: #1976d2;
                        ">
                        <p style="margin: 0 0 10px 0;"><strong>⚙️ 修改默认下载位置：</strong></p>
                        <ol style="margin: 0 0 10px 0; padding-left: 20px;">
                            <li>点击"打开浏览器设置"按钮</li>
                            <li>在下载设置中修改默认保存位置</li>
                            <li>设置完成后重新导出</li>
                        </ol>
                    </div>
                </div>
                
                <!-- 操作按钮 -->
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                    flex-wrap: wrap;
                ">
                    <button onclick="closeWeChatExportOptionsModal()" style="
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
                        取消
                    </button>
                    
                    <button onclick="openWeChatBrowserSettings()" style="
                        padding: 12px 24px;
                        background: #17a2b8;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                    " onmouseover="this.style.background='#138496'" onmouseout="this.style.background='#17a2b8'">
                        ⚙️ 打开浏览器设置
                    </button>
                    
                    <button onclick="startWeChatWorkExportWithOptions()" style="
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
                    💡 提示：企业微信环境下，建议使用"另存为"方式选择保存位置，这样可以完全控制文件的保存位置。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 存储导出信息
    window.wechatExportOptionsInfo = { 
        exportUrl, 
        actionType, 
        customFileName: defaultFileName 
    };
}

// 关闭企业微信导出选项对话框
function closeWeChatExportOptionsModal() {
    const modal = document.getElementById('wechatExportOptionsModal');
    if (modal) modal.remove();
}

// 打开企业微信浏览器设置
function openWeChatBrowserSettings() {
    try {
        // 尝试打开浏览器设置
        if (typeof window.openBrowserSettings === 'function') {
            window.openBrowserSettings();
        } else {
            // 显示设置指导
            showWeChatSettingsInstructions();
        }
    } catch (error) {
        console.error('打开浏览器设置失败:', error);
        showWeChatSettingsInstructions();
    }
}

// 显示企业微信设置指导
function showWeChatSettingsInstructions() {
    const modalHTML = `
        <div id="wechatSettingsModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10001;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 90%;
                width: 500px;
                max-height: 90vh;
                overflow-y: auto;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #17a2b8, #138496);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    ⚙️
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">浏览器下载设置指导</h3>
                
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>🔧 修改默认下载位置：</strong></p>
                    <ol style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>按 <kbd>Ctrl+Shift+Delete</kbd> (Windows) 或 <kbd>Cmd+Shift+Delete</kbd> (Mac)</li>
                        <li>选择"设置"或"首选项"</li>
                        <li>找到"下载内容"或"下载"设置</li>
                        <li>点击"更改"选择新的下载位置</li>
                        <li>确认设置并关闭</li>
                    </ol>
                    
                    <p style="margin: 0;"><strong>💡 提示：</strong>设置完成后，所有下载文件都会保存到新位置</p>
                </div>
                
                <button onclick="closeWeChatSettingsModal()" style="
                    padding: 12px 24px;
                    background: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: background-color 0.2s;
                " onmouseover="this.style.background='#138496'" onmouseout="this.style.background='#17a2b8'">
                    我知道了
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭企业微信设置指导
function closeWeChatSettingsModal() {
    const modal = document.getElementById('wechatSettingsModal');
    if (modal) modal.remove();
}

// 开始企业微信导出（带选项）
function startWeChatWorkExportWithOptions() {
    if (window.wechatExportOptionsInfo) {
        const { exportUrl, actionType, customFileName } = window.wechatExportOptionsInfo;
        
        // 获取用户输入的文件名
        const fileNameInput = document.getElementById('wechatFileName');
        const finalFileName = fileNameInput ? fileNameInput.value.trim() : customFileName;
        
        // 确保文件名有.xlsx扩展名
        const fileNameWithExt = finalFileName.endsWith('.xlsx') ? finalFileName : finalFileName + '.xlsx';
        
        console.log('开始企业微信导出，文件名:', fileNameWithExt);
        
        // 关闭选项对话框
        closeWeChatExportOptionsModal();
        
        // 执行实际导出
        performWeChatWorkActualExportWithFileName(exportUrl, fileNameWithExt);
    }
}

// 执行企业微信实际导出（带文件名）
function performWeChatWorkActualExportWithFileName(exportUrl, fileName) {
    console.log('执行企业微信实际导出:', { exportUrl, fileName });
    
    try {
        // 方法1：尝试使用fetch下载
        fetch(exportUrl, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin'
        })
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
                link.download = fileName;
                link.style.display = 'none';
                
                // 在企业微信环境下，先显示保存路径选择提示
                showWeChatSavePathDialog(url, fileName, blob.size);
                
                // 清理URL（延迟清理，确保下载完成）
        setTimeout(() => {
                    window.URL.revokeObjectURL(url);
                }, 30000);
                
                // 显示成功提示
                showWeChatWorkExportSuccessWithPath(fileName);
                
            })
            .catch(error => {
                console.error('fetch下载失败:', error);
                // 回退到传统方法
                performSimpleExportForWeChatWithFileName(exportUrl, fileName);
            });
            
    } catch (error) {
        console.error('企业微信导出失败:', error);
        // 回退到简单导出
        performSimpleExportForWeChatWithFileName(exportUrl, fileName);
    }
}

// 企业微信简单导出（带文件名）
function performSimpleExportForWeChatWithFileName(exportUrl, fileName) {
    console.log('使用企业微信简单导出方式，文件名:', fileName);
    
    try {
        // 企业微信特殊处理：先获取文件内容，确保文件完整性
        fetch(exportUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/octet-stream',
                'Cache-Control': 'no-cache',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin'  // 包含session cookies
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.blob();
        })
        .then(blob => {
            console.log('文件获取成功，大小:', blob.size, '字节');
            
            // 创建下载链接
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.style.display = 'none';
            link.download = fileName;
            
            // 企业微信特殊处理：添加时间戳避免缓存问题
            link.download = fileName.replace('.xlsx', `_${Date.now()}.xlsx`);
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // 清理URL对象
            window.URL.revokeObjectURL(url);
            
            console.log('企业微信简单导出完成');
            
            // 显示成功提示
            showWeChatWorkExportSuccessWithPath(fileName);
        })
        .catch(error => {
            console.error('fetch下载失败，回退到传统方法:', error);
            
            // 回退到传统方法
            const link = document.createElement('a');
            link.href = exportUrl;
            link.style.display = 'none';
            link.download = fileName;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            console.log('企业微信传统导出完成');
            showWeChatWorkExportSuccessWithPath(fileName);
        });
        
    } catch (error) {
        console.error('企业微信简单导出失败:', error);
        alert('导出失败，请重试');
    }
}

// 显示企业微信导出成功提示（带路径）
function showWeChatWorkExportSuccessWithPath(fileName) {
    // 检测操作系统和下载路径
    const osInfo = detectOSAndDownloadPath();
    const defaultPath = osInfo.downloadPath;
    
    const modalHTML = `
        <div id="wechatSuccessWithPathModal" style="
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
                width: 600px;
                max-height: 90vh;
                overflow-y: auto;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
            ">
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
                ">导出成功！</h3>
                
                <!-- 文件信息 -->
                <div style="
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #2e7d32;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>📄 文件信息：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>文件名：${fileName}</li>
                        <li>导出时间：${new Date().toLocaleString('zh-CN')}</li>
                        <li>文件格式：Excel (.xlsx)</li>
                        <li>下载状态：文件已开始下载</li>
                    </ul>
                </div>
                
                <!-- 保存位置 -->
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>💾 保存位置：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>操作系统：${osInfo.osName}</li>
                        <li>默认路径：${defaultPath}</li>
                        <li>环境说明：企业微信PC端下载目录</li>
                    </ul>
                    
                    <!-- 完整文件路径 -->
                    <div style="
                        margin-top: 10px;
                        padding: 10px;
                        background: #e8f5e8;
                        border: 1px solid #4caf50;
                        border-radius: 4px;
                    ">
                        <strong>📂 完整文件路径：</strong><br>
                        <span style="color: #2e7d32; font-weight: bold;">${defaultPath}${osInfo.osName === 'Windows' ? '\\\\' : '/'}${fileName}</span>
                    </div>
                </div>
                
                <!-- 操作按钮 -->
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                    flex-wrap: wrap;
                ">
                    <button onclick="closeWeChatSuccessWithPathModal()" style="
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
                        ✕ 关闭
                    </button>
                    
                    <button onclick="copyFilePath('${defaultPath}${osInfo.osName === 'Windows' ? '\\\\' : '/'}${fileName}')" style="
                        padding: 12px 16px;
                        background: #28a745;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.2s;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                    " onmouseover="this.style.background='#218838'" onmouseout="this.style.background='#28a745'">
                        📋 复制路径
                    </button>
                </div>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：文件已开始下载，请检查您的下载文件夹或企业微信下载记录。如需选择其他保存位置，请在下次导出时使用"另存为"功能。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭企业微信成功提示（带路径）
function closeWeChatSuccessWithPathModal() {
    const modal = document.getElementById('wechatSuccessWithPathModal');
    if (modal) modal.remove();
}

// 显示企业微信保存路径选择对话框
function showWeChatSavePathDialog(fileUrl, fileName, fileSize) {
    const modalHTML = `
        <div id="wechatSavePathModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10002;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 90%;
                width: 600px;
                max-height: 90vh;
                overflow-y: auto;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid #e0e0e0;
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #FF9800, #F57C00);
                    border-radius: 50%;
                    margin: 0 auto 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                       color: white;
                    font-size: 24px;
                ">
                    💾
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">选择保存位置</h3>
                
                <!-- 文件信息 -->
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>📄 准备下载：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>文件名：${fileName}</li>
                        <li>文件大小：${(fileSize / 1024).toFixed(2)} KB</li>
                        <li>文件类型：Excel (.xlsx)</li>
                        <li>下载时间：${new Date().toLocaleString('zh-CN')}</li>
                    </ul>
                </div>
                
                <!-- 保存位置选择说明 -->
                <div style="
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #856404;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>💡 如何选择保存位置：</strong></p>
                    <ol style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li><strong>点击"下载并选择位置"按钮</strong></li>
                        <li><strong>在弹出的"另存为"对话框中：</strong>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>浏览并选择您想要的保存文件夹</li>
                                <li>可以修改文件名（如果需要）</li>
                                <li>点击"保存"完成下载</li>
                            </ul>
                        </li>
                        <li><strong>如果没有弹出对话框</strong>，文件将保存到默认下载位置</li>
                    </ol>
                    
                    <p style="margin: 0; font-weight: bold;">🎯 这样您就可以完全控制文件的保存位置了！</p>
                </div>
                
                <!-- 操作按钮 -->
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                    flex-wrap: wrap;
                ">
                    <button onclick="closeWeChatSavePathModal()" style="
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
                        取消下载
                    </button>
                    
                    <button onclick="triggerWeChatSaveAsDownload('${fileUrl}', '${fileName}')" style="
                        padding: 12px 24px;
                        background: #FF9800;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 600;
                        transition: background-color 0.2s;
                    " onmouseover="this.style.background='#F57C00'" onmouseout="this.style.background='#FF9800'">
                        💾 下载并选择位置
                    </button>
                </div>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：点击"下载并选择位置"后，请在浏览器的"另存为"对话框中选择您想要的保存位置。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭企业微信保存路径对话框
function closeWeChatSavePathModal() {
    const modal = document.getElementById('wechatSavePathModal');
    if (modal) modal.remove();
}

// 触发企业微信另存为下载
function triggerWeChatSaveAsDownload(fileUrl, fileName) {
    console.log('触发企业微信另存为下载:', { fileUrl, fileName });
    
    try {
        // 创建下载链接
        const link = document.createElement('a');
        link.href = fileUrl;
        link.download = fileName;
        link.style.display = 'none';
        
        // 添加到页面
        document.body.appendChild(link);
        
        // 模拟用户点击，这应该会触发"另存为"对话框
        link.click();
        
        // 清理
        document.body.removeChild(link);
        
        // 关闭对话框
        closeWeChatSavePathModal();
        
        // 延迟显示成功提示
        setTimeout(() => {
            showWeChatSaveSuccessMessage(fileName);
        }, 1000);
        
        console.log('企业微信另存为下载已触发');
        
    } catch (error) {
        console.error('触发企业微信另存为下载失败:', error);
        
        // 如果失败，尝试直接打开文件URL
        try {
            window.open(fileUrl, '_blank');
            closeWeChatSavePathModal();
            showWeChatSaveSuccessMessage(fileName);
        } catch (openError) {
            console.error('打开文件URL也失败:', openError);
            alert('下载失败，请重试或联系技术支持');
        }
    }
}

// 显示企业微信保存成功消息
function showWeChatSaveSuccessMessage(fileName) {
    const modalHTML = `
        <div id="wechatSaveSuccessModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10003;
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
                ">下载已开始！</h3>
                
                <div style="
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #2e7d32;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>📄 下载信息：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>文件名：${fileName}</li>
                        <li>下载时间：${new Date().toLocaleString('zh-CN')}</li>
                        <li>保存位置：您在"另存为"对话框中选择的位置</li>
                    </ul>
                    
                    <p style="margin: 0;"><strong>💾 说明：</strong>如果弹出了"另存为"对话框，文件将保存到您选择的位置；如果没有弹出，文件已保存到默认下载位置。</p>
                </div>
                
                <button onclick="closeWeChatSaveSuccessModal()" style="
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
                    我知道了
                </button>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：如果需要再次下载或更改保存位置，请重新点击导出按钮。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭企业微信保存成功提示
function closeWeChatSaveSuccessModal() {
    const modal = document.getElementById('wechatSaveSuccessModal');
    if (modal) modal.remove();
}

// 增强版导出保存对话框 - 让用户选择保存路径
function enhancedExportWithSaveDialog(blob, fileName) {
    console.log('enhancedExportWithSaveDialog被调用:', { fileName, blobSize: blob.size });
    
    try {
        // 检测环境
        const isWeChat = isWeChatWorkPC();
        const isMobileDevice = isMobile();
        
        console.log('环境检测结果:', {
            isWeChat: isWeChat,
            isMobileDevice: isMobileDevice,
            userAgent: navigator.userAgent
        });
        
        // 如果是企业微信PC端，显示保存路径选择对话框
        if (isWeChat) {
            console.log('企业微信PC端，显示保存路径选择对话框');
            showWeChatSavePathDialog('', fileName, blob.size);
            
            // 存储blob数据供后续下载使用
            window.pendingDownloadBlob = blob;
            window.pendingDownloadFileName = fileName;
            
        } else if (isMobileDevice) {
            // 移动端使用简单下载
            console.log('移动端，使用简单下载');
            performMobileDownload(blob, fileName);
            
        } else {
            // PC端使用增强版保存对话框
            console.log('PC端，使用增强版保存对话框');
            showPCSavePathDialog(blob, fileName);
        }
        
    } catch (error) {
        console.error('enhancedExportWithSaveDialog执行出错:', error);
        
        // 出错时回退到简单下载
        console.log('回退到简单下载方式');
        performSimpleDownload(blob, fileName);
    }
}

// PC端保存路径选择对话框
function showPCSavePathDialog(blob, fileName) {
    const modalHTML = `
        <div id="pcSavePathModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10004;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 90%;
                width: 600px;
                max-height: 90vh;
                overflow-y: auto;
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
                    💾
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">选择保存位置</h3>
                
                <!-- 文件信息 -->
                <div style="
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #1976d2;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>📄 准备下载：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>文件名：${fileName}</li>
                        <li>文件大小：${(blob.size / 1024).toFixed(2)} KB</li>
                        <li>文件类型：Excel (.xlsx)</li>
                        <li>下载时间：${new Date().toLocaleString('zh-CN')}</li>
                    </ul>
                </div>
                
                <!-- 保存位置选择说明 -->
                <div style="
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #856404;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>💡 如何选择保存位置：</strong></p>
                    <ol style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li><strong>点击"下载并选择位置"按钮</strong></li>
                        <li><strong>在弹出的"另存为"对话框中：</strong>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>浏览并选择您想要的保存文件夹</li>
                                <li>可以修改文件名（如果需要）</li>
                                <li>点击"保存"完成下载</li>
                            </ul>
                        </li>
                        <li><strong>如果没有弹出对话框</strong>，文件将保存到默认下载位置</li>
                    </ol>
                    
                    <p style="margin: 0; font-weight: bold;">🎯 这样您就可以完全控制文件的保存位置了！</p>
                </div>
                
                <!-- 操作按钮 -->
                <div style="
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 25px;
                    flex-wrap: wrap;
                ">
                    <button onclick="closePCSavePathModal()" style="
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
                        取消下载
                    </button>
                    
                    <button onclick="triggerPCSaveAsDownload()" style="
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
                        💾 下载并选择位置
                    </button>
                </div>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：点击"下载并选择位置"后，请在浏览器的"另存为"对话框中选择您想要的保存位置。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 存储blob数据供后续下载使用
    window.pendingDownloadBlob = blob;
    window.pendingDownloadFileName = fileName;
}

// 关闭PC端保存路径对话框
function closePCSavePathModal() {
    const modal = document.getElementById('pcSavePathModal');
    if (modal) modal.remove();
    
    // 清理存储的数据
    delete window.pendingDownloadBlob;
    delete window.pendingDownloadFileName;
}

// 触发PC端另存为下载
function triggerPCSaveAsDownload() {
    try {
        const blob = window.pendingDownloadBlob;
        const fileName = window.pendingDownloadFileName;
        
        if (!blob || !fileName) {
            console.error('下载数据不可用');
            return;
        }
        
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        link.style.display = 'none';
        
        // 添加到页面并点击
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 清理URL
        window.URL.revokeObjectURL(url);
        
        // 关闭对话框
        closePCSavePathModal();
        
        // 显示成功提示
        showPCDownloadSuccess(fileName);
        
        // 清理存储的数据
        delete window.pendingDownloadBlob;
        delete window.pendingDownloadFileName;
        
    } catch (error) {
        console.error('PC端下载失败:', error);
        alert('下载失败，请重试');
    }
}

// 显示PC端下载成功提示
function showPCDownloadSuccess(fileName) {
    const modalHTML = `
        <div id="pcDownloadSuccessModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10005;
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
                ">下载已开始！</h3>
                
                <div style="
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #2e7d32;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>📄 下载信息：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>文件名：${fileName}</li>
                        <li>下载时间：${new Date().toLocaleString('zh-CN')}</li>
                        <li>保存位置：您在"另存为"对话框中选择的位置</li>
                    </ul>
                    
                    <p style="margin: 0;"><strong>💾 说明：</strong>如果弹出了"另存为"对话框，文件将保存到您选择的位置；如果没有弹出，文件已保存到默认下载位置。</p>
                </div>
                
                <button onclick="closePCDownloadSuccessModal()" style="
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
                    我知道了
                </button>
                
                <p style="
                    margin: 20px 0 0 0;
                    font-size: 12px;
                    color: #999;
                    line-height: 1.4;
                ">
                    💡 提示：如果需要再次下载或更改保存位置，请重新点击导出按钮。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭PC端下载成功提示
function closePCDownloadSuccessModal() {
    const modal = document.getElementById('pcDownloadSuccessModal');
    if (modal) modal.remove();
}

// 移动端简单下载
function performMobileDownload(blob, fileName) {
    try {
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        link.style.display = 'none';
        
        // 添加到页面并点击
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 清理URL
        window.URL.revokeObjectURL(url);
        
        // 显示成功提示
        showQuickMessage('文件下载已开始，请查看下载文件夹', 'success');
        
    } catch (error) {
        console.error('移动端下载失败:', error);
        showQuickMessage('下载失败，请重试', 'error');
    }
}

// 简单下载（回退方式）
function performSimpleDownload(blob, fileName) {
    try {
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        link.style.display = 'none';
        
        // 添加到页面并点击
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 清理URL
        window.URL.revokeObjectURL(url);
        
        // 显示成功提示
        showQuickMessage('文件下载已开始', 'success');
        
    } catch (error) {
        console.error('简单下载失败:', error);
        showQuickMessage('下载失败，请重试', 'error');
    }
}

