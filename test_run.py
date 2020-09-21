
class VizList(list):
    def __init__(self, array):
        self._array = array
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
        return self._array.__ge__(*args, **kwargs)
    def __getitem__(self, *args, **kwargs):
        return self._array.__getitem__(*args, **kwargs)
    def __getslice__(self, *args, **kwargs):
        return self._array.__getslice__(*args, **kwargs)
    def __gt__(self, *args, **kwargs):
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
    

def test_list_fetch():
    _list_1 = VizList([1, 2, 3])
    _list_2 = VizList([4, 5, 6])
    print(_list_1[1:3])
    print(sum(_list_1))
    print(_list_1 + _list_2)

if __name__ == "__main__":
    test_list_fetch()