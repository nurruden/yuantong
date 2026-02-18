/**
 * Material Icons 字体加载检测和备用方案
 * 当字体加载失败时，自动使用Unicode字符作为备用图标
 * 注意：此脚本已被禁用，以避免双图标问题
 */

(function() {
    'use strict';
    
    console.log('Material Icons 备用方案已禁用，避免双图标问题');
    
    // 禁用所有备用图标功能
    return;
    
    // 以下代码已被禁用
    /*
    // 图标映射表
    const iconMap = {
        'menu': '☰',
        'person': '👤',
        'logout': '↗',
        'save': '💾',
        'edit': '✏️',
        'delete': '🗑️',
        'add': '➕',
        'search': '🔍',
        'close': '✕',
        'chevron_right': '▶',
        'star': '★',
        'home': '🏠',
        'settings': '⚙️',
        'notifications': '🔔',
        'help': '❓',
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
        'refresh': '🔄',
        'download': '⬇️',
        'upload': '⬆️',
        'print': '🖨️',
        'email': '📧',
        'phone': '📞',
        'location': '📍',
        'calendar': '📅',
        'time': '⏰',
        'folder': '📁',
        'file': '📄',
        'image': '🖼️',
        'video': '🎥',
        'audio': '🎵',
        'link': '🔗',
        'share': '📤',
        'favorite': '❤️',
        'like': '👍',
        'dislike': '👎',
        'comment': '💬',
        'reply': '↩️',
        'forward': '↪️',
        'back': '⬅️',
        'next': '➡️',
        'first': '⏮️',
        'last': '⏭️',
        'play': '▶️',
        'pause': '⏸️',
        'stop': '⏹️',
        'volume': '🔊',
        'mute': '🔇',
        'fullscreen': '⛶',
        'minimize': '🗕',
        'maximize': '🗗',
        'restore': '🗖',
        'lock': '🔒',
        'unlock': '🔓',
        'visibility': '👁️',
        'visibility_off': '👁️‍🗨️',
        'key': '🔑',
        'security': '🛡️',
        'verified': '✅',
        'unverified': '❌',
        'check': '✓',
        'clear': '✗',
        'done': '✓',
        'done_all': '✓✓',
        'remove': '−',
        'add_circle': '➕',
        'remove_circle': '➖',
        'radio_button_checked': '●',
        'radio_button_unchecked': '○',
        'check_box': '☑️',
        'check_box_outline_blank': '☐',
        'indeterminate_check_box': '☒'
    };
    
    // 检测字体是否加载成功
    function checkFontLoaded() {
        return new Promise((resolve) => {
            if (document.fonts && document.fonts.check) {
                // 现代浏览器使用 Font Loading API
                if (document.fonts.check('1em Material Icons')) {
                    resolve(true);
                } else {
                    // 等待字体加载
                    document.fonts.ready.then(() => {
                        resolve(document.fonts.check('1em Material Icons'));
                    });
                }
            } else {
                // 备用检测方法
                const testElement = document.createElement('span');
                testElement.className = 'material-icons';
                testElement.style.position = 'absolute';
                testElement.style.left = '-9999px';
                testElement.style.visibility = 'hidden';
                testElement.textContent = 'menu';
                document.body.appendChild(testElement);
                
                setTimeout(() => {
                    const computedStyle = window.getComputedStyle(testElement);
                    const fontFamily = computedStyle.fontFamily;
                    document.body.removeChild(testElement);
                    resolve(fontFamily.includes('Material Icons'));
                }, 100);
            }
        });
    }
    
    // 为所有Material Icons元素添加备用图标
    function addFallbackIcons() {
        const materialIcons = document.querySelectorAll('.material-icons');
        
        materialIcons.forEach(icon => {
            // 检查是否已经处理过这个图标
            if (icon.hasAttribute('data-processed')) {
                return;
            }
            
            const iconName = icon.textContent.trim();
            const fallbackChar = iconMap[iconName];
            
            if (fallbackChar) {
                icon.setAttribute('data-icon', iconName);
                icon.setAttribute('title', iconName);
                
                // 如果字体加载失败，显示备用图标
                if (!icon.style.fontFamily.includes('Material Icons')) {
                    icon.style.fontFamily = 'Arial, sans-serif';
                    icon.textContent = fallbackChar;
                }
                
                // 标记为已处理
                icon.setAttribute('data-processed', 'true');
            }
        });
    }
    
    // 监听DOM变化，为新添加的图标元素添加备用方案
    function observeDOMChanges() {
        if (window.MutationObserver) {
            let timeoutId = null;
            
            const observer = new MutationObserver((mutations) => {
                // 使用防抖，避免频繁处理
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }
                
                timeoutId = setTimeout(() => {
                    let hasNewIcons = false;
                    
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach((node) => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    if (node.classList && node.classList.contains('material-icons')) {
                                        hasNewIcons = true;
                                    } else if (node.querySelectorAll) {
                                        const icons = node.querySelectorAll('.material-icons');
                                        if (icons.length > 0) {
                                            hasNewIcons = true;
                                        }
                                    }
                                }
                            });
                        }
                    });
                    
                    if (hasNewIcons) {
                        addFallbackIcons();
                    }
                }, 100); // 100ms防抖
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    }
    
    // 初始化
    function init() {
        // 检查字体加载状态
        checkFontLoaded().then((fontLoaded) => {
            if (!fontLoaded) {
                console.log('Material Icons 字体加载失败，使用备用图标');
                // 为现有图标添加备用方案
                addFallbackIcons();
            } else {
                console.log('Material Icons 字体加载成功');
                // 即使字体加载成功，也添加data-icon属性以便备用
                const materialIcons = document.querySelectorAll('.material-icons');
                materialIcons.forEach(icon => {
                    const iconName = icon.textContent.trim();
                    if (iconMap[iconName]) {
                        icon.setAttribute('data-icon', iconName);
                        icon.setAttribute('title', iconName);
                    }
                });
            }
        });
        
        // 监听DOM变化
        observeDOMChanges();
    }
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 导出函数供外部使用
    window.MaterialIconsFallback = {
        checkFontLoaded,
        addFallbackIcons,
        iconMap
    };
    
})(); 