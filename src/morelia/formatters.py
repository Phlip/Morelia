from abc import ABCMeta, abstractmethod
import sys

colors = {
    'normal': u'\x1b[30m',
    'fail': u'\x1b[31m',
    'error': u'\x1b[31m',
    'pass': u'\x1b[32m',
    'reset': u'\x1b[0m',
}


class IFormatter(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def output(self, node, line, status, duration):
        pass  # pragma: nocover


class NullFormatter(IFormatter):

    def output(self, node, line, status, duration):
        pass


class PlainTextFormatter(IFormatter):

    def __init__(self, stream=None):
        self._stream = stream if stream is not None else sys.stderr

    def output(self, node, line, status, duration):
        if node.is_executable():
            status = status.lower()
            text = '%-40s # %-5s %.3fs\n' % (
                line.strip('\n'),
                status,
                duration,
            )
        else:
            text = '%s\n' % line.strip('\n')
        self._stream.write(text)
        self._stream.flush()


class ColorTextFormatter(PlainTextFormatter):

    def output(self, node, line, status, duration):
        if node.is_executable():
            status = status.lower()
            text = '%s%-40s # %.3fs%s\n' % (
                colors[status],
                line.strip('\n'),
                duration,
                colors['reset']
            )
        else:
            text = '%s\n' % line.strip('\n')
        self._stream.write(text)
        self._stream.flush()
