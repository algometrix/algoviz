from vizlist import VizList

def countSubstrings(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    dp = VizList(dp, column_index=list(s),row_index=list(s), title_name='DP Table')
    res = 0
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            dp[i][j] = s[i] == s[j] and ((j - i + 1) < 3 or dp[i + 1][j - 1])
            res += dp[i][j]
    return res


if __name__ == '__main__':
    s = 'aabaa'
    res = countSubstrings(s)
    print('Output : {}'.format(res))
