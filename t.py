from vizlist import VizList


def minCut(s):
    cut = VizList([x for x in range(-1, len(s))])
    s = VizList(list(s))
    r = []
    for i in range(0, len(s)):
        for j in range(i, len(s)):
            if s[i:j] == s[j:i:-1]:
                r.append(s[i: j + 1])
                cut[j + 1] = min(cut[j + 1], cut[i] + 1)
    # print(r)
    return cut[-1]


if __name__ == '__main__':
    s = "aab"
    res = minCut(s)
    print('Output : {}'.format(res))
