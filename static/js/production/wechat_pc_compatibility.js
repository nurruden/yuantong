/**
 * 企业微信PC端JavaScript兼容性解决方案
 * 解决企业微信PC端环境下JavaScript执行限制的问题
 * 支持大塬qc报表和长富qc报表
 */

(function() {
    'use strict';
    
    // 检测企业微信PC端环境
    function isWxWorkPC() {
        const userAgent = navigator.userAgent;
        const isWxWork = /wxwork/i.test(userAgent);
        const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        return isWxWork && !isMobile;
    }
    
    // 如果不在企业微信PC端环境，直接返回
    if (!isWxWorkPC()) {
        return;
    }
    
    console.log('🔧 检测到企业微信PC端环境，启用兼容性解决方案');
    
    // 企业微信PC端兼容性修复
    function applyWxWorkPCCompatibility() {
        console.log('🔧 应用企业微信PC端兼容性修复...');
        
        // 1. 确保关键函数在全局作用域可用（支持大塬和长富）
        const reportFunctions = [
            'loadDayuanHistoryData',    // 大塬qc报表
            'loadChangfuHistoryData'    // 长富qc报表
        ];
        
        let availableFunctions = [];
        
        reportFunctions.forEach(funcName => {
            if (typeof window[funcName] === 'undefined') {
                console.warn(`⚠️ ${funcName} 函数未定义，尝试修复...`);
                
                // 等待外部JavaScript文件加载完成
                const checkInterval = setInterval(() => {
                    if (typeof window[funcName] === 'function') {
                        clearInterval(checkInterval);
                        console.log(`✅ ${funcName} 函数已可用`);
                        availableFunctions.push(funcName);
                        
                        // 触发页面初始化
                        if (typeof window[`initialize${funcName.replace('load', '').replace('Data', '')}Page`] === 'function') {
                            window[`initialize${funcName.replace('load', '').replace('Data', '')}Page`]();
                        }
                    }
                }, 100);
                
                // 设置超时
                setTimeout(() => {
                    clearInterval(checkInterval);
                    console.warn(`⚠️ 等待 ${funcName} 函数超时`);
                }, 10000);
            } else {
                console.log(`✅ ${funcName} 函数已可用`);
                availableFunctions.push(funcName);
            }
        });
        
        // 2. 修复fetch API兼容性问题
        if (typeof fetch === 'undefined') {
            console.warn('⚠️ fetch API 不可用，使用 XMLHttpRequest 替代');
            
            // 实现简单的fetch替代
            window.fetch = function(url, options = {}) {
                return new Promise((resolve, reject) => {
                    const xhr = new XMLHttpRequest();
                    xhr.open(options.method || 'GET', url);
                    
                    // 设置请求头
                    if (options.headers) {
                        Object.keys(options.headers).forEach(key => {
                            xhr.setRequestHeader(key, options.headers[key]);
                        });
                    }
                    
                    xhr.onload = function() {
                        const response = {
                            ok: xhr.status >= 200 && xhr.status < 300,
                            status: xhr.status,
                            statusText: xhr.statusText,
                            headers: xhr.getAllResponseHeaders(),
                            text: () => Promise.resolve(xhr.responseText),
                            json: () => Promise.resolve(JSON.parse(xhr.responseText))
                        };
                        resolve(response);
                    };
                    
                    xhr.onerror = function() {
                        reject(new Error('Network error'));
                    };
                    
                    xhr.send(options.body);
                });
            };
        }
        
        // 3. 修复Promise兼容性问题
        if (typeof Promise === 'undefined') {
            console.warn('⚠️ Promise 不可用，使用 polyfill');
            
            // 简单的Promise polyfill
            window.Promise = function(executor) {
                let resolve, reject;
                let state = 'pending';
                let value;
                
                this.then = function(onFulfilled, onRejected) {
                    if (state === 'fulfilled') {
                        onFulfilled(value);
                    } else if (state === 'rejected') {
                        onRejected(value);
                    }
                    return this;
                };
                
                executor(function(val) {
                    state = 'fulfilled';
                    value = val;
                }, function(val) {
                    state = 'rejected';
                    value = val;
                });
            };
        }
        
        // 4. 修复localStorage兼容性问题
        if (typeof localStorage === 'undefined') {
            console.warn('⚠️ localStorage 不可用，使用内存存储替代');
            
            const memoryStorage = {};
            window.localStorage = {
                getItem: function(key) {
                    return memoryStorage[key] || null;
                },
                setItem: function(key, value) {
                    memoryStorage[key] = value;
                },
                removeItem: function(key) {
                    delete memoryStorage[key];
                },
                clear: function() {
                    Object.keys(memoryStorage).forEach(key => delete memoryStorage[key]);
                }
            };
        }
        
        // 5. 修复事件监听器兼容性问题
        if (typeof window.addEventListener === 'undefined') {
            console.warn('⚠️ addEventListener 不可用，使用 attachEvent 替代');
            
            window.addEventListener = function(type, listener) {
                if (window.attachEvent) {
                    window.attachEvent('on' + type, listener);
                }
            };
        }
        
        // 6. 修复DOMContentLoaded事件
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.log('✅ DOM加载完成，初始化企业微信PC端兼容性');
                initializeWxWorkPCFeatures();
            });
        } else {
            // DOM已经加载完成
            initializeWxWorkPCFeatures();
        }
    }
    
    // 初始化企业微信PC端特有功能
    function initializeWxWorkPCFeatures() {
        console.log('🔧 初始化企业微信PC端特有功能...');
        
        // 1. 确保过滤表单事件绑定（支持大塬和长富）
        const filterForm = document.getElementById('filterForm');
        if (filterForm) {
            console.log('✅ 找到过滤表单，绑定事件');
            
            // 移除可能存在的旧事件监听器
            const newForm = filterForm.cloneNode(true);
            filterForm.parentNode.replaceChild(newForm, filterForm);
            
            // 重新绑定事件
            newForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // 根据当前页面确定使用哪个函数
                const currentPath = window.location.pathname;
                let loadFunction = null;
                
                if (currentPath.includes('/dayuan_report/history/')) {
                    loadFunction = 'loadDayuanHistoryData';
                    console.log('🔍 大塬报表 - 过滤表单提交事件触发（企业微信PC端）');
                } else if (currentPath.includes('/changfu_report/history/')) {
                    loadFunction = 'loadChangfuHistoryData';
                    console.log('🔍 长富报表 - 过滤表单提交事件触发（企业微信PC端）');
                }
                
                if (loadFunction && typeof window[loadFunction] === 'function') {
                    window[loadFunction](1);
                } else {
                    console.error(`❌ ${loadFunction} 函数不可用`);
                    alert('系统正在初始化，请稍后再试...');
                }
            });
        }
        
        // 2. 自动加载第一页数据（支持大塬和长富）
        setTimeout(() => {
            const currentPath = window.location.pathname;
            let loadFunction = null;
            
            if (currentPath.includes('/dayuan_report/history/')) {
                loadFunction = 'loadDayuanHistoryData';
                console.log('🔄 自动加载第一页数据（大塬报表 - 企业微信PC端）');
            } else if (currentPath.includes('/changfu_report/history/')) {
                loadFunction = 'loadChangfuHistoryData';
                console.log('🔄 自动加载第一页数据（长富报表 - 企业微信PC端）');
            }
            
            if (loadFunction && typeof window[loadFunction] === 'function') {
                window[loadFunction](1);
            } else {
                console.warn(`⚠️ 无法自动加载数据，${loadFunction} 函数不可用`);
            }
        }, 2000);
        
        // 3. 添加企业微信PC端特有的错误处理
        window.addEventListener('error', function(e) {
            console.error('企业微信PC端JavaScript错误:', e.error);
            
            // 如果是函数未定义错误，尝试重新加载
            if (e.message.includes('is not defined') || e.message.includes('is not a function')) {
                console.log('🔄 检测到函数未定义错误，尝试重新初始化...');
                setTimeout(applyWxWorkPCCompatibility, 1000);
            }
        });
    }
    
    // 应用兼容性修复
    applyWxWorkPCCompatibility();
    
    // 导出兼容性函数供外部使用
    window.wxWorkPCCompatibility = {
        isWxWorkPC: isWxWorkPC,
        applyCompatibility: applyWxWorkPCCompatibility,
        initializeFeatures: initializeWxWorkPCFeatures
    };
    
    console.log('✅ 企业微信PC端兼容性解决方案已加载（支持大塬和长富qc报表）');
    
})();

