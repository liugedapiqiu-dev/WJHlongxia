#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
南野科技团队工作计划甘特图生成器
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 团队人员数据 (从飞书导出的数据中提取)
team_data = {
    '王健豪': [
        {'task': '高尔夫磁吸毛巾', 'start': '2025-09-29', 'end': '2025-10-30', 'status': '进行中'},
        {'task': '高尔夫磁吸毛巾彩盒', 'start': '2025-09-29', 'end': '2025-10-30', 'status': '进行中'},
        {'task': '采购助理招聘', 'start': '2025-09-29', 'end': '2025-10-05', 'status': '进行中'},
        {'task': '水疗套装开发', 'start': '2025-10-20', 'end': '2025-11-15', 'status': '已完成'},
    ],
    '周凡': [
        {'task': 'Switch 元素设计', 'start': '2025-09-29', 'end': '2025-10-05', 'status': '已完成'},
        {'task': '男同学蜘蛛书包', 'start': '2025-09-29', 'end': '2025-09-30', 'status': '已完成'},
        {'task': '毛巾说明书', 'start': '2025-09-29', 'end': '2025-09-30', 'status': '已完成'},
        {'task': '圣诞花环主图/A+', 'start': '2025-10-11', 'end': '2025-10-20', 'status': '进行中'},
    ],
    '徐龙宾': [
        {'task': '产品利润表', 'start': '2025-02-24', 'end': '2025-02-28', 'status': '已完成'},
        {'task': '灯芯绒三包图案', 'start': '2025-03-10', 'end': '2025-03-12', 'status': '未开始'},
        {'task': 'baby 类目拓展', 'start': '2025-02-28', 'end': '2025-03-15', 'status': '进行中'},
        {'task': '女生书包设计', 'start': '2026-01-01', 'end': '2026-01-15', 'status': '已完成'},
        {'task': '涤纶书包包型', 'start': '2026-01-15', 'end': '2026-01-25', 'status': '已完成'},
        {'task': '女生书包挂件', 'start': '2026-02-01', 'end': '2026-02-15', 'status': '进行中'},
    ],
    '许瑶': [
        {'task': '游戏毯 A+ 和图需', 'start': '2025-10-21', 'end': '2025-10-24', 'status': '已完成'},
        {'task': '水疗套装协助', 'start': '2025-10-20', 'end': '2025-10-25', 'status': '已完成'},
        {'task': '采购下单表补充', 'start': '2025-10-25', 'end': '2025-11-01', 'status': '已完成'},
        {'task': '毛绒玩具牛主图', 'start': '2025-11-03', 'end': '2025-11-08', 'status': '进行中'},
    ],
    '张新': [
        {'task': '水疗礼品套装分析', 'start': '2025-11-11', 'end': '2025-11-15', 'status': '已完成'},
        {'task': '玫瑰仿真花分析', 'start': '2025-11-25', 'end': '2025-11-28', 'status': '已完成'},
        {'task': '一品红假花分析', 'start': '2025-12-01', 'end': '2025-12-05', 'status': '进行中'},
    ],
    '黄宗旨': [
        {'task': '游戏毯主图设计', 'start': '2025-09-29', 'end': '2025-09-30', 'status': '已完成'},
        {'task': '毛巾说明书设计', 'start': '2025-09-29', 'end': '2025-09-30', 'status': '已完成'},
        {'task': '圣诞花环主图', 'start': '2025-10-11', 'end': '2025-10-20', 'status': '进行中'},
        {'task': '游戏毯 A+ 设计', 'start': '2025-10-11', 'end': '2025-10-25', 'status': '未开始'},
    ],
    '易灵': [
        {'task': '高尔夫毛巾调研', 'start': '2026-01-01', 'end': '2026-01-05', 'status': '已完成'},
        {'task': '女生书包跟进', 'start': '2026-01-15', 'end': '2026-01-20', 'status': '已完成'},
        {'task': '女生书包设计', 'start': '2026-01-20', 'end': '2026-01-25', 'status': '已完成'},
        {'task': '涤纶书包跟进', 'start': '2026-02-01', 'end': '2026-02-15', 'status': '进行中'},
    ],
    '陈亮亮': [
        {'task': '游戏毯物流跟踪', 'start': '2025-09-27', 'end': '2025-09-30', 'status': '已完成'},
        {'task': '花环到货跟踪', 'start': '2025-09-30', 'end': '2025-10-11', 'status': '已完成'},
        {'task': '手机支架丢件处理', 'start': '2025-10-11', 'end': '2025-10-20', 'status': '进行中'},
        {'task': 'VAT 申报', 'start': '2025-10-11', 'end': '2025-10-31', 'status': '进行中'},
        {'task': '工资发放', 'start': '2025-10-15', 'end': '2025-10-15', 'status': '已完成'},
    ],
    '卢思圻': [
        {'task': '数据记录整理', 'start': '2025-09-01', 'end': '2025-12-31', 'status': '进行中'},
        {'task': '高尔夫毛巾拍摄', 'start': '2026-01-05', 'end': '2026-01-10', 'status': '已完成'},
    ],
}

# 状态颜色映射
status_colors = {
    '已完成': '#4CAF50',      # 绿色
    '进行中': '#2196F3',      # 蓝色
    '未开始': '#FFC107',      # 黄色
    '已延期': '#F44336',      # 红色
}

# 创建图表
fig, ax = plt.subplots(figsize=(16, 10))

# 人员列表（正序，让第一个人显示在最上面）
people = list(team_data.keys())

# 计算每个人的任务数量，用于分配 y 轴位置
max_tasks_per_person = max(len(team_data[p]) for p in team_data)

# 绘制甘特图
bars = []
y_offset = 0

for i, person in enumerate(people):
    tasks = team_data[person]
    # 每个人的任务在 y 轴上占据一个区域
    base_y = len(people) - 1 - i
    
    for j, task in enumerate(tasks):
        start_date = datetime.strptime(task['start'], '%Y-%m-%d')
        end_date = datetime.strptime(task['end'], '%Y-%m-%d')
        duration = (end_date - start_date).days + 1
        
        # 计算 y 位置（每个人的任务稍微错开）
        y_pos = base_y - (j * 0.6 / max_tasks_per_person)
        
        # 绘制条形
        bar = ax.barh(y_pos, duration, left=start_date, 
                      color=status_colors.get(task['status'], '#9E9E9E'),
                      edgecolor='white', linewidth=0.5)
        
        # 添加任务标签
        ax.text(start_date, y_pos, f" {task['task']} ", 
                va='center', fontsize=7, color='white', fontweight='bold')

# 设置 x 轴日期格式
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45)

# 设置 y 轴
ax.set_yticks(range(len(people)))
ax.set_yticklabels(people, fontsize=10)

# 添加图例
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=status) 
                   for status, color in status_colors.items()]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))

# 添加标题和标签
plt.title('南野科技团队工作计划甘特图', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('日期', fontsize=12)
plt.ylabel('团队成员', fontsize=12)

# 添加网格
ax.grid(True, alpha=0.3, linestyle='--')

# 调整布局
plt.tight_layout()

# 保存图片到 BOOK 文件夹
save_path = '/Users/jo/Desktop/Development/BOOK/团队工作计划甘特图.png'
plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"✅ 甘特图已保存至：{save_path}")

print("\n🎉 甘特图生成完成！")
