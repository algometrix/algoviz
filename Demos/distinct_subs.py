from vizlist import VizList


def numDistinct(s: str, t: str) -> int:
    m, n = len(s) + 1, len(t) + 1
    dp = [[0] * n for _ in range(m)]
    dp = VizList(dp, title_name='DP Table', row_index=' ' + s, column_index=' ' + t)
    for j in range(m):
        dp[j][0] = 1

    for i in range(1, m):
        for j in range(1, n):
            dp.print(f'dp[{i}][{j}] = dp[{i - 1}][{j}] + dp[{i - 1}][{j - 1}] * ({s[i - 1]} == {t[j - 1]})')
            dp[i][j] = dp[i - 1][j] + dp[i - 1][j - 1] * (s[i - 1] == t[j - 1])

    return dp[-1][-1]


if __name__ == '__main__':
    s = "rabbit"
    t = "rabbit"
    res = numDistinct(s, t)
    print(f'Output : {res}')
