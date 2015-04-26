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

    ''' Abstract Base Class for all formatters. '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def output(self, node, line, status, duration):
        ''' Method called after execution each step.

        :param INode node: node representing step
        :param str line: text of executed step
        :param str status: execution status
        :param float duration: step execution duration
        '''
        pass  # pragma: nocover


class NullFormatter(IFormatter):

    ''' Formatter that... do nothing. '''

    def output(self, node, line, status, duration):
        ''' See :py:meth:`IFormatter.output` '''

        pass


class PlainTextFormatter(IFormatter):

    ''' Formatter that prints all executed steps in plain text to a given stream. '''

    def __init__(self, stream=None):
        ''' Initialize formatter.

        :param file stream: file-like stream to output executed steps
        '''
        self._stream = stream if stream is not None else sys.stderr

    def output(self, node, line, status, duration):
        ''' See :py:meth:`IFormatter.output` '''

        if node.is_executable():
            status = status.lower()
            text = '%-60s # %-5s %.3fs\n' % (
                line.strip('\n'),
                status,
                duration,
            )
        else:
            text = '%s\n' % line.strip('\n')
        self._stream.write(text)
        self._stream.flush()


class ColorTextFormatter(PlainTextFormatter):

    ''' Formatter that prints all executed steps in color to a given stream. '''

    def output(self, node, line, status, duration):
        ''' See :py:meth:`IFormatter.output` '''

        if node.is_executable():
            status = status.lower()
            text = '%s%-60s # %.3fs%s\n' % (
                colors[status],
                line.strip('\n'),
                duration,
                colors['reset']
            )
        else:
            text = '%s\n' % line.strip('\n')
        self._stream.write(text)
        self._stream.flush()
