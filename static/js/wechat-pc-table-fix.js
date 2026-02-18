/**
 * 企业微信PC端表格选中行样式强制修复
 * 通过JavaScript动态覆盖样式，确保在企业微信PC端中选中行颜色更柔和
 */

(function() {
    'use strict';
    
    // 检测企业微信PC端环境
    function isWxWorkPC() {
        const userAgent = navigator.userAgent;
        const isWxWork = /wxwork/i.test(userAgent);
        const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        const isPC = !isMobile;
        
        console.log('🔍 环境检测:', {
            userAgent: userAgent,
            isWxWork: isWxWork,
            isMobile: isMobile,
            isPC: isPC,
            result: isWxWork && isPC
        });
        
        return isWxWork && isPC;
    }
    
    // 如果不在企业微信PC端环境，直接返回
    if (!isWxWorkPC()) {
        return;
    }
    
    console.log('🔧 检测到企业微信PC端环境，启用表格选中行样式强制修复');
    
    // 强制修复表格选中行样式
    function forceFixTableHoverStyles() {
        console.log('🔧 强制修复表格选中行样式...');
        
        // 创建强制样式
        const style = document.createElement('style');
        style.id = 'wechat-pc-table-force-fix';
        style.textContent = `
            /* 企业微信PC端强制样式修复 - 超强制覆盖 */
            html body .sticky-table-container tbody tr:hover,
            html body table tbody tr:hover,
            html body tbody tr:hover,
            html body .table-container tbody tr:hover,
            html body .data-table tbody tr:hover,
            html body .page-container table tbody tr:hover,
            html body .page-container .sticky-table-container tbody tr:hover,
            html body tr:hover,
            html body .table tr:hover,
            html body .data-table tr:hover,
            html body .sticky-table-container tr:hover {
                background-color: #ffffff !important;
                background: #ffffff !important;
                transition: background-color 0.2s ease !important;
                box-shadow: inset 0 0 0 1px #f0f0f0 !important;
            }
            
            /* 选中状态样式 - 超强制 */
            html body .page-container table tbody tr.selected,
            html body .page-container table tbody tr:focus,
            html body .sticky-table-container tbody tr.selected,
            html body .sticky-table-container tbody tr:focus {
                background-color: #ffffff !important;
                background: #ffffff !important;
                outline: 1px solid #e0e0e0 !important;
                outline-offset: -1px !important;
                box-shadow: inset 0 0 0 1px #f0f0f0 !important;
            }
            
            /* 深色模式 */
            @media (prefers-color-scheme: dark) {
                html body .sticky-table-container tbody tr:hover,
                html body table tbody tr:hover,
                html body tbody tr:hover,
                html body .table-container tbody tr:hover,
                html body .data-table tbody tr:hover,
                html body .page-container table tbody tr:hover,
                html body .page-container .sticky-table-container tbody tr:hover,
                html body tr:hover,
                html body .table tr:hover,
                html body .data-table tr:hover,
                html body .sticky-table-container tr:hover {
                    background-color: #6c757d !important;
                    background: #6c757d !important;
                    transition: background-color 0.2s ease !important;
                }
            }
        `;
        
        // 移除旧的样式（如果存在）
        const oldStyle = document.getElementById('wechat-pc-table-force-fix');
        if (oldStyle) {
            oldStyle.remove();
        }
        
        // 添加新样式到head
        document.head.appendChild(style);
        
        console.log('✅ 企业微信PC端表格选中行样式强制修复已应用 - 使用极浅色 #ffffff + 淡边框');
        
        // 直接修改所有表格行的样式
        setTimeout(() => {
            const allRows = document.querySelectorAll('table tbody tr, .sticky-table-container tbody tr');
            console.log(`🔧 找到 ${allRows.length} 个表格行，直接修改样式`);
            
            allRows.forEach((row, index) => {
                // 添加鼠标悬停事件监听器
                row.addEventListener('mouseenter', function() {
                    this.style.backgroundColor = '#ffffff';
                    this.style.background = '#ffffff';
                    this.style.boxShadow = 'inset 0 0 0 1px #f0f0f0';
                });
                
                row.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = '';
                    this.style.background = '';
                    this.style.boxShadow = '';
                });
            });
            
            console.log('✅ 直接样式修改已应用到所有表格行');
        }, 1000);
    }
    
    // 监听表格内容变化，重新应用样式
    function observeTableChanges() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // 检查是否有新的表格行添加
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            if (node.tagName === 'TR' || node.querySelector && node.querySelector('tr')) {
                                console.log('🔄 检测到表格内容变化，重新应用样式修复');
                                setTimeout(forceFixTableHoverStyles, 100);
                            }
                        }
                    });
                }
            });
        });
        
        // 观察所有表格容器
        const tableContainers = document.querySelectorAll('.sticky-table-container, .table-container, .page-container');
        tableContainers.forEach(function(container) {
            observer.observe(container, {
                childList: true,
                subtree: true
            });
        });
    }
    
    // 初始化修复
    function initFix() {
        // 立即应用样式修复
        forceFixTableHoverStyles();
        
        // 监听表格变化
        observeTableChanges();
        
        // 定期重新应用样式（防止被其他样式覆盖）
        setInterval(function() {
            const style = document.getElementById('wechat-pc-table-force-fix');
            if (!style) {
                console.log('🔄 样式被移除，重新应用企业微信PC端表格修复');
                forceFixTableHoverStyles();
            }
        }, 5000);
    }
    
    // 等待DOM加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFix);
    } else {
        initFix();
    }
    
    // 导出函数供外部使用
    window.wechatPCTableFix = {
        isWxWorkPC: isWxWorkPC,
        forceFix: forceFixTableHoverStyles,
        init: initFix
    };
    
    console.log('✅ 企业微信PC端表格选中行样式强制修复脚本已加载');
    
})();
