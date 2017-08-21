# Copyright 2017 Cédric Legrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from lxml import objectify, etree

_DOCTYPE = '<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n'.encode("utf-8")
_ANDROID = "{http://schemas.android.com/apk/res/android}%s"

def avd2svg(contents):
    tree = etree.fromstring(contents)
    errs = []
    for e in tree.iter("*"):
        try:
            errs += _elements[e.tag](e)
        except KeyError:
            errs.append("%s: unsupported tag, ignored" % e.tag)
    objectify.deannotate(tree, cleanup_namespaces=True)
    return _DOCTYPE + etree.tostring(tree).replace(
        b'<svg',
        b'<svg xmlns="http://www.w3.org/2000/svg"'
    ), errs


def _vector(e):
    width = None
    height = None
    viewportWidth = None
    viewportHeight = None

    errs = []
    for a, v in e.items():
        if a == _ANDROID % 'width':
            width = v
        elif a == _ANDROID % 'height':
            height = v
        elif a == _ANDROID % 'viewportWidth':
            viewportWidth = v
        elif a == _ANDROID % 'viewportHeight':
            viewportHeight = v
        else:
            errs.append("%s: unsupported attribute, it have been ignored" % a)

    e.attrib.clear()
    e.set('width', width)
    e.set('height', height)
    e.set('viewBox', "0 0 {0} {1}".format(viewportWidth, viewportHeight))
    e.tag = "svg"
    return errs

def _path(e):
    fill = None
    stroke = None
    strokeWidth = None
    d = None

    errs = []
    for a, v in e.items():
        if a == _ANDROID % 'fillColor':
            fill = v
        elif a == _ANDROID % 'strokeWidth':
            strokeWidth = v
        elif a == _ANDROID % 'strokeColor':
            stroke = v
        elif a == _ANDROID % 'pathData':
            d = v
        else:
            errs.append("%s: unsupported attribute, it have been ignored" % a)

    e.attrib.clear()
    e.set('fill', fill)
    e.set('stroke', stroke)
    e.set('stroke-width', strokeWidth)
    e.set('d', d)
    return errs


_elements = {
    "vector": _vector,
    "path": _path
}


def svg2avd(contents):
    print("SVG to AVD conveersion is not implemented")
