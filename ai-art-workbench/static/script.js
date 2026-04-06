// 模型数据
const MODELS = {
    "1K": [
        "nano-banana-pro-1k-16:9",
        "nano-banana-pro-1k-9:16",
        "nano-banana-pro-1k-1:1",
        "nano-banana-pro-1k-4:3",
        "nano-banana-pro-1k-3:4",
        "nano-banana-2-1k-16:9",
        "nano-banana-2-1k-9:16",
        "nano-banana-2-1k-1:1",
        "nano-banana-2-1k-4:3",
        "nano-banana-2-1k-3:4",
    ],
    "2K": [
        "nano-banana-pro-2k-16:9",
        "nano-banana-pro-2k-9:16",
        "nano-banana-pro-2k-1:1",
        "nano-banana-pro-2k-4:3",
        "nano-banana-pro-2k-3:4",
        "nano-banana-2-2k-16:9",
        "nano-banana-2-2k-9:16",
        "nano-banana-2-2k-1:1",
        "nano-banana-2-2k-4:3",
        "nano-banana-2-2k-3:4",
    ],
    "4K": [
        "nano-banana-pro-4k-16:9",
        "nano-banana-pro-4k-9:16",
        "nano-banana-pro-4k-1:1",
        "nano-banana-pro-4k-4:3",
        "nano-banana-pro-4k-3:4",
        "nano-banana-2-4k-16:9",
        "nano-banana-2-4k-9:16",
        "nano-banana-2-4k-1:1",
        "nano-banana-2-4k-4:3",
        "nano-banana-2-4k-3:4",
    ]
};

// 状态
let currentTool = 'text2image';
let uploadedImage = null;
let isGenerating = false;
let currentResolution = '2K';
let currentRatio = '16:9';
let currentApiKey = '';
let chatHistory = [];

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadTheme();
    loadHistory();
    initModelSelect();
    setupEventListeners();
});

// 加载设置 - 不自动填充API Key，保证隐私
function loadSettings() {
    // 只加载分辨率和宽高比设置，不加载API Key
    currentResolution = localStorage.getItem('resolution') || '2K';
    currentRatio = localStorage.getItem('ratio') || '16:9';
    
    // 更新UI
    document.querySelectorAll('.resolution-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.res === currentResolution);
    });
    document.querySelectorAll('.ratio-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.ratio === currentRatio);
    });
}

// 保存API Key
function saveApiKey() {
    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        alert('请输入 API Key');
        return;
    }
    localStorage.setItem('apiKey', apiKey);
    currentApiKey = apiKey;
    alert('保存成功!');
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
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
}

// 初始化模型选择
function initModelSelect() {
    updateModelSelect();
}

function updateModelSelect() {
    const modelSelect = document.getElementById('modelSelect');
    const models = MODELS[currentResolution] || [];
    
    modelSelect.innerHTML = '';
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = formatModelName(model);
        modelSelect.appendChild(option);
    });
}

// 格式化模型名称
function formatModelName(model) {
    const parts = model.split('-');
    if (parts.length >= 5) {
        let version = '';
        if (parts[2] === 'pro') {
            version = 'Pro ';
        } else if (!isNaN(parts[2])) {
            version = 'V' + parts[2] + ' ';
        }
        const resolution = parts[parts.length - 2].toUpperCase();
        const ratio = parts[parts.length - 1];
        return version + resolution + ' ' + ratio;
    }
    return model;
}

// 设置分辨率
function setResolution(res) {
    currentResolution = res;
    localStorage.setItem('resolution', res);
    document.querySelectorAll('.resolution-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.res === res);
    });
    updateModelSelect();
}

// 设置宽高比
function setRatio(ratio) {
    currentRatio = ratio;
    localStorage.setItem('ratio', ratio);
    document.querySelectorAll('.ratio-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.ratio === ratio);
    });
}

// 切换工具
function switchTool(tool) {
    currentTool = tool;
    document.querySelectorAll('.tool-item').forEach(item => {
        item.classList.toggle('active', item.dataset.tool === tool);
    });
    
    // 显示/隐藏图片上传按钮
    const attachBtn = document.getElementById('attachBtn');
    attachBtn.style.display = tool === 'image2image' ? 'flex' : 'none';
    
    // 清空输入
    document.getElementById('messageInput').value = '';
}

// 事件监听
function setupEventListeners() {
    const input = document.getElementById('messageInput');
    input.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// 图片上传
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedImage = e.target.result;
        document.getElementById('previewImg').src = uploadedImage;
        document.getElementById('inputToolbar').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function removeUploadedImage() {
    uploadedImage = null;
    document.getElementById('imageInput').value = '';
    document.getElementById('previewImg').src = '';
    document.getElementById('inputToolbar').style.display = 'none';
}

// 发送消息
async function sendMessage() {
    if (isGenerating) return;
    
    const input = document.getElementById('messageInput');
    const prompt = input.value.trim();
    
    // 图生图需要上传图片
    if (currentTool === 'image2image' && !uploadedImage) {
        alert('请先上传图片');
        return;
    }
    
    if (!prompt) {
        alert('请输入描述');
        return;
    }
    
    if (!currentApiKey) {
        alert('请先设置 API Key');
        return;
    }
    
    // 隐藏欢迎信息
    document.getElementById('welcomeMessage').style.display = 'none';
    
    // 添加用户消息
    addMessage('user', prompt);
    input.value = '';
    input.style.height = 'auto';
    
    // 清空上传的图片
    if (uploadedImage) {
        removeUploadedImage();
    }
    
    // 开始生成
    isGenerating = true;
    const loadingId = addLoadingMessage();
    
    try {
        await generateImage(prompt, loadingId);
    } catch (error) {
        updateLoadingMessage(loadingId, '生成失败: ' + error.message);
    }
    
    isGenerating = false;
}

// 添加消息
function addMessage(role, content, imageUrl = null) {
    const container = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatarIcon = role === 'user' ? '👤' : '🎨';
    
    let html = `
        <div class="message-avatar">${avatarIcon}</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(content)}</div>
    `;
    
    if (imageUrl) {
        html += `
            <div class="image-result">
                <img src="${imageUrl}" alt="生成结果" onclick="window.open('${imageUrl}', '_blank')">
                <div class="image-actions">
                    <button onclick="viewImage('${imageUrl}')">查看大图</button>
                    <button onclick="downloadImage('${imageUrl}')">下载</button>
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    messageDiv.innerHTML = html;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    // 保存到历史
    if (role === 'user') {
        addToHistory(content);
    }
}

// 添加加载消息
function addLoadingMessage() {
    const container = document.getElementById('chatMessages');
    const id = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.id = id;
    messageDiv.innerHTML = `
        <div class="message-avatar">🎨</div>
        <div class="message-content">
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
            <div class="loading-text" style="color: var(--text-muted); font-size: 13px; margin-top: 8px;">AI 正在生成图片...</div>
        </div>
    `;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    return id;
}

// 更新加载消息
function updateLoadingMessage(id, text, imageUrl = null) {
    const messageDiv = document.getElementById(id);
    if (!messageDiv) return;
    
    if (imageUrl) {
        messageDiv.innerHTML = `
            <div class="message-avatar">🎨</div>
            <div class="message-content">
                <div class="loading-text" style="color: var(--success);">生成完成!</div>
                <div class="image-result">
                    <img src="${imageUrl}" alt="生成结果" onclick="window.open('${imageUrl}', '_blank')">
                    <div class="image-actions">
                        <button onclick="viewImage('${imageUrl}')">查看大图</button>
                        <button onclick="downloadImage('${imageUrl}')">下载</button>
                    </div>
                </div>
            </div>
        `;
    } else {
        messageDiv.querySelector('.loading-text').textContent = text;
    }
}

// 生成图片
async function generateImage(prompt, loadingId) {
    const model = document.getElementById('modelSelect').value;
    const stream = document.getElementById('streamToggle').checked;
    
    const endpoint = currentTool === 'text2image' ? '/api/text-to-image' : '/api/image-to-image';
    const data = {
        apiKey: currentApiKey,
        model: model,
        prompt: prompt,
        ...(currentTool === 'image2image' && { image: uploadedImage })
    };
    
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    let imageUrl = null;
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.image) {
                        imageUrl = data.image;
                        updateLoadingMessage(loadingId, '生成完成!', imageUrl);
                    } else if (data.error) {
                        throw new Error(data.error);
                    }
                } catch (e) {
                    // 忽略解析错误
                }
            }
        }
    }
    
    if (!imageUrl) {
        throw new Error('未获取到生成的图片');
    }
}

// 查看大图
function viewImage(url) {
    window.open(url, '_blank');
}

// 下载图片
function downloadImage(url) {
    const link = document.createElement('a');
    link.href = `/api/download?url=${encodeURIComponent(url)}`;
    link.download = `ai-image-${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 历史记录
function addToHistory(prompt) {
    const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    const item = { id: Date.now(), prompt: prompt, time: new Date().toLocaleString() };
    history.unshift(item);
    if (history.length > 20) history.pop();
    localStorage.setItem('chatHistory', JSON.stringify(history));
    loadHistory();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    const container = document.getElementById('historyList');
    container.innerHTML = history.map(item => `
        <div class="history-item" onclick="loadHistoryItem('${escapeHtml(item.prompt)}')">
            ${escapeHtml(item.prompt.substring(0, 30))}${item.prompt.length > 30 ? '...' : ''}
        </div>
    `).join('');
}

function loadHistoryItem(prompt) {
    document.getElementById('messageInput').value = prompt;
}

// 清空对话
function clearChat() {
    document.getElementById('chatMessages').innerHTML = '';
    document.getElementById('welcomeMessage').style.display = 'flex';
    document.getElementById('messageInput').value = '';
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}