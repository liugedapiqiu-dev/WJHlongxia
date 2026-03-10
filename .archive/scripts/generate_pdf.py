#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 12)
        # Title
        self.cell(0, 10, '南野科技 - 项目组合管理月报', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, 6, '报告周期：2025 年 9 月 - 2026 年 3 月 | 生成时间：2026-03-01 01:45', 0, 1, 'C')
        self.cell(0, 6, '保密级别：内部机密 | 汇报对象：供应链主管 王健豪', 0, 1, 'C')
        self.ln(5)
        # Line
        self.line(10, 35, 200, 35)
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, '第 ' + str(self.page_no()) + ' 页 / 共 {nb} 页 - AI 助手 阿豪 生成', 0, 0, 'C')

    def chapter_title(self, label):
        # Arial 12
        self.set_font('Arial', 'B', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 8, label, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        # Times 10
        self.set_font('Times', '', 10)
        # Output justified text
        self.multi_cell(0, 6, body)
        self.ln()

    def add_table(self, headers, rows):
        # Column widths
        col_widths = [25, 50, 25, 25, 25, 30]
        
        # Header
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(220, 230, 240)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C', 1)
        self.ln()
        
        # Rows
        self.set_font('Times', '', 9)
        for row in rows:
            for i, cell in enumerate(row):
                # Handle emojis by replacing them
                cell_clean = str(cell).replace('🟢', '[OK]').replace('🟡', '[!]').replace('🔴', '[X]').replace('ℹ️', '[i]').replace('✅', '[V]')
                self.cell(col_widths[i], 6, cell_clean[:20], 1, 0, 'C')
            self.ln()
        self.ln(3)

# Create PDF
pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Executive Summary
pdf.chapter_title('执行摘要 (Executive Summary)')
summary_data = [
    ['指标', '数值', '状态', '指标', '数值', '状态'],
    ['活跃项目数', '11', '[OK] 正常', '本月预算执行', '88%', '[OK] 正常'],
    ['按期完成率', '76%', '[!] 需关注', '暂停项目', '1', '[i] 蜘蛛侠书包'],
    ['资源利用率', '78%', '[OK] 良好', '高风险项目', '1', '[!] 需关注'],
]
pdf.add_table(*zip(*summary_data))

pdf.chapter_body('核心洞察：\n'
    '- 蜘蛛侠书包项目已暂停，资源重新分配\n'
    '- 女生书包、Switch 书包持续推进中\n'
    '- 助理资源（许瑶）可优化配置\n'
    '- 婴童类新市场开拓尚未启动，建议加速')

# Project Portfolio
pdf.add_page()
pdf.chapter_title('项目组合仪表盘')
pdf.chapter_body('按产品线分布：\n'
    '- 书包开发：40% (4 个项目，1 个暂停)\n'
    '- 家居用品：30% (3 个项目)\n'
    '- 高尔夫系列：20% (2 个项目)\n'
    '- 婴童类：10% (2 个项目)\n\n'
    '按状态分布：\n'
    '- 已完成：4 个 (36%)\n'
    '- 进行中：5 个 (45%)\n'
    '- 已暂停：1 个 (9%)\n'
    '- 未开始：1 个 (10%)')

# Resource Allocation
pdf.add_page()
pdf.chapter_title('资源分配矩阵')
resource_headers = ['成员', '角色', '主责领域', '负载率', '状态']
resource_rows = [
    ['王健豪', '供应链主管', '物流/财务/采购', '75%', '[OK]'],
    ['徐龙宾', '产品开发', '书包/婴童类', '85%', '[OK]'],
    ['卢思圻', '运营', '上架/VAT/财税', '70%', '[OK]'],
    ['许瑶', '助理', '协助/文档/测试', '55%', '[OK]'],
    ['周凡', '开发/设计', '书包/毛巾', '80%', '[OK]'],
    ['张新', '助理', '调研/数据/AI', '60%', '[OK]'],
    ['黄宗旨', '设计', '主图/A+/说明书', '85%', '[OK]'],
    ['易灵', '助理', '测试/调研', '50%', '[OK]'],
    ['陈亮亮', '财务/物流', '银行/社保/ERP', '75%', '[OK]'],
]
pdf.add_table(resource_headers, resource_rows)

pdf.chapter_body('资源优化建议：\n'
    '- 设计团队产能缓解：蜘蛛侠项目暂停后，黄宗旨负载降至 85%\n'
    '- 许瑶定位为助理，可承担更多协调工作')

# Risk Register
pdf.add_page()
pdf.chapter_title('风险登记册 (Risk Register)')
risk_headers = ['ID', '风险描述', '概率', '影响', '风险分', '缓解措施']
risk_rows = [
    ['R01', '婴童类市场进入延迟', '中', '中', '6/10', '加速市场调研'],
    ['R02', 'Switch 配色确认延迟', '低', '中', '4/10', '每日跟进确认'],
    ['R03', '莆田银行开户未完成', '中', '低', '3/10', '每周跟进银行'],
]
pdf.add_table(risk_headers, risk_rows)
pdf.chapter_body('变更说明：设计资源不足风险已因蜘蛛侠项目暂停而消除')

# KPI Dashboard
pdf.add_page()
pdf.chapter_title('关键绩效指标 (KPI Dashboard)')
pdf.chapter_body('产品开发 KPI：\n'
    '- 新品上市数：目标 5，实际 3，达成率 60%\n'
    '- 开发周期：目标 30 天，实际 33 天，达成率 91%\n'
    '- 一次通过率：目标 80%，实际 78%，达成率 98%\n'
    '- 设计返工率：目标<15%，实际 14%，达标\n\n'
    '运营 KPI：\n'
    '- 上架及时率：目标 95%，实际 92%，达成率 97%\n'
    '- 物流准时率：目标 90%，实际 88%，达成率 98%\n'
    '- 库存周转：目标 45 天，实际 50 天，达成率 90%')

# Action Items
pdf.add_page()
pdf.chapter_title('本周行动项 (Action Items)')
action_headers = ['优先级', '行动项', '负责人', '截止日', '状态']
action_rows = [
    ['P0', 'Switch 透明款配色确认', '王健豪', '03-07', '待决策'],
    ['P1', '女生书包方案完善', '徐龙宾', '03-08', '进行中'],
    ['P1', '毛巾产品完整上架', '卢思圻', '03-07', '进行中'],
    ['P1', '莆田银行开户完成', '陈亮亮', '03-10', '进行中'],
    ['P2', '婴童类市场调研启动', '徐龙宾', '03-15', '未开始'],
    ['P2', '蜘蛛侠项目收尾文档', '周凡', '03-12', '暂停'],
]
pdf.add_table(action_headers, action_rows)

# Management Decisions
pdf.add_page()
pdf.chapter_title('管理层决策需求')
pdf.chapter_body('1. Switch 透明款配色\n'
    '   建议方案：红蓝经典配色 (3 款)\n'
    '   需决策：确认数量及配色？\n\n'
    '2. 婴童类市场进入\n'
    '   建议方案：A: 自主调研 (2 周) / B: 购买报告 (¥8000)\n'
    '   需决策：选择方案？\n\n'
    '3. 蜘蛛侠项目重启\n'
    '   建议方案：条件：市场需求明确 + 设计资源充足\n'
    '   需决策：是否保留重启可能？\n\n'
    '4. 助理资源优化\n'
    '   建议方案：许瑶可承担更多项目协调工作\n'
    '   需决策：确认职责调整？')

# Summary
pdf.add_page()
pdf.chapter_title('总结与建议')
pdf.chapter_body('整体健康度：良好（蜘蛛侠暂停后风险降低）\n\n'
    '三大优先事项：\n'
    '1. Switch 配色确认（本周决策）\n'
    '2. 女生书包加速推进（下周评审）\n'
    '3. 婴童类市场调研启动（3 月中旬）\n\n'
    '资源建议：\n'
    '- 蜘蛛侠暂停后，设计产能已缓解\n'
    '- 许瑶可更多参与项目协调，提升团队效率\n'
    '- 建议评估蜘蛛侠项目未来重启条件\n\n'
    '报告结束\n'
    '下次自动汇报：2026-03-08\n'
    '报告生成：AI 助手 阿豪\n\n'
    '附录：\n'
    '- 详细项目数据见飞书多维表格\n'
    '- 原始数据 Token: UPcwbHbUwah0d4s937ncGpL1nQe')

# Save PDF
output_path = '/Users/jo/.openclaw/workspace/南野科技项目月报_2026-03-修正版.pdf'
pdf.output(output_path)
print(f'PDF 已生成：{output_path}')
print(f'文件大小：{os.path.getsize(output_path) / 1024:.1f} KB')
