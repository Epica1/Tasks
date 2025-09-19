### Задание №2 ###

def massive(nums1, m, nums2, n):

    i = m - 1
    j = n - 1
    k = m + n - 1

    while i >= 0 and j >= 0:
        if nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1
        else:
            nums1[k] = nums2[j]
            j -= 1
        k -= 1

    while j >= 0:
        nums1[k] = nums2[j]
        j -= 1
        k -= 1

print("Введите элементы первого массива nums1 через пробел:")
nums1 = list(map(int, input().split()))

print("Введите количество элементов m в первом массиве:")
m = int(input())

print("Введите элементы второго массива nums2 через пробел:")
nums2 = list(map(int, input().split()))

print("Введите количество элементов n во втором массиве:")
n = int(input())

nums1 = nums1[:m] + [0] * n

massive(nums1, m, nums2, n)
print("Объединенный отсортированный массив:")
print(nums1)
