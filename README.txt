# AlgoViz

Creates tables for python list and highlights indexes on index access.

## Installation
```pip install algoviz```


## Example

```
from algoviz.vizlist import VizList


def countSubstrings(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    dp = VizList(dp, column_index=list(s), row_index=list(s), title_name='DP Table')
    res = 0
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            dp[i][j] = s[i] == s[j] and ((j - i + 1) < 3 or dp[i + 1][j - 1])
            res += dp[i][j]
        dp.print(f'i = {i} | This works like a normal print.',
                 f'#[{i}]')
        # The second parameter is evaluated using eval and printed.
        # Note to access the internal array, the array name should be replace by a #
    return res


if __name__ == '__main__':
    s = 'aab'
    res = countSubstrings(s)
```

The above code will generate
```
          DP Table Init
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ _     ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ 0     │ 0     │
│ b [2] │ 0     │ 0     │ 0     │
└───────┴───────┴───────┴───────┘
            DP Table
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ _     ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ 0     │ 0     │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
i = 2 | This works like a normal print. [0, 0, True]
            DP Table
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ _     ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ True  │ 0     │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ _     ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
i = 1 | This works like a normal print. [0, True, False]
            DP Table
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ _     ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ True  │ 0     │ 0     │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ _     ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ True  │ True  │ 0     │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ _     ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ True  │ True  │ False │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
i = 0 | This works like a normal print. [True, True, False]
```
