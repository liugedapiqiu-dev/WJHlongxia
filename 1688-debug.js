#!/usr/bin/env node
/**
 * 1688 旺旺聊天 - 快速调试脚本
 * 目标：找出输入框在哪个 frame 里
 */

const puppeteer = require('puppeteer-core');

async function main() {
    console.log('🔬 开始调试...\n');
    
    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:18800',
        defaultViewport: null
    });
    
    const pages = await browser.pages();
    console.log(`📑 标签页：${pages.length}`);
    
    for (const page of pages) {
        const url = page.url();
        if (!url.includes('1688')) continue;
        
        console.log(`\n💬 页面：${url.substring(0, 60)}...`);
        
        const frames = page.frames();
        console.log(`📦 Frames: ${frames.length}\n`);
        
        for (const frame of frames) {
            const frameUrl = frame.url();
            try {
                const inputs = await frame.evaluate(() => {
                    const found = [];
                    document.querySelectorAll('textarea, input, div[contenteditable="true"]').forEach((el, i) => {
                        const ph = el.getAttribute('placeholder') || el.innerText?.substring(0, 30) || '';
                        if (ph.includes('请输入') || ph.includes('消息') || el.id || el.className?.includes('input')) {
                            found.push({ tag: el.tagName, ph: ph.substring(0, 40), class: el.className?.substring(0, 30) });
                        }
                    });
                    return found;
                });
                
                if (inputs.length > 0) {
                    console.log(`✅ 找到输入框 @ Frame: ${frameUrl.substring(0, 50)}...`);
                    inputs.forEach(i => console.log(`   - <${i.tag}> "${i.ph}" class="${i.class}"`));
                }
            } catch (e) {
                // Frame 可能无法访问
            }
        }
    }
    
    await browser.disconnect();
    console.log('\n✅ 调试完成');
}

main().catch(console.error);
