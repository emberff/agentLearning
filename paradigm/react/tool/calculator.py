from sympy import *
import re


from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)


transformations = (
    standard_transformations +
    (implicit_multiplication_application,)
)


import re

def preprocess(expression: str) -> str:
    """
    将自然语言转换为 SymPy 可解析的表达式
    """

    expression = expression.strip()

    # 中文符号
    expression = expression.replace("（", "(")
    expression = expression.replace("）", ")")
    expression = expression.replace("，", ",")
    expression = expression.replace("。", "")

    # 数学符号
    expression = expression.replace("×", "*")
    expression = expression.replace("x", "*")
    expression = expression.replace("X", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("^", "**")

    # 去掉问号
    expression = expression.replace("=", "")
    expression = expression.replace("？", "")
    expression = expression.replace("?", "")

    # 去掉文字
    expression = re.sub(r"计算|请计算|等于多少|结果是多少", "", expression)

    return expression.strip()

def calculator(expression: str) -> str:
    """
    一个基于 SymPy 的数学计算工具。

    支持：
    - 四则运算
    - 幂运算
    - 三角函数
    - 对数
    - 指数
    - 求导
    - 积分
    - 解方程
    """

    print(f"🧮 正在执行数学计算: {expression}")

    try:
        expression = preprocess(expression)
        expr = parse_expr(
            expression,
            transformations=transformations,
            evaluate=True
        )

        result = expr.doit()

        return (
            f"表达式: {expression}\n"
            f"解析后: {expr}\n"
            f"计算结果: {result}"
        )

    except Exception as e:
        return f"计算失败：{e}"