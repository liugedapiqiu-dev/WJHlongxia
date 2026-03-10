#!/usr/bin/env node
/**
 * 1688 旺旺聊天 - CDP 终极方案
 * 使用 CDP 原生协议发送输入事件，绕过 iframe 限制
 */

const puppeteer = require('puppeteer-core');

async function main() {
    console.log('🚀 CDP 终极方案启动...\n');
    
    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:18800',
        defaultViewport: null
    });
    
    const pages = await browser.pages();
    let chatPage = null;
    
    for (const page of pages) {
        if (page.url().includes('air.1688.com') && page.url().includes('web_im')) {
            chatPage = page;
            console.log(`✅ 找到聊天页`);
            break;
        }
    }
    
    if (!chatPage) {
        console.log('❌ 未找到聊天页面');
        process.exit(1);
    }
    
    // 获取 CDP Session
    const client = await chatPage.createCDPSession();
    
    // 启用 DOM 和输入域
    await client.send('DOM.enable');
    await client.send('Runtime.enable');
    
    console.log('📡 CDP Session 已启用\n');
    
    // 1. 获取扁平化的 DOM（包括所有 iframe）
    const { root } = await client.send('DOM.getFlattenedDocument', { depth: -1, pierce: true });
    console.log(`📄 根节点：${root.nodeId} (扁平化 DOM)`);
    
    // 2. 用 CSS 选择器查询输入框（跨 iframe）
    const testMessage = '你好！我是阿豪，AI 客服助手。';
    
    // 查询所有可能的输入元素
    const queryResult = await client.send('DOM.querySelectorAll', {
        nodeId: root.nodeId,
        selector: 'textarea, input, div[contenteditable="true"]'
    });
    
    console.log(`🔍 找到 ${queryResult.nodeIds.length} 个输入元素\n`);
    
    // 3. 对每个节点检查 placeholder 和 backendNodeId
    let targetNodeId = null;
    let targetBackendNodeId = null;
    
    for (const nodeId of queryResult.nodeIds) {
        try {
            const { node } = await client.send('DOM.describeNode', { nodeId, depth: 0 });
            const attrs = node.attributes || [];
            const backendNodeId = node.backendNodeId;
            
            // 检查 placeholder 属性
            for (let i = 0; i < attrs.length; i += 2) {
                if (attrs[i] === 'placeholder') {
                    const ph = attrs[i+1];
                    console.log(`   nodeId: ${nodeId}, placeholder: "${ph.substring(0, 50)}..."`);
                    if (ph.includes('请输入消息') || ph.includes('发送') || ph.includes('Enter')) {
                        targetNodeId = nodeId;
                        targetBackendNodeId = backendNodeId;
                        console.log(`✅ 找到目标输入框!`);
                        break;
                    }
                }
            }
            if (targetNodeId) break;
        } catch (e) {
            // 某些节点可能无法描述
        }
    }
    
    if (!targetNodeId) {
        console.log('\n❌ 未找到匹配的 placeholder');
        // 尝试找 contenteditable 的 div
        for (const nodeId of queryResult.nodeIds) {
            try {
                const { node } = await client.send('DOM.describeNode', { nodeId });
                if (node.nodeName === 'DIV' && node.attributes?.includes('contenteditable')) {
                    targetNodeId = nodeId;
                    targetBackendNodeId = node.backendNodeId;
                    console.log(`✅ 使用 contenteditable div (nodeId: ${nodeId})`);
                    break;
                }
            } catch (e) {}
        }
    }
    
    if (!targetNodeId && queryResult.nodeIds.length > 0) {
        // 最后的备用方案：使用第一个有 backendNodeId 的节点
        for (const nodeId of queryResult.nodeIds) {
            try {
                const { node } = await client.send('DOM.describeNode', { nodeId });
                if (node.backendNodeId) {
                    targetNodeId = nodeId;
                    targetBackendNodeId = node.backendNodeId;
                    console.log(`⚠️  备用方案：使用 nodeId ${nodeId}`);
                    break;
                }
            } catch (e) {}
        }
    }
    
    if (!targetNodeId) {
        console.log('❌ 完全找不到输入框');
        process.exit(1);
    }
    
    // 4. 使用 backendNodeId 获取 frame 并计算位置
    console.log('\n📍 计算元素位置...');
    
    let centerX, centerY;
    
    try {
        // 尝试直接获取 box model
        const { model } = await client.send('DOM.getBoxModel', { nodeId: targetNodeId });
        centerX = (model.content[0] + model.content[2]) / 2;
        centerY = (model.content[1] + model.content[3]) / 2;
        console.log(`   位置：(${centerX}, ${centerY})`);
    } catch (e) {
        // 如果是跨 frame，使用 RemoteObject 获取位置
        console.log('   直接获取 box model 失败，尝试使用 RemoteObject...');
        
        const { object } = await client.send('DOM.resolveNode', { backendNodeId: targetBackendNodeId });
        const { result } = await client.send('Runtime.callFunctionOn', {
            objectId: object.objectId,
            functionDeclaration: `function() {
                const rect = this.getBoundingClientRect();
                return { x: rect.left + rect.width/2, y: rect.top + rect.height/2, width: rect.width, height: rect.height };
            }`
        });
        
        if (result.value) {
            centerX = result.value.x;
            centerY = result.value.y;
            console.log(`   位置：(${centerX}, ${centerY}) (通过 getBoundingClientRect)`);
        } else {
            console.log('❌ 无法获取元素位置');
            process.exit(1);
        }
    }
    
    // 5. 点击输入框获得焦点
    console.log('🖱️  点击输入框...');
    await client.send('Input.dispatchMouseEvent', {
        type: 'mousePressed',
        x: centerX,
        y: centerY,
        button: 'left'
    });
    await client.send('Input.dispatchMouseEvent', {
        type: 'mouseReleased',
        x: centerX,
        y: centerY,
        button: 'left'
    });
    
    await new Promise(r => setTimeout(r, 200));
    
    // 6. 逐字输入（模拟真人键盘事件）
    console.log(`⌨️  输入："${testMessage}"`);
    
    for (const char of testMessage) {
        await client.send('Input.dispatchKeyEvent', {
            type: 'keyDown',
            text: char,
            unmodifiedText: char
        });
        await client.send('Input.dispatchKeyEvent', {
            type: 'keyUp',
            text: char,
            unmodifiedText: char
        });
        await new Promise(r => setTimeout(r, 30 + Math.random() * 30)); // 30-60ms 随机延迟
    }
    
    console.log('✅ 输入完成');
    await new Promise(r => setTimeout(r, 300));
    
    // 7. 找到发送按钮并点击
    const sendQuery = await client.send('DOM.querySelectorAll', {
        nodeId: root.nodeId,
        selector: 'button'
    });
    
    let sendNodeId = null;
    for (const nodeId of sendQuery.nodeIds) {
        try {
            const result = await client.send('Runtime.callFunctionOn', {
                functionDeclaration: `function() { return this.textContent || this.innerText || ''; }`,
                objectId: (await client.send('DOM.resolveNode', { nodeId })).object.objectId
            });
            if (result.result.value?.includes('发送')) {
                sendNodeId = nodeId;
                console.log('✅ 找到发送按钮');
                break;
            }
        } catch (e) {}
    }
    
    if (sendNodeId) {
        const { model } = await client.send('DOM.getBoxModel', { nodeId: sendNodeId });
        const btnX = (model.content[0] + model.content[2]) / 2;
        const btnY = (model.content[1] + model.content[3]) / 2;
        
        console.log(`🖱️  点击发送按钮 (${btnX}, ${btnY})...`);
        await client.send('Input.dispatchMouseEvent', {
            type: 'mousePressed',
            x: btnX,
            y: btnY,
            button: 'left'
        });
        await client.send('Input.dispatchMouseEvent', {
            type: 'mouseReleased',
            x: btnX,
            y: btnY,
            button: 'left'
        });
        console.log('✅ 消息已发送！');
    } else {
        // 按 Enter 发送
        console.log('⌨️  按 Enter 发送...');
        await client.send('Input.dispatchKeyEvent', {
            type: 'keyDown',
            code: 'Enter',
            key: 'Enter'
        });
        await client.send('Input.dispatchKeyEvent', {
            type: 'keyUp',
            code: 'Enter',
            key: 'Enter'
        });
        console.log('✅ Enter 发送完成！');
    }
    
    // 8. 输出结果
    console.log('\n=== 📊 任务完成 ===');
    console.log(JSON.stringify({
        status: 'success',
        message_sent: testMessage
    }, null, 2));
    
    await browser.disconnect();
}

main().catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
});
