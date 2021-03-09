import heapq
from vizlist import VizList


def searchRange(nums, target):
    nums = VizList(nums, title_name='Sorted Array')
    l, r = 0, len(nums) - 1
    print('Left\n')
    while l < r:
        mid = (l + r) // 2
        nums.show_additional_data(f'\n\nmid = ({l} + {r}) // 2 = ', f'({l} + {r}) // 2', end='\n')
        nums[l]
        nums[r]
        if nums[mid] < target:
            l = mid + 1
        else:
            r = mid

    left = l
    print('Right\n')
    l, r = 0, len(nums) - 1
    while l < r:
        mid = (l + r) // 2
        nums.show_additional_data(f'\n\nmid = ({l} + {r}) // 2 = ', f'({l} + {r}) // 2', end='\n')
        nums[l]
        nums[r]
        if nums[mid] <= target:
            l = mid + 1
        else:
            r = mid

    right = l
    if left == right:
        return [-1, -1]
    return left, right - 1


if __name__ == '__main__':
    A = [1,2,3,4,5,6,7,7,7,7,7,7,8,9,10]
    target = 7
    print(f'Target : {target}')
    print(searchRange(A, target))
