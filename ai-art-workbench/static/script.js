// 模型数据
const MODELS = {
    "1K": [
        // firefly-gpt-image-2 系列
        "firefly-gpt-image-2-16x9",
        "firefly-gpt-image-2-1x1",
        "firefly-gpt-image-2-2x3",
        "firefly-gpt-image-2-3x2",
        // nano-banana 系列
        "firefly-nano-banana-1k-16x9",
        "firefly-nano-banana-1k-1x1",
        "firefly-nano-banana-1k-21x9",
        "firefly-nano-banana-1k-3x4",
        "firefly-nano-banana-1k-4x3",
        "firefly-nano-banana-1k-4x5",
        "firefly-nano-banana-1k-5x4",
        "firefly-nano-banana-1k-9x16",
        "firefly-nano-banana-pro-1k-16x9",
        "firefly-nano-banana-pro-1k-1x1",
        "firefly-nano-banana-pro-1k-21x9",
        "firefly-nano-banana-pro-1k-3x4",
        "firefly-nano-banana-pro-1k-4x3",
        "firefly-nano-banana-pro-1k-4x5",
        "firefly-nano-banana-pro-1k-5x4",
        "firefly-nano-banana-pro-1k-9x16",
        "firefly-nano-banana2-1k-16x9",
        "firefly-nano-banana2-1k-1x1",
        "firefly-nano-banana2-1k-1x4",
        "firefly-nano-banana2-1k-1x8",
        "firefly-nano-banana2-1k-21x9",
        "firefly-nano-banana2-1k-2x3",
        "firefly-nano-banana2-1k-3x2",
        "firefly-nano-banana2-1k-3x4",
        "firefly-nano-banana2-1k-4x3",
        "firefly-nano-banana2-1k-4x5",
        "firefly-nano-banana2-1k-5x4",
        "firefly-nano-banana2-1k-8x1",
        "firefly-nano-banana2-1k-9x16",
    ],
    "2K": [
        "firefly-nano-banana-2k-16x9",
        "firefly-nano-banana-2k-1x1",
        "firefly-nano-banana-2k-21x9",
        "firefly-nano-banana-2k-3x4",
        "firefly-nano-banana-2k-4x3",
        "firefly-nano-banana-2k-4x5",
        "firefly-nano-banana-2k-5x4",
        "firefly-nano-banana-2k-9x16",
        "firefly-nano-banana-pro-2k-16x9",
        "firefly-nano-banana-pro-2k-1x1",
        "firefly-nano-banana-pro-2k-21x9",
        "firefly-nano-banana-pro-2k-3x4",
        "firefly-nano-banana-pro-2k-4x3",
        "firefly-nano-banana-pro-2k-4x5",
        "firefly-nano-banana-pro-2k-5x4",
        "firefly-nano-banana-pro-2k-9x16",
        "firefly-nano-banana2-2k-16x9",
        "firefly-nano-banana2-2k-1x1",
        "firefly-nano-banana2-2k-1x4",
        "firefly-nano-banana2-2k-1x8",
        "firefly-nano-banana2-2k-21x9",
        "firefly-nano-banana2-2k-2x3",
        "firefly-nano-banana2-2k-3x2",
        "firefly-nano-banana2-2k-3x4",
        "firefly-nano-banana2-2k-4x3",
        "firefly-nano-banana2-2k-4x5",
        "firefly-nano-banana2-2k-5x4",
        "firefly-nano-banana2-2k-8x1",
        "firefly-nano-banana2-2k-9x16",
    ],
    "4K": [
        "firefly-nano-banana-4k-16x9",
        "firefly-nano-banana-4k-1x1",
        "firefly-nano-banana-4k-21x9",
        "firefly-nano-banana-4k-3x4",
        "firefly-nano-banana-4k-4x3",
        "firefly-nano-banana-4k-4x5",
        "firefly-nano-banana-4k-5x4",
        "firefly-nano-banana-4k-9x16",
        "firefly-nano-banana-pro-4k-16x9",
        "firefly-nano-banana-pro-4k-1x1",
        "firefly-nano-banana-pro-4k-21x9",
        "firefly-nano-banana-pro-4k-3x4",
        "firefly-nano-banana-pro-4k-4x3",
        "firefly-nano-banana-pro-4k-4x5",
        "firefly-nano-banana-pro-4k-5x4",
        "firefly-nano-banana-pro-4k-9x16",
        "firefly-nano-banana2-4k-16x9",
        "firefly-nano-banana2-4k-1x1",
        "firefly-nano-banana2-4k-1x4",
        "firefly-nano-banana2-4k-1x8",
        "firefly-nano-banana2-4k-21x9",
        "firefly-nano-banana2-4k-2x3",
        "firefly-nano-banana2-4k-3x2",
        "firefly-nano-banana2-4k-3x4",
        "firefly-nano-banana2-4k-4x3",
        "firefly-nano-banana2-4k-4x5",
        "firefly-nano-banana2-4k-5x4",
        "firefly-nano-banana2-4k-8x1",
        "firefly-nano-banana2-4k-9x16",
    ],
    "GPT2": [
        // firefly-gpt-image-2 标准比例
        "firefly-gpt-image-2-16x9",
        "firefly-gpt-image-2-1x1",
        "firefly-gpt-image-2-2x3",
        "firefly-gpt-image-2-3x2",
        "firefly-gpt-image-2-4x3",
        "firefly-gpt-image-2-4x5",
        "firefly-gpt-image-2-5x4",
        "firefly-gpt-image-2-9x16",
        // firefly-gpt-image-2-4k 系列 (h=高质量, l=低质量, m=中等质量)
        "firefly-gpt-image-2-4k-16x9-h",
        "firefly-gpt-image-2-4k-16x9-m",
        "firefly-gpt-image-2-4k-16x9-l",
        "firefly-gpt-image-2-4k-1x1-h",
        "firefly-gpt-image-2-4k-1x1-m",
        "firefly-gpt-image-2-4k-1x1-l",
        "firefly-gpt-image-2-4k-2x3-h",
        "firefly-gpt-image-2-4k-2x3-m",
        "firefly-gpt-image-2-4k-2x3-l",
        "firefly-gpt-image-2-4k-3x2-h",
        "firefly-gpt-image-2-4k-3x2-m",
        "firefly-gpt-image-2-4k-3x2-l",
        "firefly-gpt-image-2-4k-4x3-h",
        "firefly-gpt-image-2-4k-4x3-m",
        "firefly-gpt-image-2-4k-4x3-l",
        "firefly-gpt-image-2-4k-4x5-h",
        "firefly-gpt-image-2-4k-4x5-m",
        "firefly-gpt-image-2-4k-4x5-l",
        "firefly-gpt-image-2-4k-5x4-h",
        "firefly-gpt-image-2-4k-5x4-m",
        "firefly-gpt-image-2-4k-5x4-l",
        "firefly-gpt-image-2-4k-9x16-h",
        "firefly-gpt-image-2-4k-9x16-m",
        "firefly-gpt-image-2-4k-9x16-l",
    ],
};

// 状态
let currentResolution = '2K';
let currentMode = 'text2image';  // text2image 或 image2image 或 batch
let uploadedImages = [null, null, null, null, null, null];  // 6张参考图
let currentUploadIndex = 0;  // 当前上传的索引

// 批量生成状态
let batchTasks = [
    { images: [null, null, null], prompt: '', result: null, status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, status: 'pending' },
    { images: [null, null, null], prompt: '', result: null, status: 'pending' }
];
let currentBatchUploadTask = 0;
let currentBatchUploadIndex = 0;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadTheme();
    loadHistory();
    loadApiKey();
    initModelSelect();
    initBatchModelSelect();
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
    document.getElementById('welcomeMessage').style.display = 'flex';
    
    // 聚焦到输入框
    document.getElementById('messageInput').focus();
}

// 加载设置
function loadSettings() {
    currentResolution = localStorage.getItem('resolution') || '2K';

    // 更新UI
    document.querySelectorAll('.resolution-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.res === currentResolution);
    });

    // 更新模型列表
    updateModels();
}

// 加载保存的API Key
function loadApiKey() {
    const savedApiKey = localStorage.getItem('apiKey');
    if (savedApiKey) {
        document.getElementById('apiKey').value = savedApiKey;
        document.getElementById('apiKeySaved').style.display = 'inline';
    }
}

// 加载主题
function loadTheme() {
    const theme = localStorage.getItem('theme') || 'dark';
    setTheme(theme);
}

// 切换主题
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

// 设置主题
function setTheme(theme) {
    if (theme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
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
    select.innerHTML = '';
    
    const models = MODELS[currentResolution] || [];
    let lastVersion = '';
    
    models.forEach(model => {
        const version = getModelVersion(model);
        if (version !== lastVersion) {
            // 添加版本分组标题
            const group = document.createElement('optgroup');
            group.label = version;
            select.appendChild(group);
            lastVersion = version;
        }
        
        const option = document.createElement('option');
        option.value = model;
        option.textContent = '  ' + getRatioDisplay(model);
        select.appendChild(option);
    });
}

// 获取模型版本
function getModelVersion(model) {
    if (model.includes('gpt-image-2')) return 'firefly-gpt-image-2';
    if (model.includes('nano-banana-pro')) return 'firefly-nano-banana-pro';
    if (model.includes('nano-banana2')) return 'firefly-nano-banana2';
    if (model.includes('nano-banana')) return 'firefly-nano-banana';
    return model.split('-').slice(0, 3).join('-');
}

// 获取比例显示
function getRatioDisplay(model) {
    // GPT Image 2 4K 模型特殊处理
    if (model.includes('gpt-image-2-4k-')) {
        const match = model.match(/gpt-image-2-4k-(\d+)x(\d+)-([hml])/);
        if (match) {
            const w = match[1], h = match[2], quality = match[3];
            const qualityMap = { h: '高质量', m: '中质量', l: '低质量' };
            const qLabel = qualityMap[quality] || quality;
            const label = w === h ? '方形' : (parseInt(w) > parseInt(h) ? '横屏' : '竖屏');
            return `${w}:${h} ${label} (${qLabel})`;
        }
    }
    
    const ratioMatch = model.match(/(\d+)x(\d+)/);
    if (ratioMatch) {
        const w = ratioMatch[1];
        const h = ratioMatch[2];
        const label = w === h ? '方形' : (parseInt(w) > parseInt(h) ? '横屏' : '竖屏');
        return `${w}:${h} ${label}`;
    }
    return model;
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
            document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentMode = this.dataset.mode;

            const uploadArea = document.getElementById('uploadArea');
            const batchArea = document.getElementById('batchArea');

            if (currentMode === 'image2image') {
                uploadArea.style.display = 'flex';
                batchArea.style.display = 'none';
                document.getElementById('welcomeMessage').style.display = 'none';
            } else if (currentMode === 'batch') {
                uploadArea.style.display = 'none';
                batchArea.style.display = 'block';
                document.getElementById('welcomeMessage').style.display = 'none';
            } else {
                uploadArea.style.display = 'none';
                batchArea.style.display = 'none';
                document.getElementById('welcomeMessage').style.display = 'flex';
            }
        });
    });

    // 分辨率按钮
    document.querySelectorAll('.resolution-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.resolution-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentResolution = this.dataset.res;
            localStorage.setItem('resolution', currentResolution);
            updateModels();
        });
    });

    // 批量生成分辨率切换
    document.getElementById('batchResolutionSelect').addEventListener('change', function() {
        currentResolution = this.value;
        updateBatchModels();
    });

    // API Key 自动保存（使用 blur 事件，避免浏览器自动填充触发保存）
    const apiKeyInput = document.getElementById('apiKey');
    const apiKeySaved = document.getElementById('apiKeySaved');
    
    // 保存函数
    function saveApiKey() {
        const value = apiKeyInput.value.trim();
        if (value) {
            localStorage.setItem('apiKey', value);
            apiKeySaved.style.display = 'inline';
        } else {
            localStorage.removeItem('apiKey');
            apiKeySaved.style.display = 'none';
        }
    }
    
    // 失去焦点时保存（用户主动离开输入框时）
    apiKeyInput.addEventListener('blur', saveApiKey);
    
    // 按回车时也保存
    apiKeyInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            saveApiKey();
            apiKeyInput.blur();
        }
    });
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
    
    // 图生图模式检查（至少上传一张图）
    if (currentMode === 'image2image' && !uploadedImages.some(img => img !== null)) {
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
        
        // 图生图模式添加多张参考图
        if (currentMode === 'image2image') {
            const images = uploadedImages.filter(img => img !== null);
            if (images.length === 1) {
                requestBody.image = images[0];
            } else {
                requestBody.images = images;
            }
        }
        
        const response = await fetchWithRetry('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        // 检查响应状态
        if (!response.ok) {
            document.getElementById('resultLoading').style.display = 'none';
            document.getElementById('resultContent').innerHTML = `<div class="error">请求失败: HTTP ${response.status}</div>`;
            return;
        }

        // 检查响应内容
        const responseText = await response.text();
        if (!responseText.trim()) {
            document.getElementById('resultLoading').style.display = 'none';
            document.getElementById('resultContent').innerHTML = `<div class="error">服务器返回空响应，请稍后重试</div>`;
            return;
        }

        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            document.getElementById('resultLoading').style.display = 'none';
            console.error('JSON解析失败:', responseText.substring(0, 200));
            document.getElementById('resultContent').innerHTML = `<div class="error">响应格式错误，请稍后重试</div>`;
            return;
        }

        if (data.error) {
            document.getElementById('resultLoading').style.display = 'none';
            document.getElementById('resultContent').innerHTML = `<div class="error">生成失败: ${data.error}</div>`;
            if (data.debug) console.log('Debug:', data.debug);
            return;
        }

        if (data.image) {
            const httpsUrl = ensureHttps(data.image);
            document.getElementById('resultLoading').style.display = 'none';
            document.getElementById('resultContent').innerHTML = `
                <img src="${httpsUrl}" alt="生成结果" onclick="window.open('${httpsUrl}', '_blank')">
                <div class="result-actions">
                    <button onclick="viewImage('${httpsUrl}')">查看大图</button>
                    <button onclick="downloadImage('${httpsUrl}')">下载</button>
                </div>
            `;
        }

    } catch (error) {
        document.getElementById('resultLoading').style.display = 'none';
        let errorMsg = error.message;
        if (error.name === 'AbortError') {
            errorMsg = '请求超时(3分钟)，请检查网络后重试';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('net::ERR')) {
            errorMsg = '网络连接被重置，已自动重试多次，请重试';
        }
        document.getElementById('resultContent').innerHTML = `<div class="error">请求失败: ${errorMsg}</div>`;
        console.error('Request error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = '开始生成';
    }
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

// 下载图片
function downloadImage(url) {
    console.log('下载图片:', url);
    if (!url) {
        alert('没有可下载的图片');
        return;
    }

    // 如果是 data URL（base64），直接下载
    if (url.startsWith('data:')) {
        const link = document.createElement('a');
        link.href = url;
        link.download = `ai-image-${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        return;
    }

    // 通过后端代理下载（处理跨域问题）
    const downloadUrl = `/api/download?url=${encodeURIComponent(url)}`;
    console.log('下载链接:', downloadUrl);

    // 使用 fetch 下载并转换为 blob，然后触发下载
    fetch(downloadUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('下载失败: ' + response.status);
            }
            return response.blob();
        })
        .then(blob => {
            const blobUrl = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = `ai-image-${Date.now()}.jpg`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(blobUrl);
        })
        .catch(error => {
            console.error('下载失败:', error);
            // 降级：尝试直接打开链接
            window.open(downloadUrl, '_blank');
        });
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
        <div class="history-item" onclick="useHistoryPrompt('${escapeHtml(item.prompt)}')">
            <div class="history-prompt">${escapeHtml(item.prompt.substring(0, 50))}${item.prompt.length > 50 ? '...' : ''}</div>
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
function initBatchModelSelect() {
    updateBatchModels();
}

// 更新批量模型列表
function updateBatchModels() {
    const select = document.getElementById('batchModelSelect');
    select.innerHTML = '';

    const models = MODELS[currentResolution] || [];
    let lastVersion = '';

    models.forEach(model => {
        const version = getModelVersion(model);
        if (version !== lastVersion) {
            const group = document.createElement('optgroup');
            group.label = version;
            select.appendChild(group);
            lastVersion = version;
        }

        const option = document.createElement('option');
        option.value = model;
        option.textContent = '  ' + getRatioDisplay(model);
        select.appendChild(option);
    });
}

// 应用设置到所有任务
function applySettingsToAll() {
    const model = document.getElementById('batchModelSelect').value;
    const resolution = document.getElementById('batchResolutionSelect').value;

    // 更新所有卡片的提示输入框placeholder或提示（这里只是视觉反馈）
    const cards = document.querySelectorAll('.batch-card');
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
    const card = document.querySelectorAll('.batch-card')[taskIndex];
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
    const card = document.querySelectorAll('.batch-card')[taskIndex];
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
        const requestBody = {
            apiKey: apiKey,
            model: document.getElementById('batchModelSelect').value,
            prompt: task.prompt
        };

        // 添加参考图
        const images = task.images.filter(img => img !== null);
        if (images.length > 0) {
            requestBody.images = images;
        }

        const response = await fetchWithRetry('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        // 检查响应状态
        if (!response.ok) {
            task.status = 'failed';
            updateTaskUI(taskIndex);
            alert(`任务${taskIndex + 1}请求失败: HTTP ${response.status}`);
            return;
        }

        // 检查响应内容
        const responseText = await response.text();
        if (!responseText.trim()) {
            task.status = 'failed';
            updateTaskUI(taskIndex);
            alert(`任务${taskIndex + 1}收到空响应，服务器可能正在重启`);
            return;
        }

        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            task.status = 'failed';
            updateTaskUI(taskIndex);
            console.error('JSON解析失败:', responseText.substring(0, 200));
            alert(`任务${taskIndex + 1}响应格式错误`);
            return;
        }

        if (data.error) {
            task.status = 'failed';
            updateTaskUI(taskIndex);
            alert(`任务${taskIndex + 1}生成失败: ${data.error}`);
            return;
        }

        if (data.image) {
            task.result = ensureHttps(data.image);
            task.status = 'completed';
            updateTaskUI(taskIndex);
        }

    } catch (error) {
        task.status = 'failed';
        updateTaskUI(taskIndex);
        console.error('Task error:', error);
        let errorMsg = '网络连接失败';
        if (error.name === 'AbortError') {
            errorMsg = '请求超时(3分钟)，请检查网络后重试';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('net::ERR')) {
            errorMsg = '网络连接被重置，已自动重试多次，请重试';
        }
        alert(`任务${taskIndex + 1}错误: ${errorMsg}`);
    }
}

// 更新任务UI
function updateTaskUI(taskIndex) {
    const task = batchTasks[taskIndex];
    const card = document.querySelectorAll('.batch-card')[taskIndex];
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
        else if (task.status === 'completed') downloadImage(task.result);
        else if (task.status === 'failed') startTask(taskIndex);
    };

    // 更新结果
    if (task.result) {
        resultEl.style.display = 'block';
        resultEl.querySelector('img').src = task.result;
        resultEl.querySelector('img').onclick = () => window.open(task.result, '_blank');
    } else {
        resultEl.style.display = 'none';
    }
}

// 更新任务状态显示
function updateTaskStatus(taskIndex) {
    const task = batchTasks[taskIndex];
    const card = document.querySelectorAll('.batch-card')[taskIndex];
    const statusEl = card.querySelector('.batch-card-status');
    statusEl.dataset.status = task.status;
}

// 清除单个任务
function clearTask(taskIndex) {
    batchTasks[taskIndex] = {
        images: [null, null, null],
        prompt: '',
        result: null,
        status: 'pending'
    };

    const card = document.querySelectorAll('.batch-card')[taskIndex];
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
        const card = document.querySelectorAll('.batch-card')[i];
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
            link.download = `batch-image-${index + 1}-${Date.now()}.jpg`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });

    if (!hasResults) {
        alert('没有可下载的结果');
    }
}