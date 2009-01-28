
def printf (*args):
    for i in args:
        print i,
    print

def function_class (func):
    return func.im_class

# ugh: function_class (foo) = bar
# gives: SyntaxError: can't assign to function call

function_get_class = function_class

def function_set_class (func, cls):
    func.im_class = cls
