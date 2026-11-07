"""Автоматичні перевірки лексера, парсера, інтерпретатора та транслятора."""

import contextlib
import io
import unittest
from lexer import tokenize
from parser import parse_code
from interpreter import Interpreter
from codegen import CodeGenerator


class ParserTests(unittest.TestCase):
    def evaluate_both(self, code):
        ast = parse_code(code)
        interpreted = Interpreter(verbose=False).execute(ast)
        generated = CodeGenerator().generate(ast)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(generated, "<згенерований код>", "exec"), {})
        displayed = {}
        for line in output.getvalue().splitlines():
            name, value = line.split(" = ", 1)
            original = interpreted[name]
            if original is None:
                displayed[name] = value
            elif isinstance(original, float):
                displayed[name] = float(value)
            else:
                displayed[name] = int(value)
        self.assertEqual(interpreted, displayed)
        return interpreted, ast, generated

    def test_arithmetic(self):
        result, _, _ = self.evaluate_both("int a=10+5*2; int b=(10+5)*2;")
        self.assertEqual(result, {"a": 20, "b": 30})

    def test_integer_division(self):
        result, _, _ = self.evaluate_both("int a=17/5; int b=-17/5; float c=17.0/5;")
        self.assertEqual(result, {"a": 3, "b": -3, "c": 3.4})

    def test_loop_and_if(self):
        code = """int a=5; int sum=0;
        while (a>0) { sum=sum+a; a=a-1; }
        if (sum==15) {sum=sum*2;} else {sum=0;}
        """
        result, ast, _ = self.evaluate_both(code)
        self.assertEqual(result, {"a": 0, "sum": 30})
        self.assertEqual(ast["body"][2]["type"], "WhileStatement")

    def test_dangling_else(self):
        code = """int a=1; int b=0; int r=0;
        if(a>0) if(b>0) r=1; else r=2;
        """
        result, ast, _ = self.evaluate_both(code)
        self.assertEqual(result["r"], 2)
        self.assertIsNone(ast["body"][3]["alternate"])
        self.assertIsNotNone(ast["body"][3]["consequent"]["alternate"])

    def test_shadowing(self):
        code = "int a=10; {int a=20; a=a+5;} a=a+1;"
        result, _, generated = self.evaluate_both(code)
        self.assertEqual(result["a"], 11)
        self.assertIn("cvar_", generated)

    def test_nested_while(self):
        code = """int i=0; int total=0;
        while (i<3) {int j=0; while(j<2){total=total+1;j=j+1;} i=i+1;}
        """
        result, _, _ = self.evaluate_both(code)
        self.assertEqual(result, {"i": 3, "total": 6})

    def test_float_and_comparison(self):
        result, _, _ = self.evaluate_both("float a=7.5/2; int b=a>3.5;")
        self.assertEqual(result, {"a": 3.75, "b": 1})

    def test_python_keyword_identifier(self):
        result, _, generated = self.evaluate_both("int class=3; int result=class*2;")
        self.assertEqual(result["result"], 6)
        self.assertIn("cvar_", generated)

    def test_empty_blocks(self):
        result, _, _ = self.evaluate_both("int a=1; if(a) {} else {} while(a<0) {}")
        self.assertEqual(result, {"a": 1})

    def test_empty_program(self):
        result, _, _ = self.evaluate_both(" // порожня програма\n")
        self.assertEqual(result, {})

    def test_lexical_error(self):
        with self.assertRaises(SyntaxError):
            parse_code("int a=1 @ 2;")

    def test_syntax_error(self):
        with self.assertRaises(SyntaxError):
            parse_code("int a=1 int b=2;")

    def test_uninitialized(self):
        ast = parse_code("int a; int b=a+1;")
        with self.assertRaisesRegex(RuntimeError, "Неініціалізована"):
            Interpreter(verbose=False).execute(ast)
        generated = CodeGenerator().generate(ast)
        with self.assertRaisesRegex(RuntimeError, "Неініціалізована"):
            exec(generated, {})

    def test_division_by_zero(self):
        ast = parse_code("int a=1/0;")
        with self.assertRaisesRegex(RuntimeError, "Ділення на нуль"):
            Interpreter(verbose=False).execute(ast)
        with self.assertRaisesRegex(RuntimeError, "Ділення на нуль"):
            exec(CodeGenerator().generate(ast), {})

    def test_iteration_guard(self):
        ast = parse_code("int a=1; while(a) {}")
        with self.assertRaisesRegex(RuntimeError, "ліміт ітерацій"):
            Interpreter(verbose=False, max_iterations=10).execute(ast)

    def test_tokens(self):
        self.assertEqual([t["type"] for t in tokenize("int a=2;")],
                         ["INT", "ID", "ASSIGN", "NUMBER", "SEMICOLON"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
