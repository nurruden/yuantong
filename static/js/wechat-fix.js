/**
 * 企业微信内置浏览器兼容性修复脚本
 * 解决企业微信内置浏览器中菜单点击无反应的问题
 */

(function() {
    'use strict';
    
    console.log('企业微信兼容性修复脚本已加载');
    
    // 检测是否为企业微信内置浏览器
    function isWeChatBrowser() {
        const userAgent = navigator.userAgent.toLowerCase();
        return userAgent.includes('micromessenger') || userAgent.includes('wxwork');
    }
    
    // 检测是否为移动设备
    function isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth <= 768;
    }
    
    // 企业微信专用菜单控制器
    class WeChatMenuController {
        constructor() {
            this.sideMenu = null;
            this.mobileMenuBtn = null;
            this.menuCloseBtn = null;
            this.mobileOverlay = null;
            this.isMenuOpen = false;
            this.isInitialized = false;
            
            this.init();
        }
        
        init() {
            console.log('初始化企业微信菜单控制器');
            
            // 等待DOM加载完成
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setupMenu());
            } else {
                this.setupMenu();
            }
        }
        
        setupMenu() {
            console.log('设置企业微信菜单');
            
            // 获取DOM元素
            this.sideMenu = document.getElementById('sideMenu');
            this.mobileMenuBtn = document.getElementById('mobileMenuBtn');
            this.menuCloseBtn = document.getElementById('menuCloseBtn');
            this.mobileOverlay = document.getElementById('mobileOverlay');
            
            console.log('DOM元素检查:', {
                sideMenu: !!this.sideMenu,
                mobileMenuBtn: !!this.mobileMenuBtn,
                menuCloseBtn: !!this.menuCloseBtn,
                mobileOverlay: !!this.mobileOverlay
            });
            
            if (!this.sideMenu || !this.mobileMenuBtn) {
                console.error('菜单元素不存在，无法初始化');
                return;
            }
            
            // 移除可能存在的旧事件监听器
            this.removeOldListeners();
            
            // 绑定新的事件监听器
            this.bindEvents();
            
            // 添加企业微信专用样式
            this.addWeChatStyles();
            
            this.isInitialized = true;
            console.log('企业微信菜单控制器初始化完成');
        }
        
        removeOldListeners() {
            console.log('移除旧的事件监听器');
            
            if (this.mobileMenuBtn) {
                // 克隆元素来移除所有事件监听器
                const newBtn = this.mobileMenuBtn.cloneNode(true);
                this.mobileMenuBtn.parentNode.replaceChild(newBtn, this.mobileMenuBtn);
                this.mobileMenuBtn = newBtn;
            }
            
            if (this.menuCloseBtn) {
                const newCloseBtn = this.menuCloseBtn.cloneNode(true);
                this.menuCloseBtn.parentNode.replaceChild(newCloseBtn, this.menuCloseBtn);
                this.menuCloseBtn = newCloseBtn;
            }
            
            if (this.mobileOverlay) {
                const newOverlay = this.mobileOverlay.cloneNode(true);
                this.mobileOverlay.parentNode.replaceChild(newOverlay, this.mobileOverlay);
                this.mobileOverlay = newOverlay;
            }
        }
        
        bindEvents() {
            console.log('绑定企业微信专用事件监听器');
            
            // 菜单按钮点击事件 - 使用多种方式确保兼容性
            if (this.mobileMenuBtn) {
                // 方式1：addEventListener
                this.mobileMenuBtn.addEventListener('click', (e) => {
                    console.log('菜单按钮被点击 (addEventListener)');
                    this.handleMenuClick(e);
                });
                
                // 方式2：onclick属性
                this.mobileMenuBtn.onclick = (e) => {
                    console.log('菜单按钮被点击 (onclick)');
                    this.handleMenuClick(e);
                };
                
                // 方式3：触摸事件
                this.mobileMenuBtn.addEventListener('touchstart', (e) => {
                    console.log('菜单按钮触摸开始');
                    e.preventDefault();
                }, { passive: false });
                
                this.mobileMenuBtn.addEventListener('touchend', (e) => {
                    console.log('菜单按钮触摸结束');
                    e.preventDefault();
                    this.handleMenuClick(e);
                }, { passive: false });
            }
            
            // 关闭按钮事件
            if (this.menuCloseBtn) {
                this.menuCloseBtn.addEventListener('click', (e) => {
                    console.log('关闭按钮被点击');
                    this.closeMenu();
                });
                
                this.menuCloseBtn.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                }, { passive: false });
                
                this.menuCloseBtn.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.closeMenu();
                }, { passive: false });
            }
            
            // 遮罩点击事件
            if (this.mobileOverlay) {
                this.mobileOverlay.addEventListener('click', (e) => {
                    console.log('遮罩被点击');
                    this.closeMenu();
                });
                
                this.mobileOverlay.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                }, { passive: false });
                
                this.mobileOverlay.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.closeMenu();
                }, { passive: false });
            }
            
            // 监听窗口大小变化
            window.addEventListener('resize', () => {
                if (window.innerWidth > 768 && this.isMenuOpen) {
                    this.closeMenu();
                }
            });
        }
        
        handleMenuClick(e) {
            console.log('处理菜单点击事件');
            
            // 阻止默认行为和事件冒泡
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            // 添加点击反馈
            this.addClickFeedback();
            
            // 切换菜单状态
            if (this.isMenuOpen) {
                this.closeMenu();
            } else {
                this.openMenu();
            }
        }
        
        addClickFeedback() {
            if (this.mobileMenuBtn) {
                this.mobileMenuBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.mobileMenuBtn.style.transform = '';
                }, 150);
            }
        }
        
        openMenu() {
            console.log('打开菜单');
            
            if (!this.sideMenu) return;
            
            this.sideMenu.classList.add('expanded');
            if (this.mobileOverlay) {
                this.mobileOverlay.classList.add('active');
            }
            
            this.isMenuOpen = true;
            
            // 禁用背景滚动
            document.body.style.overflow = 'hidden';
            
            // 添加动画效果
            this.sideMenu.style.transition = 'left 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            
            console.log('菜单已打开');
        }
        
        closeMenu() {
            console.log('关闭菜单');
            
            if (!this.sideMenu) return;
            
            this.sideMenu.classList.remove('expanded');
            if (this.mobileOverlay) {
                this.mobileOverlay.classList.remove('active');
            }
            
            this.isMenuOpen = false;
            
            // 恢复背景滚动
            document.body.style.overflow = '';
            
            console.log('菜单已关闭');
        }
        
        addWeChatStyles() {
            console.log('添加企业微信专用样式');
            
            const style = document.createElement('style');
            style.textContent = `
                /* 企业微信专用样式 */
                .mobile-menu-btn {
                    -webkit-tap-highlight-color: transparent !important;
                    -webkit-touch-callout: none !important;
                    -webkit-user-select: none !important;
                    -khtml-user-select: none !important;
                    -moz-user-select: none !important;
                    -ms-user-select: none !important;
                    user-select: none !important;
                    cursor: pointer !important;
                    z-index: 1002 !important;
                }
                
                .mobile-menu-btn:active {
                    background-color: rgba(0, 0, 0, 0.1) !important;
                }
                
                .side-menu {
                    -webkit-overflow-scrolling: touch !important;
                    -webkit-transform: translateZ(0) !important;
                    transform: translateZ(0) !important;
                }
                
                .mobile-overlay {
                    -webkit-tap-highlight-color: transparent !important;
                }
                
                /* 确保按钮在移动端可见 */
                @media (max-width: 768px) {
                    .mobile-menu-btn {
                        display: flex !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                        pointer-events: auto !important;
                    }
                }
            `;
            
            document.head.appendChild(style);
        }
    }
    
    // 初始化
    if (isWeChatBrowser() && isMobileDevice()) {
        console.log('检测到企业微信移动端，启动专用修复');
        
        // 延迟初始化，确保DOM完全加载
        setTimeout(() => {
            new WeChatMenuController();
        }, 100);
        
        // 备用初始化方案
        setTimeout(() => {
            if (!window.wechatMenuController) {
                console.log('备用初始化企业微信菜单控制器');
                window.wechatMenuController = new WeChatMenuController();
            }
        }, 500);
        
        // 监听页面可见性变化，重新初始化
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && isWeChatBrowser()) {
                console.log('页面重新可见，重新初始化菜单');
                setTimeout(() => {
                    if (window.wechatMenuController) {
                        window.wechatMenuController.setupMenu();
                    }
                }, 100);
            }
        });
    } else {
        console.log('非企业微信移动端，跳过专用修复');
    }
    
    // 导出到全局作用域，方便调试
    window.WeChatMenuController = WeChatMenuController;
    
})();
