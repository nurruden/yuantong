// 远通QC报表独立JS
// 仅服务于 yuantong_report.html 和 yuantong_report_history.html
// 保证表头与数据顺序严格一致，避免错位

// 立即执行函数：确保exportToExcel函数正确定义，避免递归调用
(function() {
    // 检查是否已经存在exportToExcel函数
    if (typeof window.exportToExcel === 'function') {
        console.log('检测到全局exportToExcel函数，将使用包装函数避免递归');
        // 保存全局函数引用
        const globalExportToExcel = window.exportToExcel;
        
        // 定义远通报表的导出函数
        window.exportYuantongReportToExcel = async function() {
            console.log('远通报表 exportYuantongReportToExcel 被调用');
            
            try {
                // 获取当前筛选条件
                const filterForm = document.getElementById('filterForm');
                const params = new URLSearchParams();
                if (filterForm) {
                    const formData = new FormData(filterForm);
                    for (const [key, value] of formData.entries()) {
                        if (value && key !== 'csrfmiddlewaretoken') {
                            params.append(key, value);
                        }
                    }
                }
                // 构建导出URL
                const exportUrl = `/yuantong_report/export_excel/?${params.toString()}`;
                console.log('构建的导出URL:', exportUrl);
                
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
                
                // 使用增强版导出功能
                if (typeof globalExportToExcel === 'function') {
                    console.log('使用增强版导出功能');
                    // 调用qc_report_common.js中的增强导出函数
                    globalExportToExcel(exportUrl, 'filterForm', 'export', '远通QC报表');
                } else {
                    console.log('增强版导出功能不可用，使用回退方式');
                    
                    // 如果是企业微信PC端，使用特殊处理
                    if (isWeChatPC) {
                        console.log('企业微信PC端，使用特殊导出处理');
                        performWeChatWorkExport(exportUrl, 'export', '远通QC报表');
                    } else {
                        // 回退到原有方式
                        performLegacyExport(exportUrl);
                    }
                }
            } catch (error) {
                console.error('导出失败:', error);
                showError('导出失败：' + error.message);
            }
        };
        
        // 定义包装函数，避免递归调用
        window.exportToExcel = async function() {
            console.log('导出Excel包装函数被调用，转发给 exportYuantongReportToExcel');
            return await window.exportYuantongReportToExcel();
        };
        
    } else {
        console.log('未检测到全局exportToExcel函数，将直接定义远通报表导出函数');
        // 直接定义远通报表的导出函数
        window.exportToExcel = async function() {
            console.log('远通报表 exportToExcel 被调用');
            
            try {
                // 获取当前筛选条件
                const filterForm = document.getElementById('filterForm');
                const params = new URLSearchParams();
                if (filterForm) {
                    const formData = new FormData(filterForm);
                    for (const [key, value] of formData.entries()) {
                        if (value && key !== 'csrfmiddlewaretoken') {
                            params.append(key, value);
                        }
                    }
                }
                // 构建导出URL
                const exportUrl = `/yuantong_report/export_excel/?${params.toString()}`;
                console.log('构建的导出URL:', exportUrl);
                
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
                
                // 使用回退方式
                console.log('增强版导出功能不可用，使用回退方式');
                
                // 如果是企业微信PC端，使用特殊处理
                if (isWeChatPC) {
                    console.log('企业微信PC端，使用特殊导出处理');
                    performWeChatWorkExport(exportUrl, 'export', '远通QC报表');
                } else {
                    // 回退到原有方式
                    performLegacyExport(exportUrl);
                }
            } catch (error) {
                console.error('导出失败:', error);
                showError('导出失败：' + error.message);
            }
        };
    }
})();

document.addEventListener('DOMContentLoaded', function() {
    // 判断是否为历史页面（路径包含 /yuantong_report/history/）
    if (window.location.pathname.includes('/yuantong_report/history/')) {
        // 支持筛选表单自动加载
        const filterForm = document.getElementById('filterForm');
        if (filterForm) {
            filterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                loadYuantongHistoryData(1);
            });
        }
        // 页面初次加载时自动加载第一页
        setTimeout(() => loadYuantongHistoryData(1), 100);
    }
    // 表单页面初始化
    if (window.location.pathname === '/yuantong_report/') {
        // 初始化计算逻辑
        initCalculationLogic();
    }
    // flatpickr日期和时间选择器通用初始化
    initDateTimePickers();
});

// 初始化计算逻辑
function initCalculationLogic() {
    console.log('=== initCalculationLogic 开始 ===');

    // 加载系数参数
    loadCoefficients().then(() => {
        console.log('系数参数加载完成，开始初始化');
        // 初始化完成后设置系数值
        updateCoefficientsByMaterialType();
        // 设置字段可编辑性
        updateFieldEditability();
        // 执行初始计算
        console.log('执行初始计算');
        calculateAllValues();
        console.log('初始计算完成');
    });

    // 为物料类型添加变化监听器
    const materialTypeSelect = document.getElementById('material_type');
    console.log('物料类型选择器:', materialTypeSelect);

    if (materialTypeSelect) {
        console.log('添加物料类型变化监听器');
        materialTypeSelect.addEventListener('change', function() {
            console.log('=== 物料类型切换事件触发 ===');
            console.log('切换到的物料类型:', this.value);

            // 记录切换前的字段值
            const wetCakeDensityBefore = document.getElementById('wet_cake_density')?.value;
            const yuantongCakeDensityBefore = document.getElementById('yuantong_cake_density')?.value;
            const changfuCakeDensityBefore = document.getElementById('changfu_cake_density')?.value;

            console.log('切换前 - 饼密度:', wetCakeDensityBefore);
            console.log('切换前 - 远通饼密度:', yuantongCakeDensityBefore);
            console.log('切换前 - 长富饼密度:', changfuCakeDensityBefore);

            updateCoefficientsByMaterialType();
            updateFieldEditability();
            calculateAllValues(true); // 跳过自动填充
            setTimeout(() => {
                calculateAllValues(false); // 再补一次自动填充，保证字段有值
            }, 100);

            // 记录切换后的字段值
            setTimeout(() => {
                const wetCakeDensityAfter = document.getElementById('wet_cake_density')?.value;
                const yuantongCakeDensityAfter = document.getElementById('yuantong_cake_density')?.value;
                const changfuCakeDensityAfter = document.getElementById('changfu_cake_density')?.value;

                console.log('切换后 - 饼密度:', wetCakeDensityAfter);
                console.log('切换后 - 远通饼密度:', yuantongCakeDensityAfter);
                console.log('切换后 - 长富饼密度:', changfuCakeDensityAfter);
                console.log('=== 物料类型切换完成 ===');
            }, 200);
        });
    } else {
        console.log('未找到物料类型选择器');
    }

    // 为相关字段添加事件监听器
    const calculationFields = ['yuantong_permeability_coefficient', 'yuantong_sample_weight', 'yuantong_filter_area', 'cake_thickness', 'water_viscosity', 'filter_time'];
    console.log('为计算字段添加事件监听器:', calculationFields);

    calculationFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            console.log(`为字段 ${fieldId} 添加事件监听器`);
            field.addEventListener('input', calculateAllValues);
            field.addEventListener('change', calculateAllValues);
        } else {
            console.log(`未找到字段 ${fieldId}`);
        }
    });

    // 表单提交处理
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            calculateAllValues(false); // 提交前强制自动填充，保证所有字段有值
            // 获取表单数据
            const formData = new FormData(form);
            const params = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                if (key !== 'csrfmiddlewaretoken') {
                    // 对于日期和时间字段，允许空字符串（即用户清空后不传递参数）
                    if (['start_date','end_date','start_time','end_time'].includes(key)) {
                        if (value.trim() !== '') {
                            params.append(key, value);
                        }
                    } else {
                        if (value) {
                            params.append(key, value);
                        }
                    }
                }
            }
            params.set('page', 1); // 强制重置页码为1
            params.set('page_size', currentPageSize); // 使用当前每页大小
            const apiUrl = `/api/yuantong-report/?${params.toString()}`;
            try {
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    }
                });
                if (response.ok) {
                    const result = await response.json();
                    if (result.status === 'success') {
                        displayYuantongHistoryData(result.data);
                // 记录查看操作日志（仅在第一次加载或页面变化时记录）
                if (page === 1) {
                    logViewOperation();
                }
                

                        updateYuantongPagination(result.current_page, result.total_pages, result.total_count);
                    } else {
                        showError('数据加载失败：' + (result.message || '未知错误'));
                    }
                } else {
                    showError('请求失败，状态码：' + response.status);
                }
            } catch (error) {
                showError('数据加载异常：' + error.message);
            }
        });
    }

    console.log('=== initCalculationLogic 完成 ===');
}

// 系数参数
let coefficients = {
    yuantong_permeability: 6.4,
    yuantong_sample_weight: 5,
    yuantong_filter_area: 3.14
};

// 从服务器加载系数参数
async function loadCoefficients() {
    try {
        // 加载远通渗透率系数
        const response1 = await fetch('/api/report-parameters/yuantong_permeability_coefficient/');
        const result1 = await response1.json();
        if (result1.status === 'success') {
            coefficients.yuantong_permeability = parseFloat(result1.data.value);
        }

        // 加载远通样品重量
        const response2 = await fetch('/api/report-parameters/yuantong_sample_weight/');
        const result2 = await response2.json();
        if (result2.status === 'success') {
            coefficients.yuantong_sample_weight = parseFloat(result2.data.value);
        }

        // 加载远通过滤面积
        const response3 = await fetch('/api/report-parameters/yuantong_filter_area/');
        const result3 = await response3.json();
        if (result3.status === 'success') {
            coefficients.yuantong_filter_area = parseFloat(result3.data.value);
        }

        console.log('系数参数已加载:', coefficients);
    } catch (error) {
        console.warn('加载系数参数失败，使用默认值:', error);
    }
}

// 根据物料类型设置系数值
function updateCoefficientsByMaterialType() {
    const materialType = document.getElementById('material_type')?.value;
    console.log('=== updateCoefficientsByMaterialType 开始 ===');
    console.log('当前物料类型:', materialType);

    if (!materialType) {
        console.log('物料类型为空，退出');
        return;
    }

    if (materialType === '助熔煅烧品') {
        console.log('处理助熔煅烧品模式');
        // 从后台参数管理读取值
        const coefficientField = document.getElementById('yuantong_permeability_coefficient');
        const sampleWeightField = document.getElementById('yuantong_sample_weight');
        const filterAreaField = document.getElementById('yuantong_filter_area');

        if (coefficientField) coefficientField.value = coefficients.yuantong_permeability || '';
        if (sampleWeightField) sampleWeightField.value = coefficients.yuantong_sample_weight || '';
        if (filterAreaField) filterAreaField.value = coefficients.yuantong_filter_area || '';

        console.log('助熔煅烧品系数设置完成:', {
            coefficient: coefficients.yuantong_permeability,
            sampleWeight: coefficients.yuantong_sample_weight,
            filterArea: coefficients.yuantong_filter_area
        });
    } else if (materialType === '煅烧品') {
        console.log('处理煅烧品模式');
        // 使用固定值
        const coefficientField = document.getElementById('yuantong_permeability_coefficient');
        const sampleWeightField = document.getElementById('yuantong_sample_weight');
        const filterAreaField = document.getElementById('yuantong_filter_area');
        const cakeThicknessField = document.getElementById('cake_thickness');

        if (coefficientField) coefficientField.value = '6.4';
        if (sampleWeightField) sampleWeightField.value = '5';
        if (filterAreaField) filterAreaField.value = '3.14';
        if (cakeThicknessField) cakeThicknessField.value = '7'; // 设置默认饼厚值

        console.log('煅烧品系数设置完成:', {
            coefficient: '6.4',
            sampleWeight: '5',
            filterArea: '3.14',
            cakeThickness: '7'
        });
    }

    console.log('=== updateCoefficientsByMaterialType 完成 ===');
}

// 根据物料类型更新字段可编辑性
function updateFieldEditability() {
    const materialType = document.getElementById('material_type')?.value;
    if (!materialType) return;

    console.log('=== updateFieldEditability 开始 ===');
    console.log('当前物料类型:', materialType);

    const yuantongCakeDensityField = document.getElementById('yuantong_cake_density');
    const changfuCakeDensityField = document.getElementById('changfu_cake_density');
    const wetCakeDensityField = document.getElementById('wet_cake_density');

    if (materialType === '助熔煅烧品') {
        console.log('处理助熔煅烧品模式');
        // 助熔煅烧品：远通饼密度，长富饼密度两个字段不可编辑
        if (yuantongCakeDensityField) {
            console.log('清空远通饼密度字段');
            yuantongCakeDensityField.readOnly = true;
            yuantongCakeDensityField.style.backgroundColor = '#f5f5f5';
            yuantongCakeDensityField.title = '此字段由系统自动计算';
            // 清空远通饼密度和长富饼密度
            yuantongCakeDensityField.value = '';
        }
        if (changfuCakeDensityField) {
            console.log('清空长富饼密度字段');
            changfuCakeDensityField.readOnly = true;
            changfuCakeDensityField.style.backgroundColor = '#f5f5f5';
            changfuCakeDensityField.title = '此字段由系统自动计算';
            // 清空长富饼密度
            changfuCakeDensityField.value = '';
        }
        if (wetCakeDensityField) {
            console.log('启用饼密度字段编辑');
            wetCakeDensityField.readOnly = false;
            wetCakeDensityField.style.backgroundColor = '';
            wetCakeDensityField.title = '';
        }
    } else if (materialType === '煅烧品') {
        console.log('处理煅烧品模式');
        // 煅烧品：饼密度字段不可编辑
        if (wetCakeDensityField) {
            console.log('清空饼密度字段');
            wetCakeDensityField.readOnly = true;
            wetCakeDensityField.style.backgroundColor = '#f5f5f5';
            wetCakeDensityField.title = '此字段由系统自动计算';
            // 清空饼密度
            wetCakeDensityField.value = '';
        }
        if (yuantongCakeDensityField) {
            console.log('启用远通饼密度字段编辑');
            yuantongCakeDensityField.readOnly = false;
            yuantongCakeDensityField.style.backgroundColor = '';
            yuantongCakeDensityField.title = '';
        }
        if (changfuCakeDensityField) {
            console.log('启用长富饼密度字段编辑');
            changfuCakeDensityField.readOnly = false;
            changfuCakeDensityField.style.backgroundColor = '';
            changfuCakeDensityField.title = '';
        }
    }

    console.log('=== updateFieldEditability 完成 ===');
}

// 执行所有计算
function calculateAllValues(skipAutoFill = false) {
    console.log('=== calculateAllValues 开始 ===');
    console.log('skipAutoFill参数:', skipAutoFill);

    const materialType = document.getElementById('material_type')?.value;
    console.log('当前物料类型:', materialType);

    if (!materialType) {
        console.log('物料类型为空，退出计算');
        return;
    }

    // 获取输入值
    const yuantongCoefficient = parseFloat(document.getElementById('yuantong_permeability_coefficient')?.value) || 0;
    const yuantongSampleWeight = parseFloat(document.getElementById('yuantong_sample_weight')?.value) || 0;
    const yuantongFilterArea = parseFloat(document.getElementById('yuantong_filter_area')?.value) || 0;
    const cakeThickness = parseFloat(document.getElementById('cake_thickness')?.value) || 0;
    const waterViscosity = parseFloat(document.getElementById('water_viscosity')?.value) || 0;
    const filterTime = parseFloat(document.getElementById('filter_time')?.value) || 0;

    console.log('计算参数:', {
        yuantongCoefficient,
        yuantongSampleWeight,
        yuantongFilterArea,
        cakeThickness,
        waterViscosity,
        filterTime
    });

    if (materialType === '助熔煅烧品') {
        console.log('调用助熔煅烧品计算函数');
        calculateForFluxCalcined();
    } else if (materialType === '煅烧品') {
        console.log('调用煅烧品计算函数');
        calculateForCalcined(skipAutoFill);
    }

    console.log('=== calculateAllValues 完成 ===');
}

// 助熔煅烧品的计算逻辑
function calculateForFluxCalcined() {
    const yuantongCoefficient = parseFloat(document.getElementById('yuantong_permeability_coefficient')?.value) || 0;
    const yuantongSampleWeight = parseFloat(document.getElementById('yuantong_sample_weight')?.value) || 0;
    const yuantongFilterArea = parseFloat(document.getElementById('yuantong_filter_area')?.value) || 0;
    const cakeThickness = parseFloat(document.getElementById('cake_thickness')?.value) || 0;
    const waterViscosity = parseFloat(document.getElementById('water_viscosity')?.value) || 0;
    const filterTime = parseFloat(document.getElementById('filter_time')?.value) || 0;

    // 远通渗透率 = 远通渗透率系数 * 饼厚 * 水黏度 / 过滤时间
    let yuantongPermeability = null;
    if (yuantongCoefficient && cakeThickness && waterViscosity && filterTime) {
        yuantongPermeability = (yuantongCoefficient * cakeThickness * waterViscosity / filterTime);
        document.getElementById('permeability').value = yuantongPermeability.toFixed(4);
    } else {
        document.getElementById('permeability').value = '';
    }

    // 长富渗透率 = (远通渗透率 - 0.366) / 1.23
    if (yuantongPermeability !== null) {
        const changfuPermeability = (yuantongPermeability - 0.366) / 1.23;
        document.getElementById('permeability_long').value = changfuPermeability.toFixed(4);
    } else {
        document.getElementById('permeability_long').value = '';
    }

    // 饼密度 = 远通样品重量 / 远通过滤面积 / 饼厚
    if (yuantongSampleWeight && yuantongFilterArea && cakeThickness) {
        const cakeDensity = yuantongSampleWeight / yuantongFilterArea / cakeThickness;
        document.getElementById('wet_cake_density').value = cakeDensity.toFixed(3);
    } else {
        document.getElementById('wet_cake_density').value = '';
    }

    // 远通饼密度和长富饼密度不可编辑，由系统计算
    // 这里可以根据需要设置固定值或其他计算逻辑
    document.getElementById('yuantong_cake_density').value = '';
    document.getElementById('changfu_cake_density').value = '';
}

// 煅烧品的计算逻辑
function calculateForCalcined(skipAutoFill = false) {
    console.log('=== calculateForCalcined 开始 ===');
    console.log('skipAutoFill参数:', skipAutoFill);

    const yuantongCoefficient = parseFloat(document.getElementById('yuantong_permeability_coefficient')?.value) || 0;
    const yuantongSampleWeight = parseFloat(document.getElementById('yuantong_sample_weight')?.value) || 0;
    const yuantongFilterArea = parseFloat(document.getElementById('yuantong_filter_area')?.value) || 0;
    const cakeThickness = parseFloat(document.getElementById('cake_thickness')?.value) || 0;
    const waterViscosity = parseFloat(document.getElementById('water_viscosity')?.value) || 0;
    const filterTime = parseFloat(document.getElementById('filter_time')?.value) || 0;

    console.log('计算参数:', {
        yuantongCoefficient,
        yuantongSampleWeight,
        yuantongFilterArea,
        cakeThickness,
        waterViscosity,
        filterTime
    });

    // 远通渗透率 = 远通渗透率系数 * 饼厚 * 水粘度 / 过滤时间
    let yuantongPermeability = null;
    if (yuantongCoefficient && cakeThickness && waterViscosity && filterTime) {
        yuantongPermeability = (yuantongCoefficient * cakeThickness * waterViscosity / filterTime);
        document.getElementById('permeability').value = yuantongPermeability.toFixed(4);
    } else {
        document.getElementById('permeability').value = '';
    }

    // 长富渗透率 = 远通渗透率 - 0.02
    if (yuantongPermeability !== null) {
        const changfuPermeability = yuantongPermeability - 0.02;
        document.getElementById('permeability_long').value = changfuPermeability.toFixed(4);
    } else {
        document.getElementById('permeability_long').value = '';
    }

    // 饼密度计算
    // 远通饼密度 = 远通样品重量 / 远通过滤面积 / 饼厚
    // 在煅烧品模式下，如果饼厚为空，则使用默认值1进行计算
    if (yuantongSampleWeight && yuantongFilterArea) {
        const effectiveCakeThickness = cakeThickness || 1; // 如果饼厚为空，使用默认值1
        const yuantongCakeDensity = yuantongSampleWeight / yuantongFilterArea / effectiveCakeThickness;
        console.log('计算出的饼密度值:', yuantongCakeDensity);
        console.log('使用的饼厚值:', effectiveCakeThickness);

        // 如果skipAutoFill为true，则不自动填充饼密度字段
        if (!skipAutoFill) {
            console.log('自动填充饼密度字段');
            document.getElementById('wet_cake_density').value = yuantongCakeDensity.toFixed(3);
        } else {
            console.log('跳过饼密度字段自动填充（skipAutoFill=true）');
        }

        // 注意：在煅烧品模式下，远通饼密度和长富饼密度字段是可编辑的
        // 当参数变化时，自动重新计算这些字段
        const yuantongCakeDensityField = document.getElementById('yuantong_cake_density');
        const changfuCakeDensityField = document.getElementById('changfu_cake_density');

        // 如果skipAutoFill为true，则不自动填充
        if (!skipAutoFill) {
            console.log('处理远通饼密度和长富饼密度字段');
            // 自动计算并填充远通饼密度和长富饼密度
            if (yuantongCakeDensityField) {
                console.log('自动填充远通饼密度字段');
                yuantongCakeDensityField.value = yuantongCakeDensity.toFixed(3);
            }
            if (changfuCakeDensityField) {
                const changfuCakeDensity = yuantongCakeDensity - 0.02;
                console.log('自动填充长富饼密度字段');
                changfuCakeDensityField.value = changfuCakeDensity.toFixed(3);
            }
        } else {
            console.log('跳过远通饼密度和长富饼密度字段自动填充（skipAutoFill=true）');
        }
    } else {
        console.log('计算参数不完整，清空相关字段');
        // 如果skipAutoFill为true，则不自动清空饼密度字段
        if (!skipAutoFill) {
            console.log('自动清空饼密度字段');
            document.getElementById('wet_cake_density').value = '';
        } else {
            console.log('跳过饼密度字段自动清空（skipAutoFill=true）');
        }
        // 清空远通饼密度和长富饼密度
        const yuantongCakeDensityField = document.getElementById('yuantong_cake_density');
        const changfuCakeDensityField = document.getElementById('changfu_cake_density');
        if (yuantongCakeDensityField) {
            yuantongCakeDensityField.value = '';
        }
        if (changfuCakeDensityField) {
            changfuCakeDensityField.value = '';
        }
    }

    console.log('=== calculateForCalcined 完成 ===');
}

let currentPageSize = 10;

async function loadYuantongHistoryData(page = 1, pageSize = currentPageSize) {
    const filterForm = document.getElementById('filterForm');
    const params = new URLSearchParams();
    if (filterForm) {
        const formData = new FormData(filterForm);
        for (const [key, value] of formData.entries()) {
            if (key !== 'csrfmiddlewaretoken') {
                // 对于日期和时间字段，允许空字符串（即用户清空后不传递参数）
                if (['start_date','end_date','start_time','end_time'].includes(key)) {
                    if (value.trim() !== '') {
                        params.append(key, value);
                    }
                } else {
                    if (value) {
                        params.append(key, value);
                    }
                }
            }
        }
    }
    params.set('page', page);
    params.set('page_size', pageSize);
    const apiUrl = `/api/yuantong-report/?${params.toString()}`;
    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'success') {
                displayYuantongHistoryData(result.data);
                // 记录查看操作日志（仅在第一次加载或页面变化时记录）
                if (page === 1) {
                    logViewOperation();
                }
                

                updateYuantongPagination(result.current_page, result.total_pages, result.total_count);
            } else {
                showError('数据加载失败：' + (result.message || '未知错误'));
            }
        } else {
            showError('请求失败，状态码：' + response.status);
        }
    } catch (error) {
        showError('数据加载异常：' + error.message);
    }
}


function displayYuantongHistoryData(data) {
    const tbody = document.querySelector('#reportTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="38" style="text-align: center; padding: 40px; color: #666;">暂无数据</td></tr>';
        return;
    }
    // yuangtong字段顺序
    const yuantongFields = [
        'username', 'date', 'time', 'moisture_after_drying', 'alkali_content', 'flux', 'product_name',
        'permeability', 'permeability_long',  'filter_time','water_viscosity','cake_thickness','wet_cake_density','yuantong_cake_density','changfu_cake_density','bulk_density',
        'sieving_14m', 'sieving_30m', 'sieving_40m', 'sieving_80m', 'sieving_100m', 'sieving_150m',
        'sieving_200m', 'sieving_325m', 'fe_ion', 'ca_ion', 'al_ion', 'brightness',
        'swirl', 'odor', 'conductance', 'ph', 'oil_absorption', 'water_absorption',
        'moisture', 'bags', 'packaging', 'tons', 'batch_number', 'remarks', 'shift'
    ];
    data.forEach(item => {
        const row = document.createElement('tr');
        let tds = '';
        yuantongFields.forEach(field => {
            tds += `<td>${item[field] !== undefined && item[field] !== null && item[field] !== '' ? item[field] : '-'}</td>`;
        });
        // 操作列
        const canEdit = item.can_edit || false;
        const canDelete = item.can_delete || false;
        const permissionReason = item.permission_reason || '';
        tds += `<td><div class="action-buttons-cell">`;
        if (canEdit) {
            tds += `<button class="btn btn-sm btn-primary" onclick="editYuantongRecord(${item.id})" title="编辑记录"><span class="material-icons" data-icon="edit">edit</span> 编辑</button>`;
        } else {
            tds += `<button class="btn btn-sm btn-secondary" disabled title="${permissionReason}"><span class="material-icons" data-icon="lock">lock</span> 已锁定</button>`;
        }
        if (canDelete) {
            tds += `<button class="btn btn-sm btn-danger" onclick="deleteYuantongRecord(${item.id})" title="删除记录"><span class="material-icons" data-icon="delete">delete</span> 删除</button>`;
        } else {
            tds += `<button class="btn btn-sm btn-secondary" disabled title="${permissionReason}"><span class="material-icons" data-icon="lock">lock</span> 无权限</button>`;
        }
        tds += `</div></td>`;
        row.innerHTML = tds;
        tbody.appendChild(row);
    });
}


function getCSRFToken() {
    // 优先从表单隐藏字段获取
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenElement) {
        return tokenElement.value;
    }
    // 再从cookie获取
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

function updateYuantongPagination(currentPage, totalPages, totalCount) {
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
        paginationHTML += `<button onclick="loadYuantongHistoryData(${currentPage - 1}, ${currentPageSize})">上一页</button>`;
    }
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    if (startPage > 1) {
        paginationHTML += `<button onclick="loadYuantongHistoryData(1, ${currentPageSize})">1</button>`;
        if (startPage > 2) {
            paginationHTML += `<span style="padding: 8px;">...</span>`;
        }
    }
    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            paginationHTML += `<button class="current-page">${i}</button>`;
        } else {
            paginationHTML += `<button onclick="loadYuantongHistoryData(${i}, ${currentPageSize})">${i}</button>`;
        }
    }
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<span style="padding: 8px;">...</span>`;
        }
        paginationHTML += `<button onclick="loadYuantongHistoryData(${totalPages}, ${currentPageSize})">${totalPages}</button>`;
    }
    if (currentPage < totalPages) {
        paginationHTML += `<button onclick="loadYuantongHistoryData(${currentPage + 1}, ${currentPageSize})">下一页</button>`;
    }
    paginationHTML += '</div>';
    paginationContainer.innerHTML = paginationHTML;
    // 事件绑定
    document.getElementById('pageSizeSelect').addEventListener('change', function() {
        currentPageSize = parseInt(this.value);
        loadYuantongHistoryData(1, currentPageSize);
    });
    document.getElementById('gotoPageBtn').addEventListener('click', function() {
        const page = parseInt(document.getElementById('gotoPageInput').value);
        if (page >= 1 && page <= totalPages) {
            loadYuantongHistoryData(page, currentPageSize);
        }
    });
    // 支持回车跳页
    document.getElementById('gotoPageInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const page = parseInt(this.value);
            if (page >= 1 && page <= totalPages) {
                loadYuantongHistoryData(page, currentPageSize);
            }
        }
    });
}
function showError(msg) {
    alert(msg);
}
function editRecord(id) {
    window.location.href = `/yuantong-report-edit/${id}/`;
}
async function deleteRecord(id) {
    if (!confirm('确定要删除这条记录吗？')) return;
    try {
        const response = await fetch(`/api/yuantong-report/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        const result = await response.json();
        if (response.ok) {
            alert('删除成功');
            loadYuantongHistoryData(1); // 刷新数据
        } else {
            alert('删除失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        alert('删除请求失败: ' + error.message);
    }
}

// 导出Excel功能，使用增强版导出功能（已注释，使用立即执行函数中的版本）
// async function exportToExcel() {
//             console.log('远通报表 exportToExcel 被调用');
    
//     try {
//         // 获取当前筛选条件
//         const filterForm = document.getElementById('filterForm');
//         const params = new URLSearchParams();
//         if (filterForm) {
//             const formData = new FormData(filterForm);
//             for (const [key, value] of formData.entries()) {
//                 if (value && key !== 'csrfmiddlewaretoken') {
//                     params.append(key, value);
//                 }
//             }
//         }
//         // 构建导出URL
//         const exportUrl = `/yuantong_report/export_excel/?${params.toString()}`;
//         console.log('构建的导出URL:', exportUrl);
        
//         // 检测环境
//         const userAgent = navigator.userAgent;
//         const isWxwork = /wxwork/i.test(userAgent);
//         const isNotMobile = !/mobile/i.test(userAgent);
//         const isPC = /windows|macintosh|linux/i.test(userAgent);
//         const isWeChatPC = isWxwork && isNotMobile && isPC;
        
//         console.log('环境检测结果:', {
//             userAgent: userAgent,
//             isWxwork: isWxwork,
//             isNotMobile: isNotMobile,
//             isPC: isPC,
//             isWeChatPC: isWeChatPC
//         });
        
//         // 使用增强版导出功能
//         if (typeof window.exportToExcel === 'function') {
//             console.log('使用增强版导出功能');
//             // 调用qc_report_common.js中的增强导出函数
//             window.exportToExcel(exportUrl, 'filterForm', 'export', '远通QC报表');
//         } else {
//             console.log('增强版导出功能不可用，使用回退方式');
            
//             // 如果是企业微信PC端，使用特殊处理
//             if (isWeChatPC) {
//                 console.log('企业微信PC端，使用特殊导出处理');
//                 performWeChatWorkExport(exportUrl, 'export', '远通QC报表');
//             } else {
//                 // 回退到原有方式
//                 performLegacyExport(exportUrl);
//             }
//         }
//     } catch (error) {
//         console.error('导出失败:', error);
//         showError('导出失败：' + error.message);
//     }
// }

// 原有的导出方式（作为回退）
function performLegacyExport(exportUrl) {
    // 检测是否为移动设备
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (isMobile) {
        showMobileDownloadLink(exportUrl);
    } else {
        const link = document.createElement('a');
        link.href = exportUrl;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showSuccess('Excel导出已开始，请稍候...');
    }
}
// 显示移动端下载链接
function showMobileDownloadLink(exportUrl) {
    const modalHTML = `
        <div id="downloadModal" style="position: fixed;top: 0;left: 0;width: 100%;height: 100%;background: rgba(0,0,0,0.5);display: flex;justify-content: center;align-items: center;z-index: 10000;">
            <div style="background: white;padding: 20px;border-radius: 8px;max-width: 90%;width: 400px;text-align: center;box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                <h3 style="margin-top: 0; color: #333;">Excel导出</h3>
                <p style="color: #666; margin: 15px 0;">点击下方链接下载Excel文件：</p>
                <a href="${exportUrl}" target="_blank" style="display: inline-block;background: #4CAF50;color: white;padding: 12px 24px;text-decoration: none;border-radius: 4px;margin: 10px 0;font-weight: bold;">📥 下载Excel文件</a>
                <div style="margin-top: 15px;"><button onclick="closeMobileDownloadModal()" style="background: #f5f5f5;border: 1px solid #ddd;padding: 8px 16px;border-radius: 4px;cursor: pointer;">关闭</button></div>
                <p style="font-size: 12px; color: #999; margin-top: 10px;">💡 提示：文件将下载到您的设备下载文件夹</p>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}
function closeMobileDownloadModal() {
    const modal = document.getElementById('downloadModal');
    if (modal) modal.remove();
}
function showSuccess(msg) {
    alert(msg);
}

// 企业微信PC端特殊导出处理
function performWeChatWorkExport(exportUrl, actionType = 'export', customFileName = '') {
    console.log('开始企业微信PC端特殊导出处理:', { exportUrl, actionType, customFileName });
    
    try {
        // 调用qc_report_common.js中的增强版企业微信导出功能
        if (typeof window.performWeChatWorkExport === 'function' && window.performWeChatWorkExport !== performWeChatWorkExport) {
            console.log('使用qc_report_common.js中的增强版企业微信导出功能');
            window.performWeChatWorkExport(exportUrl, actionType, customFileName);
        } else {
            console.log('使用本地企业微信导出功能');
            // 显示企业微信专用提示
            showWeChatWorkExportPrompt(exportUrl);
            
            // 延迟执行实际导出
            setTimeout(() => {
                console.log('执行企业微信导出...');
                performWeChatWorkActualExport(exportUrl);
            }, 1000);
        }
        
    } catch (error) {
        console.error('企业微信导出处理失败:', error);
        // 回退到简单导出
        performSimpleExportForWeChat(exportUrl, customFileName);
    }
}

// 显示企业微信导出提示
function showWeChatWorkExportPrompt(exportUrl) {
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
                        <li>导出类型：远通QC报表Excel</li>
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
    window.wechatExportInfo = { exportUrl };
}

// 关闭企业微信导出提示
function closeWeChatExportModal() {
    const modal = document.getElementById('wechatExportModal');
    if (modal) modal.remove();
}

// 开始企业微信导出
function startWeChatWorkExport() {
    if (window.wechatExportInfo) {
        const { exportUrl } = window.wechatExportInfo;
        closeWeChatExportModal();
        performWeChatWorkActualExport(exportUrl);
    }
}

// 执行企业微信实际导出
function performWeChatWorkActualExport(exportUrl) {
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
                link.download = '远通QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx';
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
                performSimpleExportForWeChat(exportUrl);
            });
            
    } catch (error) {
        console.error('企业微信导出失败:', error);
        // 回退到简单导出
        performSimpleExportForWeChat(exportUrl);
    }
}

// 企业微信简单导出（回退）
function performSimpleExportForWeChat(exportUrl) {
    console.log('使用企业微信简单导出方式');
    
    try {
        const fileName = '远通QC报表_' + new Date().toISOString().split('T')[0] + '.xlsx';
        
        // 创建下载链接
        const link = document.createElement('a');
        link.href = exportUrl;
        link.style.display = 'none';
        link.download = fileName;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('企业微信简单导出完成');
        
        // 显示成功提示
        showWeChatWorkExportSuccess();
        
    } catch (error) {
        console.error('企业微信简单导出失败:', error);
        showError('导出失败，请重试');
    }
}

// 显示企业微信导出成功提示
function showWeChatWorkExportSuccess() {
    const modalHTML = `
        <div id="wechatSuccessModal" style="
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
                    ✅
                </div>
                
                <h3 style="
                    margin: 0 0 20px 0;
                    color: #333;
                    font-size: 20px;
                    font-weight: 600;
                ">导出成功！</h3>
                
                <div style="
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                    color: #2e7d32;
                ">
                    <p style="margin: 0 0 15px 0;"><strong>📄 导出信息：</strong></p>
                    <ul style="margin: 0 0 15px 0; padding-left: 20px;">
                        <li>文件类型：远通QC报表Excel</li>
                        <li>导出时间：${new Date().toLocaleString('zh-CN')}</li>
                        <li>下载状态：文件已开始下载</li>
                    </ul>
                    
                    <p style="margin: 0;"><strong>💾 保存位置：</strong>企业微信下载目录或系统默认下载文件夹</p>
                </div>
                
                <button onclick="closeWeChatSuccessModal()" style="
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
                    💡 提示：文件已开始下载，请检查您的下载文件夹或企业微信下载记录。
                </p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 关闭企业微信成功提示
function closeWeChatSuccessModal() {
    const modal = document.getElementById('wechatSuccessModal');
    if (modal) modal.remove();
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
            locale: 'zh',

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

// 获取当前时间最近的5分钟倍数（如14:03->14:05, 14:07->14:05, 14:12->14:10）
function getNearest5MinuteTime() {
    // 确保使用本地时间，而不是UTC时间
    const now = new Date();
    
    // 获取本地时间的分钟数
    const localMinutes = now.getMinutes();
    const localHours = now.getHours();
    
    // 计算最近的5分钟倍数
    const nearest = Math.round(localMinutes / 5) * 5;
    
    // 创建新的时间对象，使用本地时间
    const nearestTime = new Date();
    nearestTime.setHours(localHours);
    nearestTime.setMinutes(nearest);
    nearestTime.setSeconds(0);
    nearestTime.setMilliseconds(0);
    
    console.log('时间选择器 - 当前时间:', now.toLocaleString('zh-CN'));
    console.log('时间选择器 - 最近5分钟倍数:', nearestTime.toLocaleString('zh-CN'));
    
    return nearestTime;
}

function resetFilters() {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) return;
    // 重置所有input
    filterForm.reset();
    // 清空flatpickr日期/时间
    ['startDate','endDate','startTime','endTime'].forEach(id => {
        const el = document.getElementById(id);
        if (el && el._flatpickr) {
            el._flatpickr.clear();
        } else if (el) {
            el.value = '';
        }
    });
    // 立即刷新数据
    loadYuantongHistoryData(1);
}

function editYuantongRecord(id) {
    window.location.href = `/yuantong-report-edit/${id}/`;
}

async function deleteYuantongRecord(id) {
    if (!confirm('确定要删除这条记录吗？此操作不可恢复。')) return;
    const apiUrl = `/api/yuantong-report/${id}/`;
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
            loadYuantongHistoryData(1);
        } else {
            alert('删除失败，状态码：' + response.status);
        }
    } catch (error) {
        alert('删除异常：' + error.message);
    }
}// 昨日产量统计功能
async function calculateYesterdayProduction() {
    try {
        // 显示加载提示
        const loadingMsg = '正在统计昨日产量数据...';
        console.log(loadingMsg);

        // 调用API获取昨日产量统计
        const response = await fetch('/api/yuantong-report/?action=yesterday_production', {
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

// 显示昨日产量统计结果
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
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: 600; color: #1976d2;">${tons.toFixed(3)}</td>
            </tr>
        `;
    });

    // 添加总计行
    html += `
                        <tr style="background: #e3f2fd; font-weight: 600;">
                            <td colspan="4" style="padding: 12px; border: 1px solid #ddd; text-align: center;">总计</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #1976d2; font-size: 16px;">${totalTons.toFixed(2)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="closeProductionModal()" style="padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">
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

// 关闭产量统计模态框
function closeProductionModal() {
    const modal = document.getElementById('productionModal');
    if (modal) {
        modal.remove();
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
                report_type: 'yuantong',
                operation_type: 'VIEW',
                operation_detail: '查看远通QC报表历史记录',
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
