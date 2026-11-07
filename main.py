import argparse
import json
from pathlib import Path
from lexer import tokenize
from parser import parse_code
from interpreter import Interpreter
from codegen import CodeGenerator


def main():
    root = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Аналізатор навчальної підмножини C (Lex/YACC)")
    ap.add_argument("source", nargs="?", default=str(root / "examples" / "demo.c"),
                    help="Шлях до вихідного файлу з C-кодом")
    ap.add_argument("--tokens", action="store_true", help="Показати токени")
    ap.add_argument("--ast", action="store_true", help="Показати AST у терміналі")
    ap.add_argument("--no-run", action="store_true", help="Не запускати інтерпретатор")
    ap.add_argument("--output", default=str(root / "generated.py"),
                    help="Файл для згенерованого Python-коду")
    ap.add_argument("--json", default=str(root / "ast.json"),
                    help="JSON для візуалізації у браузері")
    args = ap.parse_args()

    try:
        code = Path(args.source).read_text(encoding="utf-8-sig")
        print(f"ДЖЕРЕЛО: {args.source}")
        if args.tokens:
            print("\nТОКЕНИ:")
            for item in tokenize(code):
                print(f"{item['type']:<12} {str(item['value']):<12} рядок {item['line']}")
        ast = parse_code(code)
        print("СИНТАКСИЧНИЙ АНАЛІЗ: УСПІШНО")
        if args.ast:
            print(json.dumps(ast, indent=2, ensure_ascii=False))
        Path(args.json).write_text(json.dumps(ast, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"AST записано: {args.json}")

        if not args.no_run:
            Interpreter().execute(ast)

        code_python = CodeGenerator().generate(ast)
        Path(args.output).write_text(code_python, encoding="utf-8")
        print(f"Python-код записано: {args.output}")

    except (OSError, SyntaxError, RuntimeError, ValueError) as error:
        ap.exit(1, f"ПОМИЛКА: {error}\n")


if __name__ == "__main__":
    main()
