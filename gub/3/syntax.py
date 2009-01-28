
printf = print

def function_class (func):
    try:
        return func.__self__.__class__
    except:
        class C:
            pass
        return C

# ugh: function_class (foo) = bar
# gives: SyntaxError: can't assign to function call

function_get_class = function_class

def function_set_class (func, cls):
    try:
        func.__self__.__class__ = cls
    except:
        pass

next = next
