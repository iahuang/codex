import math


# the first 10 fibonacci numbers
fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

# write fibs to fibs.txt as a comma-separated list
with open('fibs.txt', 'w') as f:
    f.write(','.join(str(fib) for fib in fibs))

