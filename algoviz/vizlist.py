from rich.console import Console
from rich.table import Table
# from rich import print
import time

DEBUG = False


class VizList(list):
    status = {'override_get': True}

    def __init__(self, array, title_name='Array', sleep_time=0, highlight_color='red', show_init=True, parent=None,
                 override_get=True, row_index=None, column_index=None):
        # print('New : ', title_name, array)
        list_1d, list_2d = 1, 2
        self.array_type = list_1d
        self.col_index = list(column_index) if column_index else None
        self.row_index = list(row_index) if row_index else None
        self.debug_print(f'Array Type : {self.array_type}.')
        if len(array) > 0 and isinstance(array[0], list):
            self.array_type = list_2d
            self._array = []
            for i in range(len(array)):
                self._array.append(
                    VizList(array[i], show_init=False, parent=self, title_name=f'{title_name}-' + str(i),
                            override_get=False, column_index=self.col_index, row_index=self.row_index)
                )
        else:
            self._array = array

        self._ = self._array
        self.parent = parent
        self._last_get_index = None
        self.sleep_time = sleep_time
        self.table_name = title_name
        self.highlight_color = highlight_color
        self.parent_list = False
        self.last_index_get = None
        self.override_get = override_get
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
        # global status
        res = self._array.__getitem__(*args, **kwargs)
        if not self.status['override_get']:  # or not self.override_get:
            return res
        # print('\nList get ', self.table_name, self._array)
        # If result in not a list
        if not isinstance(res, list):
            self.debug_print(f'Array is not list')
            index = args[0]
            # If get is not for a 2D List
            # print('D : ', self.parent_list)
            if not self.parent_list:
                self.show_list(highlight=[index, index], table_name=f'{self.table_name} [{index}]')
            else:
                # print('I : ', self.last_index_get, index)
                self.show_list(highlight=[index, self.last_index_get], table_name=self.parent.table_name)

            self.parent_list = None
            return res
        elif isinstance(res, list):
            self.debug_print('Array is list')
            # args is a splice
            if not isinstance(args[0], int):
                self.debug_print(f'Argument is not type int : {args}')
                # print('Returning list and is splice')
                start = args[0].start
                stop = args[0].stop
                # print(res, args, left, stop)
                self.show_list(table_name=f'{self.table_name} [{start}:{stop}]', show_index=True,
                               highlight=[start, stop], is_splice=True)
                #self.debug_print(f'Creating new array')
                return res #VizList(res, show_init=False, column_index=self.col_index)
            else:
                # TODO : Broken 2D Handling
                # print('list')
                # print(args)
                index = args[0]
                res.parent_list = self
                res.last_index_get = index
                # print('Args : ', args)
                # self._array[index] = res

            # print(res)
            return res

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
        self._array.append(*args, **kwargs)
        self.show_list(table_name=self.table_name)

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
        self.show_list(table_name=self.table_name)

    def remove(self, *args, **kwargs):
        return self._array.remove(*args, **kwargs)

    def reverse(self, *args, **kwargs):
        return self._array.reverse(*args, **kwargs)

    def sort(self, *args, **kwargs):
        return self._array.sort(*args, **kwargs)

    def render_list(self, array, highlight=[-1, -1], highlight_color='red', is_splice=False, one_dimension=True):
        # array.__getitem__ = super().__getitem__
        if not is_splice:
            if highlight:
                return tuple([f'[{highlight_color}]' + str(val) + f'[/{highlight_color}]' if highlight[0] <= index <=
                                                                                             highlight[1] else str(val)
                              for
                              index, val in
                              enumerate(array)])
            else:
                return tuple([str(val)
                              for
                              index, val in
                              enumerate(array)])
        else:
            if highlight:
                return tuple([f'[{highlight_color}]' + str(val) + f'[/{highlight_color}]' if highlight[0] <= index <
                                                                                             highlight[1] else str(val)
                              for
                              index, val in
                              enumerate(array)])

    def show_list(self, table_name='List', show_index=True, highlight=None, is_splice=False, one_dimension=True):
        n = len(self._array)
        list_1d, list_2d = 1, 2
        list_type = None
        display = self._array if not self.parent_list else self.parent_list
        if n and isinstance(display, list) and isinstance(display[0], list):
            list_type = list_2d
        elif n and isinstance(display, list) and not isinstance(display[0], list):
            list_type = list_1d

        table = Table(title=table_name, show_header=show_index)
        if list_type == list_1d:
            self.debug_print(f'Array Type is {list_type}. Show Index : {show_index}')
            if show_index:
                for i in range(n):
                    table.add_column(str(i))

            if isinstance(highlight, list):
                table.add_row(*self.render_list(self._array, highlight=highlight, is_splice=is_splice,
                                                highlight_color=self.highlight_color, one_dimension=one_dimension))
            else:
                table.add_row(*self.render_list(self._array, highlight_color=self.highlight_color))

        elif list_type == list_2d:
            bkp_getter = self.__getitem__
            # global status
            self.status['override_get'] = False
            row, col = len(display), len(display[0])
            if show_index:
                if self.row_index:
                    table.add_column('_')
                for index, val in enumerate(self.col_index or range(col)):
                    table.add_column(f'{val} [{index}]')
            for i in range(row):
                if highlight:
                    if self.row_index:
                        table.add_row(f'{self.row_index[i]} [{i}]',
                                      *self.render_list(display[i], highlight_color=self.highlight_color,
                                                        highlight=[highlight[0], highlight[0]] if i == highlight[
                                                            1] else [
                                                            -1, -1]))
                    else:
                        table.add_row(*self.render_list(display[i], highlight_color=self.highlight_color,
                                                        highlight=[highlight[0], highlight[0]] if i == highlight[
                                                            1] else [
                                                            -1, -1]))
                else:
                    if self.row_index:
                        table.add_row(f'{self.row_index[i]} [{i}]',
                                      *self.render_list(display[i], highlight_color=self.highlight_color))
                    else:
                        table.add_row(*self.render_list(display[i], highlight_color=self.highlight_color))

            self.status['override_get'] = True

        console = Console()
        console.print(table)
        time.sleep(self.sleep_time)

    def print(self, string, data='', end=''):
        # global status
        # print('A')
        self.status['override_get'] = False
        if len(data) == 0:
            print(string, end)
        else:
            data = data.replace('#', 'self._')
            # print(data)
            print(string, eval(data), end)
        self.status['override_get'] = True
        # print('E')

    def debug_print(self, *args):
        if DEBUG: print(*args)
