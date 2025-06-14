// 全局变量
let currentComposition = null;
let compositionId = null;

// DOM元素
const backBtn = document.getElementById('backBtn');
const printBtn = document.getElementById('printBtn');
const copyBtn = document.getElementById('copyBtn');
const regenerateBtn = document.getElementById('regenerateBtn');
const saveBtn = document.getElementById('saveBtn');
const validateBtn = document.getElementById('validateBtn');
const executeBtn = document.getElementById('executeBtn');
const simulateBtn = document.getElementById('simulateBtn');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadCompositionFromUrl();
    
    // 配置marked选项
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
    });
});

// 设置事件监听器
function setupEventListeners() {
    backBtn.addEventListener('click', () => {
        window.location.href = '/';
    });
    
    printBtn.addEventListener('click', () => {
        window.print();
    });
    
    copyBtn.addEventListener('click', copyContent);
    regenerateBtn.addEventListener('click', regenerateComposition);
    saveBtn.addEventListener('click', saveComposition);
    validateBtn.addEventListener('click', validateComposition);
    executeBtn.addEventListener('click', executeComposition);
    simulateBtn.addEventListener('click', simulateComposition);
}

// 从URL参数加载组合数据
function loadCompositionFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    compositionId = urlParams.get('id');
    
    if (compositionId) {
        loadCompositionById(compositionId);
    } else {
        // 尝试从sessionStorage获取最新的组合结果
        const latestComposition = sessionStorage.getItem('latestComposition');
        if (latestComposition) {
            currentComposition = JSON.parse(latestComposition);
            displayComposition(currentComposition);
        } else {
            showError('未找到组合数据');
        }
    }
}

// 根据ID加载组合
async function loadCompositionById(id) {
    try {
        const response = await fetch(`/api/compositions/${id}`);
        const composition = await response.json();
        
        if (composition.error) {
            showError('加载组合失败: ' + composition.error);
        } else {
            currentComposition = composition;
            displayComposition(composition);
        }
    } catch (error) {
        showError('加载组合失败: ' + error.message);
    }
}

// 显示组合内容
function displayComposition(composition) {
    // 更新头部信息
    document.getElementById('compositionId').textContent = 
        composition.composition_id || composition.id || '未命名组合';
    document.getElementById('compositionTime').textContent = 
        '创建时间: ' + (composition.created_at || new Date().toLocaleString());
    
    // 渲染Markdown内容
    const markdownContent = document.getElementById('markdownContent');
    
    let markdownText = '';
    
    if (composition.markdown_content) {
        // 如果有专门的markdown字段
        markdownText = composition.markdown_content;
    } else if (composition.workflow) {
        // 检查workflow是否就是markdown格式的字符串
        markdownText = composition.workflow;
    } else {
        // 从现有字段构建markdown
        markdownText = buildMarkdownFromComposition(composition);
    }
    
    // 处理转义的换行符和特殊字符
    markdownText = markdownText
        .replace(/\\n/g, '\n')  // 替换 \n 为真正的换行
        .replace(/\\"/g, '"')   // 替换 \" 为 "
        .replace(/\\t/g, '\t')  // 替换 \t 为 tab
        .trim();
    
    // 渲染为HTML
    markdownContent.innerHTML = marked.parse(markdownText);
    
    // 应用代码高亮
    markdownContent.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    // 美化JSON代码块
    markdownContent.querySelectorAll('pre code.language-json').forEach((block) => {
        try {
            const jsonObj = JSON.parse(block.textContent);
            block.textContent = JSON.stringify(jsonObj, null, 2);
            hljs.highlightElement(block);
        } catch (e) {
            // 如果不是有效JSON，保持原样
        }
    });
}

// 从组合对象构建Markdown内容
function buildMarkdownFromComposition(composition) {
    let markdown = '';
    
    // 标题
    markdown += `# ${composition.composition_id || '服务组合方案'}\n\n`;
    
    // 概述
    if (composition.workflow) {
        markdown += `## 方案概述\n\n${composition.workflow}\n\n`;
    }
    
    // 服务列表
    if (composition.services && composition.services.length > 0) {
        markdown += `## 涉及服务\n\n`;
        composition.services.forEach((service, index) => {
            markdown += `### ${index + 1}. ${service.name || '未命名服务'}\n\n`;
            if (service.description) {
                markdown += `**描述**: ${service.description}\n\n`;
            }
            if (service.endpoint) {
                markdown += `**端点**: \`${service.endpoint}\`\n\n`;
            }
            if (service.parameters) {
                markdown += `**参数**:\n\`\`\`json\n${JSON.stringify(service.parameters, null, 2)}\n\`\`\`\n\n`;
            }
        });
    }
    
    // 执行计划
    if (composition.execution_plan) {
        markdown += `## 执行计划\n\n`;
        if (Array.isArray(composition.execution_plan)) {
            composition.execution_plan.forEach((step, index) => {
                markdown += `${index + 1}. ${step}\n`;
            });
            markdown += '\n';
        } else {
            markdown += `${composition.execution_plan}\n\n`;
        }
    }
    
    // 预期结果
    if (composition.expected_outcome) {
        markdown += `## 预期结果\n\n${composition.expected_outcome}\n\n`;
    }
    
    // 约束满足情况
    if (composition.constraints_satisfied) {
        markdown += `## 约束满足情况\n\n`;
        if (Array.isArray(composition.constraints_satisfied)) {
            composition.constraints_satisfied.forEach(constraint => {
                markdown += `- ✅ ${constraint}\n`;
            });
            markdown += '\n';
        } else {
            markdown += `${composition.constraints_satisfied}\n\n`;
        }
    }
    
    // 技术细节
    markdown += `## 技术细节\n\n`;
    markdown += `\`\`\`json\n${JSON.stringify(composition, null, 2)}\n\`\`\`\n\n`;
    
    return markdown;
}

// 复制内容
async function copyContent() {
    try {
        const content = document.getElementById('markdownContent').textContent;
        await navigator.clipboard.writeText(content);
        showNotification('内容已复制到剪贴板', 'success');
    } catch (error) {
        showNotification('复制失败: ' + error.message, 'error');
    }
}

// 重新生成组合
function regenerateComposition() {
    if (confirm('确定要重新生成服务组合吗？这将覆盖当前内容。')) {
        // 跳转回主页面并触发重新生成
        window.location.href = '/?regenerate=true';
    }
}

// 保存组合
async function saveComposition() {
    if (!currentComposition) {
        showNotification('没有可保存的组合', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/compositions/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentComposition)
        });
        
        const result = await response.json();
        
        if (result.error) {
            showNotification('保存失败: ' + result.error, 'error');
        } else {
            showNotification('组合已保存', 'success');
        }
    } catch (error) {
        showNotification('保存失败: ' + error.message, 'error');
    }
}

// 验证组合
async function validateComposition() {
    if (!currentComposition) {
        showNotification('没有可验证的组合', 'error');
        return;
    }
    
    showExecutionResult('正在验证组合...', 'info');
    
    try {
        const response = await fetch('/api/compositions/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentComposition)
        });
        
        const result = await response.json();
        
        if (result.valid) {
            showExecutionResult('✅ 组合验证通过', 'success');
        } else {
            showExecutionResult('❌ 组合验证失败: ' + result.message, 'error');
        }
    } catch (error) {
        showExecutionResult('验证失败: ' + error.message, 'error');
    }
}

// 执行组合
async function executeComposition() {
    if (!currentComposition) {
        showNotification('没有可执行的组合', 'error');
        return;
    }
    
    if (!confirm('确定要执行此服务组合吗？这将在实际环境中运行。')) {
        return;
    }
    
    showExecutionResult('正在执行组合...', 'info');
    
    try {
        const response = await fetch('/api/compositions/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentComposition)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showExecutionResult('✅ 组合执行成功', 'success');
        } else {
            showExecutionResult('❌ 组合执行失败: ' + result.message, 'error');
        }
    } catch (error) {
        showExecutionResult('执行失败: ' + error.message, 'error');
    }
}

// 模拟执行
async function simulateComposition() {
    if (!currentComposition) {
        showNotification('没有可模拟的组合', 'error');
        return;
    }
    
    showExecutionResult('正在模拟执行...', 'info');
    
    try {
        const response = await fetch('/api/compositions/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentComposition)
        });
        
        const result = await response.json();
        
        showExecutionResult('🎯 模拟执行完成:\n' + result.simulation_log, 'success');
    } catch (error) {
        showExecutionResult('模拟失败: ' + error.message, 'error');
    }
}

// 显示执行结果
function showExecutionResult(message, type) {
    const resultDiv = document.getElementById('executionResult');
    resultDiv.textContent = message;
    resultDiv.className = `execution-result ${type}`;
    resultDiv.classList.remove('hidden');
}

// 显示错误
function showError(message) {
    const markdownContent = document.getElementById('markdownContent');
    markdownContent.innerHTML = `
        <div style="text-align: center; padding: 50px; color: #d73a49;">
            <h2>❌ 加载失败</h2>
            <p>${message}</p>
            <button onclick="window.location.reload()" class="btn btn-primary">重新加载</button>
        </div>
    `;
}

// 显示通知
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s;
    `;
    
    if (type === 'success') {
        notification.style.backgroundColor = '#28a745';
    } else if (type === 'info') {
        notification.style.backgroundColor = '#17a2b8';
    } else {
        notification.style.backgroundColor = '#dc3545';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 100);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
// 在composition_result.js中添加目录生成功能
function generateTableOfContents() {
    const headers = document.querySelectorAll('.markdown-body h1, .markdown-body h2, .markdown-body h3');
    if (headers.length === 0) return;
    
    const toc = document.createElement('div');
    toc.className = 'toc';
    toc.innerHTML = '<h4>📑 目录</h4>';
    
    const tocList = document.createElement('ul');
    
    headers.forEach((header, index) => {
        // 为标题添加ID
        const id = `heading-${index}`;
        header.id = id;
        
        // 创建目录项
        const li = document.createElement('li');
        li.style.paddingLeft = `${(parseInt(header.tagName.charAt(1)) - 1) * 1}em`;
        
        const a = document.createElement('a');
        a.href = `#${id}`;
        a.textContent = header.textContent;
        a.style.textDecoration = 'none';
        a.style.color = '#0969da';
        
        li.appendChild(a);
        tocList.appendChild(li);
    });
    
    toc.appendChild(tocList);
    
    // 插入到内容开头
    const markdownContent = document.querySelector('.markdown-body');
    markdownContent.insertBefore(toc, markdownContent.firstChild);
}