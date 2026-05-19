#!/usr/bin/env python3
"""
用地面积统计与平衡表生成脚本

功能：统计要素类中各类用地的面积，生成用地平衡表，支持导出CSV
用法：
    python land_use_stats.py --input C:/Data/Project.gdb/parcels --field LANDUSE_CODE --output C:/Output/balance.csv
"""

import arcpy
import csv
import argparse


# 地类编码→名称映射（按国土空间规划用地用海分类，可根据实际需要调整）
LANDUSE_NAMES = {
    # 建设用地
    '01': '耕地', '02': '园地', '03': '林地', '04': '草地', '05': '湿地',
    '06': '农业设施建设用地', '07': '居住用地', '08': '公共管理与公共服务用地',
    '09': '商业服务业用地', '10': '工业用地', '11': '仓储用地',
    '12': '交通运输用地', '13': '公用设施用地', '14': '绿地与开敞空间用地',
    '15': '特殊用地', '16': '留白用地',
    # 非建设
    '17': '陆地水域', '18': '海域', '19': '其他土地',
}

# 大类映射
CATEGORIES = {
    '01': '农用地', '02': '农用地', '03': '农用地', '04': '农用地',
    '05': '生态用地', '06': '农业设施', 
    '07': '建设用地', '08': '建设用地', '09': '建设用地',
    '10': '建设用地', '11': '建设用地', '12': '建设用地',
    '13': '建设用地', '14': '建设用地', '15': '特殊用地', '16': '留白',
    '17': '水域', '18': '海域', '19': '其他',
}


def land_use_stats(input_fc, code_field="LANDUSE_CODE", output_csv=None):
    """
    用地面积统计
    
    参数:
        input_fc: 输入要素类
        code_field: 地类编码字段
        output_csv: 输出CSV路径（可选）
    """
    stats = {}
    
    with arcpy.da.SearchCursor(input_fc, [code_field, "SHAPE@AREA"]) as cursor:
        for row in cursor:
            code = str(row[0]).strip() if row[0] else "未知"
            area_sqm = row[1]
            
            if code not in stats:
                stats[code] = {'sqm': 0, 'mu': 0, 'ha': 0, 'count': 0}
            stats[code]['sqm'] += area_sqm
            stats[code]['mu'] += area_sqm / 666.67
            stats[code]['ha'] += area_sqm / 10000
            stats[code]['count'] += 1
    
    # 按大类汇总
    category_stats = {}
    for code, s in stats.items():
        cat = CATEGORIES.get(code[:2] if len(code) >= 2 else code[0], '其他')
        if cat not in category_stats:
            category_stats[cat] = {'sqm': 0, 'mu': 0, 'ha': 0, 'count': 0}
        category_stats[cat]['sqm'] += s['sqm']
        category_stats[cat]['mu'] += s['mu']
        category_stats[cat]['ha'] += s['ha']
        category_stats[cat]['count'] += s['count']
    
    # 输出明细表
    total_mu = sum(s['mu'] for s in stats.values())
    
    print(f"\n{'='*72}")
    print(f"用地平衡表")
    print(f"{'='*72}")
    print(f"{'编码':<6} {'用地名称':<18} {'大类':<8} {'图斑数':>6} {'面积(亩)':>12} {'占比':>8}")
    print(f"{'-'*72}")
    
    for code in sorted(stats.keys()):
        name = LANDUSE_NAMES.get(code[:2] if len(code) >= 2 else code, '未分类')
        cat = CATEGORIES.get(code[:2] if len(code) >= 2 else code[0], '其他')
        s = stats[code]
        pct = s['mu'] / total_mu * 100 if total_mu > 0 else 0
        print(f"{code:<6} {name:<18} {cat:<8} {s['count']:>6} {s['mu']:>12.2f} {pct:>7.1f}%")
    
    print(f"{'-'*72}")
    print(f"{'合计':<32} {sum(s['count'] for s in stats.values()):>6} {total_mu:>12.2f} {'100.0%':>8}")
    
    # 大类汇总
    print(f"\n{'='*40}")
    print(f"大类汇总")
    print(f"{'='*40}")
    for cat in sorted(category_stats.keys()):
        s = category_stats[cat]
        pct = s['mu'] / total_mu * 100 if total_mu > 0 else 0
        print(f"{cat:<12} {s['count']:>6}个图斑 {s['mu']:>10.2f}亩 {pct:>6.1f}%")
    
    # 导出CSV
    if output_csv:
        os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['编码', '用地名称', '大类', '图斑数', '面积(平方米)', '面积(亩)', '面积(公顷)', '占比(%)'])
            for code in sorted(stats.keys()):
                name = LANDUSE_NAMES.get(code[:2] if len(code) >= 2 else code, '未分类')
                cat = CATEGORIES.get(code[:2] if len(code) >= 2 else code[0], '其他')
                s = stats[code]
                pct = s['mu'] / total_mu * 100 if total_mu > 0 else 0
                writer.writerow([code, name, cat, s['count'], f"{s['sqm']:.2f}", f"{s['mu']:.2f}", f"{s['ha']:.4f}", f"{pct:.1f}"])
        print(f"\n已导出: {output_csv}")
    
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="用地面积统计与平衡表生成")
    parser.add_argument("--input", required=True, help="输入要素类路径")
    parser.add_argument("--field", default="LANDUSE_CODE", help="地类编码字段名")
    parser.add_argument("--output", help="输出CSV文件路径")
    
    args = parser.parse_args()
    land_use_stats(args.input, args.field, args.output)
