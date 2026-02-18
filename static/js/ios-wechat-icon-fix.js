/**
 * iOS企业微信专用图标修复脚本
 * 专门解决iPhone企业微信应用中的双图标问题
 */

(function() {
    'use strict';
    
    console.log('iOS企业微信图标修复脚本已加载');
    
    // 检测是否为iOS企业微信
    function isIOSWeChat() {
        const userAgent = navigator.userAgent.toLowerCase();
        const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
        const isWeChat = userAgent.includes('micromessenger') || userAgent.includes('wxwork');
        const isHighDPI = window.devicePixelRatio >= 2;
        
        return isIOS && isWeChat && isHighDPI;
    }
    
    // 检测是否为iPhone
    function isIPhone() {
        return /iphone/i.test(navigator.userAgent);
    }
    
    // 强制修复iOS企业微信图标
    function forceFixIOSWeChatIcons() {
        console.log('强制修复iOS企业微信图标');
        
        // 查找所有Material Icons元素
        const materialIcons = document.querySelectorAll('.material-icons');
        
        materialIcons.forEach((icon, index) => {
            console.log(`处理iOS企业微信图标 ${index + 1}:`, icon.textContent.trim());
            
            // 移除所有可能导致重复的属性
            icon.removeAttribute('data-icon');
            icon.removeAttribute('data-processed');
            icon.removeAttribute('data-icon-fixed');
            
            // 确保只保留一个图标文本
            const iconText = icon.textContent.trim();
            if (iconText) {
                // 清理文本内容，移除可能的重复字符
                const cleanText = iconText.replace(/(.)\1+/g, '$1');
                icon.textContent = cleanText;
            }
            
            // 强制设置iOS企业微信专用样式
            icon.style.cssText = `
                font-family: 'Material Icons', sans-serif !important;
                font-size: 24px !important;
                display: inline-block !important;
                vertical-align: middle !important;
                margin: 0 !important;
                padding: 0 !important;
                background: none !important;
                border: none !important;
                position: static !important;
                transform: none !important;
                -webkit-transform: none !important;
                color: #4fc3f7 !important;
                text-align: center !important;
                line-height: 1 !important;
                -webkit-line-height: 1 !important;
                -webkit-text-size-adjust: none !important;
                -moz-text-size-adjust: none !important;
                -ms-text-size-adjust: none !important;
                text-size-adjust: none !important;
                -webkit-appearance: none !important;
                -moz-appearance: none !important;
                appearance: none !important;
                outline: none !important;
                -webkit-outline: none !important;
            `;
            
            // 标记为已修复
            icon.setAttribute('data-ios-wechat-fixed', 'true');
        });
        
        // 特殊处理菜单按钮图标
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        if (mobileMenuBtn) {
            const menuIcon = mobileMenuBtn.querySelector('.material-icons');
            if (menuIcon) {
                menuIcon.textContent = 'menu';
                menuIcon.style.fontSize = '20px';
                menuIcon.style.color = '#333';
                menuIcon.setAttribute('data-ios-wechat-fixed', 'true');
                console.log('修复iOS企业微信菜单按钮图标');
            }
        }
        
        // 特殊处理用户信息图标
        const userInfo = document.querySelector('.user-info');
        if (userInfo) {
            const personIcon = userInfo.querySelector('.material-icons');
            if (personIcon) {
                personIcon.textContent = 'person';
                personIcon.style.fontSize = '18px';
                personIcon.style.color = '#666';
                personIcon.setAttribute('data-ios-wechat-fixed', 'true');
                console.log('修复iOS企业微信用户信息图标');
            }
        }
        
        // 特殊处理退出按钮图标
        const logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn) {
            const logoutIcon = logoutBtn.querySelector('.material-icons');
            if (logoutIcon) {
                logoutIcon.textContent = 'logout';
                logoutIcon.style.fontSize = '18px';
                logoutIcon.style.color = '#666';
                logoutIcon.setAttribute('data-ios-wechat-fixed', 'true');
                console.log('修复iOS企业微信退出按钮图标');
            }
        }
        
        console.log(`iOS企业微信图标修复完成，共处理 ${materialIcons.length} 个图标`);
    }
    
    // 移除所有伪元素
    function removePseudoElements() {
        console.log('移除iOS企业微信伪元素');
        
        // 创建样式来隐藏所有伪元素
        const style = document.createElement('style');
        style.textContent = `
            .material-icons::before,
            .material-icons::after {
                display: none !important;
                content: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                position: absolute !important;
                left: -9999px !important;
                top: -9999px !important;
                width: 0 !important;
                height: 0 !important;
                overflow: hidden !important;
                font-size: 0 !important;
                line-height: 0 !important;
            }
        `;
        
        // 如果样式已存在，先移除
        const existingStyle = document.querySelector('#ios-wechat-icon-fix-style');
        if (existingStyle) {
            existingStyle.remove();
        }
        
        style.id = 'ios-wechat-icon-fix-style';
        document.head.appendChild(style);
    }
    
    // 监听DOM变化，处理动态添加的图标
    function observeDOMChanges() {
        if (window.MutationObserver) {
            const observer = new MutationObserver((mutations) => {
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
                    console.log('检测到新的图标元素，重新修复iOS企业微信图标');
                    setTimeout(() => {
                        forceFixIOSWeChatIcons();
                    }, 100);
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            console.log('iOS企业微信DOM变化监听器已启动');
        }
    }
    
    // 强制重新加载Material Icons字体
    function reloadMaterialIconsFont() {
        console.log('重新加载iOS企业微信Material Icons字体');
        
        // 移除现有的字体链接
        const existingLinks = document.querySelectorAll('link[href*="material-icons"]');
        existingLinks.forEach(link => {
            if (link.href.includes('material-icons')) {
                link.remove();
            }
        });
        
        // 重新添加字体链接
        const newLink = document.createElement('link');
        newLink.href = 'https://fonts.googleapis.com/icon?family=Material+Icons';
        newLink.rel = 'stylesheet';
        newLink.type = 'text/css';
        document.head.appendChild(newLink);
        
        console.log('iOS企业微信Material Icons字体已重新加载');
    }
    
    // 初始化修复
    function init() {
        if (!isIOSWeChat()) {
            console.log('非iOS企业微信，跳过专用修复');
            return;
        }
        
        console.log('检测到iOS企业微信，开始专用图标修复');
        
        // 移除伪元素
        removePseudoElements();
        
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    forceFixIOSWeChatIcons();
                    observeDOMChanges();
                }, 100);
            });
        } else {
            setTimeout(() => {
                forceFixIOSWeChatIcons();
                observeDOMChanges();
            }, 100);
        }
        
        // 延迟修复，确保所有脚本都加载完成
        setTimeout(() => {
            forceFixIOSWeChatIcons();
        }, 500);
        
        // 再次延迟修复，确保字体加载完成
        setTimeout(() => {
            forceFixIOSWeChatIcons();
        }, 1000);
        
        // 多次修复，确保iOS企业微信的特殊处理
        setTimeout(() => {
            forceFixIOSWeChatIcons();
        }, 2000);
        
        setTimeout(() => {
            forceFixIOSWeChatIcons();
        }, 3000);
    }
    
    // 页面加载完成后初始化
    init();
    
    // 监听页面可见性变化，重新修复
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && isIOSWeChat()) {
            console.log('页面重新可见，重新修复iOS企业微信图标');
            setTimeout(() => {
                forceFixIOSWeChatIcons();
            }, 100);
        }
    });
    
    // 监听窗口大小变化
    window.addEventListener('resize', () => {
        if (isIOSWeChat()) {
            console.log('窗口大小变化，重新修复iOS企业微信图标');
            setTimeout(() => {
                forceFixIOSWeChatIcons();
            }, 100);
        }
    });
    
    // 监听页面焦点变化
    window.addEventListener('focus', () => {
        if (isIOSWeChat()) {
            console.log('页面获得焦点，重新修复iOS企业微信图标');
            setTimeout(() => {
                forceFixIOSWeChatIcons();
            }, 100);
        }
    });
    
    // 导出函数供外部使用
    window.IOSWeChatIconFix = {
        forceFixIOSWeChatIcons,
        removePseudoElements,
        reloadMaterialIconsFont,
        isIOSWeChat,
        isIPhone
    };
    
})();
