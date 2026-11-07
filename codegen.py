"""Трансляція AST навчальної підмножини C у виконуваний Python-код."""

import keyword
from pathlib import Path
from parser import parse_code
 
class CodeGenerator:
    def __init__(self):
        self.scopes = [{}]
        self.used_names = set()
        self.counter = 0
        self.needs_division = False
        self.global_names = {}
        self.lines = []
        self.iteration_limit = 10000

    def fresh_name(self, original):
        # Власне ім'я для кожного оголошення зберігає затінення змінних.
        candidate = original
        if (keyword.iskeyword(candidate) or candidate.startswith('__lab3_')
                or candidate in self.used_names):
            self.counter += 1
            candidate = f"cvar_{self.counter}_{original}"
        while candidate in self.used_names or keyword.iskeyword(candidate):
            self.counter += 1
            candidate = f"cvar_{self.counter}_{original}"
        self.used_names.add(candidate)
        return candidate

    def find(self, original):
        for scope in reversed(self.scopes):
            if original in scope:
                return scope[original]
        raise ValueError(f"Неоголошена змінна: {original}")

    def expression(self, node):
        kind = node["type"]
        if kind == "Number":
            return repr(node["value"])
        if kind == "Identifier":
            name, _ = self.find(node["name"])
            # Неініціалізоване значення має викликати помилку, як в інтерпретаторі.
            return f"__lab3_read({name}, {node['name']!r})"
        if kind == "UnaryExpression":
            return f"(-{self.expression(node['operand'])})"
        if kind == "BinaryExpression":
            left = self.expression(node["left"])
            right = self.expression(node["right"])
            op = node["operator"]
            if op == "/":
                self.needs_division = True
                return f"__lab3_div({left}, {right})"
            if op in ("==", "!=", "<", "<=", ">", ">="):
                return f"int(({left} {op} {right}))"
            return f"({left} {op} {right})"
        raise ValueError(f"Непідтримуваний вираз: {kind}")

    def emit(self, indent, line):
        self.lines.append("    " * indent + line)

    def statement(self, node, indent):
        kind = node["type"]
        if kind == "VariableDeclaration":
            original = node["name"]
            if original in self.scopes[-1]:
                raise ValueError(f"Повторне оголошення в блоці: {original}")
            # Ініціалізатор обчислюється до створення нової змінної.
            value = ("None" if node["value"] is None else
                     f"{node['dataType']}({self.expression(node['value'])})")
            target = self.fresh_name(original)
            self.scopes[-1][original] = (target, node["dataType"])
            if len(self.scopes) == 1:
                self.global_names[original] = target
            self.emit(indent, f"{target} = {value}")
            return
        if kind == "Assignment":
            target, data_type = self.find(node["name"])
            value = self.expression(node["value"])
            self.emit(indent, f"{target} = {data_type}({value})")
            return
        if kind == "BlockStatement":
            self.scopes.append({})
            try:
                if not node["body"]:
                    self.emit(indent, "pass")
                for child in node["body"]:
                    self.statement(child, indent)
            finally:
                self.scopes.pop()
            return
        if kind == "IfStatement":
            condition = self.expression(node["condition"])
            self.emit(indent, f"if {condition}:")
            self.statement(node["consequent"], indent + 1)
            if node["alternate"] is not None:
                self.emit(indent, "else:")
                self.statement(node["alternate"], indent + 1)
            return
        if kind == "WhileStatement":
            condition = self.expression(node["condition"])
            self.emit(indent, f"while {condition}:")
            self.emit(indent + 1, "__lab3_iterations += 1")
            self.emit(indent + 1, "if __lab3_iterations > 10000:")
            self.emit(indent + 2, "raise RuntimeError('Перевищено ліміт ітерацій')")
            self.statement(node["body"], indent + 1)
            return
        raise ValueError(f"Непідтримувана інструкція: {kind}")

    def generate(self, ast):
        if ast["type"] != "Program":
            raise ValueError("Некоректний корінь AST")
        # Повторна генерація тим самим об'єктом починається з чистого стану.
        self.__init__()
        for item in ast["body"]:
            self.statement(item, 0)

        header = [
            "# Автоматично згенерований Python-код із навчальної підмножини C.",
            "# Вхідна граматика реалізована засобами Lex/YACC (PLY).",
            "",
            "def __lab3_read(value, name):",
            "    # Перевірка читання неініціалізованої змінної.",
            "    if value is None:",
            "        raise RuntimeError(f'Неініціалізована змінна: {name}')",
            "    return value",
            "",
        ]
        if self.needs_division:
            header += [
                "def __lab3_div(a, b):",
                "    # Цілочисельне ділення C відкидає дробову частину до нуля.",
                "    if b == 0:",
                "        raise RuntimeError('Ділення на нуль')",
                "    if isinstance(a, int) and isinstance(b, int):",
                "        q = abs(a) // abs(b)",
                "        return -q if (a < 0) != (b < 0) else q",
                "    return a / b",
                "",
            ]
        header += ["__lab3_iterations = 0", ""]
        footer = ["", "# Підсумкові значення глобальних змінних."]
        for original, target in self.global_names.items():
            footer.append(f"print({original!r}, '=', {target})")
        if not self.global_names:
            footer.append("# Глобальних змінних немає.")
        return "\n".join(header + self.lines + footer) + "\n"


if __name__ == "__main__":
    code = """int a = 5;
int sum = 0;
while (a > 0) { sum = sum + a; a = a - 1; }
if (sum == 15) { sum = sum * 2; } else { sum = 0; }
"""
    result = CodeGenerator().generate(parse_code(code))
    target = Path(__file__).with_name("generated.py")
    target.write_text(result, encoding="utf-8")
    print(result)
    print(f"Згенерований код збережено: {target.name}")
