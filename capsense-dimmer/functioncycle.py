class FunctionCycle:
    """
    Cycles over a list of functions while calling them.
    Instanciate with a list, then call the instance to call-and-cycle the list of
    functions.
    The callable instance takes an optional argument `index` which tells it to call the
    function at `index` and continue from there.

    def func1():
        print('test1')

    def func2():
        print('test2')

    def func3():
        print('test3')

    fcycle = FunctionCycle([func1, func2, func3])
    fcycle()
    fcycle(2)
    """

    def __init__(self, functions):
        self.functions = functions
        # This should make sure the first function to run is index 0
        self.index = -1

    def __call__(self, index=None):
        """
        Run function at specified/next index (or wrap around)
        """
        if index is not None:
            self.index = index
        else:
            self.index += 1
            if self.index == len(self.functions):
                self.index = 0

        f = self.functions[self.index]
        print('Calling {}'.format(f))
        f()
