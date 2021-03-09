from vizlist import VizList


def minFlipsMonoIncr(S):
    P = [0]
    for x in S:
        P.append(P[-1] + int(x))

    P = VizList(P, title_name='Flips')
    res = float('inf')
    for j in range(1, len(P)):
        P.print(f'res = min(P[{j}] + {len(S)} - {j} - (P[-1] - P[{j}]), {res})')
        res = min(P[j] + len(S) - j - (P[-1] - P[j]), res)

    return res


if __name__ == '__main__':
    S = "010000110"
    res = minFlipsMonoIncr(S)
    print('Output : {}'.format(res))
