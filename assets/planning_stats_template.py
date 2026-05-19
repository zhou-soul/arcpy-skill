#!/usr/bin/env python3
"""
规划统计报告模板

功能：生成村庄规划用地统计报告（Markdown格式）
典型应用：村庄规划文本中的用地平衡表、指标统计

使用方式：修改下方参数后运行，输出Markdown报告
"""

import arcpy
import os
from datetime import datetime


# ===================== 配置 =====================

CONFIG = {
    "project_name": "XX村村庄规划",
    "county": "盐边县",
    "town": "永兴镇",
    "village": "XX村",
    "parcels_fc": r"C:\Data\Project.gdb\parcels",
    "code_field": "LANDUSE_CODE",
    "output_path": r"C:\Output\planning_report.md",
}


# ===================== 执行 =====================

def generate_planning_report(config):
    """生成规划统计报告"""
    
    fc = config["parcels_fc"]
    code_field = config["code_field"]
    
    # 统计
    stats = {}
    with arcpy.da.SearchCursor(fc, [code_field, "SHAPE@AREA"]) as cursor:
        for row in cursor:
            code = str(row[0]).strip() if row[0] else "未知"
            area_sqm = row[1]
            if code not in stats:
                stats[code] = {'sqm': 0, 'count': 0}
            stats[code]['sqm'] += area_sqm
            stats[code]['count'] += 1
    
    total_sqm = sum(s['sqm'] for s in stats.values())
    total_mu = total_sqm / 666.67
    total_ha = total_sqm / 10000
    
    # 生成Markdown报告
    lines = []
    lines.append(f"# {config['project_name']}用地统计报告\n")
    lines.append(f"- **县（区）**：{config['county']}")
    lines.append(f"- **乡镇**：{config['town']}")
    lines.append(f"- **村**：{config['village']}")
    lines.append(f"- **生成日期**：{datetime.now().strftime('%Y年%m月%d日')}")
    lines.append(f"- **规划范围总面积**：{total_mu:.2f}亩（{total_ha:.4f}公顷）\n")
    
    # 用地平衡表
    lines.append("## 用地平衡表\n")
    lines.append("| 编码 | 面积(亩) | 面积(公顷) | 图斑数 | 占比(%) |")
    lines.append("|------|---------|-----------|--------|---------|")
    
    for code in sorted(stats.keys()):
        s = stats[code]
        mu = s['sqm'] / 666.67
        ha = s['sqm'] / 10000
        pct = mu / total_mu * 100 if total_mu > 0 else 0
        lines.append(f"| {code} | {mu:.2f} | {ha:.4f} | {s['count']} | {pct:.1f} |")
    
    lines.append(f"| **合计** | **{total_mu:.2f}** | **{total_ha:.4f}** | **{sum(s['count'] for s in stats.values())}** | **100.0** |")
    
    # 主要指标
    lines.append("\n## 主要指标\n")
    lines.append(f"- 规划范围总面积：{total_mu:.2f}亩")
    lines.append(f"- 图斑总数：{sum(s['count'] for s in stats.values())}个")
    lines.append(f"- 地类数量：{len(stats)}种")
    
    # 保存报告
    report = "\n".join(lines)
    os.makedirs(os.path.dirname(config["output_path"]) or ".", exist_ok=True)
    with open(config["output_path"], "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"报告已生成: {config['output_path']}")
    print(f"\n预览:\n")
    print(report[:500] + "...")
    
    return report


if __name__ == "__main__":
    generate_planning_report(CONFIG)
