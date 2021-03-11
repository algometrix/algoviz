from rich.console import Console
from rich.table import Table
import time
import copy

from enum import Enum

DEBUG = False


class ListType(Enum):
    ONE_D_LIST = 1
    TWO_D_LIST = 2


class VizList(list):
    status = {'override_get': True}

    def __init__(self, array, title_name='Array', sleep_time=0, get_highlight_color='red', set_highlight_color='blue',
                 show_init=True, parent=None,
                 override_get=True, row_index=None, column_index=None, show_header=True):
        if isinstance(array[0], list):
            self.array_type = ListType.TWO_D_LIST
        else:
            self.array_type = ListType.ONE_D_LIST

        self.debug_print(f'Array Type : {self.array_type}.')
        self.col_index = list(column_index) if column_index else None
        self.row_index = list(row_index) if row_index else None
        self.show_header = show_header
        self.parent = parent
        self._last_get_index = None
        self.sleep_time = sleep_time
        self.table_name = title_name
        self.get_highlight_color = get_highlight_color
        self.set_highlight_color = set_highlight_color
        self.get_highlight_tracker = []
        self.set_highlight_tracker = []
        self.parent_list = False
        self.last_index_get = None
        self.override_get = override_get
        self.table = None
        if self.array_type == ListType.TWO_D_LIST:
            for i in range(len(array)):
                array[i] = VizList(array[i], sleep_time=sleep_time, parent=self, show_init=False,
                                   row_index=[self.row_index[i]] if self.row_index else None)

        self._array = array
        self._ = self._array
        if show_init:
            self.show_list(table_name=self.table_name + ' Init')

    def render_list(self, array=None):
        array = array or self._array
        self.debug_print(f'Array : {array}')
        self.debug_print(f'Highlight Data : {self.get_highlight_tracker} | {self.set_highlight_tracker}')
        if self.array_type == ListType.ONE_D_LIST:
            rendered_list = [f'{self.row_index[0]}'] if self.row_index else []
            for index, val in enumerate(self._array):
                for start, end in self.set_highlight_tracker:
                    if start <= index < end:
                        rendered_item = f'[{self.set_highlight_color}]{val}[/{self.set_highlight_color}]'
                        break
                else:
                    for start, end in self.get_highlight_tracker:
                        if start <= index < end:
                            rendered_item = f'[{self.get_highlight_color}]{val}[/{self.get_highlight_color}]'
                            break
                    else:
                        rendered_item = str(val)

                rendered_list.append(rendered_item)
        self.debug_print(f'Render : {rendered_list}')
        self.clear_highighlight_data()
        return tuple(rendered_list)

    def show_list(self, table_name=None, array=None, show_header=True):
        self.status['override_get'] = False
        table_name = table_name or self.table_name
        self.table = Table(title=table_name, show_header=show_header)
        self.debug_print(f'Printing {self.array_type}')
        # Add blank col to fit in row index values
        if self.row_index: self.table.add_column(' ')
        if self.array_type == ListType.ONE_D_LIST:
            for i in self.col_index or range(len(self._array)):
                self.table.add_column(f'{i}')
            self.table.add_row(*self.render_list(self._array))
        elif self.array_type == ListType.TWO_D_LIST:
            # Add all the column index values if there are provides. Otherwise just use range
            for i in self.col_index or range(len(self._array[0])):
                self.table.add_column(f'{i}')

            # Go through each sub array object and generate row for each sub array
            for sub_array in self._array:
                self.table.add_row(*sub_array.render_list())

        console = Console()
        console.print(self.table)
        time.sleep(self.sleep_time)
        self.status['override_get'] = True

    def print(self, string, data='', end=''):
        self.status['override_get'] = False
        if len(data) == 0:
            print(string, end)
        else:
            data = data.replace('#', 'self._')
            print(string, eval(data), end)
        self.status['override_get'] = True

    @staticmethod
    def debug_print(*args):
        if DEBUG: print(*args)

    def clear_highighlight_data(self):
        self.set_highlight_tracker = []
        self.get_highlight_tracker = []
        for i in self._array:
            if isinstance(i, VizList):
                i.clear_highighlight_data()

    def __getitem__(self, *args, **kwargs):
        res = self._array.__getitem__(*args, **kwargs)
        self.debug_print(f'Get Array called : {args} | {kwargs}')
        # If VizList is disabled
        if not self.status['override_get']:
            return res
        else:
            if self.array_type == ListType.ONE_D_LIST:
                if isinstance(args[0], slice):
                    self.get_highlight_tracker.append([args[0].start, args[0].stop])
                else:
                    self.get_highlight_tracker.append([args[0], args[0] + 1])
        return res

    def __setitem__(self, *args, **kwargs):
        self._array.__setitem__(*args, **kwargs)
        if self.status['override_get']:
            self.debug_print(f'Set Item Called : {args}')
            self.debug_print(f'Highlights : f{self.get_highlight_tracker}')
            if isinstance(args[0], slice):
                self.set_highlight_tracker.append([args[0].start, args[0].stop])
            else:
                self.set_highlight_tracker.append([args[0], args[0] + 1])

            curr = self
            # Access the parent of the updated array
            while curr.parent is not None:
                curr = curr.parent

            curr.show_list()

    def __setslice__(self, *args, **kwargs):
        return self._array.__setslice__(*args, **kwargs)

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

    def __getslice__(self, *args, **kwargs):
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

    def __sizeof__(self, *args, **kwargs):
        return self._array.__sizeof__(*args, **kwargs)

    def __str__(self, *args, **kwargs):
        return self._array.__str__(*args, **kwargs)

    def __subclasshook__(self, *args, **kwargs):
        return self._array.__subclasshook__(*args, **kwargs)

    def append(self, *args, **kwargs):
        self._array.append(*args, **kwargs)

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
