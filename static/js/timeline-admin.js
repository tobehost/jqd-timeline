/**
 * TimelineJS 数据管理脚本 - 数据库版本
 * 文件名: /static/js/timeline-admin.js
 */

// 全局数据对象
let timelineData = {
    title: {},
    events: [],
    eras: [],
    scale: "human"
};

// 配置
const API_CONFIG = {
    BASE_URL: '/api',
    ENDPOINTS: {
        CONFIG: '/config',
        EVENTS: '/events',
        ERAS: '/eras',
        GENERATE_JSON: '/generate-json',
        HEALTH: '/health'
    },
    AUTO_SAVE: false,
    AUTO_GENERATE_JSON: true // 自动生成JSON文件
};

// DOM元素引用
const elements = {
    eventsContainer: document.getElementById('eventsContainer'),
    eventCount: document.getElementById('eventCount'),
    jsonPreview: document.getElementById('jsonPreview'),
    logContainer: document.getElementById('logContainer'),
    titleHeadline: document.getElementById('titleHeadline'),
    titleText: document.getElementById('titleText'),
    scaleSelect: document.getElementById('scaleSelect'),
    erasContainer: document.getElementById('erasContainer'),
    
    // 按钮
    loadDataBtn: document.getElementById('loadDataBtn'),
    saveDataBtn: document.getElementById('saveDataBtn'),
    generateJsonBtn: document.getElementById('generateJsonBtn'),
    addEventBtn: document.getElementById('addEventBtn'),
    resetDataBtn: document.getElementById('resetDataBtn'),
    refreshPreviewBtn: document.getElementById('refreshPreviewBtn'),
    copyJsonBtn: document.getElementById('copyJsonBtn'),
    clearLogBtn: document.getElementById('clearLogBtn'),
    addEraBtn: document.getElementById('addEraBtn'),
    exportBtn: document.getElementById('exportBtn'),
    
    // 模态框相关
    eventModal: new bootstrap.Modal(document.getElementById('eventModal')),
    saveEventBtn: document.getElementById('saveEventBtn'),
    eventForm: document.getElementById('eventForm'),
    
    // 表单字段
    editIndex: document.getElementById('editIndex'),
    editId: document.getElementById('editId'),
    eventHeadline: document.getElementById('eventHeadline'),
    eventText: document.getElementById('eventText'),
    eventGroup: document.getElementById('eventGroup'),
    eventUniqueId: document.getElementById('eventUniqueId'),
    startYear: document.getElementById('startYear'),
    startMonth: document.getElementById('startMonth'),
    startDay: document.getElementById('startDay'),
    displayDate: document.getElementById('displayDate'),
    mediaUrl: document.getElementById('mediaUrl'),
    mediaCaption: document.getElementById('mediaCaption')
};

// 初始化函数
function init() {
    bindEvents();
    loadConfig();
    loadEvents();
    loadEras();
    updateUI();
    
    log('系统初始化完成');
    log(`API基础URL: ${API_CONFIG.BASE_URL}`);
}

// 绑定事件
function bindEvents() {
    // 数据操作按钮
    elements.loadDataBtn.addEventListener('click', () => {
        loadConfig();
        loadEvents();
        loadEras();
    });
    
    elements.saveDataBtn.addEventListener('click', saveConfig);
    elements.generateJsonBtn.addEventListener('click', generateJsonFile);
    elements.addEventBtn.addEventListener('click', () => openEventModal());
    elements.resetDataBtn.addEventListener('click', resetData);
    elements.refreshPreviewBtn.addEventListener('click', loadTimelineData);
    elements.copyJsonBtn.addEventListener('click', copyJsonToClipboard);
    elements.clearLogBtn.addEventListener('click', clearLog);
    elements.addEraBtn.addEventListener('click', addEra);
    elements.exportBtn.addEventListener('click', exportData);
    
    // 表单提交
    elements.saveEventBtn.addEventListener('click', saveEvent);
    
    // 配置输入监听
    elements.titleHeadline.addEventListener('input', debounce(saveConfig, 1000));
    elements.titleText.addEventListener('input', debounce(saveConfig, 1000));
    if (elements.scaleSelect) {
        elements.scaleSelect.addEventListener('change', saveConfig);
    }
}

// 防抖函数
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

// API请求辅助函数
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = endpoint.startsWith('http') ? endpoint : API_CONFIG.BASE_URL + endpoint;
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API请求失败: ${endpoint}`, error);
        throw error;
    }
}

// 加载配置
async function loadConfig() {
    try {
        const config = await apiRequest(API_CONFIG.ENDPOINTS.CONFIG);
        
        if (config) {
            elements.titleHeadline.value = config.title_headline || '';
            elements.titleText.value = config.title_text || '';
            
            if (elements.scaleSelect) {
                elements.scaleSelect.value = config.scale || 'human';
            }
            
            log('配置加载成功', 'success');
        }
    } catch (error) {
        log(`配置加载失败: ${error.message}`, 'error');
    }
}

// 保存配置
async function saveConfig() {
    const configData = {
        title_headline: elements.titleHeadline.value,
        title_text: elements.titleText.value,
        scale: elements.scaleSelect ? elements.scaleSelect.value : 'human'
    };
    
    try {
        await apiRequest(API_CONFIG.ENDPOINTS.CONFIG, 'PUT', configData);
        log('配置已保存', 'success');
        
        if (API_CONFIG.AUTO_GENERATE_JSON) {
            generateJsonFile(true);
        }
    } catch (error) {
        log(`配置保存失败: ${error.message}`, 'error');
    }
}

// 加载事件
async function loadEvents() {
    try {
        const events = await apiRequest(API_CONFIG.ENDPOINTS.EVENTS);
        timelineData.events = events;
        updateEventsList();
        updateEventCount();
        log(`已加载 ${events.length} 个事件`, 'success');
    } catch (error) {
        log(`事件加载失败: ${error.message}`, 'error');
    }
}

// 加载时代
async function loadEras() {
    try {
        const eras = await apiRequest(API_CONFIG.ENDPOINTS.ERAS);
        timelineData.eras = eras;
        updateErasList();
        log(`已加载 ${eras.length} 个时代`, 'success');
    } catch (error) {
        log(`时代加载失败: ${error.message}`, 'error');
    }
}

// 加载完整时间线数据
async function loadTimelineData() {
    try {
        const data = await apiRequest(API_CONFIG.ENDPOINTS.GENERATE_JSON);
        timelineData = data;
        updatePreview();
        log('时间线数据加载成功', 'success');
    } catch (error) {
        log(`时间线数据加载失败: ${error.message}`, 'error');
    }
}

// 生成JSON文件
async function generateJsonFile(silent = false) {
    if (!silent) {
        log('正在生成JSON文件...', 'info');
    }
    
    try {
        const result = await apiRequest(API_CONFIG.ENDPOINTS.GENERATE_JSON, 'POST');
        
        if (!silent) {
            log('JSON文件已生成', 'success');
            showNotification('JSON文件已生成', 'success');
        }
        
        // 更新预览
        timelineData = result.data;
        updatePreview();
        
        return result;
    } catch (error) {
        if (!silent) {
            log(`JSON文件生成失败: ${error.message}`, 'error');
            showNotification(`生成失败: ${error.message}`, 'error');
        }
        throw error;
    }
}

// 导出数据
async function exportData() {
    try {
        const response = await fetch('/api/export');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'timeline-export.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        log('数据已导出', 'success');
        showNotification('数据已导出为JSON文件', 'success');
    } catch (error) {
        log(`导出失败: ${error.message}`, 'error');
        showNotification(`导出失败: ${error.message}`, 'error');
    }
}

// 更新UI
function updateUI() {
    updateEventCount();
    updatePreview();
}

// 更新事件列表
function updateEventsList() {
    if (!timelineData.events || timelineData.events.length === 0) {
        elements.eventsContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-clock display-6 d-block mb-3"></i>
                <p>暂无事件数据，请点击"添加事件"按钮</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    timelineData.events.forEach((event, index) => {
        const dateText = getDateDisplay(event);
        
        html += `
            <div class="event-card">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="mb-1">${event.headline || '无标题'}</h5>
                        <p class="text-muted small mb-2">
                            <i class="bi bi-calendar-event me-1"></i>${dateText}
                            ${event.event_group ? `<span class="ms-3"><i class="bi bi-tags me-1"></i>${event.event_group}</span>` : ''}
                        </p>
                        ${event.text ? `<p class="mb-2 small">${event.text.substring(0, 100)}${event.text.length > 100 ? '...' : ''}</p>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-primary btn-action edit-event" data-id="${event.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger btn-action delete-event" data-id="${event.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    elements.eventsContainer.innerHTML = html;
    
    // 绑定事件操作按钮
    document.querySelectorAll('.edit-event').forEach(btn => {
        btn.addEventListener('click', function() {
            const eventId = parseInt(this.getAttribute('data-id'));
            openEventModal(eventId);
        });
    });
    
    document.querySelectorAll('.delete-event').forEach(btn => {
        btn.addEventListener('click', function() {
            const eventId = parseInt(this.getAttribute('data-id'));
            deleteEvent(eventId);
        });
    });
}

// 获取日期显示文本
function getDateDisplay(event) {
    if (event.display_date) {
        return event.display_date;
    }
    
    if (event.start_display_date) {
        return event.start_display_date;
    }
    
    let dateText = `${event.start_year}年`;
    if (event.start_month) {
        dateText += `${event.start_month}月`;
        if (event.start_day) {
            dateText += `${event.start_day}日`;
        }
    }
    
    if (event.end_year) {
        dateText += ` - ${event.end_year}年`;
        if (event.end_month) {
            dateText += `${event.end_month}月`;
            if (event.end_day) {
                dateText += `${event.end_day}日`;
            }
        }
    }
    
    return dateText;
}

// 更新事件计数
function updateEventCount() {
    elements.eventCount.textContent = timelineData.events ? timelineData.events.length : 0;
}

// 更新时代列表
function updateErasList() {
    if (!timelineData.eras || timelineData.eras.length === 0) {
        elements.erasContainer.innerHTML = '<div class="text-muted small">暂无时代数据</div>';
        return;
    }
    
    let html = '';
    timelineData.eras.forEach((era, index) => {
        html += `
            <div class="border-bottom pb-2 mb-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${era.headline || '未命名时代'}</strong>
                        <div class="small text-muted">
                            ${era.start_year} - ${era.end_year}
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-danger delete-era" data-id="${era.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    elements.erasContainer.innerHTML = html;
    
    // 绑定删除时代按钮
    document.querySelectorAll('.delete-era').forEach(btn => {
        btn.addEventListener('click', function() {
            const eraId = parseInt(this.getAttribute('data-id'));
            deleteEra(eraId);
        });
    });
}

// 添加时代
function addEra() {
    const eraName = prompt('请输入时代名称:');
    if (!eraName) return;
    
    const startYear = prompt('请输入开始年份:');
    if (!startYear || isNaN(startYear)) {
        alert('请输入有效的年份');
        return;
    }
    
    const endYear = prompt('请输入结束年份:');
    if (!endYear || isNaN(endYear)) {
        alert('请输入有效的年份');
        return;
    }
    
    const eraData = {
        headline: eraName,
        start_year: parseInt(startYear),
        end_year: parseInt(endYear),
        text: ""
    };
    
    apiRequest(API_CONFIG.ENDPOINTS.ERAS, 'POST', eraData)
        .then(result => {
            log(`添加时代: ${eraName}`, 'success');
            loadEras();
            if (API_CONFIG.AUTO_GENERATE_JSON) {
                generateJsonFile(true);
            }
        })
        .catch(error => {
            log(`添加时代失败: ${error.message}`, 'error');
        });
}

// 删除时代
async function deleteEra(eraId) {
    if (confirm('确定要删除这个时代吗？')) {
        try {
            await apiRequest(`${API_CONFIG.ENDPOINTS.ERAS}/${eraId}`, 'DELETE');
            log(`时代已删除`, 'warning');
            loadEras();
            if (API_CONFIG.AUTO_GENERATE_JSON) {
                generateJsonFile(true);
            }
        } catch (error) {
            log(`删除时代失败: ${error.message}`, 'error');
        }
    }
}

// 打开事件模态框
async function openEventModal(eventId = null) {
    // 重置表单
    elements.eventForm.reset();
    elements.editId.value = eventId || '';
    
    // 如果是编辑模式，加载事件数据
    if (eventId) {
        try {
            const event = await apiRequest(`${API_CONFIG.ENDPOINTS.EVENTS}/${eventId}`);
            
            elements.eventHeadline.value = event.headline || '';
            elements.eventText.value = event.text || '';
            elements.eventGroup.value = event.event_group || '';
            elements.eventUniqueId.value = event.unique_id || '';
            elements.startYear.value = event.start_year || '';
            elements.startMonth.value = event.start_month || '';
            elements.startDay.value = event.start_day || '';
            elements.displayDate.value = event.display_date || '';
            elements.mediaUrl.value = event.media_url || '';
            elements.mediaCaption.value = event.media_caption || '';
        } catch (error) {
            log(`加载事件失败: ${error.message}`, 'error');
        }
    }
    
    elements.eventModal.show();
}

// 保存事件
async function saveEvent() {
    // 验证表单
    if (!elements.eventHeadline.value.trim()) {
        alert('请输入事件标题');
        elements.eventHeadline.focus();
        return;
    }
    
    if (!elements.startYear.value || isNaN(elements.startYear.value)) {
        alert('请输入有效的开始年份');
        elements.startYear.focus();
        return;
    }
    
    // 创建事件对象
    const eventData = {
        headline: elements.eventHeadline.value,
        text: elements.eventText.value,
        start_year: parseInt(elements.startYear.value),
        event_group: elements.eventGroup.value || null,
        unique_id: elements.eventUniqueId.value || null,
        display_date: elements.displayDate.value || null,
        media_url: elements.mediaUrl.value || null,
        media_caption: elements.mediaCaption.value || null
    };
    
    // 添加可选字段
    if (elements.startMonth.value) eventData.start_month = parseInt(elements.startMonth.value);
    if (elements.startDay.value) eventData.start_day = parseInt(elements.startDay.value);
    
    const eventId = elements.editId.value;
    
    try {
        if (eventId) {
            // 更新现有事件
            await apiRequest(`${API_CONFIG.ENDPOINTS.EVENTS}/${eventId}`, 'PUT', eventData);
            log(`事件已更新: ${eventData.headline}`, 'info');
        } else {
            // 添加新事件
            await apiRequest(API_CONFIG.ENDPOINTS.EVENTS, 'POST', eventData);
            log(`事件已添加: ${eventData.headline}`, 'success');
        }
        
        // 关闭模态框并刷新
        elements.eventModal.hide();
        loadEvents();
        
        if (API_CONFIG.AUTO_GENERATE_JSON) {
            generateJsonFile(true);
        }
    } catch (error) {
        log(`保存事件失败: ${error.message}`, 'error');
    }
}

// 删除事件
async function deleteEvent(eventId) {
    if (confirm('确定要删除这个事件吗？')) {
        try {
            await apiRequest(`${API_CONFIG.ENDPOINTS.EVENTS}/${eventId}`, 'DELETE');
            log(`事件已删除`, 'warning');
            loadEvents();
            
            if (API_CONFIG.AUTO_GENERATE_JSON) {
                generateJsonFile(true);
            }
        } catch (error) {
            log(`删除事件失败: ${error.message}`, 'error');
        }
    }
}

// 重置数据
function resetData() {
    if (confirm('确定要重置所有数据吗？此操作将删除所有事件和时代。')) {
        // TODO: 实现重置功能
        log('重置功能待实现', 'warning');
    }
}

// 更新JSON预览
function updatePreview() {
    elements.jsonPreview.textContent = JSON.stringify(timelineData, null, 2);
}

// 复制JSON到剪贴板
function copyJsonToClipboard() {
    navigator.clipboard.writeText(JSON.stringify(timelineData, null, 2))
        .then(() => {
            log('JSON已复制到剪贴板', 'success');
            showNotification('JSON已复制到剪贴板', 'success');
        })
        .catch(err => {
            console.error('复制失败:', err);
            log('复制失败: ' + err.message, 'error');
            showNotification('复制失败: ' + err.message, 'error');
        });
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }
    }, 3000);
}

// 日志函数
function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const typeClass = {
        'success': 'text-success',
        'error': 'text-danger',
        'warning': 'text-warning',
        'info': 'text-info'
    }[type] || 'text-secondary';
    
    const logEntry = document.createElement('div');
    logEntry.className = `border-bottom pb-1 mb-1 ${typeClass}`;
    logEntry.innerHTML = `<small><strong>[${timestamp}]</strong> ${message}</small>`;
    
    elements.logContainer.prepend(logEntry);
    
    // 限制日志数量
    const logs = elements.logContainer.children;
    if (logs.length > 20) {
        elements.logContainer.removeChild(logs[logs.length - 1]);
    }
}

// 清空日志
function clearLog() {
    elements.logContainer.innerHTML = '<div class="text-muted">日志已清空</div>';
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);