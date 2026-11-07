"""Виконання AST: арифметика, умови, цикли та області видимості."""

from parser import parse_code


class Interpreter:
    def __init__(self, max_iterations=10000, verbose=True):
        self.scopes = [{}]
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def find_variable(self, name):
        # Пошук починається з найближчої області видимості.
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise RuntimeError(f"Неоголошена змінна: {name}")

    @staticmethod
    def convert_value(value, data_type):
        if data_type == "int":
            return int(value)
        if data_type == "float":
            return float(value)
        raise RuntimeError(f"Непідтримуваний тип: {data_type}")

    def evaluate(self, node):
        kind = node["type"]
        if kind == "Number":
            return node["value"]
        if kind == "Identifier":
            name = node["name"]
            value = self.find_variable(name)["value"]
            if value is None:
                raise RuntimeError(f"Неініціалізована змінна: {name}")
            return value
        if kind == "UnaryExpression":
            if node["operator"] != "-":
                raise RuntimeError("Невідомий унарний оператор")
            return -self.evaluate(node["operand"])
        if kind == "BinaryExpression":
            left = self.evaluate(node["left"])
            right = self.evaluate(node["right"])
            op = node["operator"]
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                if right == 0:
                    raise RuntimeError("Ділення на нуль")
                if isinstance(left, int) and isinstance(right, int):
                    # У C ціле ділення округлюється до нуля, не до -∞.
                    quotient = abs(left) // abs(right)
                    return -quotient if (left < 0) != (right < 0) else quotient
                return left / right
            comparisons = {
                "==": left == right, "!=": left != right,
                "<": left < right, "<=": left <= right,
                ">": left > right, ">=": left >= right,
            }
            if op in comparisons:
                return int(comparisons[op])
            raise RuntimeError(f"Невідомий оператор: {op}")
        raise RuntimeError(f"Невідомий тип виразу: {kind}")

    def execute_statement(self, node):
        kind = node["type"]
        if kind == "VariableDeclaration":
            name = node["name"]
            if name in self.scopes[-1]:
                raise RuntimeError(f"Повторне оголошення змінної: {name}")
            data_type = node["dataType"]
            value = (None if node["value"] is None else
                     self.convert_value(self.evaluate(node["value"]), data_type))
            self.scopes[-1][name] = {"type": data_type, "value": value}
            self.log(f"ОГОЛОШЕННЯ {data_type} {name} = {value}")
            return
        if kind == "Assignment":
            name = node["name"]
            variable = self.find_variable(name)
            variable["value"] = self.convert_value(
                self.evaluate(node["value"]), variable["type"]
            )
            self.log(f"ПРИСВОЄННЯ {name} = {variable['value']}")
            return
        if kind == "BlockStatement":
            self.scopes.append({})
            try:
                for statement in node["body"]:
                    self.execute_statement(statement)
            finally:
                self.scopes.pop()
            return
        if kind == "IfStatement":
            condition = self.evaluate(node["condition"])
            self.log(f"УМОВА if: {'ІСТИНА' if condition else 'ХИБА'}")
            branch = node["consequent"] if condition else node["alternate"]
            if branch is not None:
                self.execute_statement(branch)
            return
        if kind == "WhileStatement":
            self.log("ПОЧАТОК циклу while")
            while self.evaluate(node["condition"]) != 0:
                self.iteration_count += 1
                if self.iteration_count > self.max_iterations:
                    raise RuntimeError("Перевищено ліміт ітерацій: можливий нескінченний цикл")
                self.execute_statement(node["body"])
            self.log("КІНЕЦЬ циклу while")
            return
        raise RuntimeError(f"Непідтримувана інструкція: {kind}")

    def execute(self, ast):
        if ast["type"] != "Program":
            raise RuntimeError("Некоректний кореневий вузол AST")
        # Повторний запуск не повинен зберігати стан попередньої програми.
        self.scopes = [{}]
        self.iteration_count = 0
        self.log("\nВИКОНАННЯ ПРОГРАМИ\n" + "-" * 45)
        for statement in ast["body"]:
            self.execute_statement(statement)
        result = {name: variable["value"] for name, variable in self.scopes[0].items()}
        self.log("\nКІНЦЕВІ ЗНАЧЕННЯ ГЛОБАЛЬНИХ ЗМІННИХ\n" + "-" * 45)
        for name, variable in self.scopes[0].items():
            self.log(f"{variable['type']:<7} {name:<15} = {variable['value']}")
        return result


if __name__ == "__main__":
    code = """int a = 5;
int sum = 0;
while (a > 0) { sum = sum + a; a = a - 1; }
if (sum == 15) { sum = sum * 2; } else { sum = 0; }
"""
    Interpreter().execute(parse_code(code))
