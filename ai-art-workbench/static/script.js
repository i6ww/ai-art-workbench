// 模型数据
const MODELS = {
    "1K": [
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
    ]
};

// 状态
let currentResolution = '2K';
let currentMode = 'text2image';  // text2image 或 image2image
let uploadedImages = [null, null, null, null, null, null];  // 6张参考图
let currentUploadIndex = 0;  // 当前上传的索引

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadTheme();
    loadHistory();
    initModelSelect();
    setupEventListeners();
});

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
    if (model.includes('nano-banana-pro')) return 'firefly-nano-banana-pro';
    if (model.includes('nano-banana2')) return 'firefly-nano-banana2';
    if (model.includes('nano-banana')) return 'firefly-nano-banana';
    return model.split('-').slice(0, 3).join('-');
}

// 获取比例显示
function getRatioDisplay(model) {
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
            if (currentMode === 'image2image') {
                uploadArea.style.display = 'flex';
                document.getElementById('welcomeMessage').style.display = 'none';
            } else {
                uploadArea.style.display = 'none';
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
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('resultLoading').style.display = 'none';
            document.getElementById('resultContent').innerHTML = `<div class="error">生成失败: ${data.error}</div>`;
            if (data.debug) console.log('Debug:', data.debug);
            return;
        }
        
        if (data.image) {
            document.getElementById('resultLoading').style.display = 'none';
            document.getElementById('resultContent').innerHTML = `
                <img src="${data.image}" alt="生成结果" onclick="window.open('${data.image}', '_blank')">
                <div class="result-actions">
                    <button onclick="viewImage('${data.image}')">查看大图</button>
                    <button onclick="downloadImage('${data.image}')">下载</button>
                </div>
            `;
        }
        
    } catch (error) {
        document.getElementById('resultLoading').style.display = 'none';
        document.getElementById('resultContent').innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
        console.error('Request error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = '开始生成';
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