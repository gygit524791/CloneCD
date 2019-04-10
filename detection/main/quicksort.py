def quick_sort(list, dict, left, right):
    if left < right:
        mid = partition(list, dict, left, right)
        quick_sort(list, dict, left,  mid-1)
        quick_sort(list, dict, mid+1, right)

def partition(list, dict, left, right):
    tmpkey = list[left]
    tmpvalue = dict[list[left]]
    while left < right:
        while left < right and dict[list[right]] >= tmpvalue:
            right -= 1
        list[left] = list[right]
        while left < right and dict[list[left]] <= tmpvalue:
            left += 1
        list[right] = list[left]
    list[left] = tmpkey
    return left