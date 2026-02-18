// 通用工具函数

/**
 * 格式化日期时间
 * @param {string} dateStr - 日期时间字符串
 * @returns {string} - 格式化后的日期时间字符串
 */
function formatDateTime(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success/error/info)
 */
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // 3秒后自动消失
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

/**
 * 确认对话框
 * @param {string} message - 确认消息
 * @returns {Promise} - 用户确认结果
 */
function confirmDialog(message) {
    return new Promise((resolve) => {
        if (window.confirm(message)) {
            resolve(true);
        } else {
            resolve(false);
        }
    });
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} - 防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 获取CSRF Token
 * @returns {string} - CSRF Token
 */
function getCsrfToken() {
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
    return cookieValue;
}

/**
 * 发送API请求
 * @param {string} url - 请求URL
 * @param {Object} options - 请求选项
 * @returns {Promise} - 请求结果
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        credentials: 'same-origin'
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    if (finalOptions.body && typeof finalOptions.body === 'object') {
        finalOptions.body = JSON.stringify(finalOptions.body);
    }
    
    try {
        const response = await fetch(url, finalOptions);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// 侧边栏菜单展开/收起函数
function toggleSubmenu(header) {
    const submenu = header.nextElementSibling;
    const arrow = header.querySelector('.arrow');
    if (submenu.style.maxHeight) {
        submenu.style.maxHeight = null;
        arrow.style.transform = 'rotate(0deg)';
        header.setAttribute('aria-expanded', 'false');
    } else {
        submenu.style.maxHeight = submenu.scrollHeight + 'px';
        arrow.style.transform = 'rotate(90deg)';
        header.setAttribute('aria-expanded', 'true');
    }
}
function toggleMobileMenu() {
    const sideMenu = document.getElementById('sideMenu');
    const menuToggle = document.getElementById('menuToggle');
    if (sideMenu.classList.contains('expanded')) {
        sideMenu.classList.remove('expanded');
        menuToggle.textContent = '菜单';
    } else {
        sideMenu.classList.add('expanded');
        menuToggle.textContent = '关闭';
    }
}

/**
 * 初始化图标替换系统
 * 将Material Icons文本替换为对应的Unicode图标
 * 注意：此功能已被禁用，以避免双图标问题
 */
function initIconReplacement() {
    console.log('图标替换系统已禁用，避免双图标问题');
    return;
    
    // 以下代码已被禁用
    /*
    const iconMap = {
        'menu': '☰',
        'person': '👤',
        'logout': '⤴',
        'star': '★',
        'close': '✕',
        'chevron_right': '▶',
        'add': '➕',
        'edit': '✏',
        'delete': '🗑',
        'search': '🔍',
        'home': '🏠',
        'settings': '⚙',
        'arrow_back': '←',
        'arrow_forward': '→',
        'check': '✓',
        'clear': '✗',
        'history': '📋',
        'hourglass_empty': '⏳'
    };
    
    // 处理所有Material Icons元素
    function processIcons() {
        const icons = document.querySelectorAll('.material-icons');
        icons.forEach(icon => {
            const iconText = icon.textContent.trim();
            const dataIcon = icon.getAttribute('data-icon');
            
            // 如果已经有data-icon属性，跳过
            if (dataIcon) return;
            
            // 根据文本内容设置data-icon属性
            if (iconMap[iconText]) {
                icon.setAttribute('data-icon', iconText);
                icon.style.fontSize = '0';
            }
        });
    }
    
    // 初始化时处理所有图标
    processIcons();
    */
    
    // 监听DOM变化，处理动态添加的图标
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // 处理新添加的Material Icons
                        if (node.classList && node.classList.contains('material-icons')) {
                            const iconText = node.textContent.trim();
                            if (iconMap[iconText]) {
                                node.setAttribute('data-icon', iconText);
                                node.style.fontSize = '0';
                            }
                        }
                        
                        // 处理子元素中的Material Icons
                        const childIcons = node.querySelectorAll && node.querySelectorAll('.material-icons');
                        if (childIcons) {
                            childIcons.forEach(icon => {
                                const iconText = icon.textContent.trim();
                                if (iconMap[iconText] && !icon.getAttribute('data-icon')) {
                                    icon.setAttribute('data-icon', iconText);
                                    icon.style.fontSize = '0';
                                }
                            });
                        }
                    }
                });
            }
        });
    });
    
    // 开始监听DOM变化
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// 页面加载完成后初始化图标替换
document.addEventListener('DOMContentLoaded', function() {
    initIconReplacement();
});

// 为了确保兼容性，也在window.load事件中初始化
window.addEventListener('load', function() {
    // 延迟一点再处理，确保所有动态内容都已加载
    setTimeout(initIconReplacement, 100);
});
