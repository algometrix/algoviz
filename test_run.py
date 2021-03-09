from vizlist import VizList


def test_list_fetch():
    _list_1 = VizList([[1, 2], [3, 4]])
    print(_list_1[0]
          )
    # l = _list_1[:2]
    # print(l)
    # print('Getting data')
    # print(l[1])


if __name__ == "__main__":
    test_list_fetch()
