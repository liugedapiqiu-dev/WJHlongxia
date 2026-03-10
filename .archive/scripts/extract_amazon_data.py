#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Amazon 书包三件套搜索结果数据提取"""

import csv
from datetime import datetime

# 从搜索结果页面提取的产品数据
products = [
    {
        "排名": 1,
        "ASIN": "B0BX43LRLL",
        "标题": "YJMKOI 3Pcs Daisy Prints Backpack for Girls Middle-School Elementary Students Bookbag Set with Lunch Box (Black)",
        "价格": "$20.99",
        "评分": 4.7,
        "评价数": 203,
        "配送": "Tue, Mar 10",
        "Prime": "No"
    },
    {
        "排名": 2,
        "ASIN": "B0CGNKKFG8",
        "标题": "Kawaii Girls Backpack for School with Convertible Shoulder Tote Bag, Cute Teenage Multiple Pockets Backpack for Primary Elementary High School, Pink 3 Pcs Set",
        "价格": "$36.99",
        "评分": 4.7,
        "评价数": 468,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 3,
        "ASIN": "B0B8M95DZP",
        "标题": "EKUIZAI 2Pcs Daisy Prints Backpack Sets for Girl Bookbag Primary Schoolbag Elementary Students Daypack with Lunch Bag (Overall Pick)",
        "价格": "$19.99",
        "评分": 4.7,
        "评价数": 2058,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 4,
        "ASIN": "B0F1KV2FVG",
        "标题": "Girls Backpack Set, Cute Kids School Backpack For Girls, Childrens Schoolbag For Elementary Primary",
        "价格": "需查看",
        "评分": 4.8,
        "评价数": 154,
        "配送": "Tue, Mar 10",
        "Prime": "No"
    },
    {
        "排名": 5,
        "ASIN": "B0F2FLP2XS",
        "标题": "Fimibuke Backpacks for Girls, 3 PCS Waterproof School Backpack with Lunch Box & Pencil Pouch for Kids Teen Girl, Cute Bookbag School Bag for Elementary Middle High School Student Ages 6+ (Khaki)",
        "价格": "$39.99",
        "评分": 4.6,
        "评价数": 367,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 6,
        "ASIN": "B0F852KXJF",
        "标题": "Kids Backpack for Girls Flower schoolbag with Lunch Bag & Pen Case Waterproof Girl Bookbag for Elementary school (pink)",
        "价格": "$31.99",
        "评分": 5.0,
        "评价数": 22,
        "配送": "Wed, Mar 11 (Only 7 left)",
        "Prime": "No"
    },
    {
        "排名": 7,
        "ASIN": "B0F1FQJQBQ",
        "标题": "Backpack for Girls 3pcs Set, Kids Backpack for Girls with Lunch Box Pencil Case Set for Teens Elementary Middle School Bags (Purple-3 Piece Set-1)",
        "价格": "$33.99",
        "评分": 4.6,
        "评价数": 10,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 8,
        "ASIN": "B0DN6DDG18",
        "标题": "Hidds School Backpack with Lunch Box for Teens Girls Women 15.6 Inch Laptop College Backpacks with Lunch Bag Bookbag Set Corduroy Kids Elementary Middle High Bag Students Back Pack Daypack - Blue Set",
        "价格": "$39.98",
        "评分": 4.6,
        "评价数": 65,
        "配送": "Wed, Mar 11 (Only 4 left)",
        "Prime": "No"
    },
    {
        "排名": 9,
        "ASIN": "B0F2M1NRW8",
        "标题": "Backpack for Girls 15.6 Inch Laptop School Bag Kids Elementary College 3pcs Backpacks Lunch box Pencil Case Set Bookbags for Girls Teen Women Student Purple",
        "价格": "$29.98",
        "评分": 4.6,
        "评价数": 35,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 10,
        "ASIN": "B0D1P1JFQH",
        "标题": "3pcs Girls Backpack With Lunch Box & Pencil Case, Cute Rabbit Kids School Backpack Set For Kindergarten & Elementary School (Style A Pink-16.5in) - 50+ bought in past month",
        "价格": "$36.41",
        "评分": 4.6,
        "评价数": 183,
        "配送": "Thu, Mar 12 (Only 9 left)",
        "Prime": "No"
    },
    {
        "排名": 11,
        "ASIN": "B07FM2C71Q",
        "标题": "School Backpack for Teen Girls, Bookbag with Lunch Box and Pencil Case",
        "价格": "$34.99",
        "评分": 4.7,
        "评价数": 2112,
        "配送": "Wed, Mar 11 (Only 1 left)",
        "Prime": "No"
    },
    {
        "排名": 12,
        "ASIN": "B0C2KGB2RC",
        "标题": "Bluboon Bookbags School Backpack Laptop Schoolbag for Teens Girls High School - Save 7% with coupon",
        "价格": "$32.99",
        "评分": 4.6,
        "评价数": 237,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 13,
        "ASIN": "B0BTLM14Z5",
        "标题": "3Pcs Girls Rolling Backpack Kids Bookbag with Wheels Set Elementary Students Outdoors Trolley Schoolbag",
        "价格": "$40.90",
        "评分": 4.7,
        "评价数": 79,
        "配送": "Mar 10-19",
        "Prime": "No"
    },
    {
        "排名": 14,
        "ASIN": "B0F943JYBT",
        "标题": "Girls Backpack Set with Bows Heart-shaped Lightweight Schoolbags for Girl Children Spacious Bookbag Waterproof (purple-2)",
        "价格": "$36.99",
        "评分": 4.9,
        "评价数": 20,
        "配送": "Tue, Mar 10 (Only 11 left)",
        "Prime": "No"
    },
    {
        "排名": 15,
        "ASIN": "B0CC67GN3T",
        "标题": "Disney Lilo and Stitch Backpack 3 Piece | Backpack, Pencil Case and Water Bottle | Lilo & Stich Schoolbag | Multicolour",
        "价格": "需查看",
        "评分": 4.4,
        "评价数": 238,
        "配送": "Tue, Mar 10",
        "Prime": "No"
    },
    {
        "排名": 16,
        "ASIN": "B07Z6KSZ8F",
        "标题": "AGSDON 3PCS Toddler Backpack and Lunch Box for Boys, 12\" Dinosaur Preschool Kids Bookbag, Cute Animal Kindergarten Schoolbag (3 Piece Set)",
        "价格": "需查看",
        "评分": 4.8,
        "评价数": 2957,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 17,
        "ASIN": "B09R7DMG3S",
        "标题": "3Pcs Boys Galaxy Rolling Backpack Kids Backpack with Wheels Trolley Bookbag Wheeled School Bag with Lunch Bag",
        "价格": "$42.99",
        "评分": 4.4,
        "评价数": 234,
        "配送": "Thu, Mar 12 (Only 4 left)",
        "Prime": "No"
    },
    {
        "排名": 18,
        "ASIN": "B0DRVD1Z1L",
        "标题": "Backpacks for Girls Backpack Kids Travel Backpack School Bags for Girls Backpacks Ages 8-10 Bookbag",
        "价格": "$21.99",
        "评分": 4.7,
        "评价数": 175,
        "配送": "Thu, Mar 12 (Only 1 left)",
        "Prime": "No"
    },
    {
        "排名": 19,
        "ASIN": "B0F8BMBYN1",
        "标题": "Kids Backpack With Lunch Box, Lightweight School 3 Set, Boys Girls Starry Sky Schoolbag, Children Teens Elementary Middle School Christmas",
        "价格": "需查看",
        "评分": 4.3,
        "评价数": 17,
        "配送": "Wed, Mar 11",
        "Prime": "No"
    },
    {
        "排名": 20,
        "ASIN": "B07WN9SSPG",
        "标题": "Toddler Backpack for Girls and Boys, Preschool Bookbag, 12\" Cute Cartoon Animal School Bag",
        "价格": "$23.99",
        "评分": 4.8,
        "评价数": 2100,
        "配送": "Tue, Mar 10",
        "Prime": "No"
    }
]

# 保存为 CSV 文件
output_file = "/Users/jo/.openclaw/workspace/亚马逊书包三件套竞品分析_2026-02-28.csv"

with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    fieldnames = ["排名", "ASIN", "标题", "价格", "评分", "评价数", "配送", "Prime", "备注"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    writer.writeheader()
    for product in products:
        # 添加备注
        note = ""
        if "Only" in product.get("配送", ""):
            note = "库存紧张"
        if "Overall Pick" in product.get("标题", ""):
            note = "亚马逊推荐"
        if "50+ bought" in product.get("标题", ""):
            note = "热销产品"
        if "Save" in product.get("标题", ""):
            note = "有优惠券"
            
        row = {**product, "备注": note}
        writer.writerow(row)

print(f"✅ 数据已保存到：{output_file}")
print(f"📊 共提取 {len(products)} 个产品")
print(f"⏰ 数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 打印统计信息
print("\n📈 价格区间统计:")
prices = [p["价格"] for p in products if p["价格"] != "需查看"]
if prices:
    min_price = min(prices)
    max_price = max(prices)
    print(f"   最低价：{min_price}")
    print(f"   最高价：{max_price}")

print("\n⭐ 评分统计:")
ratings = [p["评分"] for p in products]
avg_rating = sum(ratings) / len(ratings)
print(f"   平均分：{avg_rating:.2f}")
print(f"   最高分：{max(ratings)}")
print(f"   最低分：{min(ratings)}")
