// 模型数据（由 /api/models 注入）
let modelsData = {};

async function loadModelsFromApi() {
    const r = await fetch('/api/models');
    if (!r.ok) {
        throw new Error('无法加载模型列表');
    }
    modelsData = await r.json();
}

// 状态
let currentResolution = '2K';
let currentMode = 'text2image';  // text2image / image2image / batch
let uploadedImages = [null, null, null, null, null, null];  // 6张参考图
let currentUploadIndex = 0;  // 当前上传的索引

// 批量生成状态
let batchTasks = [
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'image', status: 'pending' }
];
let currentBatchUploadTask = 0;
let currentBatchUploadIndex = 0;

let videoBatchTasks = [
    { images: [null, null, null], prompt: '', result: null, mediaType: 'video', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'video', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'video', status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, mediaType: 'video', status: 'pending' }
];
let currentVideoBatchUploadTask = 0;
let currentVideoBatchUploadIndex = 0;

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    loadTheme();
    loadHistory();
    try {
        await loadModelsFromApi();
    } catch (e) {
        console.error(e);
        modelsData = {};
    }
    loadSettings();
    loadApiKey();
    initModelSelect();
    ensureBatchTaskCards();
    initBatchModelSelect();
    initVideoBatch();
    setupEventListeners();
});

// 新建对话
function newChat() {
    // 清空输入框
    document.getElementById('messageInput').value = '';
    
    // 清空上传的图片
    uploadedImages = [null, null, null, null, null, null];
    for (let i = 0; i < 6; i++) {
        updateUploadPreview(i);
    }
    
    // 清空结果区域
    document.getElementById('resultArea').style.display = 'none';
    document.getElementById('resultContent').innerHTML = '';
    
    // 切换回文生图模式
    document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('.mode-tab[data-mode="text2image"]').classList.add('active');
    currentMode = 'text2image';
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('batchArea').style.display = 'none';
    document.getElementById('videoBatchArea').style.display = 'none';
    document.getElementById('welcomeMessage').style.display = 'flex';
    
    // 聚焦到输入框
    document.getElementById('messageInput').focus();
}

// 加载设置
function loadSettings() {
    currentResolution = localStorage.getItem('resolution') || '2K';
    if (currentResolution === 'Video') {
        currentResolution = '2K';
        localStorage.setItem('resolution', currentResolution);
    }

    // 更新UI
    document.querySelectorAll('.resolution-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.res === currentResolution);
    });

    // 更新模型列表
    updateModels();
    if (!modelsData[currentResolution]?.length) {
        switchResolution('2K');
    }
}

// 加载保存的 API Key（仅当用户勾选「记住」）
function loadApiKey() {
    const remember = localStorage.getItem('rememberApiKey') === '1';
    const cb = document.getElementById('rememberApiKey');
    if (cb) {
        cb.checked = remember;
    }
    if (remember) {
        const savedApiKey = localStorage.getItem('apiKey');
        if (savedApiKey) {
            document.getElementById('apiKey').value = savedApiKey;
            document.getElementById('apiKeySaved').style.display = 'inline';
        }
    } else {
        localStorage.removeItem('apiKey');
    }
}

// 加载主题
function loadTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    setTheme(theme);
}

// 切换主题
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

// 设置主题
function setTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        document.getElementById('themeIcon').innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
    } else {
        document.documentElement.removeAttribute('data-theme');
        document.getElementById('themeIcon').innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
    }
}

// 初始化模型选择
function initModelSelect() {
    updateModels();
}

// 更新模型列表
function updateModels() {
    const select = document.getElementById('modelSelect');
    const models = modelsData[currentResolution] || [];
    renderModelOptions(select, models);
}

function renderModelOptions(select, models) {
    select.innerHTML = '';

    if (!models.length) {
        const option = document.createElement('option');
        option.disabled = true;
        option.selected = true;
        option.textContent = '暂无可用模型';
        select.appendChild(option);
        return;
    }

    const groups = new Map();
    models.forEach(model => {
        const groupLabel = getModelGroupLabel(model);
        let group = groups.get(groupLabel);
        if (!group) {
            group = document.createElement('optgroup');
            group.label = groupLabel;
            select.appendChild(group);
            groups.set(groupLabel, group);
        }

        const option = document.createElement('option');
        option.value = model;
        option.textContent = getRatioDisplay(model);
        option.title = model;
        group.appendChild(option);
    });
}

// 获取模型版本
function getModelVersion(model) {
    return getModelGroupLabel(model);
}

function getModelGroupLabel(model) {
    const mediaType = isVideoModel(model) ? '视频模型' : '图片模型';
    return `${mediaType} / ${getModelFamilyLabel(model)}`;
}

function getModelFamilyLabel(model) {
    if (model.startsWith('firefly-sora2-')) return 'Sora 2';
    if (model.startsWith('firefly-veo31-ref-')) return 'Veo 3.1 参考图';
    if (model.startsWith('firefly-veo31-fast-')) return 'Veo 3.1 极速';
    if (model.startsWith('firefly-veo31-')) return 'Veo 3.1 标准';
    if (model.startsWith('firefly-kling3-')) return 'Kling 3.0';
    if (model === 'gpt-image-2' || model.includes('firefly-gpt-image')) return 'GPT Image 2';
    if (model.includes('nano-banana-pro')) return 'Nano Banana Pro';
    if (model.includes('nano-banana2')) return 'Nano Banana 2';
    if (model.includes('nano-banana')) return 'Nano Banana';
    return model.split('-').slice(0, 3).join('-');
}

// 获取比例显示
function getRatioDisplay(model) {
    if (isVideoModel(model)) {
        const duration = (model.match(/-(\d+s)-/) || [])[1] || '';
        const ratio = (model.match(/-(16x9|9x16)(?:-|$)/) || [])[1] || '';
        const resolution = (model.match(/-(1080p|720p)$/) || [])[1] || '';
        const ratioLabel = ratio ? formatRatioLabel(ratio) : '';
        return [duration, ratioLabel, resolution].filter(Boolean).join(' / ') || model;
    }
    if (model === 'firefly-gpt-image-2-4k') {
        return '4K / 默认比例';
    }
    // GPT Image 2 4K 模型特殊处理
    if (model.includes('gpt-image-2-4k-')) {
        const match = model.match(/gpt-image-2-4k-(\d+)x(\d+)-([hml])/);
        if (match) {
            const w = match[1], h = match[2], quality = match[3];
            const qualityMap = { h: '高质量', m: '中质量', l: '低质量' };
            const qLabel = qualityMap[quality] || quality;
            return `4K / ${formatRatioLabel(`${w}x${h}`)} / ${qLabel}`;
        }
    }
    
    const ratioMatch = model.match(/(\d+)x(\d+)/);
    if (ratioMatch) {
        const size = getImageSizeLabel(model);
        return [size, formatRatioLabel(`${ratioMatch[1]}x${ratioMatch[2]}`)].filter(Boolean).join(' / ');
    }
    return model;
}

function getImageSizeLabel(model) {
    if (model.includes('gpt-image-2-4k')) return '4K';
    const size = model.match(/-(1k|2k|4k)(?:-|$)/i);
    return size ? size[1].toUpperCase() : '';
}

function formatRatioLabel(ratio) {
    const match = String(ratio || '').match(/^(\d+)x(\d+)$/);
    if (!match) return ratio;
    const w = parseInt(match[1], 10);
    const h = parseInt(match[2], 10);
    const direction = w === h ? '方形' : (w > h ? '横屏' : '竖屏');
    return `${w}:${h} ${direction}`;
}

function isVideoModel(model) {
    return !!model && (
        model.startsWith('firefly-sora2-') ||
        model.startsWith('firefly-veo31-') ||
        model.startsWith('firefly-kling3-')
    );
}

function isVideoMode() {
    return currentMode === 'text2video' || currentMode === 'image2video';
}

function isImageInputMode() {
    return currentMode === 'image2image' || currentMode === 'image2video';
}

function switchResolution(resolution) {
    if (resolution === 'Video') {
        resolution = '2K';
    }
    currentResolution = resolution;
    localStorage.setItem('resolution', currentResolution);
    document.querySelectorAll('.resolution-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.res === currentResolution);
    });
    updateModels();
}

function applyModeUi() {
    const uploadArea = document.getElementById('uploadArea');
    const batchArea = document.getElementById('batchArea');
    const videoBatchArea = document.getElementById('videoBatchArea');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const messageInput = document.getElementById('messageInput');
    const resultLoadingText = document.querySelector('#resultLoading span');

    if (isImageInputMode()) {
        uploadArea.style.display = 'flex';
        updateUploadSlotsForMode();
        uploadArea.querySelector('.upload-footer span').textContent = isVideoMode()
            ? '参考图：Sora 支持 1 张；Veo/Kling 支持 1-3 张，单张建议不超过 10MB'
            : '📎 参考图最大支持 10MB';
    } else {
        uploadArea.style.display = 'none';
    }

    batchArea.style.display = currentMode === 'batch' ? 'block' : 'none';
    videoBatchArea.style.display = currentMode === 'videoBatch' ? 'block' : 'none';
    welcomeMessage.style.display = currentMode === 'batch' || currentMode === 'videoBatch' || isImageInputMode() ? 'none' : 'flex';
    messageInput.placeholder = isVideoMode()
        ? '描述你想生成的视频镜头、运动、主体和风格...'
        : '描述你想要生成的图片...';
    if (resultLoadingText) {
        resultLoadingText.textContent = isVideoMode() ? '正在生成视频...' : '正在生成图片...';
    }
}

function updateUploadSlotsForMode() {
    const maxSlots = currentMode === 'image2video' ? 3 : 6;
    document.querySelectorAll('.upload-item').forEach((item, index) => {
        item.style.display = index < maxSlots ? 'block' : 'none';
        if (index >= maxSlots && uploadedImages[index]) {
            uploadedImages[index] = null;
            updateUploadPreview(index);
        }
    });
}

function maxVideoReferenceImages(model) {
    if (model.startsWith('firefly-sora2-')) return 1;
    if (model.startsWith('firefly-veo31-ref-')) return 3;
    if (model.startsWith('firefly-veo31-')) return 2;
    if (model.startsWith('firefly-kling3-')) return 2;
    return 1;
}

// 设置事件监听
function setupEventListeners() {
    // 输入框快捷键
    const input = document.getElementById('messageInput');
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendGenerate();
        }
    });

    // 生成按钮
    document.getElementById('generateBtn').addEventListener('click', sendGenerate);

    // 模式切换
    document.querySelectorAll('.mode-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            if (this.dataset.mode === 'text2video' || this.dataset.mode === 'image2video' || this.dataset.mode === 'videoBatch') {
                return;
            }
            document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentMode = this.dataset.mode;
            if (isVideoMode()) {
                switchResolution('Video');
            } else if (currentMode === 'videoBatch') {
                updateVideoBatchModels();
            } else if (currentMode === 'batch') {
                currentResolution = document.getElementById('batchResolutionSelect').value;
                updateBatchModels();
            } else if (currentMode !== 'batch' && currentResolution === 'Video') {
                switchResolution('2K');
            }
            applyModeUi();
        });
    });

    // 分辨率按钮
    document.querySelectorAll('.resolution-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchResolution(this.dataset.res);
            if (currentResolution === 'Video' && (currentMode === 'text2image' || currentMode === 'image2image')) {
                currentMode = currentMode === 'image2image' ? 'image2video' : 'text2video';
                document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
                document.querySelector(`.mode-tab[data-mode="${currentMode}"]`).classList.add('active');
            } else if (currentResolution !== 'Video' && isVideoMode()) {
                currentMode = currentMode === 'image2video' ? 'image2image' : 'text2image';
                document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
                document.querySelector(`.mode-tab[data-mode="${currentMode}"]`).classList.add('active');
            }
            applyModeUi();
        });
    });

    // 批量生成分辨率切换
    document.getElementById('batchResolutionSelect').addEventListener('change', function() {
        currentResolution = this.value;
        updateBatchModels();
    });

    const apiKeyInput = document.getElementById('apiKey');
    const apiKeySaved = document.getElementById('apiKeySaved');
    const rememberApiKey = document.getElementById('rememberApiKey');

    function saveApiKey() {
        const remember = rememberApiKey && rememberApiKey.checked;
        localStorage.setItem('rememberApiKey', remember ? '1' : '0');
        const value = apiKeyInput.value.trim();
        if (remember && value) {
            localStorage.setItem('apiKey', value);
            apiKeySaved.style.display = 'inline';
        } else {
            localStorage.removeItem('apiKey');
            apiKeySaved.style.display = 'none';
        }
    }

    apiKeyInput.addEventListener('blur', saveApiKey);

    apiKeyInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            saveApiKey();
            apiKeyInput.blur();
        }
    });

    if (rememberApiKey) {
        rememberApiKey.addEventListener('change', function() {
            if (!this.checked) {
                localStorage.setItem('rememberApiKey', '0');
                localStorage.removeItem('apiKey');
                apiKeySaved.style.display = 'none';
            } else {
                localStorage.setItem('rememberApiKey', '1');
                saveApiKey();
            }
        });
    }
}

// 触发上传（指定索引）
function triggerUpload(index) {
    currentUploadIndex = index;
    document.getElementById('imageInput').click();
}

// 处理图片上传
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        uploadedImages[currentUploadIndex] = e.target.result;
        updateUploadPreview(currentUploadIndex);
    };
    reader.readAsDataURL(file);
}

// 更新上传预览
function updateUploadPreview(index) {
    const item = document.querySelectorAll('.upload-item')[index];
    const img = item.querySelector('.preview-img');
    const placeholder = item.querySelector('.upload-placeholder');
    const removeBtn = item.querySelector('.btn-remove');
    
    if (uploadedImages[index]) {
        img.src = uploadedImages[index];
        img.style.display = 'block';
        placeholder.style.display = 'none';
        removeBtn.style.display = 'block';
    } else {
        img.src = '';
        img.style.display = 'none';
        placeholder.style.display = 'flex';
        removeBtn.style.display = 'none';
    }
}

// 移除已上传图片
function removeUploadedImage(index) {
    uploadedImages[index] = null;
    updateUploadPreview(index);
    document.getElementById('imageInput').value = '';
}

/**
 * 若服务端仍返回上游英文说明，转为对用户可读的中文。
 */
function localizeApiErrorMessage(status, rawMsg) {
    const msg = (rawMsg || '').trim();
    if (!msg) return msg;
    const low = msg.toLowerCase();
    if (
        status === 400 &&
        (low.includes('image too large') ||
            low.includes('image_too_large') ||
            (low.includes('too large') && low.includes('mb') && low.includes('max')))
    ) {
        return (
            '参考图体积过大：上游限制单张不超过约 10MB，请压缩或裁剪图片后再试；' +
            '多张参考图时可减少张数。'
        );
    }
    if (status === 400 && low.includes('payload too large')) {
        return '请求体过大：请压缩参考图或减少图片数量后再试。';
    }
    return msg;
}

function formatStructuredError(data, fallbackStatus) {
    if (!data || typeof data !== 'object') {
        return localizeApiErrorMessage(fallbackStatus || 500, '');
    }
    const status = data.statusCode || data.upstreamStatus || fallbackStatus || 500;
    const parts = [];
    const main = localizeApiErrorMessage(status, data.error || '请求失败');
    if (main) parts.push(main);
    if (data.hint) parts.push(`建议：${data.hint}`);

    const details = [];
    if (data.code) details.push(`错误码 ${data.code}`);
    if (data.stage) details.push(`阶段 ${data.stage}`);
    if (data.upstreamStatus) details.push(`上游 HTTP ${data.upstreamStatus}`);
    if (details.length) parts.push(`技术信息：${details.join(' / ')}`);

    if (data.upstreamMessage && data.upstreamMessage !== data.error) {
        parts.push(`上游原始信息：${String(data.upstreamMessage).slice(0, 300)}`);
    }
    return parts.join('\n');
}

/**
 * 请求失败后展示给用户的说明：优先使用服务端 JSON 里的 error 字段。
 */
function describeHttpFailure(status, responseText) {
    if (responseText && responseText.trim()) {
        try {
            const j = JSON.parse(responseText);
            if (j && typeof j === 'object' && (j.error || j.hint || j.code)) {
                return formatStructuredError(j, status);
            }
        } catch (_) {
            const snippet = responseText.trim().slice(0, 120);
            if (snippet && status >= 500) {
                return `服务暂时异常（HTTP ${status}）。请稍后重试；若持续出现请联系管理员。`;
            }
        }
    }
    const hints = {
        400: '请求无效：请检查是否选择了模型、填写了提示词；图生图时请上传参考图，且单张参考图建议不超过约 10MB。',
        401: '认证失败：API Key 无效、已过期或未填写。请在右侧「API 设置」中重新粘贴密钥，或登录控制台核对 Key 是否仍然有效。',
        403: '权限不足：当前 Key 无权使用该模型或调用接口，请更换 Key 或联系管理员开通权限。',
        404: '接口不存在或服务未就绪，请稍后重试。',
        408: '请求超时，请稍后重试。',
        413: '上传内容过大：请减少参考图数量或缩小图片后再试。',
        429: '请求过于频繁：请等待片刻后再生成。',
        500: '服务器处理出错：请稍后重试；若反复出现请截图联系管理员。',
        502: '上游网关或服务不可用：请稍后重试。',
        503: '服务繁忙或维护中：请稍后再试。',
    };
    return hints[status] || `请求未完成（HTTP ${status}）。请检查网络后重试；若多次失败请联系管理员。`;
}

async function submitGenerateJob(requestBody) {
    const response = await fetchWithRetry('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    });
    const responseText = await response.text();
    if (!response.ok) {
        throw new Error(describeHttpFailure(response.status, responseText));
    }
    let data = null;
    try {
        data = JSON.parse(responseText);
    } catch (_) {
        throw new Error('任务提交成功但响应格式异常');
    }
    if (!data || !data.jobId) {
        throw new Error('任务提交失败：缺少 jobId');
    }
    return data.jobId;
}

async function pollGenerateJob(jobId, timeout = 600000) {
    const startedAt = Date.now();
    while (Date.now() - startedAt < timeout) {
        const response = await fetchWithRetry(`/api/jobs/${encodeURIComponent(jobId)}`, {
            method: 'GET'
        }, 2, 30000);
        const responseText = await response.text();
        if (!response.ok) {
            throw new Error(describeHttpFailure(response.status, responseText));
        }
        let data = {};
        try {
            data = JSON.parse(responseText);
        } catch (_) {
            throw new Error('任务查询响应格式错误');
        }
        if (data.status === 'succeeded') return data.result || {};
        if (data.status === 'failed') {
            throw new Error(formatStructuredError(data, data.statusCode || 500));
        }
        await new Promise(resolve => setTimeout(resolve, 1500));
    }
    throw new Error('任务等待超时，请稍后重试');
}

// 发送生成请求
async function sendGenerate() {
    const prompt = document.getElementById('messageInput').value.trim();
    const apiKey = document.getElementById('apiKey').value.trim();
    const model = document.getElementById('modelSelect').value;
    
    if (!apiKey) {
        alert('请输入 API Key');
        return;
    }
    
    if (!prompt) {
        alert('请输入描述');
        return;
    }
    
    if (isVideoMode() && !isVideoModel(model)) {
        alert('请选择 Video 分组中的视频模型');
        return;
    }

    if (!isVideoMode() && isVideoModel(model)) {
        alert('视频模型请使用文生视频或图生视频模式');
        return;
    }

    // 图生图/图生视频模式检查（至少上传一张图）
    if (isImageInputMode() && !uploadedImages.some(img => img !== null)) {
        alert('请至少上传一张参考图');
        return;
    }
    
    // 显示加载状态
    const btn = document.getElementById('generateBtn');
    btn.disabled = true;
    btn.textContent = '生成中...';
    
    // 添加提示词到历史
    addToHistory(prompt);
    
    // 显示结果区域
    document.getElementById('resultArea').style.display = 'block';
    document.getElementById('welcomeMessage').style.display = 'none';
    document.getElementById('resultLoading').style.display = 'flex';
    document.getElementById('resultContent').innerHTML = '';
    
    try {
        const requestBody = {
            apiKey: apiKey,
            model: model,
            prompt: prompt
        };
        
        // 图生图/图生视频模式添加多张参考图
        if (isImageInputMode()) {
            const images = uploadedImages.filter(img => img !== null);
            if (isVideoMode() && images.length > maxVideoReferenceImages(model)) {
                alert(`当前视频模型最多支持 ${maxVideoReferenceImages(model)} 张参考图`);
                return;
            }
            if (images.length === 1) {
                requestBody.image = images[0];
            } else {
                requestBody.images = images;
            }
        }
        
        btn.textContent = '排队中...';
        const jobId = await submitGenerateJob(requestBody);
        btn.textContent = '生成中...';
        const data = await pollGenerateJob(jobId);
        renderResult(data);

    } catch (error) {
        document.getElementById('resultLoading').style.display = 'none';
        let errorMsg = error.message || '请求失败';
        if (error.name === 'AbortError') {
            errorMsg = '请求超时(3分钟)，请检查网络后重试';
        } else if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('net::ERR'))) {
            errorMsg = '网络连接被重置，已自动重试多次，请重试';
        }
        document.getElementById('resultContent').innerHTML = renderErrorBlock(errorMsg);
        console.error('Request error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = '开始生成';
    }
}

function renderErrorBlock(message) {
    const lines = String(message || '请求失败').split('\n').filter(Boolean);
    const title = lines.shift() || '请求失败';
    const detail = lines.map(line => `<p>${escapeHtml(line)}</p>`).join('');
    return `<div class="error"><strong>${escapeHtml(title)}</strong>${detail}</div>`;
}

// 将 HTTP URL 转换为 HTTPS，解决混合内容问题
function ensureHttps(url) {
    if (!url) return url;
    // 将 HTTP URL 转换为 HTTPS
    if (url.startsWith('http://')) {
        return url.replace('http://', 'https://');
    }
    return url;
}

// 查看大图
function viewImage(url) {
    window.open(ensureHttps(url), '_blank');
}

function renderResult(data) {
    const mediaType = data.mediaType || (data.video ? 'video' : 'image');
    const rawUrl = data.video || data.image || data.media;
    const mediaUrl = ensureHttps(rawUrl);
    document.getElementById('resultLoading').style.display = 'none';

    if (!mediaUrl) {
        document.getElementById('resultContent').innerHTML = '<div class="error">未找到生成媒体</div>';
        return;
    }

    if (mediaType === 'video') {
        document.getElementById('resultContent').innerHTML = `
            <video src="${mediaUrl}" controls playsinline preload="metadata"></video>
            <div class="result-actions">
                <button onclick="viewImage('${mediaUrl}')">打开视频</button>
                <button onclick="downloadMedia('${mediaUrl}', 'video')">下载</button>
            </div>
        `;
        return;
    }

    document.getElementById('resultContent').innerHTML = `
        <img src="${mediaUrl}" alt="生成结果" onclick="window.open('${mediaUrl}', '_blank')">
        <div class="result-actions">
            <button onclick="viewImage('${mediaUrl}')">查看大图</button>
            <button onclick="downloadMedia('${mediaUrl}', 'image')">下载</button>
        </div>
    `;
}

// 下载媒体（代理下载失败时会弹出可读错误说明）
async function downloadMedia(url, mediaType = 'image') {
    console.log('下载媒体:', url);
    if (!url) {
        alert('没有可下载的媒体');
        return;
    }

    if (url.startsWith('data:')) {
        const link = document.createElement('a');
        link.href = url;
        link.download = mediaType === 'video' ? `ai-video-${Date.now()}.mp4` : `ai-image-${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        return;
    }

    const downloadUrl = `/api/download?url=${encodeURIComponent(url)}`;
    console.log('下载链接:', downloadUrl);

    try {
        const response = await fetch(downloadUrl);
        if (!response.ok) {
            const text = await response.text();
            alert(describeHttpFailure(response.status, text));
            return;
        }
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = mediaType === 'video' ? `ai-video-${Date.now()}.mp4` : `ai-image-${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error('下载失败:', error);
        try {
            window.open(downloadUrl, '_blank');
        } catch (_) {}
    }
}

function downloadImage(url) {
    return downloadMedia(url, 'image');
}

// 历史记录
function addToHistory(prompt) {
    const history = JSON.parse(localStorage.getItem('promptHistory') || '[]');
    const item = { id: Date.now(), prompt: prompt, time: new Date().toLocaleString() };
    history.unshift(item);
    if (history.length > 20) history.pop();
    localStorage.setItem('promptHistory', JSON.stringify(history));
    loadHistory();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('promptHistory') || '[]');
    const container = document.getElementById('historyList');
    container.innerHTML = history.map(item => `
        <div class="history-item" title="${escapeHtml(item.prompt)}" onclick="useHistoryPrompt('${escapeHtml(item.prompt)}')">
            <div class="history-prompt">${escapeHtml(item.prompt)}</div>
        </div>
    `).join('');
}

function useHistoryPrompt(prompt) {
    document.getElementById('messageInput').value = prompt;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function clearHistory() {
    localStorage.removeItem('promptHistory');
    loadHistory();
}

// ==================== 批量生成功能 ====================

// 初始化批量模型选择
function ensureBatchTaskCards() {
    const grid = document.querySelector('#batchArea .batch-grid');
    if (!grid) return;

    for (let index = grid.querySelectorAll('.batch-card').length; index < batchTasks.length; index++) {
        const card = document.createElement('div');
        card.className = 'batch-card';
        card.dataset.taskId = String(index);
        card.innerHTML = `
            <div class="batch-card-header">
                <span class="batch-card-title">任务 ${index + 1}</span>
                <span class="batch-card-status" data-status="pending">待开始</span>
                <button class="btn-clear-task" onclick="clearTask(${index})">x</button>
            </div>
            <div class="batch-card-images">
                <div class="batch-upload-item" onclick="triggerBatchUpload(${index}, 0)"><span>+</span></div>
                <div class="batch-upload-item" onclick="triggerBatchUpload(${index}, 1)"><span>+</span></div>
                <div class="batch-upload-item" onclick="triggerBatchUpload(${index}, 2)"><span>+</span></div>
            </div>
            <textarea class="batch-prompt" placeholder="输入提示词..." rows="2"></textarea>
            <div class="batch-card-result" style="display: none;">
                <img src="" alt="结果">
            </div>
            <div class="batch-card-actions">
                <button class="btn-batch-start" onclick="startTask(${index})">开始</button>
            </div>
        `;
        grid.appendChild(card);
    }
}

function getBatchCards() {
    return document.querySelectorAll('#batchArea .batch-card');
}

function initBatchModelSelect() {
    updateBatchModels();
}

// 更新批量模型列表
function updateBatchModels() {
    const select = document.getElementById('batchModelSelect');

    if (currentResolution === 'Video') {
        currentResolution = '2K';
    }
    const models = (modelsData[currentResolution] || []).filter(model => !isVideoModel(model));
    renderModelOptions(select, models);
}

// 应用设置到所有任务
function applySettingsToAll() {
    const model = document.getElementById('batchModelSelect').value;
    const resolution = document.getElementById('batchResolutionSelect').value;

    // 更新所有卡片的提示输入框placeholder或提示（这里只是视觉反馈）
    const cards = getBatchCards();
    cards.forEach((card, index) => {
        // 保存当前提示词
        const task = batchTasks[index];
        // 更新状态显示
        updateTaskStatus(index);
    });

    alert('已应用设置到所有任务');
}

// 触发批量上传
function triggerBatchUpload(taskIndex, imgIndex) {
    currentBatchUploadTask = taskIndex;
    currentBatchUploadIndex = imgIndex;
    document.getElementById('batchImageInput').click();
}

// 处理批量图片上传
function handleBatchImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        batchTasks[currentBatchUploadTask].images[currentBatchUploadIndex] = e.target.result;
        updateBatchUploadPreview(currentBatchUploadTask, currentBatchUploadIndex);
    };
    reader.readAsDataURL(file);
}

// 更新批量上传预览
function updateBatchUploadPreview(taskIndex, imgIndex) {
    const card = getBatchCards()[taskIndex];
    const imgContainer = card.querySelectorAll('.batch-upload-item')[imgIndex];
    const img = batchTasks[taskIndex].images[imgIndex];

    if (img) {
        imgContainer.classList.add('has-image');
        imgContainer.innerHTML = `<img src="${img}" alt="参考图"><button class="btn-remove-img" onclick="event.stopPropagation(); removeBatchImage(${taskIndex}, ${imgIndex})">✕</button>`;
    } else {
        imgContainer.classList.remove('has-image');
        imgContainer.innerHTML = '<span>+</span>';
    }
}

// 移除批量图片
function removeBatchImage(taskIndex, imgIndex) {
    batchTasks[taskIndex].images[imgIndex] = null;
    updateBatchUploadPreview(taskIndex, imgIndex);
}

function initVideoBatch() {
    renderVideoBatchCards();
    updateVideoBatchModels();
}

function updateVideoBatchModels() {
    const select = document.getElementById('videoBatchModelSelect');
    if (!select) return;

    const models = modelsData.Video || [];
    renderModelOptions(select, models);
}

function renderVideoBatchCards() {
    const grid = document.getElementById('videoBatchGrid');
    if (!grid) return;
    grid.innerHTML = videoBatchTasks.map((_, index) => `
        <div class="batch-card video-batch-card" data-video-task-id="${index}">
            <div class="batch-card-header">
                <span class="batch-card-title">视频 ${index + 1}</span>
                <span class="batch-card-status" data-status="pending">待开始</span>
                <button class="btn-clear-task" onclick="clearVideoTask(${index})">×</button>
            </div>
            <div class="batch-card-images">
                <div class="batch-upload-item" onclick="triggerVideoBatchUpload(${index}, 0)"><span>+</span></div>
                <div class="batch-upload-item" onclick="triggerVideoBatchUpload(${index}, 1)"><span>+</span></div>
                <div class="batch-upload-item" onclick="triggerVideoBatchUpload(${index}, 2)"><span>+</span></div>
            </div>
            <textarea class="batch-prompt" placeholder="输入视频提示词..." rows="3"></textarea>
            <div class="batch-card-result" style="display: none;"></div>
            <div class="batch-card-actions">
                <button class="btn-batch-start" onclick="startVideoTask(${index})">开始</button>
            </div>
        </div>
    `).join('');
    videoBatchTasks.forEach((_, index) => updateVideoTaskUI(index));
}

function triggerVideoBatchUpload(taskIndex, imgIndex) {
    currentVideoBatchUploadTask = taskIndex;
    currentVideoBatchUploadIndex = imgIndex;
    document.getElementById('videoBatchImageInput').click();
}

function handleVideoBatchImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        videoBatchTasks[currentVideoBatchUploadTask].images[currentVideoBatchUploadIndex] = e.target.result;
        updateVideoBatchUploadPreview(currentVideoBatchUploadTask, currentVideoBatchUploadIndex);
    };
    reader.readAsDataURL(file);
    event.target.value = '';
}

function updateVideoBatchUploadPreview(taskIndex, imgIndex) {
    const card = document.querySelectorAll('.video-batch-card')[taskIndex];
    const imgContainer = card.querySelectorAll('.batch-upload-item')[imgIndex];
    const img = videoBatchTasks[taskIndex].images[imgIndex];

    if (img) {
        imgContainer.classList.add('has-image');
        imgContainer.innerHTML = `<img src="${img}" alt="参考图"><button class="btn-remove-img" onclick="event.stopPropagation(); removeVideoBatchImage(${taskIndex}, ${imgIndex})">✕</button>`;
    } else {
        imgContainer.classList.remove('has-image');
        imgContainer.innerHTML = '<span>+</span>';
    }
}

function removeVideoBatchImage(taskIndex, imgIndex) {
    videoBatchTasks[taskIndex].images[imgIndex] = null;
    updateVideoBatchUploadPreview(taskIndex, imgIndex);
}

// 带超时和重试的 fetch 函数
async function fetchWithRetry(url, options, retries = 3, timeout = 180000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const fetchOptions = {
        ...options,
        signal: controller.signal
    };

    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            const response = await fetch(url, fetchOptions);
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (attempt === retries) {
                throw error;
            }
            // 网络错误时重试
            const isNetworkError = error.name === 'AbortError' ||
                                    error.message.includes('Failed to fetch') ||
                                    error.message.includes('net::ERR') ||
                                    error.message.includes('network');
            if (isNetworkError) {
                console.log(`请求失败，${attempt}/${retries} 次重试...`);
                await new Promise(resolve => setTimeout(resolve, 2000 * attempt));
                const newController = new AbortController();
                setTimeout(() => newController.abort(), timeout);
                fetchOptions.signal = newController.signal;
            } else {
                throw error;
            }
        }
    }
}

// 开始单个任务
async function startTask(taskIndex) {
    const task = batchTasks[taskIndex];
    const card = getBatchCards()[taskIndex];
    const promptInput = card.querySelector('.batch-prompt');
    const btn = card.querySelector('.btn-batch-start');

    // 获取提示词
    task.prompt = promptInput.value.trim();

    if (!task.prompt) {
        alert('请输入提示词');
        return;
    }

    // 检查API Key
    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        alert('请输入 API Key');
        return;
    }

    // 更新状态
    task.status = 'generating';
    updateTaskUI(taskIndex);

    try {
        const selectedModel = document.getElementById('batchModelSelect').value;
        if (isVideoModel(selectedModel)) {
            alert('图片批量不支持视频模型，请使用「视频批量」模块');
            task.status = 'failed';
            updateTaskUI(taskIndex);
            return;
        }
        const requestBody = {
            apiKey: apiKey,
            model: selectedModel,
            prompt: task.prompt
        };

        // 添加参考图
        const images = task.images.filter(img => img !== null);
        if (images.length > 0) {
            if (isVideoModel(selectedModel) && images.length > maxVideoReferenceImages(selectedModel)) {
                alert(`任务${taskIndex + 1}参考图过多：当前视频模型最多支持 ${maxVideoReferenceImages(selectedModel)} 张`);
                task.status = 'failed';
                updateTaskUI(taskIndex);
                return;
            }
            requestBody.images = images;
        }

        const jobId = await submitGenerateJob(requestBody);
        const data = await pollGenerateJob(jobId);

        if (data.image || data.video || data.media) {
            task.result = ensureHttps(data.image || data.video || data.media);
            task.mediaType = data.mediaType || (data.video ? 'video' : 'image');
            task.status = 'completed';
            updateTaskUI(taskIndex);
        }

    } catch (error) {
        task.status = 'failed';
        updateTaskUI(taskIndex);
        console.error('Task error:', error);
        let errorMsg = error.message || '网络连接失败';
        if (error.name === 'AbortError') {
            errorMsg = '请求超时(3分钟)，请检查网络后重试';
        } else if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('net::ERR'))) {
            errorMsg = '网络连接被重置，已自动重试多次，请重试';
        }
        alert(`任务${taskIndex + 1}错误: ${errorMsg}`);
    }
}

// 更新任务UI
function updateTaskUI(taskIndex) {
    const task = batchTasks[taskIndex];
    const card = getBatchCards()[taskIndex];
    const statusEl = card.querySelector('.batch-card-status');
    const btn = card.querySelector('.btn-batch-start');
    const resultEl = card.querySelector('.batch-card-result');

    // 更新状态标签
    statusEl.dataset.status = task.status;
    const statusMap = {
        pending: '待开始',
        generating: '生成中',
        completed: '已完成',
        failed: '失败'
    };
    statusEl.textContent = statusMap[task.status] || '待开始';

    // 更新按钮
    btn.dataset.status = task.status;
    const btnMap = {
        pending: '开始',
        generating: '停止',
        completed: '下载',
        failed: '重试'
    };
    btn.textContent = btnMap[task.status] || '开始';

    // 绑定新的点击事件
    btn.onclick = () => {
        if (task.status === 'pending') startTask(taskIndex);
        else if (task.status === 'generating') task.status = 'pending';
        else if (task.status === 'completed') downloadMedia(task.result, task.mediaType || 'image');
        else if (task.status === 'failed') startTask(taskIndex);
    };

    // 更新结果
    if (task.result) {
        resultEl.style.display = 'block';
        if (task.mediaType === 'video') {
            resultEl.innerHTML = `<video src="${task.result}" controls playsinline preload="metadata"></video>`;
            resultEl.querySelector('video').onclick = () => window.open(task.result, '_blank');
        } else {
            resultEl.innerHTML = `<img src="${task.result}" alt="结果">`;
            resultEl.querySelector('img').onclick = () => window.open(task.result, '_blank');
        }
    } else {
        resultEl.style.display = 'none';
    }
}

// 更新任务状态显示
function updateTaskStatus(taskIndex) {
    const task = batchTasks[taskIndex];
    const card = getBatchCards()[taskIndex];
    const statusEl = card.querySelector('.batch-card-status');
    statusEl.dataset.status = task.status;
}

// 清除单个任务
function clearTask(taskIndex) {
    batchTasks[taskIndex] = {
        images: [null, null, null],
        prompt: '',
        result: null,
        mediaType: 'image',
        status: 'pending'
    };

    const card = getBatchCards()[taskIndex];
    card.querySelector('.batch-prompt').value = '';
    card.querySelector('.batch-card-result').style.display = 'none';

    // 清除图片预览
    const imgContainers = card.querySelectorAll('.batch-upload-item');
    imgContainers.forEach((container, index) => {
        container.classList.remove('has-image');
        container.innerHTML = '<span>+</span>';
    });

    updateTaskUI(taskIndex);
}

// 全部开始
async function startAllTasks() {
    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        alert('请输入 API Key');
        return;
    }

    // 获取所有有提示词的任务并开始
    for (let i = 0; i < batchTasks.length; i++) {
        const task = batchTasks[i];
        const card = getBatchCards()[i];
        task.prompt = card.querySelector('.batch-prompt').value.trim();

        if (task.prompt && task.status === 'pending') {
            await startTask(i);
        }
    }
}

// 清除所有任务
function clearAllTasks() {
    for (let i = 0; i < batchTasks.length; i++) {
        clearTask(i);
    }
}

// 下载所有结果
function downloadAllResults() {
    let hasResults = false;

    batchTasks.forEach((task, index) => {
        if (task.result) {
            hasResults = true;
            // 使用后端下载接口，支持跨域
            const link = document.createElement('a');
            link.href = `/api/download?url=${encodeURIComponent(task.result)}`;
            link.download = task.mediaType === 'video'
                ? `batch-video-${index + 1}-${Date.now()}.mp4`
                : `batch-image-${index + 1}-${Date.now()}.jpg`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });

    if (!hasResults) {
        alert('没有可下载的结果');
    }
}

async function startVideoTask(taskIndex) {
    const task = videoBatchTasks[taskIndex];
    const card = document.querySelectorAll('.video-batch-card')[taskIndex];
    const promptInput = card.querySelector('.batch-prompt');

    task.prompt = promptInput.value.trim();
    if (!task.prompt) {
        alert('请输入视频提示词');
        return;
    }

    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        alert('请输入 API Key');
        return;
    }

    const selectedModel = document.getElementById('videoBatchModelSelect').value;
    if (!selectedModel || !isVideoModel(selectedModel)) {
        alert('请选择视频模型');
        return;
    }

    const images = task.images.filter(img => img !== null);
    if (images.length > maxVideoReferenceImages(selectedModel)) {
        alert(`视频 ${taskIndex + 1} 参考图过多：当前模型最多支持 ${maxVideoReferenceImages(selectedModel)} 张`);
        return;
    }

    task.status = 'generating';
    updateVideoTaskUI(taskIndex);

    try {
        const requestBody = {
            apiKey,
            model: selectedModel,
            prompt: task.prompt
        };
        if (images.length === 1) {
            requestBody.image = images[0];
        } else if (images.length > 1) {
            requestBody.images = images;
        }

        const jobId = await submitGenerateJob(requestBody);
        const data = await pollGenerateJob(jobId, 900000);
        if (data.video || data.media) {
            task.result = ensureHttps(data.video || data.media);
            task.mediaType = 'video';
            task.status = 'completed';
        } else {
            task.status = 'failed';
            alert(`视频 ${taskIndex + 1} 没有返回视频结果`);
        }
    } catch (error) {
        task.status = 'failed';
        console.error('Video task error:', error);
        alert(`视频 ${taskIndex + 1} 错误: ${error.message || '生成失败'}`);
    } finally {
        updateVideoTaskUI(taskIndex);
    }
}

function updateVideoTaskUI(taskIndex) {
    const task = videoBatchTasks[taskIndex];
    const card = document.querySelectorAll('.video-batch-card')[taskIndex];
    if (!card) return;
    const statusEl = card.querySelector('.batch-card-status');
    const btn = card.querySelector('.btn-batch-start');
    const resultEl = card.querySelector('.batch-card-result');

    const statusMap = {
        pending: '待开始',
        generating: '生成中',
        completed: '已完成',
        failed: '失败'
    };
    statusEl.dataset.status = task.status;
    statusEl.textContent = statusMap[task.status] || '待开始';

    const btnMap = {
        pending: '开始',
        generating: '生成中',
        completed: '下载',
        failed: '重试'
    };
    btn.dataset.status = task.status;
    btn.textContent = btnMap[task.status] || '开始';
    btn.disabled = task.status === 'generating';
    btn.onclick = () => {
        if (task.status === 'completed') downloadMedia(task.result, 'video');
        else startVideoTask(taskIndex);
    };

    if (task.result) {
        resultEl.style.display = 'block';
        resultEl.innerHTML = `<video src="${task.result}" controls playsinline preload="metadata"></video>`;
    } else {
        resultEl.style.display = 'none';
        resultEl.innerHTML = '';
    }
}

function clearVideoTask(taskIndex) {
    videoBatchTasks[taskIndex] = {
        images: [null, null, null],
        prompt: '',
        result: null,
        mediaType: 'video',
        status: 'pending'
    };
    const card = document.querySelectorAll('.video-batch-card')[taskIndex];
    card.querySelector('.batch-prompt').value = '';
    card.querySelector('.batch-card-result').style.display = 'none';
    card.querySelectorAll('.batch-upload-item').forEach(container => {
        container.classList.remove('has-image');
        container.innerHTML = '<span>+</span>';
    });
    updateVideoTaskUI(taskIndex);
}

async function startAllVideoTasks() {
    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        alert('请输入 API Key');
        return;
    }

    for (let i = 0; i < videoBatchTasks.length; i++) {
        const task = videoBatchTasks[i];
        const card = document.querySelectorAll('.video-batch-card')[i];
        task.prompt = card.querySelector('.batch-prompt').value.trim();
        if (task.prompt && task.status === 'pending') {
            await startVideoTask(i);
        }
    }
}

function clearAllVideoTasks() {
    for (let i = 0; i < videoBatchTasks.length; i++) {
        clearVideoTask(i);
    }
}

function downloadAllVideoResults() {
    let hasResults = false;
    videoBatchTasks.forEach((task, index) => {
        if (task.result) {
            hasResults = true;
            const link = document.createElement('a');
            link.href = `/api/download?url=${encodeURIComponent(task.result)}`;
            link.download = `batch-video-${index + 1}-${Date.now()}.mp4`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });

    if (!hasResults) {
        alert('没有可下载的视频结果');
    }
}
