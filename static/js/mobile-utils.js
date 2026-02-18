/**
 * 移动端专用工具函数
 * 处理移动端特有的交互逻辑和优化
 */

// 检测是否为移动设备
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           window.innerWidth <= 768;
}

// 检测是否为触摸设备
function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

// 移动端菜单控制
class MobileMenuController {
    constructor() {
        this.sideMenu = document.getElementById('sideMenu');
        this.mobileMenuBtn = document.getElementById('mobileMenuBtn');
        this.menuCloseBtn = document.getElementById('menuCloseBtn');
        this.mobileOverlay = document.getElementById('mobileOverlay');
        this.isMenuOpen = false;
        
        this.init();
    }
    
    init() {
        if (!this.sideMenu || !this.mobileMenuBtn) return;
        
        // 绑定事件
        this.mobileMenuBtn.addEventListener('click', () => this.openMenu());
        if (this.menuCloseBtn) {
            this.menuCloseBtn.addEventListener('click', () => this.closeMenu());
        }
        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', () => this.closeMenu());
        }
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => this.handleResize());
        
        // 监听触摸手势
        this.initTouchGestures();
        
        // 防止页面滚动穿透
        this.preventScrollThrough();
    }
    
    openMenu() {
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
    }
    
    closeMenu() {
        if (!this.sideMenu) return;
        
        this.sideMenu.classList.remove('expanded');
        if (this.mobileOverlay) {
            this.mobileOverlay.classList.remove('active');
        }
        this.isMenuOpen = false;
        
        // 恢复背景滚动
        document.body.style.overflow = '';
        
        // 添加动画效果
        this.sideMenu.style.transition = 'left 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    }
    
    handleResize() {
        // 如果窗口变大到桌面端，自动关闭移动端菜单
        if (window.innerWidth > 768 && this.isMenuOpen) {
            this.closeMenu();
        }
    }
    
    initTouchGestures() {
        if (!isTouchDevice()) return;
        
        let startX = 0;
        let startY = 0;
        let currentX = 0;
        let currentY = 0;
        let isDragging = false;
        
        // 触摸开始
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isDragging = false;
        }, { passive: true });
        
        // 触摸移动
        document.addEventListener('touchmove', (e) => {
            if (!isDragging) {
                currentX = e.touches[0].clientX;
                currentY = e.touches[0].clientY;
                
                const deltaX = Math.abs(currentX - startX);
                const deltaY = Math.abs(currentY - startY);
                
                // 如果水平滑动距离大于垂直滑动距离，且大于阈值，则认为是滑动
                if (deltaX > deltaY && deltaX > 50) {
                    isDragging = true;
                }
            }
        }, { passive: true });
        
        // 触摸结束
        document.addEventListener('touchend', (e) => {
            if (isDragging) {
                const deltaX = currentX - startX;
                
                // 从左边缘向右滑动打开菜单
                if (startX < 50 && deltaX > 100 && !this.isMenuOpen) {
                    this.openMenu();
                }
                // 从右向左滑动关闭菜单
                else if (deltaX < -100 && this.isMenuOpen) {
                    this.closeMenu();
                }
            }
            
            isDragging = false;
        }, { passive: true });
    }
    
    preventScrollThrough() {
        // 防止菜单打开时背景滚动
        if (this.sideMenu) {
            this.sideMenu.addEventListener('touchmove', (e) => {
                if (this.isMenuOpen) {
                    e.stopPropagation();
                }
            }, { passive: false });
        }
    }
}

// 初始化移动端功能
document.addEventListener('DOMContentLoaded', () => {
    if (isMobileDevice()) {
        // 初始化移动端菜单控制器
        new MobileMenuController();
        
        // 添加移动端类名到body
        document.body.classList.add('mobile-device');
        
        console.log('移动端优化已启用');
    }
});
