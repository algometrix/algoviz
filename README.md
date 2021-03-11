# AlgoViz

Creates table for python list and highlights indexes on index access.

## Installation
```pip install algoviz```


## Examples
### Example 1 : Coin Change Problem
```
from algoviz.vizlist import VizList


def coinChange(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    dp = VizList(dp, title_name='Coin Change')
    for coin in coins:
        for val in range(amount + 1):
            if coin <= val:
                dp.print(f'Coin = {coin} | dp[{val}] += dp[{val} - {coin}] =', f'#[{val}] + #[{val} - {coin}]')
                '''
                dp.print :
                Param 1 : Normal Print
                Param 2: eval is run on this string. Replace array name with # to access original array.
                '''
                dp[val] += dp[val - coin]

    return dp[-1]


if __name__ == '__main__':
    coins = [1, 2]
    amount = 3
    res = coinChange(coins, amount)
    print(f'Output : {res}')

```
Output:
```
Coin Change Init 
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 1 │ 0 │ 0 │ 0 │
└───┴───┴───┴───┘
Coin = 1 | dp[1] += dp[1 - 1] = 1 
   Coin Change   
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 1 │ 1 │ 0 │ 0 │
└───┴───┴───┴───┘
Coin = 1 | dp[2] += dp[2 - 1] = 1 
   Coin Change   
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 1 │ 1 │ 1 │ 0 │
└───┴───┴───┴───┘
Coin = 1 | dp[3] += dp[3 - 1] = 1 
   Coin Change   
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 1 │ 1 │ 1 │ 1 │
└───┴───┴───┴───┘
Coin = 2 | dp[2] += dp[2 - 2] = 2 
   Coin Change   
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 1 │ 1 │ 2 │ 1 │
└───┴───┴───┴───┘
Coin = 2 | dp[3] += dp[3 - 2] = 2 
   Coin Change   
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 1 │ 1 │ 2 │ 2 │
└───┴───┴───┴───┘
Output : 2
```


### Example 2 : Count number of palindromes
```
def countSubstrings(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    dp = VizList(dp, column_index=list(s), row_index=list(s), title_name='DP Table', sleep_time=1, set_highlight_color='blue')
    res = 0
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            dp[i][j] = s[i] == s[j] and ((j - i + 1) < 3 or dp[i + 1][j - 1])
            res += dp[i][j]
            dp.clear_highighlight_data() # Clears highlight tracking data. It's done automatically on list assignment operators
        # The second parameter is evaluated using eval and printed.
        # Note : to access the internal array, the array name should be replace by a #
    return res


if __name__ == '__main__':
    s = 'aab'
    res = countSubstrings(s)
    print('Output : {}'.format(res))
```

The above code will generate
```
          DP Table Init          
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ 0     │ 0     │
│ b [2] │ 0     │ 0     │ 0     │
└───────┴───────┴───────┴───────┘
            DP Table             
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ 0     │ 0     │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table             
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ True  │ 0     │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table             
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ 0     │ 0     │ 0     │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table             
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ True  │ 0     │ 0     │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table             
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ True  │ True  │ 0     │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
            DP Table             
┏━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃       ┃ a [0] ┃ a [1] ┃ b [2] ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ a [0] │ True  │ True  │ False │
│ a [1] │ 0     │ True  │ False │
│ b [2] │ 0     │ 0     │ True  │
└───────┴───────┴───────┴───────┘
Output : 4
```
