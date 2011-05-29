#! /usr/bin/env python

'''
=======================
 ANSI Screen Rendition
=======================

Library to help you use ANSI graphics on text terminals, featuring
cursor movement and color support.


Usage
=====

Clear screen::

    >>> from ansi import clear
    >>> clear()


Move cursor:

    >>> from ansi import cursor
    >>> cursor(23, 42)


Render color:

    >>> from ansi import Color
    >>> color = Color('yellow', 'red') | Color('bold')
    >>> reset = Color('reset')
    >>> print str(color) + '/!\\ Watch the snake /!\\' + str(reset)

'''

import sys

class Color(object):
    colors = dict(
        black   = 30,
        red     = 31,
        green   = 32,
        yellow  = 33,
        blue    = 34,
        magenta = 35,
        purple  = 35,
        cyan    = 36,
        white   = 37,
        gray    = 37,
        default = 39,
    )


    def __init__(self, name, back=None):
        self.bold = False
        self.italics = False
        self.underline = False
        self.inverse = False
        self.striketrough = False
        self.reset = False
        self.fg = None
        self.bg = None

        if name is None:
            self.fg = None
        elif type(name) in [int, long]:
            self.fg = name
        elif name in self.colors:
            self.fg = self.colors[name]
        elif name == 'bold':
            self.fg = False
            self.bold = True
        elif name == 'reset':
            self.reset = True
        elif name in ['italic', 'italics']:
            self.italic = True
        elif name == 'underline':
            self.underline = True
        elif name in ['inverse', 'invert']:
            self.inverse = True
        elif name in ['strike', 'striketrough']:
            self.striketrough = True
        else:
            raise ValueError('Unknown color "%s".' % (name,))

        if back is None:
            self.bg = None
        elif type(back) in [int, long]:
            self.bg = back
        elif back in self.colors:
            self.bg = self.colors[back]
        else:
            raise ValueError('Unknown color "%s".' % (back,))

    def __add__(self, other):
        if isinstance(other, Color):
            color = Color(self.fg, self.bg)
            for attr in ['bold', 'italics', 'underline', 'inverse', 'striketrough']:
                setattr(color, attr,
                    getattr(self, attr) or getattr(other, attr))
            return color
        elif isinstance(other, basestring):
            return u''.join([str(self), other])

    def __or__(self, other):
        return self.__add__(other)

    def __repr__(self):
        return repr(str(self))


    def __str__(self):
        output = []
        if self.reset:
            output.append('0')
        if self.italics:
            output.append('3')
        if self.underline:
            output.append('4')
        if self.inverse:
            output.append('7')
        if self.striketrough:
            output.append('9')

        if self.fg is not None:
            if self.bold and self.fg < 40:
                output.append(str(self.fg + 10))
            else:
                output.append(str(self.fg))
        if self.bg is not None:
            output.append(str(self.bg + 10))

        return '\x1b[%sm' % (';'.join(output),)

    def __unicode__(self):
        return unicode(str(self))


class Buffer(object):
    def __init__(self, buffer=sys.stdout):
        self.buffer = buffer

    def escape(self, data='', flush=True):
        self.write('\x1b%s' % (data,))
        if flush:
            self.flush()

    def flush(self):
        self.buffer.flush()

    def write(self, data):
        self.buffer.write(data)

    def clear(self):
        self.cursor()
        self.erase()

    def cursorUp(self, rows=1):
        self.escape('[%dA' % (rows,))

    def cursorDown(self, rows=1):
        self.escape('[%dB' % (rows,))

    def cursorForward(self, columns=1):
        self.escape('[%dC' % (columns,))

    def cursorBack(self, columns=1):
        self.escape('[%dD' % (columns,))

    def cursorNext(self, rows=1):
        self.escape('[%dE' % (rows,))

    def cursorPrevious(self, rows=1):
        self.escape('[%dF' % (rows,))

    def cursorColumn(self, column=1):
        self.escape('[%dG' % (column,))

    def cursor(self, row=1, column=1):
        self.escape('[%d;%dH' % (row, column))

    def erase(self, mode=0):
        self.escape('[%dJ' % (mode,))

    def eraseLine(self, lines=1):
        self.escape('[%dK' % (lines,))

    def scrollUp(self, rows=1):
        self.escape('[%dS' % (rows,))

    def scrollDown(self, rows=1):
        self.escape('[%dT' % (rows,))

    def save(self):
        self.escape('[s')

    def restore(self):
        self.escape('[u')

    def hide(self):
        self.escape('[?25l')

    def show(self):
        self.escape('[?25h')


ANSI = Buffer(sys.stdout)
for attr in dir(ANSI):
    globals()[attr] = getattr(ANSI, attr)


# Test case
if __name__ == '__main__':
    from io import BytesIO
    buffer = BytesIO()
    test = Buffer(buffer)
    test.clear()
    test.cursorUp()
    clear()
    print repr(buffer.getvalue())
