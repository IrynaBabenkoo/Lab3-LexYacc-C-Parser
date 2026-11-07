import ply.lex as lex

reserved = {
    "int": "INT",
    "float": "FLOAT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
}

tokens = [
    "ID", "NUMBER", "PLUS", "MINUS", "TIMES", "DIVIDE", "ASSIGN",
    "EQ", "NE", "LT", "LE", "GT", "GE", "LPAREN", "RPAREN",
    "LBRACE", "RBRACE", "SEMICOLON",
] + list(reserved.values())

# Регулярні вирази для операторів і роздільників
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_EQ = r"=="
t_NE = r"!="
t_LE = r"<="
t_GE = r">="
t_LT = r"<"
t_GT = r">"
t_ASSIGN = r"="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_SEMICOLON = r";"
t_ignore = " \t\r"


def t_COMMENT(t):
    r"//[^\n]*|/\*[\s\S]*?\*/"
    # Коментарі ігноруються, проте їхні переведення рядків враховуються.
    t.lexer.lineno += t.value.count("\n")


def t_NUMBER(t):
    r"(?:\d+\.\d+|\d+)"
    t.value = float(t.value) if "." in t.value else int(t.value)
    return t


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(t.value, "ID")
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    # На відміну від пропускання символу, помилка зупиняє розбір.
    raise SyntaxError(
        f"Лексична помилка: символ {t.value[0]!r}, рядок {t.lineno}"
    )


lexer = lex.lex()


def tokenize(code):
    """Повернути токени; корисно для демонстрації лексичного аналізу."""
    lexer.lineno = 1
    lexer.input(code)
    return [
        {"type": token.type, "value": token.value, "line": token.lineno}
        for token in iter(lexer.token, None)
    ]


if __name__ == "__main__":
    example = "int a = 10;\nfloat b = a * 2.5;\n"
    print("РЕЗУЛЬТАТ ЛЕКСИЧНОГО АНАЛІЗУ")
    for token in tokenize(example):
        print(f"{token['type']:<12} {str(token['value']):<12} рядок {token['line']}")
