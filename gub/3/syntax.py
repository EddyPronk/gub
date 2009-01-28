
printf = print

def function_class (func):
    return func.__self__.__class__

# ugh: function_class (foo) = bar
# gives: SyntaxError: can't assign to function call

function_get_class = function_class

def function_set_class (func, cls):
    func.__self__.__class__ = cls

