from vizlist import VizList


def scoreOfParentheses(S):
    stack, cur = VizList([], title_name='Stack'), 0
    for i in S:
        if i == '(':
            stack.append(cur)
            cur = 0
        else:
            cur += stack.pop() + max(cur, 1)

        stack.print(f'cur = {cur} | {i}')
    return cur


if __name__ == '__main__':
    s = "(()(()))"
    res = scoreOfParentheses(s)
    print(f'Output : {res}')
