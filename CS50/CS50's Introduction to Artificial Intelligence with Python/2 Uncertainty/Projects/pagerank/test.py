l = {
    "a": 0.25,
    "b": 0.15,
    "c": 0.35,
    "d": 0.25
}

from random import *

r = choices(list(l.keys()), list(l.values()), k=10000)

c = dict()
a = 0

for item in r:

    if item in c.keys():
        c[item] += 1
    else:
        c[item] = 1

    a += 1

print(c)

x = dict()

for item in c.keys():
    x[item] = round(c[item]/a, 2)

print(x)