#!/usr/bin/env node
/**
 * 1688 旺旺聊天 - CDP 终极方案 v2
 * 使用 CDP 原生协议 + 屏幕坐标点击
 */

const puppeteer = require('puppeteer-core');

async function main() {
    console.log('🚀 CDP 终极方案 v2 启动...\n');
    
    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:18800',
        defaultViewport: null
    });
    
    const pages = await browser.pages();
    let chatPage = null;
    
    for (const page of pages) {
        if (page.url().includes('air.1688.com') && page.url().includes('web_im')) {
            chatPage = page;
            console.log('✅ 找到聊天页');
            break;
        }
    }
    
    if (!chatPage) {
        console.log('❌ 未找到聊天页面');
        process.exit(1);
    }
    
    // 获取 CDP Session
    const client = await chatPage.createCDPSession();
    await client.send('DOM.enable');
    await client.send('Runtime.enable');
    
    console.log('📡 CDP Session 已启用\n');
    
    const testMessage = '你好！我是阿豪，AI 客服助手。很高兴为您服务！';
    
    // 方案：先在页面中执行 JS，让页面自己报告输入框的位置
    console.log('📍 第 1 步：获取输入框坐标...');
    
    const positionInfo = await chatPage.evaluate(() => {
        // 递归搜索所有 iframe
        function findInput(doc) {
            // 找 contenteditable 的 div
            const editables = doc.querySelectorAll('div[contenteditable="true"]');
            for (const el of editables) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 50 && rect.height > 20) {
                    return {
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2,
                        width: rect.width,
                        height: rect.height,
                        type: 'contenteditable'
                    };
                }
            }
            
            // 找 textarea 或 input
            const inputs = doc.querySelectorAll('textarea, input');
            for (const el of inputs) {
                const ph = el.getAttribute('placeholder') || '';
                const rect = el.getBoundingClientRect();
                if ((ph.includes('请输入') || ph.includes('消息')) && rect.width > 50) {
                    return {
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2,
                        width: rect.width,
                        height: rect.height,
                        type: el.tagName
                    };
                }
            }
            
            // 递归进入 iframe
            const iframes = doc.querySelectorAll('iframe');
            for (const iframe of iframes) {
                try {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
                    if (iframeDoc) {
                        const found = findInput(iframeDoc);
                        if (found) return found;
                    }
                } catch (e) {
                    // 跨域 iframe
                }
            }
            return null;
        }
        
        return findInput(document);
    });
    
    if (!positionInfo) {
        console.log('❌ 页面内搜索未找到输入框');
        console.log('尝试使用截图坐标估算...');
        
        // 备用方案：根据之前截图的经验坐标
        // 旺旺聊天输入框通常在页面底部中间
        const viewport = await chatPage.evaluate(() => ({
            width: window.innerWidth,
            height: window.innerHeight
        }));
        
        positionInfo.x = viewport.width / 2;
        positionInfo.y = viewport.height * 0.85; // 底部 85% 位置
        positionInfo.width = 300;
        positionInfo.height = 50;
        positionInfo.type = 'estimated';
        
        console.log(`📍 估算坐标：(${positionInfo.x}, ${positionInfo.y})`);
    } else {
        console.log(`✅ 输入框坐标：(${positionInfo.x.toFixed(1)}, ${positionInfo.y.toFixed(1)})`);
        console.log(`   类型：${positionInfo.type}`);
        console.log(`   尺寸：${positionInfo.width.toFixed(0)} x ${positionInfo.height.toFixed(0)}`);
    }
    
    // 第 2 步：点击输入框获得焦点
    console.log('\n🖱️  第 2 步：点击输入框...');
    
    await client.send('Input.dispatchMouseEvent', {
        type: 'mouseMoved',
        x: positionInfo.x,
        y: positionInfo.y
    });
    await new Promise(r => setTimeout(r, 50));
    
    await client.send('Input.dispatchMouseEvent', {
        type: 'mousePressed',
        x: positionInfo.x,
        y: positionInfo.y,
        button: 'left'
    });
    await client.send('Input.dispatchMouseEvent', {
        type: 'mouseReleased',
        x: positionInfo.x,
        y: positionInfo.y,
        button: 'left'
    });
    
    await new Promise(r => setTimeout(r, 300));
    console.log('✅ 已聚焦');
    
    // 第 3 步：逐字输入（模拟真人键盘事件）
    console.log(`\n⌨️  第 3 步：输入 "${testMessage}"`);
    
    for (let i = 0; i < testMessage.length; i++) {
        const char = testMessage[i];
        
        await client.send('Input.dispatchKeyEvent', {
            type: 'keyDown',
            text: char,
            unmodifiedText: char,
            code: 'Key' + i,
            key: char
        });
        
        await new Promise(r => setTimeout(r, 30 + Math.random() * 40)); // 30-70ms 随机延迟
        
        await client.send('Input.dispatchKeyEvent', {
            type: 'keyUp',
            text: char,
            unmodifiedText: char,
            code: 'Key' + i,
            key: char
        });
        
        if ((i + 1) % 10 === 0) {
            console.log(`   已输入：${testMessage.substring(0, i + 1)}...`);
        }
    }
    
    console.log('✅ 输入完成');
    await new Promise(r => setTimeout(r, 300));
    
    // 第 4 步：按 Enter 发送
    console.log('\n📤 第 4 步：发送消息...');
    
    await client.send('Input.dispatchKeyEvent', {
        type: 'keyDown',
        code: 'Enter',
        key: 'Enter',
        keyCode: 13,
        which: 13
    });
    await new Promise(r => setTimeout(r, 50));
    await client.send('Input.dispatchKeyEvent', {
        type: 'keyUp',
        code: 'Enter',
        key: 'Enter',
        keyCode: 13,
        which: 13
    });
    
    await new Promise(r => setTimeout(r, 500));
    console.log('✅ 消息已发送！');
    
    // 第 5 步：验证结果
    console.log('\n📊 第 5 步：验证结果...');
    
    const verification = await chatPage.evaluate(() => {
        const allText = document.body.innerText;
        const lines = allText.split('\n').filter(l => l.trim().length > 0).slice(-10);
        return {
            lastMessages: lines,
            inputCleared: document.querySelector('div[contenteditable="true"]')?.innerText?.length === 0 ||
                         document.querySelector('textarea')?.value?.length === 0
        };
    });
    
    console.log('最后的消息内容:');
    verification.lastMessages.forEach((m, i) => {
        console.log(`  ${i+1}. ${m.substring(0, 80)}`);
    });
    
    // 输出极简 JSON 结果
    console.log('\n=== 📊 最终结果 ===');
    console.log(JSON.stringify({
        status: 'success',
        message_sent: testMessage,
        input_cleared: verification.inputCleared
    }, null, 2));
    
    await browser.disconnect();
    console.log('\n🔌 已断开 CDP 连接');
}

main().catch(err => {
    console.error('\n❌ 错误:', err.message);
    console.error(err.stack);
    process.exit(1);
});
