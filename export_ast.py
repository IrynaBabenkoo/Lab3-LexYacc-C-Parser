"""Експортування AST у JSON для вебвізуалізації D3.js."""

import json
from pathlib import Path
from parser import parse_code


EXAMPLE = """int a = 5;
int sum = 0;
while (a > 0) {
    sum = sum + a;
    a = a - 1;
}
if (sum == 15) {
    sum = sum * 2;
} else {
    sum = 0;
}
"""


def export_ast(code, filename=None):
    ast = parse_code(code)
    output = Path(filename) if filename else Path(__file__).with_name("ast.json")
    output.write_text(json.dumps(ast, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Синтаксичний аналіз виконано. AST збережено: {output}")
    return ast


if __name__ == "__main__":
    export_ast(EXAMPLE)
