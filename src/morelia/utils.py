import sys

import six


def to_unicode(text):
    ''' Try convert to unicode independently on python version. '''
    try:
        text = text.decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
        pass
    return text


if six.PY2:

    def fix_exception_encoding(exc):
        if len(exc.args):
            message = exc.args[0]
            if isinstance(message, unicode):
                exc.args = (message.encode(sys.stderr.encoding or "ascii", "xmlcharrefreplace"),) + exc.args[1:]

    def to_docstring(text):
        return text.encode('utf-8')

else:

    def fix_exception_encoding(exc):
        pass

    def to_docstring(text):
        return text
