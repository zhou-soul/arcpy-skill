#!/usr/bin/env python3
"""
批量字段计算工具

功能：对要素类的字段进行批量计算，支持表达式和Python函数
用法：
    # 面积换算
    python field_calculator.py --input parcels --field AREA_MU --expression "!SHAPE.area! / 666.67"
    
    # 使用Python函数
    python field_calculator.py --input parcels --field TYPE_NAME --function "classify_type" --code "def classify_type(code): return {'A': '农业', 'B': '建设', 'C': '生态'}.get(code[0], '未知')"
"""

import arcpy
import argparse


def calculate_field(input_fc, field_name, expression=None, function_name=None, code_block=None):
    """
    批量字段计算
    
    参数:
        input_fc: 输入要素类
        field_name: 目标字段名
        expression: 计算表达式（如 "!AREA! / 666.67"）
        function_name: Python函数名（配合code_block使用）
        code_block: Python函数定义
    """
    # 检查字段是否存在
    existing_fields = [f.name for f in arcpy.ListFields(input_fc)]
    
    if field_name not in existing_fields:
        print(f"字段 '{field_name}' 不存在，请先添加字段")
        return
    
    # 构建计算表达式
    if function_name and code_block:
        calc_expression = f"{function_name}(!{field_name}!)"
        arcpy.management.CalculateField(
            input_fc, field_name, calc_expression, "PYTHON3", code_block
        )
    elif expression:
        arcpy.management.CalculateField(
            input_fc, field_name, expression, "PYTHON3"
        )
    else:
        print("请提供 expression 或 function_name+code_block")
        return
    
    # 统计结果
    with arcpy.da.SearchCursor(input_fc, [field_name]) as cursor:
        values = [row[0] for row in cursor if row[0] is not None]
    
    print(f"字段 '{field_name}' 计算完成")
    print(f"  有效值数量: {len(values)}")
    if values and isinstance(values[0], (int, float)):
        print(f"  最小值: {min(values):.4f}")
        print(f"  最大值: {max(values):.4f}")
        print(f"  平均值: {sum(values)/len(values):.4f}")


# 常用计算函数模板
COMMON_FUNCTIONS = {
    "面积转亩": {
        "field_type": "DOUBLE",
        "expression": "!SHAPE.area! / 666.67",
    },
    "面积转公顷": {
        "field_type": "DOUBLE",
        "expression": "!SHAPE.area! / 10000",
    },
    "面积转平方米": {
        "field_type": "DOUBLE",
        "expression": "!SHAPE.area!",
    },
    "计算周长": {
        "field_type": "DOUBLE",
        "expression": "!SHAPE.length!",
    },
    "提取X坐标": {
        "field_type": "DOUBLE",
        "expression": "!SHAPE.centroid.X!",
    },
    "提取Y坐标": {
        "field_type": "DOUBLE",
        "expression": "!SHAPE.centroid.Y!",
    },
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量字段计算")
    parser.add_argument("--input", required=True, help="输入要素类路径")
    parser.add_argument("--field", required=True, help="目标字段名")
    parser.add_argument("--expression", help="计算表达式")
    parser.add_argument("--function", help="Python函数名")
    parser.add_argument("--code", help="Python函数代码")
    
    args = parser.parse_args()
    calculate_field(args.input, args.field, args.expression, args.function, args.code)
