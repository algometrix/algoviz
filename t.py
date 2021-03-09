from vizlist import VizList


def minIncrementForUnique(A):
    root = {}

    def find(x):
        root[x] = find(root[x] + 1) if x in root else x
        return root[x]

    res = sum(find(a) - a for a in A)
    print(root)
    return res


if __name__ == '__main__':
    A = [3, 2, 1, 2, 1, 7]
    print(A)
    res = minIncrementForUnique(A)
    print(f'\nOutput : {res}')
