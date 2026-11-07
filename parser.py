"""Синтаксичний LALR-аналізатор і побудова AST для підмножини C."""

import json
import ply.yacc as yacc
from lexer import lexer, tokens

start = "program"

# Оператори впорядковані від нижчого пріоритету до вищого.
# IFX розв'язує неоднозначність dangling else на користь найближчого if.
precedence = (
    ("nonassoc", "IFX"),
    ("nonassoc", "ELSE"),
    ("nonassoc", "EQ", "NE", "LT", "LE", "GT", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "UMINUS"),
)


def p_program(p):
    "program : statements_opt"
    p[0] = {"type": "Program", "body": p[1]}


def p_statements_opt(p):
    """statements_opt : statements
                      | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_statements_multiple(p):
    "statements : statements statement"
    p[0] = p[1] + [p[2]]


def p_statements_single(p):
    "statements : statement"
    p[0] = [p[1]]


def p_empty(p):
    "empty :"
    p[0] = None


def p_datatype(p):
    """datatype : INT
                | FLOAT"""
    p[0] = p[1]


def p_declaration(p):
    "statement : datatype ID ASSIGN expression SEMICOLON"
    p[0] = {"type": "VariableDeclaration", "dataType": p[1],
            "name": p[2], "value": p[4]}


def p_declaration_empty(p):
    "statement : datatype ID SEMICOLON"
    p[0] = {"type": "VariableDeclaration", "dataType": p[1],
            "name": p[2], "value": None}


def p_assignment(p):
    "statement : ID ASSIGN expression SEMICOLON"
    p[0] = {"type": "Assignment", "name": p[1], "value": p[3]}


def p_statement_block(p):
    "statement : LBRACE statements_opt RBRACE"
    p[0] = {"type": "BlockStatement", "body": p[2]}


def p_statement_if(p):
    "statement : IF LPAREN expression RPAREN statement %prec IFX"
    p[0] = {"type": "IfStatement", "condition": p[3],
            "consequent": p[5], "alternate": None}


def p_statement_if_else(p):
    "statement : IF LPAREN expression RPAREN statement ELSE statement"
    p[0] = {"type": "IfStatement", "condition": p[3],
            "consequent": p[5], "alternate": p[7]}


def p_statement_while(p):
    "statement : WHILE LPAREN expression RPAREN statement"
    p[0] = {"type": "WhileStatement", "condition": p[3], "body": p[5]}


def p_expression_binary(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression"""
    p[0] = {"type": "BinaryExpression", "operator": p[2],
            "left": p[1], "right": p[3]}


def p_expression_unary(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = {"type": "UnaryExpression", "operator": "-", "operand": p[2]}


def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = {"type": "Number", "value": p[1]}


def p_expression_identifier(p):
    "expression : ID"
    p[0] = {"type": "Identifier", "name": p[1]}


def p_error(p):
    if p is None:
        raise SyntaxError("Синтаксична помилка: неочікуваний кінець коду")
    raise SyntaxError(
        f"Синтаксична помилка: токен {p.value!r} ({p.type}), рядок {p.lineno}"
    )


# Вимикаємо запис службових таблиць у корінь проєкту.
parser = yacc.yacc(debug=False, write_tables=False)


def parse_code(code):
    lexer.lineno = 1
    return parser.parse(code, lexer=lexer)


if __name__ == "__main__":
    example = """int a = 3;
while (a > 0) { a = a - 1; }
if (a == 0) { float result = 1.5; }
"""
    print(json.dumps(parse_code(example), indent=2, ensure_ascii=False))
