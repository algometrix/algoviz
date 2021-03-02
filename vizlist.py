from rich.console import Console
from rich.table import Table
import time


class VizList(list):
    def __init__(self, array, title_name='Array', sleep_time=0, highlight_color='red', show_init=True):
        self._array = array
        self._ = array
        self._last_get_index = None
        self.sleep_time = sleep_time
        self.table_name = title_name
        self.highlight_color = highlight_color
        self.recursive_list_fetch = False
        self.last_index_get = None
        if show_init: self.show_list(table_name=self.table_name + ' Init')

    def __add__(self, args):
        # Calling __add__ didn't work. Using extend workaround for now.
        self._array.extend(args)
        return self._array

    def __contains__(self, *args, **kwargs):
        return self._array.__contains__(*args, **kwargs)

    def __delattr__(self, *args, **kwargs):
        return self._array.__delattr__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self._array.__delitem__(*args, **kwargs)

    def __delslice__(self, *args, **kwargs):
        return self._array.__delslice__(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self._array.__eq__(*args, **kwargs)

    def __format__(self, *args, **kwargs):
        return self._array.__format__(*args, **kwargs)

    def __ge__(self, *args, **kwargs):
        self._array = self._array.__ge__(*args, **kwargs)
        return self

    def __getitem__(self, *args, **kwargs):
        # print('Get Item : {}'.format(args))
        res = self._array.__getitem__(*args, **kwargs)
        print(args)
        # If result in not a list
        if not isinstance(res, list):
            index = args[0]
            # If get is not for a 2D List
            print('D : ', self.recursive_list_fetch)
            if not self.recursive_list_fetch:
                self.show_list(highlight=[index, index], table_name=self.table_name)
            else:
                print('I : ', index, self.last_index_get)
                #self.show_list(highlight=[index, self.last_index_get], table_name=self.table_name)

            self.recursive_list_fetch = False
            return res
        elif isinstance(res, list):
            # args is a splice
            if not isinstance(args[0], int):
                start = args[0].start
                stop = args[0].stop
                # print(res, args, left, stop)
                self.show_list(table_name=self.table_name, show_index=False, highlight=[start, stop], is_splice=True)
                return VizList(res, show_init=False)
            else:
                print('list')
                index = args[0]
                self.recursive_list_fetch = True
                self.last_index_get = index
                pass #print(args)
                #self._array[index] = res

            return self._array




    def __getslice__(self, *args, **kwargs):
        # print('Get Slice ', args)
        self._array = self._array.__getslice__(*args, **kwargs)
        return self

    def __gt__(self, *args, **kwargs):
        # print(args)
        return self._array.__gt__(*args, **kwargs)

    def __hash__(self, *args, **kwargs):
        return self._array.__hash__(*args, **kwargs)

    def __iadd__(self, *args, **kwargs):
        return self._array.__iadd__(*args, **kwargs)

    def __imul__(self, *args, **kwargs):
        return self._array.__imul__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._array.__iter__(*args, **kwargs)

    def __le__(self, *args, **kwargs):
        return self._array.__le__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self._array.__len__(*args, **kwargs)

    def __lt__(self, *args, **kwargs):
        return self._array.__lt__(*args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return self._array.__mul__(*args, **kwargs)

    def __ne__(self, *args, **kwargs):
        return self._array.__ne__(*args, **kwargs)

    def __reduce__(self, *args, **kwargs):
        return self._array.__reduce__(*args, **kwargs)

    def __reduce_ex__(self, *args, **kwargs):
        return self._array.__reduce_ex__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self._array.__repr__(*args, **kwargs)

    def __reversed__(self, *args, **kwargs):
        return self._array.__reversed__(*args, **kwargs)

    def __rmul__(self, *args, **kwargs):
        return self._array.__rmul__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self._array.__setitem__(*args, **kwargs)

    def __setslice__(self, *args, **kwargs):
        return self._array.__setslice__(*args, **kwargs)

    def __sizeof__(self, *args, **kwargs):
        return self._array.__sizeof__(*args, **kwargs)

    def __str__(self, *args, **kwargs):
        return self._array.__str__(*args, **kwargs)

    def __subclasshook__(self, *args, **kwargs):
        return self._array.__subclasshook__(*args, **kwargs)

    def append(self, *args, **kwargs):
        return self._array.append(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self._array.count(*args, **kwargs)

    def extend(self, *args, **kwargs):
        return self._array.extend(*args, **kwargs)

    def index(self, *args, **kwargs):
        return self._array.index(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self._array.insert(*args, **kwargs)

    def pop(self, *args, **kwargs):
        return self._array.pop(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self._array.remove(*args, **kwargs)

    def reverse(self, *args, **kwargs):
        return self._array.reverse(*args, **kwargs)

    def sort(self, *args, **kwargs):
        return self._array.sort(*args, **kwargs)

    def render_list(self, array, highlight=[-1, -1], highlight_color='red', is_splice=False):
        if not is_splice:
            return tuple([f'[{highlight_color}]' + str(val) + f'[/{highlight_color}]' if highlight[0] <= index <=
                                                                                         highlight[1] else str(val) for
                          index, val in
                          enumerate(array)])
        else:
            return tuple([f'[{highlight_color}]' + str(val) + f'[/{highlight_color}]' if highlight[0] <= index <
                                                                                         highlight[1] else str(val) for
                          index, val in
                          enumerate(array)])

    def show_list(self, table_name='List', show_index=True, highlight=None, is_splice=False):
        n = len(self._array)
        list_1d, list_2d = 1, 2
        list_type = None
        if n and isinstance(self._array, list) and isinstance(self._array[0], list):
            list_type = list_2d
        elif n and isinstance(self._array, list) and not isinstance(self._array[0], list):
            list_type = list_1d

        table = Table(title=table_name, show_header=show_index)

        if list_type == list_1d:
            if show_index:
                for i in range(n):
                    table.add_column(str(i))

            if isinstance(highlight, list):
                table.add_row(*self.render_list(self._array, highlight=highlight, is_splice=is_splice,
                                                highlight_color=self.highlight_color))
            else:
                table.add_row(*self.render_list(self._array, highlight_color=self.highlight_color))

        elif list_type == list_2d:
            row, col = len(self._array), len(self._array[0])
            if show_index:
                for i in range(col):
                    table.add_column(str(i))
            for i in range(row):
                table.add_row(*self.render_list(self._array[i], highlight_color=self.highlight_color))

        console = Console()
        console.print(table)
        time.sleep(self.sleep_time)

    def show_additional_data(self, string, data):
        self.backup_getter = self.__getitem__
        self.__getitem__ = super().__getitem__
        print(string, eval(data))
        self.__getitem__ = self.backup_getter
