// 定义统一的注意事项数组（添加在文件开头）
const noticeItems = [
    "请认真阅读和填写申请表并本人手写签名",
    "所有复印件为A4纸规格且清晰可辨",
    "如持有有效期的日签，需要先消签再办理",
    "领馆可能会要求提供补充材料"
];

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成');
    
    // 填充注意事项列表
    populateNoticeItems();
    
    // 添加禁用选项的CSS样式
    const style = document.createElement('style');
    style.innerHTML = `
        .btn-outline-primary.option-card.disabled, label.disabled {
            opacity: 0.6;
            cursor: not-allowed;
            text-decoration: line-through;
        }
        
        /* 风险确认模态框样式 */
        .risk-confirmation-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1050;
            align-items: center;
            justify-content: center;
        }
        
        .risk-confirmation-content {
            background-color: white;
            border-radius: 8px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
        
        .risk-confirmation-header {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #e5e5e5;
        }
        
        .risk-confirmation-body {
            padding: 20px;
        }
        
        .risk-confirmation-footer {
            padding: 15px 20px;
            border-top: 1px solid #e5e5e5;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
    `;
    document.head.appendChild(style);
    
    // 创建风险确认模态框
    const riskModal = document.createElement('div');
    riskModal.className = 'risk-confirmation-modal';
    riskModal.id = 'riskConfirmationModal';
    riskModal.innerHTML = `
        <div class="risk-confirmation-content">
            <div class="risk-confirmation-header">
                <h5 class="mb-0"><i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>风险确认</h5>
            </div>
            <div class="risk-confirmation-body">
                <p>普通经济材料申请多次签证，如果从未访问过日本，建议申请单次签证。如继续申请多次签证，请确认以下选项：</p>
                <div class="mb-3">
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="riskOption1">
                        <label class="form-check-label" for="riskOption1">
                            去过欧洲申根国
                        </label>
                    </div>
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="riskOption2">
                        <label class="form-check-label" for="riskOption2">
                            去过美国、加拿大、澳洲、新西兰
                        </label>
                    </div>
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="riskOption3">
                        <label class="form-check-label" for="riskOption3">
                            年纳税大于1万
                        </label>
                    </div>
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="riskOption4">
                        <label class="form-check-label" for="riskOption4">
                            当前工作社保已经缴纳五年以上
                        </label>
                    </div>
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="riskOption5">
                        <label class="form-check-label" for="riskOption5">
                            领区内大城区户籍
                        </label>
                    </div>
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="riskOption6">
                        <label class="form-check-label" for="riskOption6">
                            四年全日制本科及以上学历
                        </label>
                    </div>
                </div>
                <div class="alert alert-warning small">
                    <i class="bi bi-info-circle-fill me-1"></i>请至少确认一项以继续申请多次签证。
                </div>
            </div>
            <div class="risk-confirmation-footer">
                <button type="button" class="btn btn-outline-secondary btn-sm" id="riskCancelBtn">改为申请单次签证</button>
                <button type="button" class="btn btn-primary btn-sm" id="riskConfirmBtn" disabled>确认并继续</button>
            </div>
        </div>
    `;
    document.body.appendChild(riskModal);
    
    // 获取DOM元素
    const visaForm = document.getElementById('visaForm');
    const submitBtn = document.getElementById('submitBtn');
    const submitSpinner = document.getElementById('submitSpinner');
    const formTab = document.getElementById('form-tab');
    const confirmTab = document.getElementById('confirm-tab');
    const resultTab = document.getElementById('result-tab');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultContent = document.getElementById('resultContent');
    const noResultContent = document.getElementById('noResultContent');
    const documentList = document.getElementById('documentList');
    const copyBtn = document.getElementById('copyBtn');
    const goToFormBtn = document.getElementById('goToFormBtn');
    const backToFormBtn = document.getElementById('backToFormBtn');
    const confirmAndGenerateBtn = document.getElementById('confirmAndGenerateBtn');
    
    // 获取领区选择器和警告元素
    const residenceConsulateRadios = document.querySelectorAll('input[name="residenceConsulate"]');
    const hukouConsulateRadios = document.querySelectorAll('input[name="hukouConsulate"]');
    const otherConsulateWarning = document.getElementById('otherConsulateWarning');
    
    // 获取申请类型相关元素
    const applicationType = document.getElementsByName('applicationType');
    const familyMembersSection = document.getElementById('familyMembersSection');
    const familyVisaSection = document.getElementById('familyVisaSection');
    const familyVisaInfoSection = document.getElementById('familyVisaInfoSection'); // 老版本，已弃用，但在代码中保留引用以避免错误
    const familyEconomicSection = document.getElementById('familyEconomicSection');
    const addFamilyMemberBtn = document.getElementById('addFamilyMemberBtn');
    
    // 获取办理方式相关元素
    const processType = document.getElementById('processType');
    const visaTypeSection = document.getElementById('visaTypeSection');
    const visaTypeRadios = document.querySelectorAll('input[name="visaType"]');
    const economicMaterialSection = document.getElementById('economicMaterialSection');
    const singleVisaOptions = document.getElementById('singleVisaOptions');
    const threeVisaOptions = document.getElementById('threeVisaOptions');
    const fiveVisaOptions = document.getElementById('fiveVisaOptions');
    const processTax = document.getElementById('processTax');
    const processStudent = document.getElementById('processStudent');
    const processNormal = document.getElementById('processNormal');
    const processSimplified = document.getElementById('processSimplified');
    
    // 获取办理方式模块的引用（使用更兼容的方式）
    let processTypeModule = null;
    const gearIcons = document.querySelectorAll('div.bg-light.rounded.p-3.mb-3 h5 i.bi-gear');
    if (gearIcons.length > 0) {
        let parentElement = gearIcons[0];
        // 向上查找直到找到有bg-light类的div元素
        while (parentElement && (!parentElement.classList || !parentElement.classList.contains('bg-light'))) {
            parentElement = parentElement.parentElement;
        }
        processTypeModule = parentElement;
    }
    
    // 获取表单元素
    const identityType = document.getElementById('identityType');
    const previousVisit = document.getElementById('previousVisit');
    const resultDiv = document.getElementById('result');
    const familyMembersContainer = document.getElementById('familyMembersContainer');
    const graduateStatus = document.getElementById('graduateStatus');
    const visaDuration = document.getElementById('visaDuration');
    
    // 检查DOM元素是否存在，并添加日志输出
    console.log('DOM元素检查完成');
    
    // 初始化表单状态
    resetFormState();
    
    // 检查身份类型相关限制
    checkIdentityTypeRestrictions();
    
    // 初始化办理方式选择
    handleProcessTypeChange();
    
    // Bootstrap标签页初始化
    if (window.bootstrap) {
        const tabElm = document.getElementById('mainTab');
        if (tabElm) {
            const tabList = tabElm.querySelectorAll('button[data-bs-toggle="tab"]');
            tabList.forEach(tabElement => {
                tabElement.addEventListener('shown.bs.tab', function (event) {
                    // 当切换到表单标签页时重置表单状态
                    if (event.target.id === 'form-tab') {
                        resetFormState();
                        checkIdentityTypeRestrictions();
                    }
                });
            });
        }
    }
    
    // 初始化表单验证
    if (visaForm) {
    initFormValidation();
    } else {
        console.error('找不到表单元素 #visaForm');
    }
    
    // 监听居住领区变化
    if (residenceConsulateRadios.length > 0) {
        residenceConsulateRadios.forEach(radio => {
            radio.addEventListener('change', function() {
        checkResidenceConsulate();
                
                // 如果选择了家庭申请，需要检查所有家庭成员的领区
                if (document.getElementById('typeFamily')?.checked) {
                    // 检查所有家庭成员的领区
                    const familyMemberConsulates = document.querySelectorAll('select[name^="familyMembers"][name$="[residenceConsulate]"]');
                    familyMemberConsulates.forEach(select => {
            validateMemberConsulate(select);
        });
                }
                
                // 领区变化时更新经济材料选项
                updateEconomicMaterialOptions();
                
                // 检查是否为上海领区且申请类型为绑签，是则显示签证持有人身份选项
                if (this.value === 'shanghai' && document.getElementById('typeBinding')?.checked) {
                    const familyHolderIdentitySection = document.getElementById('familyHolderIdentitySection');
                    if (familyHolderIdentitySection) {
                        familyHolderIdentitySection.classList.remove('d-none');
                        const familyHolderIdentity = document.getElementById('familyHolderIdentity');
                        if (familyHolderIdentity) {
                            familyHolderIdentity.required = true;
                        }
                    }
                } else {
                    const familyHolderIdentitySection = document.getElementById('familyHolderIdentitySection');
                    if (familyHolderIdentitySection) {
                        familyHolderIdentitySection.classList.add('d-none');
                        const familyHolderIdentity = document.getElementById('familyHolderIdentity');
                        if (familyHolderIdentity) {
                            familyHolderIdentity.required = false;
                        }
                    }
                }
                
                updateFormValidation();
            });
        });
    } else {
        console.warn('页面加载完成后无法执行初始居住领区检查，因为元素不存在');
    }
    
    // 监听身份类型变化
    const identityTypeRadios = document.getElementsByName('identityType');
    if (identityTypeRadios && identityTypeRadios.length > 0) {
        identityTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                checkIdentityTypeRestrictions();
                
                // 如果当前选择了特定大学生单次办理方式，更新大学生状态
                const processType = document.querySelector('input[name="processType"]:checked')?.value;
                if (processType === 'STUDENT') {
                    // 先完全重置大学生状态选项的禁用状态
                    const statusCurrentRadio = document.getElementById('statusCurrent');
                    const statusRecentRadio = document.getElementById('statusRecent');
                    const statusCurrentLabel = document.querySelector('label[for="statusCurrent"]');
                    const statusRecentLabel = document.querySelector('label[for="statusRecent"]');
                    
                    if (statusCurrentRadio) statusCurrentRadio.disabled = false;
                    if (statusRecentRadio) statusRecentRadio.disabled = false;
                    if (statusCurrentLabel) statusCurrentLabel.classList.remove('disabled');
                    if (statusRecentLabel) statusRecentLabel.classList.remove('disabled');
                    
                    // 然后再调用处理办理方式变化的函数来更新大学生状态选项的禁用状态
                    handleProcessTypeChange();
                }
            });
        });
    }
    
    // 监听申请类型变化
    if (applicationType && applicationType.length > 0) {
    applicationType.forEach(radio => {
        radio.addEventListener('change', function() {
                // 处理申请类型变更
                handleApplicationTypeChange();
                
                // 特殊处理：如果选择了绑签申请，且居住领区是上海，立即显示签证持有人身份选项
                if (this.value === 'BINDING') {
                    const isShanghai = document.querySelector('input[name="residenceConsulate"]:checked')?.value === 'shanghai';
                    if (isShanghai) {
                        const familyHolderIdentitySection = document.getElementById('familyHolderIdentitySection');
                        if (familyHolderIdentitySection) {
                            familyHolderIdentitySection.classList.remove('d-none');
                            const familyHolderIdentity = document.getElementById('familyHolderIdentity');
                            if (familyHolderIdentity) {
                                familyHolderIdentity.required = true;
                            }
                        }
                    }
                }
        });
    });
    } else {
        console.error('找不到申请类型元素');
    }
    
    // 监听签证类型变化
    if (visaTypeRadios && visaTypeRadios.length > 0) {
        visaTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
                console.log('签证类型变更为:', this.value);
                updateEconomicMaterialOptions();
            });
        });
    }
    
    // 监听办理方式变化
    const processTypeInputs = document.querySelectorAll('input[name="processType"]');
    processTypeInputs.forEach(radio => {
        radio.addEventListener('change', function() {
            handleProcessTypeChange();
            
            // 更新大学生状态选项的禁用视觉效果
            if (this.value === 'STUDENT') {
                const statusCurrentRadio = document.getElementById('statusCurrent');
                const statusRecentRadio = document.getElementById('statusRecent');
                const statusCurrentLabel = document.querySelector('label[for="statusCurrent"]');
                const statusRecentLabel = document.querySelector('label[for="statusRecent"]');
                
                // 清除之前的禁用样式
                if (statusCurrentLabel) statusCurrentLabel.classList.remove('disabled');
                if (statusRecentLabel) statusRecentLabel.classList.remove('disabled');
                
                // 根据申请人身份重新应用禁用样式
                const selectedIdentityType = document.querySelector('input[name="identityType"]:checked')?.value;
                if (selectedIdentityType === 'STUDENT') {
                    // 学生身份禁用毕业三年内选项
                    if (statusRecentLabel) statusRecentLabel.classList.add('disabled');
                } else {
                    // 非学生身份禁用在读学生选项
                    if (statusCurrentLabel) statusCurrentLabel.classList.add('disabled');
                }
            }
        });
    });
    
    // 检查居住领区，如果是"其他领区"则禁用提交按钮并显示警告
    function checkResidenceConsulate() {
        if (!residenceConsulateRadios || !submitBtn) {
            console.error('找不到居住领区选择元素或提交按钮');
            return;
        }
        
        const selectedConsulate = Array.from(residenceConsulateRadios).find(radio => radio.checked);
        if (selectedConsulate && selectedConsulate.value === 'other') {
            if (otherConsulateWarning) {
            otherConsulateWarning.classList.remove('d-none');
            }
            submitBtn.disabled = true;
        } else {
            if (otherConsulateWarning) {
            otherConsulateWarning.classList.add('d-none');
            }
            submitBtn.disabled = false;
        }
    }
    
    // 处理表单提交
    if (visaForm) {
        visaForm.addEventListener('submit', submitForm);
    }
    
    // 复制清单按钮事件处理
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            copyDocumentList();
        });
    } else {
        console.log('复制按钮不存在');
    }
    
    // 添加前往表单按钮的点击事件
    if (goToFormBtn) {
        goToFormBtn.addEventListener('click', function() {
            // 切换到表单标签页
            if (formTab) {
                formTab.click();
                // 重置表单状态
                resetFormState();
            }
        });
    } else {
        console.error('找不到前往表单按钮元素 #goToFormBtn');
    }
    
    // 添加家庭成员的处理函数
    let familyMemberCount = 0;
    if (addFamilyMemberBtn) {
    addFamilyMemberBtn.addEventListener('click', function() {
        const memberDiv = document.createElement('div');
        memberDiv.className = 'family-member border rounded p-3 mb-3';
            // 添加data-member-index属性来保存序号
            memberDiv.dataset.memberIndex = familyMemberCount + 1;
        memberDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">家庭成员 ${familyMemberCount + 1}</h6>
                <button type="button" class="btn btn-outline-danger btn-sm remove-member">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">居住地所在领区</label>
                    <select class="form-select" name="familyMembers[${familyMemberCount}][residenceConsulate]" required>
                        <option value="" selected disabled>请选择居住地所在领区</option>
                        <option value="beijing">北京领区</option>
                        <option value="shanghai">上海领区</option>
                        <option value="other">其他领区</option>
                    </select>
                    <div class="invalid-feedback">请选择居住地所在领区</div>
                    <div class="consulate-warning text-danger d-none">
                        家庭成员必须与主申请人居住在同一个领区
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">户籍所在地领区</label>
                    <select class="form-select" name="familyMembers[${familyMemberCount}][hukouConsulate]" required>
                        <option value="" selected disabled>请选择户籍所在地领区</option>
                        <option value="beijing">北京领区</option>
                        <option value="shanghai">上海领区</option>
                        <option value="other">其他领区</option>
                    </select>
                    <div class="invalid-feedback">请选择户籍所在地领区</div>
                </div>
                <div class="col-md-6">
                        <label class="form-label">申请人身份</label>
                    <select class="form-select" name="familyMembers[${familyMemberCount}][relation]" required>
                            <option value="" selected disabled>请选择申请人身份</option>
                            <option value="SPOUSE">主申请人的配偶</option>
                            <option value="PARENT">主申请人的父母</option>
                            <option value="CHILD">主申请人的子女</option>
                    </select>
                        <div class="invalid-feedback">请选择申请人身份</div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">身份类型</label>
                    <select class="form-select" name="familyMembers[${familyMemberCount}][identityType]" required>
                        <option value="" selected disabled>请选择身份类型</option>
                        <option value="EMPLOYED">在职人员</option>
                        <option value="STUDENT">学生</option>
                        <option value="RETIRED">退休人员</option>
                        <option value="FREELANCE">自由职业</option>
                        <option value="CHILD">学前儿童</option>
                    </select>
                    <div class="invalid-feedback">请选择身份类型</div>
                </div>
            </div>
        `;
        
        // 添加删除功能
        const removeBtn = memberDiv.querySelector('.remove-member');
            if (removeBtn) {
        removeBtn.addEventListener('click', function() {
            memberDiv.remove();
            updateFamilyMemberNumbers();
                    // 移除成员后重新检查所有家庭成员领区
                    checkAllFamilyMembersConsulates();
        });
            }
        
        // 添加居住领区验证
        const memberResidenceConsulate = memberDiv.querySelector('select[name^="familyMembers"][name$="[residenceConsulate]"]');
            if (memberResidenceConsulate) {
        memberResidenceConsulate.addEventListener('change', function() {
            validateMemberConsulate(this);
        });
        
                // 检查当前主申请人选择的领区，如果已选择则自动选择相同的领区
                const mainConsulateElem = document.querySelector('input[name="residenceConsulate"]:checked');
                if (mainConsulateElem) {
                    const mainConsulate = mainConsulateElem.value;
                    // 设置家庭成员的居住地领区与主申请人相同
                    for (let i = 0; i < memberResidenceConsulate.options.length; i++) {
                        if (memberResidenceConsulate.options[i].value === mainConsulate) {
                            memberResidenceConsulate.selectedIndex = i;
                            break;
                        }
                    }
                }
            }
            
            const familyMembersList = document.getElementById('familyMembersList');
            if (familyMembersList) {
                familyMembersList.appendChild(memberDiv);
        familyMemberCount++;
        updateFamilyMemberNumbers();
                
                // 添加新成员后验证其领区
                if (memberResidenceConsulate) {
                    validateMemberConsulate(memberResidenceConsulate);
                }
            } else {
                console.error('找不到家庭成员列表元素 #familyMembersList');
            }
        });
    } else {
        console.error('找不到添加家庭成员按钮 #addFamilyMemberBtn');
    }
    
    // 验证家庭成员居住领区
    function validateMemberConsulate(selectElement) {
        if (!selectElement) {
            console.error('居住领区选择元素不存在');
            return;
        }
        
        const memberDiv = selectElement.closest('.family-member');
        if (!memberDiv) {
            console.error('找不到家庭成员DIV元素');
            return;
        }
        
        const warningDiv = memberDiv.querySelector('.consulate-warning');
        if (!warningDiv) {
            console.error('找不到警告DIV元素');
            return;
        }
        
        const mainConsulateElem = document.querySelector('input[name="residenceConsulate"]:checked');
        if (!mainConsulateElem) {
            console.error('找不到主申请人居住领区元素');
            return;
        }
        
        const mainConsulate = mainConsulateElem.value;
        
        if (selectElement.value !== mainConsulate) {
            warningDiv.classList.remove('d-none');
            selectElement.setCustomValidity('家庭成员必须与主申请人居住在同一个领区');
            
            // 禁用提交按钮
            if (submitBtn) {
                submitBtn.disabled = true;
            }
        } else {
            warningDiv.classList.add('d-none');
            selectElement.setCustomValidity('');
            
            // 检查所有家庭成员的领区
            checkAllFamilyMembersConsulates();
        }
    }
    
    // 检查所有家庭成员的领区是否与主申请人一致
    function checkAllFamilyMembersConsulates() {
        const familyMemberConsulates = document.querySelectorAll('select[name^="familyMembers"][name$="[residenceConsulate]"]');
        const mainConsulateElem = document.querySelector('input[name="residenceConsulate"]:checked');
        
        if (!mainConsulateElem || familyMemberConsulates.length === 0) {
            // 如果没有主申请人领区或没有家庭成员，不影响提交按钮
            if (submitBtn && !otherConsulateSelected()) {
                submitBtn.disabled = false;
            }
            return;
        }
        
        const mainConsulate = mainConsulateElem.value;
        let allMatched = true;
        
        familyMemberConsulates.forEach(select => {
            if (select.value && select.value !== mainConsulate) {
                allMatched = false;
            }
        });
        
        // 根据检查结果设置提交按钮状态
        if (submitBtn) {
            // 只有当不是"其他领区"时才考虑启用按钮
            if (!otherConsulateSelected()) {
                submitBtn.disabled = !allMatched;
            }
        }
        
        return allMatched;
    }
    
    // 检查主申请人是否选择了"其他领区"
    function otherConsulateSelected() {
        const selectedConsulate = document.querySelector('input[name="residenceConsulate"]:checked');
        return selectedConsulate && selectedConsulate.value === 'other';
    }
    
    // 更新家庭成员编号
    function updateFamilyMemberNumbers() {
        const members = document.querySelectorAll('.family-member');
        if (!members || members.length === 0) {
            console.log('没有找到家庭成员元素');
            return;
        }
        
        members.forEach((member, index) => {
            const titleElement = member.querySelector('h6');
            if (titleElement) {
                const newIndex = index + 1;
                titleElement.textContent = `家庭成员 ${newIndex}`;
                member.dataset.memberIndex = newIndex;
            }
        });
    }
    
    // 初始化表单验证
    function initFormValidation() {
        'use strict';
        
        // 获取所有需要验证的表单
        const forms = document.querySelectorAll('.needs-validation');
        
        // 循环添加验证事件
        Array.from(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    }
    
    // 收集表单数据
    function collectFormData() {
        const formData = {};
        
        // 收集居住地领区
        const residenceConsulate = document.querySelector('input[name="residenceConsulate"]:checked')?.value;
        if (residenceConsulate) {
            formData.residenceConsulate = residenceConsulate;
        }
        
        // 收集户籍所在地领区
        const hukouConsulate = document.querySelector('input[name="hukouConsulate"]:checked')?.value;
        if (hukouConsulate) {
            formData.hukouConsulate = hukouConsulate;
        }
        
        // 收集申请人身份
        const identityType = document.querySelector('input[name="identityType"]:checked')?.value;
        if (identityType) {
            formData.identityType = identityType;
        }
        
        // 收集申请类型
        const applicationType = document.querySelector('input[name="applicationType"]:checked')?.value;
        if (applicationType) {
            formData.applicationType = applicationType;
            
            // 如果是家庭申请，收集家庭成员信息
            if (applicationType === 'FAMILY') {
                formData.familyMembers = collectFamilyMembersData();
            }
            
            // 如果是绑签申请，收集家属签证信息
            if (applicationType === 'BINDING') {
                const familyRelation = document.getElementById('familyRelation')?.value;
                const familyVisaType = document.getElementById('familyVisaType')?.value;
                
                if (familyRelation) {
                    formData.familyRelation = familyRelation;
                }
                
                if (familyVisaType) {
                    formData.familyVisaType = familyVisaType;
                    // 对于绑签申请，将家属签证类型也设置为申请人的签证类型
                    formData.visaType = familyVisaType;
                }
                
                // 如果是上海领区，收集签证持有人身份信息
                if (residenceConsulate === 'shanghai') {
                    const familyHolderIdentity = document.getElementById('familyHolderIdentity')?.value;
                    if (familyHolderIdentity) {
                        formData.familyHolderIdentity = familyHolderIdentity;
                    }
                }
            }
        }
        
        // 收集办理方式
        const processType = document.querySelector('input[name="processType"]:checked')?.value;
        if (processType) {
            formData.processType = processType;
        }
        
        // 收集大学生状态（仅当选择特定大学生单次办理时）
        if (processType === 'STUDENT') {
            const graduateStatus = document.querySelector('input[name="graduateStatus"]:checked')?.value;
            if (graduateStatus) {
                formData.graduateStatus = graduateStatus;
            }
        }
        
        // 收集签证类型（仅当不是绑签申请且选择税单办理或普通经济材料办理时）
        if (applicationType !== 'BINDING' && (processType === 'TAX' || processType === 'NORMAL')) {
            const visaType = document.querySelector('input[name="visaType"]:checked')?.value;
            if (visaType) {
                formData.visaType = visaType;
            }
            
            // 收集经济材料选项（仅当选择普通经济材料办理时）
            if (processType === 'NORMAL') {
                const economicMaterial = document.querySelector('input[name="economicMaterial"]:checked')?.value;
                if (economicMaterial) {
                    formData.economicMaterial = economicMaterial;
                }
            }
        }
        
        // 收集是否曾经访问日本
        const previousVisit = document.querySelector('input[name="previousVisit"]:checked')?.value;
        if (previousVisit) {
            formData.previousVisit = previousVisit;
        }
        
        return formData;
    }
    
    // 提交表单数据到服务器
    async function submitFormData(data) {
        try {
            const submitBtn = document.getElementById('submitBtn');
            const submitSpinner = document.getElementById('submitSpinner');
            
            if (submitBtn && submitSpinner) {
                submitBtn.disabled = true;
                submitSpinner.classList.remove('d-none');
            }
            
            console.log('提交表单数据:', data);
            
            const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                    'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
            });
            
            console.log('服务器响应状态码:', response.status);
            
            if (!response.ok) {
                throw new Error(`服务器响应错误: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('服务器响应数据:', result);
            
            // 检查是否有错误
            if (result.error) {
                throw new Error(result.error);
            }
            
            // 适应新的API返回格式，确保数据结构一致
            if (!result.document_list) {
                // 如果响应直接就是结果对象
                return {
                    status: 'success',
                    document_list: result,
                    ordered_sections: [
                        '基本信息', '基本材料', '学籍/学历证明', 
                        '学籍/学历证明及情况说明', '工作证明', '财力证明', 
                        '居住证明材料', '家属材料', '其他材料'
                    ]
                };
            }
            
            // 如果响应已经包含了完整结构
            return result;
        } catch (error) {
            console.error('提交表单数据时出错:', error);
            throw error;
        } finally {
            const submitBtn = document.getElementById('submitBtn');
            const submitSpinner = document.getElementById('submitSpinner');
            
            if (submitBtn && submitSpinner) {
                submitBtn.disabled = false;
                submitSpinner.classList.add('d-none');
            }
        }
    }
    
    // 渲染材料清单
    function displayDocumentList(documentList) {
        const listContainer = document.getElementById('documentList');
        const resultContent = document.getElementById('resultContent');
        const noResultContent = document.getElementById('noResultContent');
        
        if (!listContainer || !resultContent || !noResultContent) {
            console.error('找不到必要的DOM元素');
            return;
        }
        
        // 清空现有内容
        listContainer.innerHTML = '';
        
        // 获取申请类型和签证类型的文本
        const applicationType = getApplicationTypeText(document.querySelector('input[name="applicationType"]:checked')?.value);
        const applicationTypeValue = document.querySelector('input[name="applicationType"]:checked')?.value;
        let visaTypeText = '';
        const selectedVisaType = document.querySelector('input[name="visaType"]:checked')?.value;
        const selectedProcessType = document.querySelector('input[name="processType"]:checked')?.value;
        
        // 检查是否有后端返回的基本信息数据
        if (documentList['基本信息'] && documentList['基本信息'].length > 0) {
            // 创建申请信息摘要 - 使用后端返回的数据
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'alert alert-info mb-3';
            summaryDiv.innerHTML = `<h6 class="alert-heading mb-2">申请信息摘要</h6>`;
            
            // 添加每一项基本信息
            documentList['基本信息'].forEach(item => {
                const pElem = document.createElement('p');
                pElem.className = item === documentList['基本信息'][documentList['基本信息'].length - 1] ? 'mb-0' : 'mb-1';
                pElem.innerHTML = item;
                summaryDiv.appendChild(pElem);
            });
            
            listContainer.appendChild(summaryDiv);
        } else {
            // 后备方案：如果后端没有返回基本信息，使用前端生成的信息
            // 处理签证类型文本
            if (['TAX', 'NORMAL', 'SIMPLIFIED'].includes(selectedProcessType)) {
                switch(selectedVisaType) {
                    case 'SINGLE': visaTypeText = '单次签证'; break;
                    case 'THREE': visaTypeText = '三年多次签证'; break;
                    case 'FIVE': visaTypeText = '五年多次签证'; break;
                    default: visaTypeText = '单次签证';
                }
            } else if (selectedProcessType === 'STUDENT') {
                visaTypeText = '单次签证（学生专用）';
            }
            
            // 对于绑签申请，使用家属签证类型
            if (applicationTypeValue === 'BINDING') {
                const familyVisaType = document.getElementById('familyVisaType')?.value;
                visaTypeText = familyVisaType === 'THREE' ? '三年多次往返签证' : '五年多次往返签证';
            }
            
            // 创建申请信息摘要
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'alert alert-info mb-3';
            summaryDiv.innerHTML = `
                <h6 class="alert-heading mb-2">申请信息摘要</h6>
                <p class="mb-1">居住地领区: ${getConsulateText(document.querySelector('input[name="residenceConsulate"]:checked')?.value)}</p>
                <p class="mb-1">户籍所在地领区: ${getConsulateText(document.querySelector('input[name="hukouConsulate"]:checked')?.value)}</p>
                <p class="mb-1">申请类型: ${applicationType}</p>
                <p class="mb-0">签证类型: ${visaTypeText}</p>
            `;
            listContainer.appendChild(summaryDiv);
        }
        
        // 定义材料分类的显示顺序
        const categoryOrder = [
            '基本材料',
            '财力证明',
            '家属材料',
            '居住证明材料',
            '其他材料'
        ];
        
        // 按照指定顺序显示材料分类
        categoryOrder.forEach(category => {
            if (documentList[category] && documentList[category].length > 0) {
                // 创建分类标题
                const categoryTitle = document.createElement('div');
                categoryTitle.className = 'mb-3';
                categoryTitle.innerHTML = `<h5 class="mb-2"><i class="bi bi-folder me-2"></i>${category}</h5>`;
                
                // 创建材料列表
                const materialsList = document.createElement('div');
                materialsList.className = 'ms-4';
                
                // 处理每个材料项
                let currentIndex = 1;
                
                if (category === '居住证明材料') {
                    // 处理居住证明材料的特殊结构
                    let familyMemberMap = new Map();
                    let materialItems = [];
                    let isShanghai = false;
                    
                    // 记录日志，查看所有居住证明材料项
                    console.log('所有居住证明材料项:', documentList[category]);
                    
                    // 直接使用后端返回的第一行作为标题，不进行自己的解析
                    const titleItem = documentList[category][0];
                    const materialItem = document.createElement('div');
                    materialItem.className = 'alert alert-light border mb-3';
                    materialItem.innerHTML = titleItem;
                    materialsList.appendChild(materialItem);
                    
                    // 处理剩余的居住证明材料项（跳过第一行标题）
                    for (let i = 1; i < documentList[category].length; i++) {
                        const item = documentList[category][i];
                        const materialItem = document.createElement('div');
                        materialItem.className = 'mb-2 ps-3 border-start border-primary';
                        materialItem.innerHTML = item;
                        materialsList.appendChild(materialItem);
                    }
                } else if (category === '家属材料') {
                    // 特殊处理家属材料，直接显示后端返回的内容
                    console.log('家属材料项:', documentList[category]);
                    
                    // 直接显示所有家属材料项
                    documentList[category].forEach(item => {
                        const materialItem = document.createElement('div');
                        materialItem.className = 'mb-2 ps-3 border-start border-primary';
                        materialItem.innerHTML = item;
                        materialsList.appendChild(materialItem);
                    });
                } else {
                    // 其他材料类别的处理逻辑保持不变
                    documentList[category].forEach(item => {
                        const materialItem = document.createElement('div');
                        materialItem.className = 'mb-2 ps-3 border-start border-primary';
                        
                        // 检查是否是带序号的项目
                        if (/^\d+\.\s/.test(item)) {
                            materialItem.innerHTML = item;
                        } else {
                            materialItem.innerHTML = `${currentIndex}. ${item}`;
                            currentIndex++;
                        }
                        
                        materialsList.appendChild(materialItem);
                    });
                }
                
                listContainer.appendChild(categoryTitle);
                listContainer.appendChild(materialsList);
            }
        });
        
        // 显示结果内容，隐藏无结果提示
        resultContent.classList.remove('d-none');
        noResultContent.classList.add('d-none');
    }
    
    // 获取选择框的已选文本
    function getSelectedOptionText(radios) {
        if (!radios || radios.length === 0) return '未指定';
        
        const selectedRadio = Array.from(radios).find(radio => radio.checked);
        if (!selectedRadio) return '未指定';
        
        const label = selectedRadio.nextElementSibling;
        if (!label) return '未指定';
        
        const titleElement = label.querySelector('.option-title');
        return titleElement ? titleElement.textContent.trim() : '未指定';
    }
    
    // 切换到结果页面
    function switchToResultTab() {
        if (window.bootstrap) {
            const resultTabElement = document.getElementById('result-tab');
            if (resultTabElement) {
                const tab = new bootstrap.Tab(resultTabElement);
                tab.show();
            }
        } else {
            // 如果bootstrap不可用，使用简单的方式切换标签页
            const formContent = document.getElementById('form-content');
            const confirmContent = document.getElementById('confirm-content');
            const resultContent = document.getElementById('result-content');
            
            if (formContent) formContent.classList.remove('show', 'active');
            if (confirmContent) confirmContent.classList.remove('show', 'active');
            if (resultContent) {
                resultContent.classList.add('show', 'active');
                resultTab.classList.add('active');
                formTab.classList.remove('active');
                confirmTab.classList.remove('active');
            }
        }
    }
    
    // 显示或隐藏加载状态
    function showLoading(isLoading) {
        if (!submitBtn || !submitSpinner || !loadingIndicator || !resultContent || !noResultContent) {
            console.error('加载状态相关元素不存在');
            return;
        }
        
        if (isLoading) {
            submitBtn.disabled = true;
            submitSpinner.classList.remove('d-none');
            loadingIndicator.classList.remove('d-none');
            resultContent.classList.add('d-none');
            noResultContent.classList.add('d-none');
        } else {
            // 恢复提交按钮状态，仅当居住领区是"其他领区"时才禁用
            submitBtn.disabled = (residenceConsulateRadios.length > 0 && residenceConsulateRadios[0].checked && residenceConsulateRadios[0].value === 'other');
            submitSpinner.classList.add('d-none');
            loadingIndicator.classList.add('d-none');
        }
    }
    
    // 重置表单状态
    function resetFormState() {
        // 重置所有radio按钮
        if (residenceConsulateRadios) {
            residenceConsulateRadios.forEach(radio => {
                radio.checked = false;
            });
        }
        
        if (hukouConsulateRadios) {
            hukouConsulateRadios.forEach(radio => {
                radio.checked = false;
            });
        }
        
        // 移除表单验证样式
        if (visaForm) {
            visaForm.classList.remove('was-validated');
        }
        
        // 检查申请类型和居住领区，确保签证持有人身份选项在需要时显示
        const selectedApplicationType = document.querySelector('input[name="applicationType"]:checked')?.value;
        const selectedResidenceConsulate = document.querySelector('input[name="residenceConsulate"]:checked')?.value;
        
        // 如果是绑签申请且选择了上海领区，显示签证持有人身份选项
        if (selectedApplicationType === 'BINDING' && selectedResidenceConsulate === 'shanghai') {
            const familyHolderIdentitySection = document.getElementById('familyHolderIdentitySection');
            if (familyHolderIdentitySection) {
                familyHolderIdentitySection.classList.remove('d-none');
                const familyHolderIdentity = document.getElementById('familyHolderIdentity');
                if (familyHolderIdentity) {
                    familyHolderIdentity.required = true;
                }
            }
        }

        // 调用handleProcessTypeChange处理办理方式变更
        handleProcessTypeChange();
        
        // 调用handleApplicationTypeChange处理申请类型变更
        handleApplicationTypeChange();
    }
    
    // 显示无结果状态
    function showNoResult() {
        if (!resultContent || !noResultContent || !loadingIndicator) {
            console.error('结果显示相关元素不存在');
            return;
        }
        
        resultContent.classList.add('d-none');
        noResultContent.classList.remove('d-none');
        loadingIndicator.classList.add('d-none');
    }
    
    // 显示错误消息
    function showError(message, alertId) {
        console.error('错误:', message);
        
        // 如果指定了警告元素ID，尝试在页面中显示
        if (alertId) {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.textContent = message;
                alertElement.classList.remove('d-none');
                
                // 5秒后自动隐藏
                setTimeout(() => {
                    alertElement.classList.add('d-none');
                }, 5000);
                return;
            }
        }
        
        // 如果没有指定警告元素或找不到元素，使用alert
        alert('错误: ' + message);
    }
    
    // 复制材料清单
    function copyDocumentList() {
        const documentList = document.getElementById('documentList');
        if (!documentList) {
            showError('找不到材料清单元素');
            return;
        }
        
        let copyText = '日本签证申请材料清单\n\n';
        
        // 复制申请信息摘要
        const summaryDiv = documentList.querySelector('.alert');
        if (summaryDiv) {
            const summaryItems = summaryDiv.querySelectorAll('p');
            summaryItems.forEach(item => {
                copyText += `${item.textContent}\n`;
            });
            copyText += '\n';
        }
        
        // 遍历所有材料分类
        const categories = documentList.querySelectorAll('h5');
        
        if (categories && categories.length > 0) {
            categories.forEach(categoryTitle => {
                // 获取分类标题
                const title = categoryTitle.textContent.trim();
            copyText += `${title}\n`;
            
                // 获取该分类下的所有材料项
                const categoryDiv = categoryTitle.parentElement;
                const materialsList = categoryDiv.nextElementSibling;
                
                if (materialsList) {
                    const materials = materialsList.querySelectorAll('div');
                    
                    if (materials && materials.length > 0) {
                        materials.forEach(material => {
                            const materialText = material.textContent.trim();
                            if (materialText) {
                                copyText += `${materialText}\n`;
                            }
                        });
                    }
                }
                
            copyText += '\n';
        });
        }
        
        // 添加注意事项
        copyText += '注意事项:\n';
        noticeItems.forEach((item, index) => {
            copyText += `${index + 1}. ${item}\n`;
        });
        
        try {
            // 使用现代clipboard API
            navigator.clipboard.writeText(copyText).then(() => {
                const copyBtnMain = document.getElementById('copyBtn');
                if (copyBtnMain) {
                    copyBtnMain.innerHTML = '<i class="bi bi-check"></i> 已复制';
                    copyBtnMain.classList.add('btn-success');
                    copyBtnMain.classList.remove('btn-outline-primary');
                
                    setTimeout(() => {
                        copyBtnMain.innerHTML = '<i class="bi bi-clipboard"></i> 复制清单';
                        copyBtnMain.classList.remove('btn-success');
                        copyBtnMain.classList.add('btn-outline-primary');
                    }, 2000);
                }
            }).catch(err => {
                console.error('复制失败(clipboard API):', err);
                fallbackCopy(copyText);
            });
        } catch (err) {
            console.error('复制过程中出错:', err);
            fallbackCopy(copyText);
        }
    }
    
    // 后备复制方法
    function fallbackCopy(text) {
        try {
            // 创建临时文本区域
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            // 尝试执行复制命令
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (successful) {
                const copyBtnElem = document.getElementById('copyBtn');
                if (copyBtnElem) {
                    copyBtnElem.innerHTML = '<i class="bi bi-check"></i> 已复制';
                    copyBtnElem.classList.add('btn-success');
                    copyBtnElem.classList.remove('btn-outline-primary');
                
                    setTimeout(() => {
                        copyBtnElem.innerHTML = '<i class="bi bi-clipboard"></i> 复制清单';
                        copyBtnElem.classList.remove('btn-success');
                        copyBtnElem.classList.add('btn-outline-primary');
                    }, 2000);
                }
            } else {
                showError('无法复制到剪贴板，请手动复制');
            }
        } catch (err) {
            console.error('后备复制方法失败:', err);
            showError('复制失败，请手动复制');
        }
    }
    
    // 检查身份类型相关限制的函数
    function checkIdentityTypeRestrictions() {
        // 获取当前选中的身份类型
        const selectedIdentityType = document.querySelector('input[name="identityType"]:checked');
        
        if (selectedIdentityType) {
            // 获取申请类型选项
            const singleApplicationRadio = document.getElementById('typeSingle');
            const familyApplicationRadio = document.getElementById('typeFamily');
            const bindingApplicationRadio = document.getElementById('typeBinding');
            const economicApplicationRadio = document.getElementById('typeEconomic');
            const taxProcessRadio = document.getElementById('processTax');
            const studentProcessRadio = document.getElementById('processStudent');
            
            // 检查身份类型是否为在校学生或学龄前儿童
            const isStudentOrChild = (selectedIdentityType.value === 'STUDENT' || selectedIdentityType.value === 'CHILD');
            // 检查身份类型是否为退休人员或学龄前儿童
            const isRetiredOrChild = (selectedIdentityType.value === 'RETIRED' || selectedIdentityType.value === 'CHILD');
            // 检查是否仅为学龄前儿童
            const isOnlyChild = (selectedIdentityType.value === 'CHILD');
            
            // 针对在校学生和学龄前儿童的限制
            if (isStudentOrChild) {
                // 禁用家庭申请选项
                if (familyApplicationRadio) {
                    familyApplicationRadio.disabled = true;
                    
                    // 如果当前选择了家庭申请，切换到单人申请
                    if (familyApplicationRadio.checked) {
                        const singleApplicationRadio = document.getElementById('typeSingle');
                        if (singleApplicationRadio) {
                            singleApplicationRadio.checked = true;
                            // 触发change事件以更新相关UI
                            singleApplicationRadio.dispatchEvent(new Event('change'));
                        }
                    }
                }
                
                // 禁用税单办理方式
                if (taxProcessRadio) {
                    taxProcessRadio.disabled = true;
                    
                    // 如果当前选择了税单办理，切换到其他可用选项
                    if (taxProcessRadio.checked) {
                        // 对于学生，切换到特定大学生单次选项
                        if (selectedIdentityType.value === 'STUDENT') {
                            const studentProcessRadio = document.getElementById('processStudent');
                            if (studentProcessRadio) {
                                studentProcessRadio.checked = true;
                                studentProcessRadio.dispatchEvent(new Event('change'));
                            }
                        }
                        // 对于学龄前儿童，切换到普通经济材料办理
                        else {
                            const normalProcessRadio = document.getElementById('processNormal');
                            if (normalProcessRadio) {
                                normalProcessRadio.checked = true;
                                normalProcessRadio.dispatchEvent(new Event('change'));
                            }
                        }
                    }
                }
            } else {
                // 对于其他身份类型，启用所有选项
                if (familyApplicationRadio) {
                    familyApplicationRadio.disabled = false;
                }
                
                if (taxProcessRadio) {
                    taxProcessRadio.disabled = false;
                }
            }
            
            // 学龄前儿童特殊限制：禁用单人申请选项
            if (isOnlyChild) {
                if (singleApplicationRadio) {
                    singleApplicationRadio.disabled = true;
                    
                    // 如果当前选择了单人申请，切换到作为签证持有人的家属办理
                    if (singleApplicationRadio.checked && bindingApplicationRadio) {
                        bindingApplicationRadio.checked = true;
                        // 触发change事件以更新相关UI
                        bindingApplicationRadio.dispatchEvent(new Event('change'));
                    }
                    
                    // 添加视觉反馈
                    const singleLabel = document.querySelector(`label[for="${singleApplicationRadio.id}"]`);
                    if (singleLabel) {
                        singleLabel.classList.add('disabled');
                        singleLabel.title = '学龄前儿童不能选择单人申请';
                    }
                }
                
                // 确保作为签证持有人的家属办理和使用家庭成员的经济材料可用
                if (bindingApplicationRadio) {
                    bindingApplicationRadio.disabled = false;
                    const bindingLabel = document.querySelector(`label[for="${bindingApplicationRadio.id}"]`);
                    if (bindingLabel) {
                        bindingLabel.classList.remove('disabled');
                        bindingLabel.title = '';
                    }
                }
                
                if (economicApplicationRadio) {
                    economicApplicationRadio.disabled = false;
                    const economicLabel = document.querySelector(`label[for="${economicApplicationRadio.id}"]`);
                    if (economicLabel) {
                        economicLabel.classList.remove('disabled');
                        economicLabel.title = '';
                    }
                }
            } else {
                // 非学龄前儿童，启用单人申请选项
                if (singleApplicationRadio) {
                    singleApplicationRadio.disabled = false;
                    
                    // 移除视觉反馈
                    const singleLabel = document.querySelector(`label[for="${singleApplicationRadio.id}"]`);
                    if (singleLabel) {
                        singleLabel.classList.remove('disabled');
                        singleLabel.title = '';
                    }
                }
            }
            
            // 针对退休人员和学龄前儿童禁用特定大学生单次办理方式
            if (isRetiredOrChild) {
                if (studentProcessRadio) {
                    studentProcessRadio.disabled = true;
                    
                    // 如果当前选择了特定大学生单次，切换到普通经济材料办理
                    if (studentProcessRadio.checked) {
                        const normalProcessRadio = document.getElementById('processNormal');
                        if (normalProcessRadio) {
                            normalProcessRadio.checked = true;
                            normalProcessRadio.dispatchEvent(new Event('change'));
                        }
                    }
                }
            } else {
                // 对于其他身份类型，启用特定大学生单次选项
                if (studentProcessRadio && selectedIdentityType.value !== 'STUDENT') {
                    studentProcessRadio.disabled = false;
                }
            }
        }
    }
    
    // 页面加载完成后检查一次居住领区
    if (residenceConsulateRadios.length > 0) {
    checkResidenceConsulate();
    } else {
        console.warn('页面加载完成后无法执行初始居住领区检查，因为元素不存在');
    }

    // 处理办理方式变化
    function handleProcessTypeChange() {
        const selectedProcessType = document.querySelector('input[name="processType"]:checked')?.value;
        const selectedApplicationType = document.querySelector('input[name="applicationType"]:checked')?.value;
        const selectedIdentityType = document.querySelector('input[name="identityType"]:checked')?.value;
        
        // 获取DOM元素
        const graduateStatusSection = document.getElementById('graduateStatusSection');
        const visaTypeSection = document.getElementById('visaTypeSection');
        const economicMaterialSection = document.getElementById('economicMaterialSection');
        
        // 隐藏所有选项区域
        if (graduateStatusSection) graduateStatusSection.classList.add('d-none');
        if (visaTypeSection) visaTypeSection.classList.add('d-none');
        if (economicMaterialSection) economicMaterialSection.classList.add('d-none');
        
        // 处理"是否曾经访问日本"选项
        const previousVisitNoRadio = document.getElementById('previousVisitNo');
        const previousVisitYesRadio = document.getElementById('previousVisitYes');
        
        // 重置"是否曾经访问日本"选项状态
        if (previousVisitNoRadio) {
            previousVisitNoRadio.disabled = false;
            const noLabel = document.querySelector(`label[for="${previousVisitNoRadio.id}"]`);
            if (noLabel) {
                noLabel.classList.remove('disabled');
                noLabel.title = '';
            }
        }
        
        // 如果办理方式为新政简化三年，禁用"否"选项，因为新政简化三年必须曾经访问过日本
        if (selectedProcessType === 'SIMPLIFIED') {
            if (previousVisitNoRadio) {
                previousVisitNoRadio.disabled = true;
                const noLabel = document.querySelector(`label[for="${previousVisitNoRadio.id}"]`);
                if (noLabel) {
                    noLabel.classList.add('disabled');
                    noLabel.title = '新政简化三年办理必须曾经访问过日本';
                }
                
                // 如果当前选择了"否"，自动切换到"是"
                if (previousVisitNoRadio.checked && previousVisitYesRadio) {
                    previousVisitYesRadio.checked = true;
                }
            }
        }
        
        // 如果是绑签申请，不显示签证类型区域
        if (selectedApplicationType === 'BINDING') {
            return;
        }
        
        // 根据选择的办理方式显示相应区域
        if (selectedProcessType === 'STUDENT') {
            // 特定大学生单次：显示大学生状态选项
            if (graduateStatusSection) {
                graduateStatusSection.classList.remove('d-none');
                const graduateStatusInputs = document.querySelectorAll('input[name="graduateStatus"]');
                graduateStatusInputs.forEach(input => input.required = true);
                
                // 根据申请人身份控制大学生状态选项
                const statusCurrentRadio = document.getElementById('statusCurrent');
                const statusRecentRadio = document.getElementById('statusRecent');
                
                if (statusCurrentRadio && statusRecentRadio) {
                    if (selectedIdentityType === 'STUDENT') {
                        // 学生身份时：禁用毕业三年内选项
                        statusRecentRadio.disabled = true;
                        statusCurrentRadio.disabled = false;
                        
                        // 如果已选择了毕业三年内，则自动切换到在读学生
                        if (statusRecentRadio.checked) {
                            statusCurrentRadio.checked = true;
                        }
                        
                        // 给禁用的选项添加视觉反馈
                        const statusRecentLabel = document.querySelector('label[for="statusRecent"]');
                        if (statusRecentLabel) {
                            statusRecentLabel.classList.add('disabled');
                            statusRecentLabel.title = '学生身份不能选择毕业三年内选项';
                        }
                    } else {
                        // 非学生身份时：禁用在读学生选项
                        statusCurrentRadio.disabled = true;
                        statusRecentRadio.disabled = false;
                        
                        // 如果已选择了在读学生，则自动切换到毕业三年内
                        if (statusCurrentRadio.checked) {
                            statusRecentRadio.checked = true;
                        }
                        
                        // 给禁用的选项添加视觉反馈
                        const statusCurrentLabel = document.querySelector('label[for="statusCurrent"]');
                        if (statusCurrentLabel) {
                            statusCurrentLabel.classList.add('disabled');
                            statusCurrentLabel.title = '非学生身份不能选择在读学生选项';
                        }
                    }
                }
            }
        } else if (selectedProcessType === 'TAX' || selectedProcessType === 'NORMAL') {
            // 税单办理或普通经济材料办理：显示签证类型选项
            if (visaTypeSection) {
                visaTypeSection.classList.remove('d-none');
                const visaTypeInputs = document.querySelectorAll('input[name="visaType"]');
                visaTypeInputs.forEach(input => input.required = true);
            }
            
            // 如果是普通经济材料办理，显示经济材料选项
            if (selectedProcessType === 'NORMAL') {
                if (economicMaterialSection) {
                    economicMaterialSection.classList.remove('d-none');
                }
            }
        }
        
        // 更新经济材料选项
        updateEconomicMaterialOptions();
    }

    function updateEconomicMaterialOptions() {
        // 获取所需的DOM元素
        const economicMaterialSection = document.getElementById('economicMaterialSection');
        // 北京领区选项
        const singleVisaOptions = document.getElementById('singleVisaOptions');
        const threeVisaOptions = document.getElementById('threeVisaOptions');
        const fiveVisaOptions = document.getElementById('fiveVisaOptions');
        // 上海领区选项
        const singleVisaOptionsSH = document.getElementById('singleVisaOptionsSH');
        const threeVisaOptionsSH = document.getElementById('threeVisaOptionsSH');
        const fiveVisaOptionsSH = document.getElementById('fiveVisaOptionsSH');
        
        // 获取所有选项组
        const allOptions = document.querySelectorAll('.option-group');
        const beijingOptions = document.querySelectorAll('.beijing-options');
        const shanghaiOptions = document.querySelectorAll('.shanghai-options');
        
        if (!economicMaterialSection) {
            console.log('经济材料选项元素不存在');
            return;
        }
        
        // 获取申请类型和办理方式
        const applicationType = document.querySelector('input[name="applicationType"]:checked')?.value;
        const processType = document.querySelector('input[name="processType"]:checked')?.value;
        
        // 检查是否在北京或上海领区且使用普通经济材料办理
        const selectedResidenceConsulate = document.querySelector('input[name="residenceConsulate"]:checked');
        const isBeijingConsulate = selectedResidenceConsulate && selectedResidenceConsulate.value === 'beijing';
        const isShanghaiConsulate = selectedResidenceConsulate && selectedResidenceConsulate.value === 'shanghai';
        const isValidConsulate = isBeijingConsulate || isShanghaiConsulate;
        
        const isNormalProcess = processType === 'NORMAL';
        
        // 是否为允许显示经济材料选项的申请类型（单人申请和家庭申请）
        const isAllowedApplicationType = applicationType === 'SINGLE' || applicationType === 'FAMILY';
        
        console.log('updateEconomicMaterialOptions - 领区:', selectedResidenceConsulate?.value || '未选择', 
                    '办理方式:', processType || '未选择',
                    '申请类型:', applicationType || '未选择');
        
        // 如果不是普通经济材料办理，隐藏经济材料选项区域
        if (!isNormalProcess) {
            economicMaterialSection.classList.add('d-none');
            
            // 移除所有经济材料选项的必填属性
            document.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                radio.required = false;
            });
            
            console.log('经济材料选项已隐藏，原因: 非普通经济材料办理');
            return;
        }
        
        // 隐藏所有选项
        allOptions.forEach(option => option.classList.add('d-none'));
        
        if (isValidConsulate && isNormalProcess && isAllowedApplicationType) {
            const selectedVisaType = document.querySelector('input[name="visaType"]:checked');
            
            if (selectedVisaType) {
                console.log('当前选择的签证类型:', selectedVisaType.value);
                
                // 显示经济材料选项区域
                economicMaterialSection.classList.remove('d-none');
                
                // 清除之前选中的经济材料选项
                document.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                    radio.checked = false;
                    radio.required = false;
                });
                
                // 根据领区和签证类型显示对应选项
                if (isBeijingConsulate) {
                    console.log('显示北京领区经济材料选项');
                    
                    // 隐藏上海领区选项
                    shanghaiOptions.forEach(option => option.classList.add('d-none'));
                    
                    // 根据签证类型显示北京领区的选项
                    switch(selectedVisaType.value) {
                        case 'SINGLE':
                            singleVisaOptions.classList.remove('d-none');
                            // 设置单次签证经济材料选项为必填
                            singleVisaOptions.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                                radio.required = true;
                                
                                // 禁用家庭申请单次签证的信用卡选项
                                if (applicationType === 'FAMILY' && radio.id === 'creditCard') {
                                    radio.disabled = true;
                                    const label = document.querySelector(`label[for="${radio.id}"]`);
                                    if (label) {
                                        label.classList.add('disabled');
                                        label.title = '家庭申请单次签证不允许使用信用卡';
                                    }
                                } else {
                                    radio.disabled = false;
                                    const label = document.querySelector(`label[for="${radio.id}"]`);
                                    if (label) {
                                        label.classList.remove('disabled');
                                        label.title = '';
                                    }
                                }
                            });
                            break;
                        case 'THREE':
                            threeVisaOptions.classList.remove('d-none');
                            // 设置三年签证经济材料选项为必填
                            threeVisaOptions.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                                radio.required = true;
                            });
                            break;
                        case 'FIVE':
                            fiveVisaOptions.classList.remove('d-none');
                            // 设置五年签证经济材料选项为必填
                            fiveVisaOptions.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                                radio.required = true;
                            });
                            break;
                    }
                } else if (isShanghaiConsulate) {
                    console.log('显示上海领区经济材料选项');
                    
                    // 隐藏北京领区选项
                    beijingOptions.forEach(option => option.classList.add('d-none'));
                    
                    // 根据签证类型显示上海领区的选项
                    switch(selectedVisaType.value) {
                        case 'SINGLE':
                            singleVisaOptionsSH.classList.remove('d-none');
                            // 设置单次签证经济材料选项为必填
                            singleVisaOptionsSH.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                                radio.required = true;
                                
                                // 禁用家庭申请单次签证的信用卡选项
                                if (applicationType === 'FAMILY' && radio.id === 'creditCardSH') {
                                    radio.disabled = true;
                                    const label = document.querySelector(`label[for="${radio.id}"]`);
                                    if (label) {
                                        label.classList.add('disabled');
                                        label.title = '家庭申请单次签证不允许使用信用卡';
                                    }
                                } else {
                                    radio.disabled = false;
                                    const label = document.querySelector(`label[for="${radio.id}"]`);
                                    if (label) {
                                        label.classList.remove('disabled');
                                        label.title = '';
                                    }
                                }
                            });
                            break;
                        case 'THREE':
                            threeVisaOptionsSH.classList.remove('d-none');
                            // 设置三年签证经济材料选项为必填
                            threeVisaOptionsSH.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                                radio.required = true;
                            });
                            break;
                        case 'FIVE':
                            fiveVisaOptionsSH.classList.remove('d-none');
                            // 设置五年签证经济材料选项为必填
                            fiveVisaOptionsSH.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                                radio.required = true;
                            });
                            break;
                    }
                }
            } else {
                // 如果没有选择签证类型，则隐藏经济材料选项
                economicMaterialSection.classList.add('d-none');
                
                // 移除所有经济材料选项的必填属性
                document.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                    radio.required = false;
                });
            }
        } else {
            // 隐藏经济材料选项区域
            economicMaterialSection.classList.add('d-none');
            
            // 移除所有经济材料选项的必填属性
            document.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                radio.required = false;
            });
            
            console.log('经济材料选项已隐藏，原因:', 
                        !isValidConsulate ? '不是北京或上海领区' : 
                        !isNormalProcess ? '非普通经济材料办理方式' : 
                        !isAllowedApplicationType ? '申请类型不允许' : '未知原因');
        }
    }

    // 页面加载完成后检查一次办理方式
    if (processType) {
        // 如果已经选择，则调用处理函数
        handleProcessTypeChange();
    } else {
        console.log('未选择办理方式');
    }

    // 更新签证类型选项的显示
    function updateVisaTypeOptions() {
        // 获取所需的DOM元素
        const visaTypeSection = document.getElementById('visaTypeSection');
        const visaTypeRadios = document.querySelectorAll('input[name="visaType"]');
        
        if (!visaTypeSection || !visaTypeRadios || visaTypeRadios.length === 0) {
            console.warn('无法找到签证类型相关元素');
            return;
        }
        
        // 检查是否为绑签申请
        const isBindingApplication = document.getElementById('typeBinding')?.checked;
        if (isBindingApplication) {
            // 绑签申请隐藏签证类型选择
            visaTypeSection.classList.add('d-none');
            return;
        }
        
        // 获取当前选择的办理方式
        const selectedProcessType = document.querySelector('input[name="processType"]:checked')?.value;
        
        // 如果是特定大学生单次或新政简化三年，不显示签证类型选择
        if (selectedProcessType === 'STUDENT' || selectedProcessType === 'SIMPLIFIED') {
            visaTypeSection.classList.add('d-none');
            return;
        }
        
        // 对于税单办理和普通经济材料办理，显示签证类型选择
        if (selectedProcessType === 'TAX' || selectedProcessType === 'NORMAL') {
            visaTypeSection.classList.remove('d-none');
            
            // 检查是否为经济担保申请
            const isEconomicApplication = document.getElementById('typeEconomic')?.checked;
            if (isEconomicApplication) {
                // 经济担保申请锁定为单次签证
                const visaSingle = document.getElementById('visaSingle');
                const visaThree = document.getElementById('visaThree');
                const visaFive = document.getElementById('visaFive');
                
                if (visaSingle) visaSingle.checked = true;
                if (visaThree) visaThree.disabled = true;
                if (visaFive) visaFive.disabled = true;
            } else {
                // 其他情况下启用所有签证类型选项
                visaTypeRadios.forEach(radio => {
                    radio.disabled = false;
                });
            }
        }
        
        // 如果是普通经济材料办理，则更新经济材料选项显示
        if (selectedProcessType === 'NORMAL') {
            updateEconomicMaterialOptions();
        }
    }

    // 填充确认页面的信息
    function populateConfirmationPage(formData) {
        // 确保表单数据是FormData对象，否则转换
        let formDataObject;
        if (formData instanceof FormData) {
            formDataObject = Object.fromEntries(formData);
        } else {
            formDataObject = formData;
        }
        
        console.log('填充确认页面的数据:', formDataObject);
        
        // 获取相关元素
        const mainApplicantInfo = document.getElementById('mainApplicantInfo');
        const familyMembersInfoCard = document.getElementById('familyMembersInfoCard');
        const familyMembersInfo = document.getElementById('familyMembersInfo');
        const applicationDetails = document.getElementById('applicationDetails');
        
        if (!mainApplicantInfo || !applicationDetails) {
            console.error('找不到确认页面所需元素');
            return;
        }
        
        // 清空现有内容
        mainApplicantInfo.innerHTML = '';
        if (familyMembersInfo) familyMembersInfo.innerHTML = '';
        applicationDetails.innerHTML = '';
        
        // 填充主申请人信息
        const residenceConsulate = getConsulateText(formDataObject.residenceConsulate);
        const hukouConsulate = getConsulateText(formDataObject.hukouConsulate);
        const identityType = getIdentityText(formDataObject.identityType);
        
        // 创建信息项
        mainApplicantInfo.innerHTML = `
            <div class="col-md-6">
                <div class="d-flex">
                    <strong class="me-2">居住地领区:</strong>
                    <span>${residenceConsulate}</span>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex">
                    <strong class="me-2">户籍所在地领区:</strong>
                    <span>${hukouConsulate}</span>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex">
                    <strong class="me-2">申请人身份:</strong>
                    <span>${identityType}</span>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex">
                    <strong class="me-2">是否曾经访问日本:</strong>
                    <span>${formDataObject.previousVisit === 'true' ? '是' : '否'}</span>
                </div>
            </div>
        `;
        
        // 填充家庭成员信息（如果有）
        if (formDataObject.applicationType === 'FAMILY' && familyMembersInfoCard && familyMembersInfo) {
            const familyMembers = collectFamilyMembersData();
            
            if (familyMembers && familyMembers.length > 0) {
                familyMembersInfoCard.classList.remove('d-none');
                familyMembersInfo.innerHTML = ''; // 清空现有内容
                
                familyMembers.forEach((member, index) => {
                    const memberElement = document.createElement('div');
                    memberElement.className = 'mb-3 border-bottom pb-2';
                    memberElement.innerHTML = `
                        <h6 class="mt-2 mb-2">家庭成员 ${index + 1}</h6>
                        <div class="row g-2">
                            <div class="col-md-6">
                                <div class="d-flex">
                                    <strong class="me-2">与主申请人关系:</strong>
                                    <span>${getRelationText(member.relation)}</span>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="d-flex">
                                    <strong class="me-2">身份类型:</strong>
                                    <span>${getIdentityText(member.identityType)}</span>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="d-flex">
                                    <strong class="me-2">居住地领区:</strong>
                                    <span>${getConsulateText(member.residenceConsulate)}</span>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="d-flex">
                                    <strong class="me-2">户籍所在地领区:</strong>
                                    <span>${getConsulateText(member.hukouConsulate)}</span>
                                </div>
                            </div>
                        </div>
                    `;
                    familyMembersInfo.appendChild(memberElement);
                });
            } else {
                familyMembersInfoCard.classList.add('d-none');
            }
        } else {
            if (familyMembersInfoCard) {
                familyMembersInfoCard.classList.add('d-none');
            }
        }
        
        // 填充申请详情
        const applicationType = getApplicationTypeText(formDataObject.applicationType);
        const processType = getProcessTypeText(formDataObject.processType);
        let visaTypeText = '';
        
        if (['TAX', 'NORMAL', 'SIMPLIFIED'].includes(formDataObject.processType)) {
            switch(formDataObject.visaType) {
                case 'SINGLE': visaTypeText = '单次签证'; break;
                case 'THREE': visaTypeText = '三年多次签证'; break;
                case 'FIVE': visaTypeText = '五年多次签证'; break;
                default: visaTypeText = '未指定';
            }
        } else if (formDataObject.processType === 'STUDENT') {
            visaTypeText = '单次签证（学生专用）';
        }
        
        applicationDetails.innerHTML = `
            <div class="col-md-6">
                <div class="d-flex">
                    <strong class="me-2">申请类型:</strong>
                    <span>${applicationType}</span>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex">
                    <strong class="me-2">办理方式:</strong>
                    <span>${processType}</span>
                </div>
            </div>
            <div class="col-md-6">
                <div class="d-flex">
                    <strong class="me-2">签证类型:</strong>
                    <span>${visaTypeText}</span>
                </div>
            </div>
        `;
        
        // 添加特殊字段信息（如果适用）
        if (formDataObject.processType === 'STUDENT') {
            const graduateStatusText = formDataObject.graduateStatus === 'current' ? '在读学生' : '毕业三年内';
            const graduateStatusElement = document.createElement('div');
            graduateStatusElement.className = 'col-md-6';
            graduateStatusElement.innerHTML = `
                <div class="d-flex">
                    <strong class="me-2">大学生状态:</strong>
                    <span>${graduateStatusText}</span>
                </div>
            `;
            applicationDetails.appendChild(graduateStatusElement);
        }
        
        // 添加家属签证信息（如果适用）
        if (formDataObject.applicationType === 'BINDING') {
            const familyVisaTypeText = formDataObject.familyVisaType === 'THREE' ? '三年多次签证' : '五年多次签证';
            const familyRelationText = getRelationText(formDataObject.familyRelation);
            
            const bindingInfoElement = document.createElement('div');
            bindingInfoElement.className = 'col-12 mt-2';
            bindingInfoElement.innerHTML = `
                <div class="alert alert-info py-2 mb-0">
                    <strong>家属签证信息:</strong> 
                    申请人是持有${familyVisaTypeText}的家属（${familyRelationText}）
                </div>
            `;
            applicationDetails.appendChild(bindingInfoElement);
        }
        
        // 添加家属经济材料信息（如果适用）
        if (formDataObject.applicationType === 'ECONOMIC') {
            const economicInfoElement = document.createElement('div');
            economicInfoElement.className = 'col-12 mt-2';
            economicInfoElement.innerHTML = `
                <div class="alert alert-info py-2 mb-0">
                    <strong>经济材料信息:</strong> 
                    申请人使用直系亲属的经济材料
                </div>
            `;
            applicationDetails.appendChild(economicInfoElement);
        }
    }
    
    // 获取选中的单选按钮或复选框的文本
    function getSelectedOptionText(elements) {
        for (const element of elements) {
            if (element.checked) {
                const label = document.querySelector(`label[for="${element.id}"]`);
                if (label) {
                    const titleElement = label.querySelector('.option-title');
                    if (titleElement) {
                        return titleElement.textContent.trim();
                    }
                    return label.textContent.trim();
                }
                return element.value;
            }
        }
        return '';
    }
    
    // 获取领区文本
    function getConsulateText(value) {
        const consulateMap = {
            'beijing': '北京',
            'shanghai': '上海',
            'other': '其他领区'
        };
        return consulateMap[value] || value;
    }
    
    // 获取关系文本
    function getRelationText(value) {
        const relationMap = {
            'SPOUSE': '签证持有人的配偶',
            'PARENT': '签证持有人的父母',
            'CHILD': '签证持有人的子女'
        };
        return relationMap[value] || value;
    }
    
    // 获取身份类型文本
    function getIdentityText(value) {
        const identityMap = {
            'EMPLOYED': '在职人员',
            'STUDENT': '在校学生',
            'RETIRED': '退休人员',
            'FREELANCE': '自由职业',
            'CHILD': '学龄前儿童'
        };
        return identityMap[value] || value;
    }
    
    // 切换到确认页面
    function switchToConfirmTab() {
        if (window.bootstrap) {
            const confirmTabElement = document.getElementById('confirm-tab');
            if (confirmTabElement) {
                const tab = new bootstrap.Tab(confirmTabElement);
                tab.show();
            }
        } else {
            // 如果bootstrap不可用，使用简单的方式切换标签页
            const formContent = document.getElementById('form-content');
            const confirmContent = document.getElementById('confirm-content');
            const resultContent = document.getElementById('result-content');
            
            if (formContent) formContent.classList.remove('show', 'active');
            if (confirmContent) {
                confirmContent.classList.add('show', 'active');
                confirmTab.classList.add('active');
                formTab.classList.remove('active');
                resultTab.classList.remove('active');
            }
            if (resultContent) resultContent.classList.remove('show', 'active');
        }
    }
    
    // 切换到表单页面
    function switchToFormTab() {
        if (window.bootstrap) {
            const formTabElement = document.getElementById('form-tab');
            if (formTabElement) {
                const tab = new bootstrap.Tab(formTabElement);
                tab.show();
            }
        } else {
            // 如果bootstrap不可用，使用简单的方式切换标签页
            const formContent = document.getElementById('form-content');
            const confirmContent = document.getElementById('confirm-content');
            const resultContent = document.getElementById('result-content');
            
            if (formContent) {
                formContent.classList.add('show', 'active');
                formTab.classList.add('active');
                confirmTab.classList.remove('active');
                resultTab.classList.remove('active');
            }
            if (confirmContent) confirmContent.classList.remove('show', 'active');
            if (resultContent) resultContent.classList.remove('show', 'active');
        }
    }
    
    // 从确认页面返回表单页面
    if (backToFormBtn) {
        backToFormBtn.addEventListener('click', function() {
            switchToFormTab();
        });
    }
    
    // 从确认页面提交生成材料清单
    if (confirmAndGenerateBtn) {
        confirmAndGenerateBtn.addEventListener('click', async function() {
            try {
                // 显示加载状态
                showLoading(true);
                
                // 收集表单数据
                const formData = collectFormData();
                
                // 提交表单数据给服务器
                const result = await submitFormData(formData);
                
                // 检查响应
                if (result && result.status === "success" && result.document_list) {
                    // 显示材料清单
                    displayDocumentList(result.document_list);
                    // 切换到结果页面
                    switchToResultTab();
                } else {
                    throw new Error(result?.error || '生成材料清单失败，请重试');
                }
            } catch (error) {
                console.error("提交表单出错:", error);
                showError(error.message || '生成材料清单时出错，请重试');
            } finally {
                showLoading(false);
            }
        });
    }

    // 获取申请类型文本
    function getApplicationTypeText(value) {
        switch(value) {
            case 'SINGLE': return '单人申请';
            case 'FAMILY': return '家庭申请';
            case 'BINDING': return '作为签证持有人的家属办理';
            case 'ECONOMIC': return '使用家庭成员的经济材料';
            default: return '未指定';
        }
    }

    // 获取办理方式文本
    function getProcessTypeText(value) {
        switch(value) {
            case 'TAX': return '税单办理';
            case 'STUDENT': return '特定大学生单次';
            case 'NORMAL': return '普通经济材料办理';
            case 'SIMPLIFIED': return '新政简化三年';
            default: return '未指定';
        }
    }

    // 收集家庭成员数据
    function collectFamilyMembersData() {
        const familyMembers = [];
        // 修改选择器为正确的类名
        const familyMemberElements = document.querySelectorAll('.family-member');
        
        familyMemberElements.forEach((member, index) => {
            // 获取成员数据
            const relation = member.querySelector('select[name$="[relation]"]')?.value;
            const identityType = member.querySelector('select[name$="[identityType]"]')?.value;
            const residenceConsulate = member.querySelector('select[name$="[residenceConsulate]"]')?.value ||
                                      document.querySelector('input[name="residenceConsulate"]:checked')?.value;
            const hukouConsulate = member.querySelector('select[name$="[hukouConsulate]"]')?.value ||
                                  document.querySelector('input[name="hukouConsulate"]:checked')?.value;
            
            if (relation && identityType) {
                familyMembers.push({
                    relation: relation,
                    identityType: identityType,
                    residenceConsulate: residenceConsulate,
                    hukouConsulate: hukouConsulate,
                    number: index + 1
                });
            }
        });
        
        console.log('收集到的家庭成员:', familyMembers);
        return familyMembers;
    }

    // 处理申请类型变更
    function handleApplicationTypeChange() {
        // 获取选中的申请类型
        const selectedType = document.querySelector('input[name="applicationType"]:checked')?.value;
        
        // 首先隐藏所有相关区域
        if (familyMembersSection) familyMembersSection.classList.add('d-none');
        if (familyVisaSection) familyVisaSection.classList.add('d-none');
        if (familyVisaInfoSection) familyVisaInfoSection.classList.add('d-none'); // 隐藏老版本的section
        if (familyEconomicSection) familyEconomicSection.classList.add('d-none');
        
        // 默认显示办理方式模块
        if (processTypeModule) {
            processTypeModule.classList.remove('d-none');
        }

        // 重置签证类型状态和签证类型区域
        const visaTypeSection = document.getElementById('visaTypeSection');
        if (visaTypeSection) {
            visaTypeSection.classList.add('d-none'); // 默认隐藏签证类型区域
        }
        
        if (visaTypeRadios && visaTypeRadios.length > 0) {
            visaTypeRadios.forEach(radio => {
                radio.disabled = false;
                radio.required = false; // 默认不要求必填
            });
        }
        
        // 重置办理方式选项
        const processTypeInputs = document.querySelectorAll('input[name="processType"]');
        const processStudent = document.getElementById('processStudent');
        const processSimplified = document.getElementById('processSimplified');
        const processTax = document.getElementById('processTax');
        const processNormal = document.getElementById('processNormal');
        
        processTypeInputs.forEach(radio => {
            radio.disabled = false;
            radio.required = true;
        });
        
        // 重置所有select元素的required属性
        const familyVisaTypeElem = document.getElementById('familyVisaType');
        const familyRelationElem = document.getElementById('familyRelation');
        const familyHolderIdentityElem = document.getElementById('familyHolderIdentity');
        
        if (familyVisaTypeElem) familyVisaTypeElem.required = false;
        if (familyRelationElem) familyRelationElem.required = false;
        if (familyHolderIdentityElem) familyHolderIdentityElem.required = false;
        
        // 清除禁用样式
        if (processStudent) {
            const studentLabel = document.querySelector(`label[for="${processStudent.id}"]`);
            if (studentLabel) {
                studentLabel.classList.remove('disabled');
                studentLabel.title = '';
            }
        }
        if (processSimplified) {
            const simplifiedLabel = document.querySelector(`label[for="${processSimplified.id}"]`);
            if (simplifiedLabel) {
                simplifiedLabel.classList.remove('disabled');
                simplifiedLabel.title = '';
            }
        }
        
        // 根据选择显示相应区域并处理办理方式选项
        switch(selectedType) {
            case 'FAMILY':
                // 家庭申请：显示家庭成员区域
            if (familyMembersSection) familyMembersSection.classList.remove('d-none');
                // 需要选择签证类型
                if (visaTypeSection) {
                    visaTypeSection.classList.remove('d-none');
                }
                if (visaTypeRadios && visaTypeRadios.length > 0) {
                    visaTypeRadios.forEach(radio => {
                        radio.required = true;
                    });
                }
                
                // 禁用特定大学生单次和新政简化三年办理方式
                if (processStudent) {
                    processStudent.disabled = true;
                    const studentLabel = document.querySelector(`label[for="${processStudent.id}"]`);
                    if (studentLabel) {
                        studentLabel.classList.add('disabled');
                        studentLabel.title = '家庭申请不支持特定大学生单次办理';
                    }
                }
                if (processSimplified) {
                    processSimplified.disabled = true;
                    const simplifiedLabel = document.querySelector(`label[for="${processSimplified.id}"]`);
                    if (simplifiedLabel) {
                        simplifiedLabel.classList.add('disabled');
                        simplifiedLabel.title = '家庭申请不支持新政简化三年办理';
                    }
                }
                
                // 如果当前选中的是被禁用的选项，则自动选择普通经济材料办理
                if ((processStudent && processStudent.checked) || (processSimplified && processSimplified.checked)) {
                    if (processNormal) {
                        processNormal.checked = true;
                        console.log('家庭申请: 自动切换到普通经济材料办理');
                    }
                }
                break;
            case 'BINDING':
                // 绑签申请：显示家属签证信息区域，隐藏办理方式和签证类型
                if (familyVisaSection) familyVisaSection.classList.remove('d-none');
                if (processTypeModule) processTypeModule.classList.add('d-none');
                // 选中并禁用普通经济材料办理方式
                if (processNormal) {
                    processNormal.checked = true;
                    processTypeInputs.forEach(radio => {
                        radio.disabled = true;
                    });
                }
                
                // 设置familyVisaType和familyRelation为必填
                if (familyVisaTypeElem) familyVisaTypeElem.required = true;
                if (familyRelationElem) familyRelationElem.required = true;
                
                // 检查是否为上海领区，是则显示签证持有人身份选项
                const isShanghai = document.querySelector('input[name="residenceConsulate"]:checked')?.value === 'shanghai';
                const familyHolderIdentitySection = document.getElementById('familyHolderIdentitySection');
                if (isShanghai && familyHolderIdentitySection) {
                    familyHolderIdentitySection.classList.remove('d-none');
                    if (familyHolderIdentityElem) {
                        familyHolderIdentityElem.required = true;
                    }
                } else if (familyHolderIdentitySection) {
                    familyHolderIdentitySection.classList.add('d-none');
                    if (familyHolderIdentityElem) {
                        familyHolderIdentityElem.required = false;
                    }
                }
                break;
            case 'ECONOMIC':
                // 使用家庭成员经济材料：显示经济材料区域，隐藏办理方式
                if (familyEconomicSection) familyEconomicSection.classList.remove('d-none');
                if (processTypeModule) processTypeModule.classList.add('d-none');
                // 选中并禁用普通经济材料办理方式
                if (processNormal) {
                    processNormal.checked = true;
                    processTypeInputs.forEach(radio => {
                        radio.disabled = true;
                    });
                }
                // 选中并禁用单次签证
                if (visaSingle) {
                    visaSingle.checked = true;
                    visaTypeRadios.forEach(radio => {
                        radio.disabled = true;
                    });
                }
                break;
            case 'SINGLE':
                // 单人申请：显示签证类型区域
                if (visaTypeSection) {
                    visaTypeSection.classList.remove('d-none');
                }
                if (visaTypeRadios && visaTypeRadios.length > 0) {
                    visaTypeRadios.forEach(radio => {
                        radio.required = true;
                    });
                }
                break;
        }
        
        // 如果改变申请类型，需要重置经济材料选项
        updateEconomicMaterialOptions();
        
        // 确保根据当前身份类型应用相关限制
        checkIdentityTypeRestrictions();
        
        // 更新表单验证
        updateFormValidation();
    }

    // 提交表单事件处理
    async function submitForm(event) {
        // 阻止表单默认提交行为
        event.preventDefault();
        
        // 记录表单提交状态
        console.log('表单提交开始，正在验证...');
        console.log('申请人身份:', document.querySelector('input[name="identityType"]:checked')?.value);
        console.log('签证类型:', document.querySelector('input[name="visaType"]:checked')?.value);
        console.log('办理方式:', document.querySelector('input[name="processType"]:checked')?.value);
        
        const form = document.getElementById('visaForm');
        
        // 获取当前选项值
        const processType = document.querySelector('input[name="processType"]:checked')?.value;
        const applicationType = document.querySelector('input[name="applicationType"]:checked')?.value;
        const identityType = document.querySelector('input[name="identityType"]:checked')?.value;
        const visaType = document.querySelector('input[name="visaType"]:checked')?.value;
        const previousVisit = document.querySelector('input[name="previousVisit"]:checked')?.value;
        
        // 检查核心必填项
        const invalidFields = [];
        
        // 检查基本字段
        if (!document.querySelector('input[name="residenceConsulate"]:checked')) {
            invalidFields.push('居住地领区');
        }
        if (!document.querySelector('input[name="hukouConsulate"]:checked')) {
            invalidFields.push('户籍所在地领区');
        }
        if (!identityType) {
            invalidFields.push('申请人身份');
        }
        if (!applicationType) {
            invalidFields.push('申请类型');
        }
        if (!document.querySelector('input[name="previousVisit"]:checked')) {
            invalidFields.push('是否曾经访问日本');
        }
        
        // 检查办理方式
        if (!processType && applicationType !== 'BINDING') {
            invalidFields.push('办理方式');
        }
        
        // 验证新政简化三年办理方式必须曾经访问过日本
        if (processType === 'SIMPLIFIED' && previousVisit === 'false') {
            showError('新政简化三年办理方式要求申请人曾经访问过日本', 'formError');
            return; // 阻止表单继续提交
        }
        
        // 检查签证类型（如果需要）
        if (['TAX', 'NORMAL'].includes(processType) && applicationType !== 'BINDING') {
            if (!document.querySelector('input[name="visaType"]:checked')) {
                invalidFields.push('签证类型');
            }
        }
        
        // 检查特定大学生状态
        if (processType === 'STUDENT') {
            if (!document.querySelector('input[name="graduateStatus"]:checked')) {
                invalidFields.push('大学生状态');
            }
        }
        
        // 检查家属签证类型
        if (applicationType === 'BINDING') {
            const familyVisaType = document.getElementById('familyVisaType');
            const familyRelation = document.getElementById('familyRelation');
            
            if (familyVisaType && !familyVisaType.value) {
                invalidFields.push('家属签证类型');
            }
            if (familyRelation && !familyRelation.value) {
                invalidFields.push('申请人与持签人关系');
            }
            
            // 如果是上海领区，检查签证持有人身份
            const residenceConsulate = document.querySelector('input[name="residenceConsulate"]:checked')?.value;
            if (residenceConsulate === 'shanghai') {
                const familyHolderIdentity = document.getElementById('familyHolderIdentity');
                if (familyHolderIdentity && !familyHolderIdentity.value) {
                    invalidFields.push('签证持有人身份');
                }
            }
        }
        
        // 如果有未填写项，显示错误并阻止提交
        if (invalidFields.length > 0) {
            console.log('表单验证失败，未填写字段:', invalidFields);
            form.classList.add('was-validated');
            showError(`请填写所有必填项：${invalidFields.join(', ')}`, 'formErrorAlert');
            
            // 获取第一个无效的输入并滚动到它
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            return;
        }
        
        console.log('表单验证通过');
        
        // 检查家庭成员领区一致性
        if (applicationType === 'FAMILY') {
            const isValid = checkAllFamilyMembersConsulates();
            if (!isValid) {
                showError('家庭成员必须与主申请人居住在同一个领区');
                return;
            }
        }
        
        try {
            // 检查是否需要显示风险确认窗口
            // 条件：普通经济材料办理 + 申请三年或五年多次签证 + 从未访问日本
            if (processType === 'NORMAL' && 
                (visaType === 'THREE' || visaType === 'FIVE') && 
                previousVisit === 'false') {
                
                // 显示风险确认模态框
                showRiskConfirmationModal(event);
                return; // 停止表单提交，等待用户在模态框中确认
            }
            
            // 正常提交表单流程
            proceedWithFormSubmission();
        } catch (error) {
            console.error('表单提交错误:', error);
            showError(error.message || '表单提交错误，请重试');
            
            // 恢复提交按钮状态
            const submitBtn = document.getElementById('submitBtn');
            const submitSpinner = document.getElementById('submitSpinner');
            
            if (submitBtn && submitSpinner) {
                submitBtn.disabled = false;
                submitSpinner.classList.add('d-none');
            }
        }
    }
    
    // 显示风险确认模态框
    function showRiskConfirmationModal(originalEvent) {
        const modal = document.getElementById('riskConfirmationModal');
        const confirmBtn = document.getElementById('riskConfirmBtn');
        const cancelBtn = document.getElementById('riskCancelBtn');
        const checkboxes = modal.querySelectorAll('input[type="checkbox"]');
        
        // 重置所有复选框
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // 禁用确认按钮，直到至少选择一项
        confirmBtn.disabled = true;
        
        // 监听复选框变化
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // 如果有任何一个复选框被选中，则启用确认按钮
                const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
                confirmBtn.disabled = !anyChecked;
            });
        });
        
        // 确认按钮点击事件
        confirmBtn.onclick = function() {
            // 关闭模态框
            modal.style.display = 'none';
            
            // 继续表单提交流程
            proceedWithFormSubmission();
        };
        
        // 取消按钮点击事件
        cancelBtn.onclick = function() {
            // 关闭模态框
            modal.style.display = 'none';
            
            // 将签证类型改为单次
            const singleVisaRadio = document.getElementById('visaSingle');
            if (singleVisaRadio) {
                singleVisaRadio.checked = true;
                
                // 触发签证类型变化事件
                const changeEvent = new Event('change');
                singleVisaRadio.dispatchEvent(changeEvent);
                
                // 更新经济材料选项
                updateEconomicMaterialOptions();
            }
            
            // 继续表单提交流程
            proceedWithFormSubmission();
        };
        
        // 显示模态框
        modal.style.display = 'flex';
    }
    
    // 继续表单提交流程
    function proceedWithFormSubmission() {
        // 显示加载状态
        const submitBtn = document.getElementById('submitBtn');
        const submitSpinner = document.getElementById('submitSpinner');
        
        if (submitBtn && submitSpinner) {
            submitBtn.disabled = true;
            submitSpinner.classList.remove('d-none');
        }
        
        try {
            // 表单有效，切换到确认页面
            const formData = collectFormData();
            
            // 填充确认页面信息
            populateConfirmationPage(formData);
            
            // 切换到确认信息标签页
            switchToConfirmTab();
            
            // 恢复提交按钮状态
            if (submitBtn && submitSpinner) {
                submitBtn.disabled = false;
                submitSpinner.classList.add('d-none');
            }
        } catch (error) {
            console.error('切换到确认页面时出错:', error);
            showError('处理表单数据时出错，请重试');
            
            // 恢复提交按钮状态
            if (submitBtn && submitSpinner) {
                submitBtn.disabled = false;
                submitSpinner.classList.add('d-none');
            }
        }
    }

    // 更新表单验证规则
    function updateFormValidation() {
        const applicationType = document.querySelector('input[name="applicationType"]:checked')?.value;
        const processType = document.querySelector('input[name="processType"]:checked')?.value;
        const selectedResidenceConsulate = document.querySelector('input[name="residenceConsulate"]:checked');
        const isValidConsulate = selectedResidenceConsulate && 
                               (selectedResidenceConsulate.value === 'beijing' || 
                                selectedResidenceConsulate.value === 'shanghai');
        const isNormalProcess = processType === 'NORMAL';
        const isAllowedApplicationType = applicationType === 'SINGLE' || applicationType === 'FAMILY';
        
        // 家属签证信息的验证
        if (applicationType === 'BINDING') {
            const familyVisaType = document.getElementById('familyVisaType');
            const familyRelationSelect = document.getElementById('familyRelation');
            
            if (familyVisaType) {
                familyVisaType.required = true;
            }
            
            if (familyRelationSelect) {
                familyRelationSelect.required = true;
            }
            
            // 如果是上海领区，需验证持签人身份
            if (selectedResidenceConsulate && selectedResidenceConsulate.value === 'shanghai') {
                const familyHolderIdentity = document.getElementById('familyHolderIdentity');
                if (familyHolderIdentity) {
                    familyHolderIdentity.required = true;
                }
            }
        } else {
            const familyVisaType = document.getElementById('familyVisaType');
            const familyRelationSelect = document.getElementById('familyRelation');
            const familyHolderIdentity = document.getElementById('familyHolderIdentity');
            
            if (familyVisaType) {
                familyVisaType.required = false;
            }
            
            if (familyRelationSelect) {
                familyRelationSelect.required = false;
            }
            
            if (familyHolderIdentity) {
                familyHolderIdentity.required = false;
            }
        }
        
        // 家庭成员选择"使用家庭成员的经济材料"时的处理
        const economicRelation = document.getElementById('economicRelation');
        const economicProofType = document.getElementById('economicProofType');
        
        const usesFamilyMemberEconomicMaterial = applicationType === 'FAMILY_MEMBER' && document.getElementById('FAMILY_MEMBER_ECONOMIC_MATERIAL') && document.getElementById('FAMILY_MEMBER_ECONOMIC_MATERIAL').checked;
        
        // 只有在家庭成员使用家庭成员经济材料选项时才需要验证这些字段
        if (economicRelation && economicProofType) {
            if (usesFamilyMemberEconomicMaterial) {
                economicRelation.setAttribute('required', '');
                economicProofType.setAttribute('required', '');
                
                // 自动设置默认值以避免验证错误
                if (!economicRelation.value) {
                    economicRelation.value = "父母"; // 设置一个默认关系
                }
                if (!economicProofType.value) {
                    economicProofType.value = "在职收入证明"; // 设置一个默认证明类型
                }
            } else {
                economicRelation.removeAttribute('required');
                economicProofType.removeAttribute('required');
            }
        }
        
        // 大学生状态验证
        if (processType === 'STUDENT') {
            const graduateStatusRadios = document.querySelectorAll('input[name="graduateStatus"]');
            graduateStatusRadios.forEach(radio => {
                radio.required = true;
            });
        } else {
            const graduateStatusRadios = document.querySelectorAll('input[name="graduateStatus"]');
            graduateStatusRadios.forEach(radio => {
                radio.required = false;
            });
        }
        
        // 签证类型验证 - 只在非绑签申请时要求
        if ((processType === 'TAX' || processType === 'NORMAL') && applicationType !== 'BINDING') {
            const visaTypeRadios = document.querySelectorAll('input[name="visaType"]');
            visaTypeRadios.forEach(radio => {
                radio.required = true;
            });
        } else {
            const visaTypeRadios = document.querySelectorAll('input[name="visaType"]');
            visaTypeRadios.forEach(radio => {
                radio.required = false;
            });
        }
        
        // 经济材料选项验证
        const economicMaterialSection = document.getElementById('economicMaterialSection');
        
        if (economicMaterialSection && !economicMaterialSection.classList.contains('d-none')) {
            // 经济材料选项区域可见，需要验证
            const selectedVisaType = document.querySelector('input[name="visaType"]:checked');
            if (selectedVisaType && isValidConsulate && isNormalProcess && isAllowedApplicationType) {
                // 设置对应签证类型的经济材料选项为必填
                if (selectedVisaType.value === 'SINGLE') {
                    document.querySelectorAll('#singleVisaOptions input[name="economicMaterial"]').forEach(radio => {
                        radio.required = true;
                    });
                } else if (selectedVisaType.value === 'THREE') {
                    document.querySelectorAll('#threeVisaOptions input[name="economicMaterial"]').forEach(radio => {
                        radio.required = true;
                    });
                } else if (selectedVisaType.value === 'FIVE') {
                    document.querySelectorAll('#fiveVisaOptions input[name="economicMaterial"]').forEach(radio => {
                        radio.required = true;
                    });
                }
            } else {
                // 不需要经济材料选项，移除所有必填属性
                document.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                    radio.required = false;
                });
            }
        } else {
            // 经济材料选项区域不可见，移除所有必填属性
            document.querySelectorAll('input[name="economicMaterial"]').forEach(radio => {
                radio.required = false;
            });
        }
    }

    // 在表单字段变更时更新相关部分
    document.querySelectorAll('input[name="applicationType"], input[name="processType"], input[name="residenceConsulate"], input[name="visaType"]').forEach(element => {
        element.addEventListener('change', function() {
            // 移除对不存在函数的调用
            updateEconomicMaterialOptions();
            updateFormValidation();
        });
    });

    // 初始化页面
    document.addEventListener('DOMContentLoaded', function() {
        updateEconomicMaterialOptions();
        updateFormValidation();
        
        // 初始检查表单状态
        resetFormState();
        checkIdentityTypeRestrictions();
        handleProcessTypeChange();
    });

    // 处理身份类型变更
    document.querySelectorAll('input[name="identityType"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // 检查身份类型限制
            checkIdentityTypeRestrictions();
            
            // 如果当前选择了特定大学生单次办理方式，需要更新大学生状态选项
            const selectedProcessType = document.querySelector('input[name="processType"]:checked')?.value;
            if (selectedProcessType === 'STUDENT') {
                handleProcessTypeChange();
            }
        });
    });

    // 添加复制按钮的点击事件
    const copyBtnElement = document.getElementById('copyBtn');
    if (copyBtnElement) {
        copyBtnElement.addEventListener('click', copyDocumentList);
    }

    // 添加一个初始化函数，在页面加载时填充注意事项列表
    function populateNoticeItems() {
        const noticeList = document.getElementById('noticeItemsList');
        if (noticeList) {
            // 清空现有内容
            noticeList.innerHTML = '';
            
            // 添加注意事项
            noticeItems.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                noticeList.appendChild(li);
            });
        }
    }

    // 在文档加载完成后执行
    document.addEventListener('DOMContentLoaded', function() {
        // ... existing code ...
        
        // 填充注意事项列表
        populateNoticeItems();
        
        // ... existing code ...
    });
}); 