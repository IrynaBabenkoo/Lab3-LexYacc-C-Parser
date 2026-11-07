// Демонстраційна програма для лексичного та синтаксичного аналізу.
int a = 5;
int sum = 0;

while (a > 0)
{
    sum = sum + a;
    a = a - 1;
}

if (sum == 15)
{
    sum = sum * 2;
}
else
{
    sum = 0;
}

float average = sum / 2.0;
