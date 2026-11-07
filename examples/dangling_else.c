// else належить найближчому if, у якого ще немає else.
int a = 1;
int b = 0;
int result = 0;
if (a > 0)
    if (b > 0)
        result = 1;
    else
        result = 2;
