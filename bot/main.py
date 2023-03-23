

n, s = [int(x) for x in input().split()]
numbers = []
for x in range(n):
    data = input()
    min_x, max_x = data.split()[0], data.split()[1]
    print(min_x, max_x)
    unit = [int(min_x), int(min_x), int(max_x)]
    numbers.append(unit)
