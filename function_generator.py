

def function_generator():
    l = [1,]
    functions = dir(l)
    for function in functions:
        print('''def {}(self, *args, **kwargs):
    return self._array.{}(*args, **kwargs)'''.format(function, function))

if __name__ == "__main__":
    function_generator()