
from datetime import datetime
a = [1, 2, 3, 4, 5, 6, 7, 8, 9]

map_a = list(map(lambda x: x*x, a))
print(map_a)

fil_a = list(filter(lambda x: x < 3, a))
print(fil_a)


map_b = list(map(lambda x: x < 3, a))
print(map_b)

fil_b = list(filter(lambda x: x*x > 6, a))
print(fil_b)

# x = datetime.today()
# print(type(x))
# print(getattr(x, '__name__'))
# print(datetime.strftime(x))
# print((datetime.today()-1).total_seconds())


def func(*a):
    return a[0], a[1], a[2]


print(func(*a))


def func_b(a):
    print(type(a), a)
    return a[0], a[1], a[2]


print(func(a))
