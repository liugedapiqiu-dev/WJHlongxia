#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import os

# 文档路径
doc_path = '/Users/jo/.openclaw/workspace/南野科技项目月报_2026-03-修正版.pdf'
doc = SimpleDocTemplate(doc_path, pagesize=A4, 
                        rightMargin=1.5*cm, leftMargin=1.5*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

# 样式
styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, leading=22, spaceAfter=20, alignment=1)
h1_style = ParagraphStyle('H1', parent=styles['Heading2'], fontSize=14, leading=18, spaceAfter=12, spaceBefore=10)
h2_style = ParagraphStyle('H2', parent=styles['Heading3'], fontSize=12, leading=16, spaceAfter=8, spaceBefore=10)
normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=6)

# 内容
content = []

# 标题
content.append(Paragraph("南野科技 - 项目组合管理月报", title_style))
content.append(Paragraph("报告周期：2025 年 9 月 - 2026 年 3 月 | 生成时间：2026-03-01 01:45", normal_style))
content.append(Paragraph("保密级别：内部机密 | 汇报对象：供应链主管 王健豪", normal_style))
content.append(Spacer(1, 0.3*cm))

# 执行摘要
content.append(Paragraph("执行摘要 (Executive Summary)", h1_style))
summary_data = [
    ['指标', '数值', '状态'],
    ['活跃项目数', '11', '正常'],
    ['按期完成率', '76%', '需关注'],
    ['资源利用率', '78%', '良好'],
    ['高风险项目', '1', '需关注'],
    ['暂停项目', '1', '蜘蛛侠书包'],
]
summary_table = Table(summary_data, colWidths=[4*cm, 3*cm, 4*cm])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.blue),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f7ff')),
]))
content.append(summary_table)
content.append(Spacer(1, 0.2*cm))
content.append(Paragraph("核心洞察：", normal_style))
content.append(Paragraph("• 蜘蛛侠书包项目已暂停，资源重新分配", normal_style))
content.append(Paragraph("• 女生书包、Switch 书包持续推进中", normal_style))
content.append(Paragraph("• 助理资源（许瑶）可优化配置", normal_style))
content.append(Paragraph("• 婴童类新市场开拓尚未启动，建议加速", normal_style))
content.append(Spacer(1, 0.5*cm))

# 资源分配
content.append(Paragraph("资源分配矩阵", h1_style))
resource_data = [
    ['成员', '角色', '主责领域', '负载率', '状态'],
    ['王健豪', '供应链主管', '物流/财务/采购', '75%', '正常'],
    ['徐龙宾', '产品开发', '书包/婴童类', '85%', '正常'],
    ['卢思圻', '运营', '上架/VAT/财税', '70%', '正常'],
    ['许瑶', '助理', '协助/文档/测试', '55%', '正常'],
    ['周凡', '开发/设计', '书包/毛巾', '80%', '正常'],
    ['张新', '助理', '调研/数据/AI', '60%', '正常'],
    ['黄宗旨', '设计', '主图/A+/说明书', '85%', '正常'],
    ['易灵', '助理', '测试/调研', '50%', '正常'],
    ['陈亮亮', '财务/物流', '银行/社保/ERP', '75%', '正常'],
]
resource_table = Table(resource_data, colWidths=[2.5*cm, 2.5*cm, 4*cm, 2*cm, 2*cm])
resource_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.blue),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
]))
content.append(resource_table)
content.append(Spacer(1, 0.5*cm))

# 风险登记册
content.append(Paragraph("风险登记册 (Risk Register)", h1_style))
risk_data = [
    ['ID', '风险描述', '概率', '影响', '风险分', '缓解措施'],
    ['R01', '婴童类市场进入延迟', '中', '中', '6/10', '加速市场调研'],
    ['R02', 'Switch 配色确认延迟', '低', '中', '4/10', '每日跟进确认'],
    ['R03', '莆田银行开户未完成', '中', '低', '3/10', '每周跟进银行'],
]
risk_table = Table(risk_data, colWidths=[1.5*cm, 4*cm, 1.5*cm, 1.5*cm, 2*cm, 4*cm])
risk_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.blue),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('FONT', (0,0), (-1,-1), 'Helvetica', 8),
]))
content.append(risk_table)
content.append(Spacer(1, 0.2*cm))
content.append(Paragraph("变更说明：设计资源不足风险已因蜘蛛侠项目暂停而消除", normal_style))
content.append(Spacer(1, 0.5*cm))

# 行动项
content.append(Paragraph("本周行动项 (Action Items)", h1_style))
action_data = [
    ['优先级', '行动项', '负责人', '截止日', '状态'],
    ['P0', 'Switch 透明款配色确认', '王健豪', '03-07', '待决策'],
    ['P1', '女生书包方案完善', '徐龙宾', '03-08', '进行中'],
    ['P1', '毛巾产品完整上架', '卢思圻', '03-07', '进行中'],
    ['P1', '莆田银行开户完成', '陈亮亮', '03-10', '进行中'],
    ['P2', '婴童类市场调研启动', '徐龙宾', '03-15', '未开始'],
    ['P2', '蜘蛛侠项目收尾文档', '周凡', '03-12', '暂停'],
]
action_table = Table(action_data, colWidths=[1.5*cm, 5*cm, 2*cm, 2*cm, 2*cm])
action_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.blue),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
    ('BACKGROUND', (0,1), (0,1), colors.HexColor('#ffeb3b')),
]))
content.append(action_table)
content.append(Spacer(1, 0.5*cm))

# 总结
content.append(Paragraph("总结与建议", h1_style))
content.append(Paragraph("整体健康度：良好（蜘蛛侠暂停后风险降低）", normal_style))
content.append(Spacer(1, 0.2*cm))
content.append(Paragraph("三大优先事项：", normal_style))
content.append(Paragraph("1. Switch 配色确认（本周决策）", normal_style))
content.append(Paragraph("2. 女生书包加速推进（下周评审）", normal_style))
content.append(Paragraph("3. 婴童类市场调研启动（3 月中旬）", normal_style))
content.append(Spacer(1, 0.2*cm))
content.append(Paragraph("资源建议：", normal_style))
content.append(Paragraph("• 蜘蛛侠暂停后，设计产能已缓解", normal_style))
content.append(Paragraph("• 许瑶可更多参与项目协调，提升团队效率", normal_style))
content.append(Paragraph("• 建议评估蜘蛛侠项目未来重启条件", normal_style))
content.append(Spacer(1, 0.5*cm))

# 页脚
content.append(Paragraph("________________________________________", normal_style))
content.append(Paragraph("报告结束 | 下次自动汇报：2026-03-08 | 报告生成：AI 助手 阿豪", normal_style))
content.append(Paragraph("附录：详细项目数据见飞书多维表格 | Token: UPcwbHbUwah0d4s937ncGpL1nQe", normal_style))

# 构建 PDF
doc.build(content)
print(f"PDF 已生成：{doc_path}")
print(f"文件大小：{os.path.getsize(doc_path) / 1024:.1f} KB")
