### Задание №3 ###

prices = list(map(int, input("Введите цены через пробел: ").split()))
min_price = float('inf')
max_value = 0

for price in prices:
    if price < min_price:
        min_price = price
    elif price - min_price > max_value:
        max_value = price - min_price

print(f"Максимальная прибыль: {max_value}")
