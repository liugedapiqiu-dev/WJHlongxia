#!/usr/bin/env node
/**
 * 1688 旺旺聊天机器人 - CDP 中间件
 * 功能：连接本地 CDP，模拟真人操作，增量读取消息
 * 设计原则：只返回极简 JSON，绝不返回原始 DOM/HTML
 */

const puppeteer = require('puppeteer-core');

// 配置
const CDP_URL = 'http://127.0.0.1:18800';
const TARGET_URL_PATTERN = 'air.1688.com';

// 已处理消息的指纹记录（用于增量读取）
const processedMessages = new Set();

// 极简消息数据结构
class ChatMessage {
    constructor(role, content, timestamp = null) {
        this.role = role;           // 'customer' | 'seller' | 'system'
        this.content = content;      // 纯文本内容
        this.timestamp = timestamp;  // 可选时间戳
    }
}

// 生成消息指纹（用于去重）
function getMessageFingerprint(sender, content) {
    const hash = `${sender}:${content}`;
    return hash;
}

// 从 iframe 中提取消息（极简清洗）
function extractMessagesFromPage() {
    return document.querySelectorAll('.message-item, .chat-message, [class*="message"], [class*="chat-item"]').length;
}

async function main() {
    console.log('🦞 阿豪 CDP 中间件启动中...');
    console.log(`📡 连接 CDP: ${CDP_URL}`);
    
    let browser;
    
    try {
        // 1. 连接现有 Chrome 实例（CDP）
        browser = await puppeteer.connect({
            browserURL: CDP_URL,
            defaultViewport: null  // 使用现有视口
        });
        
        console.log('✅ CDP 连接成功');
        
        // 2. 获取所有页面（标签页）
        const pages = await browser.pages();
        console.log(`📑 找到 ${pages.length} 个标签页`);
        
        // 3. 找到旺旺聊天页面
        let chatPage = null;
        for (const page of pages) {
            const url = page.url();
            if (url.includes(TARGET_URL_PATTERN)) {
                chatPage = page;
                console.log(`💬 找到旺旺聊天页：${url.substring(0, 80)}...`);
                break;
            }
        }
        
        if (!chatPage) {
            console.log('❌ 未找到旺旺聊天页面');
            console.log('可用页面:');
            for (const page of pages) {
                console.log(`  - ${page.url()}`);
            }
            process.exit(1);
        }
        
        // 4. 等待页面加载完成（Puppeteer 方式）
        await chatPage.waitForNetworkIdle({ idleTime: 500, timeout: 5000 }).catch(() => {});
        await new Promise(r => setTimeout(r, 1000));
        
        // 5. 递归查找所有 frame（包括嵌套的 iframe）
        console.log('🔍 递归查找所有 frame...');
        const allFrames = chatPage.frames();
        console.log(`📦 找到 ${allFrames.length} 个 frame`);
        
        let chatFrame = null;
        
        // 打印所有 frame URL
        allFrames.forEach((f, i) => {
            console.log(`  [${i}] ${f.url().substring(0, 70)}...`);
        });
        
        // 找包含 web_im 的 frame 或者最后一个 frame（通常是聊天内容）
        for (const frame of allFrames) {
            const frameUrl = frame.url();
            if (frameUrl.includes('web_im') || frameUrl.includes('wangwang') || frameUrl.includes('def_cbu')) {
                chatFrame = frame;
                console.log(`✅ 选中 frame: ${frameUrl.substring(0, 60)}...`);
                break;
            }
        }
        
        if (!chatFrame && allFrames.length > 0) {
            // 选最后一个 frame（通常是聊天内容区）
            chatFrame = allFrames[allFrames.length - 1];
            console.log('⚠️  使用最后一个 frame');
        }
        
        // 6. 穿透 iframe - 在 frame 上下文中执行
        console.log('🎯 准备模拟真人操作...');
        
        // 7-9. 直接在 PAGE 级别操作（穿透所有 iframe）
        console.log('⌨️  模拟真人输入并发送（PAGE 级别）...');
        
        const testMessage = '你好！我是阿豪，AI 客服助手。很高兴为您服务！';
        
        // 在页面上下文中执行，递归搜索所有 iframe
        const result = await chatPage.evaluate(async (message) => {
            const results = { foundInput: false, sent: false, messages: [], error: null };
            
            // 递归搜索所有 iframe 中的元素
            function searchInFrame(doc) {
                // 先找输入框
                const inputs = doc.querySelectorAll('textarea, input, div[contenteditable="true"]');
                for (const el of inputs) {
                    const ph = el.getAttribute('placeholder') || el.innerText || '';
                    // 查找包含"请输入消息"或"发送"的输入框
                    if (ph.includes('请输入消息') || ph.includes('按 Enter') || ph.includes('发送按钮')) {
                        return { type: 'input', element: el };
                    }
                }
                
                // 递归进入子 iframe
                const iframes = doc.querySelectorAll('iframe');
                for (const iframe of iframes) {
                    try {
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
                        if (iframeDoc) {
                            const found = searchInFrame(iframeDoc);
                            if (found) return found;
                        }
                    } catch (e) {
                        // 跨域 iframe 无法访问
                    }
                }
                return null;
            }
            
            // 1. 找到输入框
            const found = searchInFrame(document);
            const inputEl = found?.element;
            
            if (!inputEl) {
                // 备用方案：找包含"发送"按钮附近的输入框
                const sendButtons = Array.from(document.querySelectorAll('button')).filter(b => b.textContent?.includes('发送'));
                if (sendButtons.length > 0) {
                    // 找发送按钮的父容器中的输入框
                    for (const btn of sendButtons) {
                        const container = btn.closest('div') || btn.parentElement;
                        if (container) {
                            const nearbyInput = container.querySelector('textarea, input, div[contenteditable="true"]');
                            if (nearbyInput) {
                                return { foundInput: true, sent: false, error: '找到输入框但未发送（备用方案）' };
                            }
                        }
                    }
                }
                results.error = '未找到输入框';
                return results;
            }
            
            results.foundInput = true;
            
            // 2. 聚焦并输入
            inputEl.scrollIntoView({ behavior: 'smooth' });
            await new Promise(r => setTimeout(r, 200));
            inputEl.focus();
            
            // 清空
            if (inputEl.tagName === 'INPUT' || inputEl.tagName === 'TEXTAREA') {
                inputEl.value = '';
            } else {
                inputEl.innerText = '';
            }
            inputEl.dispatchEvent(new InputEvent('input', { bubbles: true }));
            
            // 模拟逐字输入
            for (const char of message) {
                if (inputEl.tagName === 'INPUT' || inputEl.tagName === 'TEXTAREA') {
                    inputEl.value += char;
                } else {
                    inputEl.innerText += char;
                }
                inputEl.dispatchEvent(new InputEvent('input', { bubbles: true }));
                await new Promise(r => setTimeout(r, 30));
            }
            
            // 3. 找到并点击发送按钮
            const sendButtons = Array.from(document.querySelectorAll('button')).filter(b => b.textContent?.includes('发送'));
            if (sendButtons.length > 0) {
                sendButtons[0].click();
                results.sent = true;
            } else {
                // Enter 发送
                inputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                results.sent = true;
                results.sentVia = 'enter';
            }
            
            // 4. 提取消息
            await new Promise(r => setTimeout(r, 200));
            const allText = document.body.innerText;
            const lines = allText.split('\n').filter(l => l.trim().length > 0 && l.length < 200);
            results.messages = lines.slice(-10).map(text => ({
                role: text.includes('已读') || text.includes('智谷') ? 'seller' : 'customer',
                content: text.substring(0, 100)
            }));
            
            return results;
        }, testMessage);
        
        console.log(`✅ 找到输入框：${result.foundInput}`);
        console.log(`✅ 发送状态：${result.sent ? '成功' : '失败'}`);
        
        if (result.error) {
            console.log(`❌ 错误：${result.error}`);
            process.exit(1);
        }
        
        // 10. 读取最新消息（增量模式）
        console.log('📥 读取最新消息...');
        
        const newMessages = await chatFrame.evaluate(() => {
            // 在页面上下文中执行，返回极简数据
            const messages = [];
            
            // 尝试多种消息选择器
            const selectors = [
                '.message-item',
                '.chat-message',
                '[class*="message"]',
                '[class*="chat-item"]',
                '[role="listitem"]'
            ];
            
            let messageElements = [];
            for (const selector of selectors) {
                messageElements = document.querySelectorAll(selector);
                if (messageElements.length > 0) break;
            }
            
            // 只提取纯文本，不返回 HTML
            messageElements.forEach((el, index) => {
                const text = el.textContent?.trim() || '';
                if (text.length > 0 && text.length < 500) {  // 过滤过长内容
                    // 判断发送者角色
                    const isSelf = el.classList.contains('self') || 
                                   el.classList.contains('mine') ||
                                   el.closest('[class*="self"]') !== null;
                    
                    messages.push({
                        index: index,
                        role: isSelf ? 'seller' : 'customer',
                        content: text.substring(0, 200)  // 限制长度
                    });
                }
            });
            
            return messages;
        });
        
        // 11. 过滤已处理的消息（增量）
        const unreadMessages = [];
        for (const msg of newMessages) {
            const fingerprint = getMessageFingerprint(msg.role, msg.content);
            if (!processedMessages.has(fingerprint)) {
                processedMessages.add(fingerprint);
                unreadMessages.push(msg);
            }
        }
        
        // 12. 输出极简 JSON 结果
        console.log('\n=== 📊 结果 ===');
        console.log(JSON.stringify({
            status: 'success',
            action: 'message_sent',
            message_sent: testMessage,
            new_messages_count: unreadMessages.length,
            messages: unreadMessages.map(m => ({
                role: m.role,
                content: m.content
            }))
        }, null, 2));
        
    } catch (error) {
        console.error('❌ 错误:', error.message);
        console.error(JSON.stringify({
            status: 'error',
            error: error.message.substring(0, 200)
        }, null, 2));
        process.exit(1);
    } finally {
        if (browser) {
            // 断开连接（不关闭浏览器，因为它是共享的）
            await browser.disconnect();
            console.log('🔌 已断开 CDP 连接');
        }
    }
}

// 运行主函数
main().catch(console.error);
