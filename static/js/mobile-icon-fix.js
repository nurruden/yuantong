/**
 * 移动端图标重复显示修复脚本
 * 解决部分手机顶部菜单栏双图标问题
 */

(function() {
    'use strict';
    
    console.log('移动端图标修复脚本已加载');
    
    // 检测是否为移动设备
    function isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth <= 768;
    }
    
    // 修复图标重复显示问题
    function fixDuplicateIcons() {
        console.log('开始修复图标重复显示问题');
        
        // 查找所有Material Icons元素
        const materialIcons = document.querySelectorAll('.material-icons');
        
        materialIcons.forEach((icon, index) => {
            // 检查是否已经处理过
            if (icon.hasAttribute('data-icon-fixed')) {
                return;
            }
            
            console.log(`处理图标 ${index + 1}:`, icon.textContent.trim());
            
            // 移除所有可能导致重复的属性
            icon.removeAttribute('data-icon');
            icon.removeAttribute('data-processed');
            
            // 确保只保留一个图标文本
            const iconText = icon.textContent.trim();
            if (iconText) {
                // 清理文本内容，移除可能的重复字符
                const cleanText = iconText.replace(/(.)\1+/g, '$1');
                icon.textContent = cleanText;
            }
            
            // 强制设置正确的样式
            icon.style.fontFamily = 'Material Icons, sans-serif';
            icon.style.fontSize = '24px';
            icon.style.display = 'inline-block';
            icon.style.verticalAlign = 'middle';
            icon.style.margin = '0';
            icon.style.padding = '0';
            icon.style.background = 'none';
            icon.style.border = 'none';
            icon.style.position = 'static';
            icon.style.transform = 'none';
            
            // 移除所有伪元素
            const beforeElement = icon.querySelector('::before');
            const afterElement = icon.querySelector('::after');
            if (beforeElement) beforeElement.remove();
            if (afterElement) afterElement.remove();
            
            // 标记为已修复
            icon.setAttribute('data-icon-fixed', 'true');
        });
        
        console.log(`修复完成，共处理 ${materialIcons.length} 个图标`);
    }
    
    // 修复特定位置的图标
    function fixSpecificIcons() {
        console.log('修复特定位置的图标');
        
        // 修复移动端菜单按钮图标
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        if (mobileMenuBtn) {
            const menuIcon = mobileMenuBtn.querySelector('.material-icons');
            if (menuIcon) {
                menuIcon.textContent = 'menu';
                menuIcon.style.fontSize = '20px';
                menuIcon.style.color = '#333';
                menuIcon.setAttribute('data-icon-fixed', 'true');
                console.log('修复移动端菜单按钮图标');
            }
        }
        
        // 修复用户信息图标
        const userInfo = document.querySelector('.user-info');
        if (userInfo) {
            const personIcon = userInfo.querySelector('.material-icons');
            if (personIcon) {
                personIcon.textContent = 'person';
                personIcon.style.fontSize = '18px';
                personIcon.style.color = '#666';
                personIcon.setAttribute('data-icon-fixed', 'true');
                console.log('修复用户信息图标');
            }
        }
        
        // 修复退出按钮图标
        const logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn) {
            const logoutIcon = logoutBtn.querySelector('.material-icons');
            if (logoutIcon) {
                logoutIcon.textContent = 'logout';
                logoutIcon.style.fontSize = '18px';
                logoutIcon.style.color = '#666';
                logoutIcon.setAttribute('data-icon-fixed', 'true');
                console.log('修复退出按钮图标');
            }
        }
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
                    console.log('检测到新的图标元素，重新修复');
                    setTimeout(() => {
                        fixDuplicateIcons();
                        fixSpecificIcons();
                    }, 100);
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            console.log('DOM变化监听器已启动');
        }
    }
    
    // 强制重新加载Material Icons字体
    function reloadMaterialIconsFont() {
        console.log('重新加载Material Icons字体');
        
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
        
        console.log('Material Icons字体已重新加载');
    }
    
    // 初始化修复
    function init() {
        if (!isMobileDevice()) {
            console.log('非移动设备，跳过图标修复');
            return;
        }
        
        console.log('移动设备检测到，开始图标修复');
        
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    fixDuplicateIcons();
                    fixSpecificIcons();
                    observeDOMChanges();
                }, 100);
            });
        } else {
            setTimeout(() => {
                fixDuplicateIcons();
                fixSpecificIcons();
                observeDOMChanges();
            }, 100);
        }
        
        // 延迟修复，确保所有脚本都加载完成
        setTimeout(() => {
            fixDuplicateIcons();
            fixSpecificIcons();
        }, 500);
        
        // 再次延迟修复，确保字体加载完成
        setTimeout(() => {
            fixDuplicateIcons();
            fixSpecificIcons();
        }, 1000);
    }
    
    // 页面加载完成后初始化
    init();
    
    // 监听页面可见性变化，重新修复
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && isMobileDevice()) {
            console.log('页面重新可见，重新修复图标');
            setTimeout(() => {
                fixDuplicateIcons();
                fixSpecificIcons();
            }, 100);
        }
    });
    
    // 监听窗口大小变化
    window.addEventListener('resize', () => {
        if (isMobileDevice()) {
            console.log('窗口大小变化，重新修复图标');
            setTimeout(() => {
                fixDuplicateIcons();
                fixSpecificIcons();
            }, 100);
        }
    });
    
    // 导出函数供外部使用
    window.MobileIconFix = {
        fixDuplicateIcons,
        fixSpecificIcons,
        reloadMaterialIconsFont,
        isMobileDevice
    };
    
})();
