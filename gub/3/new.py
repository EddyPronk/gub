# http://docs.python.org/3.0/whatsnew/3.0.html
# new is `gone'.  great.
# http://osdir.com/ml/python.python-3000.cvs/2006-05/msg00002.html
#from types import ClassType as classobj
#from types import _C
class _C:
    pass
classobj = type (_C)
from types import FunctionType as function
from types import MethodType as instancemethod
from types import ModuleType as module
