
def printf (*args):
    for i in args:
        print i,
    print

def function_class (func):
    try:
        return func.im_class
    except:
        class C:
            pass
        return C

# ugh: function_class (foo) = bar
# gives: SyntaxError: can't assign to function call

function_get_class = function_class

def function_set_class (func, cls):
    try:
        func.im_class = cls
    except:
        pass
