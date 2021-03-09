from vizlist import VizList


def swaps(A):
    A = VizList(A, title_name='Swapping Array')
    for i in range(len(A)):
        A[i:i + 2] = sorted(A[i:i + 2], reverse=i % 2)
    return A


if __name__ == '__main__':
    A = [1, 9, 3, 4, 3, 2, 3, 6, 2]
    res = swaps(A)
    print(f'Output : {res}')
