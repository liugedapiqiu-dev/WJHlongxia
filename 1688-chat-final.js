#!/usr/bin/env node
/**
 * 1688 旺旺聊天 - CDP 最终决战版 v2
 * 使用 Puppeteer targets API，无外部依赖
 */

const puppeteer = require('puppeteer-core');

async function main() {
    console.log('🔥 CDP 最终决战版 v2 启动...\n');
    
    // 1. 连接到浏览器
    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:18800',
        defaultViewport: null
    });
    
    // 2. 获取所有 targets
    console.log('📡 获取所有 targets...');
    const targets = browser.targets();
    console.log(`找到 ${targets.length} 个 targets:\n`);
    
    let chatTarget = null;
    for (const target of targets) {
        const url = target.url();
        const type = target.type();
        console.log(`  - ${type}: ${url?.substring(0, 70)}...`);
        if (url?.includes('web_im') && type === 'iframe') {
            chatTarget = target;
            console.log('    ✅ 候选聊天 iframe!');
        }
    }
    
    // 3. 获取所有 pages 并检查 frames
    const pages = await browser.pages();
    console.log(`\n📑 Browser pages: ${pages.length}\n`);
    
    let foundInput = false;
    let inputCoords = null;
    
    for (const page of pages) {
        const pageUrl = page.url();
        if (!pageUrl.includes('1688')) continue;
        
        console.log(`页面：${pageUrl.substring(0, 50)}...`);
        
        const frames = page.frames();
        console.log(`  Frames: ${frames.length}`);
        
        for (let i = 0; i < frames.length; i++) {
            const frame = frames[i];
            const frameUrl = frame.url();
            
            console.log(`  [${i}] ${frameUrl.substring(0, 55)}...`);
            
            // 尝试在每个 frame 中查找输入框
            try {
                const inputInfo = await frame.evaluate(() => {
                    const inputs = document.querySelectorAll('textarea, input, div[contenteditable="true"]');
                    const results = [];
                    inputs.forEach(el => {
                        const ph = el.getAttribute('placeholder') || el.innerText || '';
                        try {
                            const rect = el.getBoundingClientRect();
                            results.push({
                                tag: el.tagName,
                                placeholder: ph.substring(0, 50),
                                width: rect.width,
                                height: rect.height,
                                x: rect.left + rect.width/2,
                                y: rect.top + rect.height/2
                            });
                        } catch (e) {
                            results.push({
                                tag: el.tagName,
                                placeholder: ph.substring(0, 50),
                                error: 'no rect'
                            });
                        }
                    });
                    return results;
                });
                
                if (inputInfo.length > 0) {
                    console.log(`    找到 ${inputInfo.length} 个输入元素:`);
                    inputInfo.forEach(info => {
                        if (info.error) {
                            console.log(`      - <${info.tag}> "${info.placeholder}" (无坐标)`);
                        } else {
                            console.log(`      - <${info.tag}> "${info.placeholder}" @ (${info.x.toFixed(0)}, ${info.y.toFixed(0)}) [${info.width.toFixed(0)}x${info.height.toFixed(0)}]`);
                            
                            // 检查是否是聊天输入框
                            if (info.placeholder.includes('请输入消息') || info.placeholder.includes('Enter') || info.placeholder.includes('发送')) {
                                console.log('    🎯 这就是目标输入框！');
                                foundInput = true;
                                inputCoords = { x: info.x, y: info.y, frame: frame };
                            }
                        }
                    });
                }
            } catch (e) {
                console.log(`    (无法访问：${e.message.substring(0, 40)})`);
            }
        }
    }
    
    // 4. 如果找到了，执行输入
    if (foundInput && inputCoords) {
        console.log('\n🎯 发现目标！开始输入...\n');
        
        const testMessage = '你好！我是阿豪，AI 客服助手。';
        const { x, y } = inputCoords;
        
        const client = await browser.createCDPSession();
        
        // 点击聚焦
        await client.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
        await client.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left' });
        await client.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left' });
        await new Promise(r => setTimeout(r, 300));
        
        // 逐字输入
        console.log(`⌨️  输入："${testMessage}"`);
        for (const char of testMessage) {
            await client.send('Input.dispatchKeyEvent', { type: 'keyDown', text: char, unmodifiedText: char });
            await new Promise(r => setTimeout(r, 40));
            await client.send('Input.dispatchKeyEvent', { type: 'keyUp', text: char, unmodifiedText: char });
        }
        
        // Enter 发送
        await client.send('Input.dispatchKeyEvent', { type: 'keyDown', code: 'Enter', key: 'Enter' });
        await client.send('Input.dispatchKeyEvent', { type: 'keyUp', code: 'Enter', key: 'Enter' });
        
        console.log('\n✅ 消息已发送！');
        
        console.log('\n=== 📊 结果 ===');
        console.log(JSON.stringify({ status: 'success', message_sent: testMessage }, null, 2));
    } else {
        console.log('\n❌ 未找到聊天输入框');
        console.log('\n=== 诊断结论 ===');
        console.log('所有 frame 都已检查，输入框不存在于任何可访问的上下文中');
        console.log('输入框可能在：');
        console.log('  1. Shadow DOM 内部');
        console.log('  2. 完全隔离的跨域 iframe (连 CDP 都无法附加)');
        console.log('  3. 动态生成，当前还未渲染');
        console.log('\n建议：尝试纯屏幕坐标硬编码方案');
    }
    
    await browser.disconnect();
}

main().catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
});
