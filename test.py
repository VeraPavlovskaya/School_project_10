def epic_hero(arr, knight):
    if knight <= arr[0]:
        return [knight] + arr
    elif len(arr) == 1:
        return arr + [knight]
    else:
        return [arr[0]] + epic_hero(arr[1:], knight)

print(epic_hero([1, 2, 3, 5, 6, 7], 0))
print(epic_hero([1, 2, 3, 5, 6, 7], 4))
print(epic_hero([1, 2, 3, 5, 6, 7], 8))