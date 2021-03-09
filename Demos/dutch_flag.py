from vizlist import VizList


def flag(A, pivot):
    A = VizList(A)
    n = len(A)
    smaller, larger, equal = 0, n - 1, 0
    while equal < larger:
        A.print(f'{smaller} | {equal} | {larger}')
        if A[equal] == pivot:
            equal += 1
        elif A[equal] < pivot:
            A[equal], A[smaller] = A[smaller], A[equal]
            smaller, equal = smaller + 1, equal + 1
        else:
            A[equal], A[larger] = A[larger], A[equal]
            larger -= 1

    return A


if __name__ == '__main__':
    A = [3, 4, 2, 1, 6, 7, 8, 4, 3, 2, 4, 5]
    pivot = 3
    res = flag(A, pivot)
    print(f'Output : {res}')
