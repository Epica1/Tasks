### Задание №1 ###

def is_true(s):
    stack = []

    pairs = {')': '(', ']': '[', '}': '{'}

    for char in s:
        if char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
        else:
            stack.append(char)

    return not stack

s = input("Введите строку со скобками: ")

print(is_true(s))

































