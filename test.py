def return_yield():
    yield 1
    yield 2
    yield 3

a = return_yield()
print(next(a))
print(next(a))
print(next(a))