### Задание №4 ###

s = input()
t = input()

if len(s) != len(t):
    print(False)
    exit()

if sorted(s) != sorted(t):
    print(False)
else:
    print(True)
