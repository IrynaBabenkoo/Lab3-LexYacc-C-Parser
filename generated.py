# Автоматично згенерований Python-код із навчальної підмножини C.
# Вхідна граматика реалізована засобами Lex/YACC (PLY).

def __lab3_read(value, name):
    # Перевірка читання неініціалізованої змінної.
    if value is None:
        raise RuntimeError(f'Неініціалізована змінна: {name}')
    return value

__lab3_iterations = 0

a = int(5)
sum = int(0)
while int((__lab3_read(a, 'a') > 0)):
    __lab3_iterations += 1
    if __lab3_iterations > 10000:
        raise RuntimeError('Перевищено ліміт ітерацій')
    sum = int((__lab3_read(sum, 'sum') + __lab3_read(a, 'a')))
    a = int((__lab3_read(a, 'a') - 1))
if int((__lab3_read(sum, 'sum') == 15)):
    sum = int((__lab3_read(sum, 'sum') * 2))
else:
    sum = int(0)

# Підсумкові значення глобальних змінних.
print('a', '=', a)
print('sum', '=', sum)
