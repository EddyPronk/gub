

class BaseException(object):

    """Superclass representing the base of the exception hierarchy.

    Provides a 'message' attribute that contains either the single
    argument to the constructor or the empty string.  This attribute
    is used in both the string and unicode representation for the
    exception.  This is so that it provides the extra details in the
    traceback.

    """

    def __init__(self, message=''):
        """Set the 'message' attribute'"""
        self.message = message

    def __str__(self):
        """Return the str of 'message'"""
        return str(self.message)

    def __unicode__(self):
        """Return the unicode of 'message'"""
        return unicode(self.message)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.message))
