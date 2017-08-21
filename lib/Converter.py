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

_SVG_DOCTYPE = '<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n'.encode("utf-8")
_AVD_DOCTYPE = '<?xml version="1.0" encoding="utf-8"?>\n'.encode("utf-8")
_ANDROID = "{http://schemas.android.com/apk/res/android}%s"
_SVG = "{http://www.w3.org/2000/svg}%s"

def avd2svg(contents):
    tree = etree.fromstring(contents)
    errs = []
    for e in tree.iter("*"):
        try:
            errs += _AVDelements[e.tag](e)
        except KeyError:
            errs.append("%s: unsupported tag, ignored" % e.tag)
    objectify.deannotate(tree, cleanup_namespaces=True)
    return _SVG_DOCTYPE + etree.tostring(tree).replace(
        b'<svg',
        b'<svg xmlns="http://www.w3.org/2000/svg"'
    ), errs


def _AVDvector(e):
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
    if width is not None:
        e.set('width', width)
    if height is not None:
        e.set('height', height)
    if viewportWidth is not None and viewportHeight is not None:
        e.set('viewBox', "0 0 {0} {1}".format(viewportWidth, viewportHeight))
    e.tag = "svg"
    return errs

def _AVDpath(e):
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
    if fill is not None:
        e.set('fill', fill)
    if stroke is not None:
        e.set('stroke', stroke)
    if strokeWidth is not None:
        e.set('stroke-width', strokeWidth)
    if d is not None:
        e.set('d', d)
    return errs


_AVDelements = {
    "vector": _AVDvector,
    "path": _AVDpath
}


def svg2avd(contents):
    contents = contents.replace(
        b'xmlns="http://www.w3.org/2000/svg"',
        b'xmlns:android="http://schemas.android.com/apk/res/android"'
    )
    tree = etree.fromstring(contents)
    errs = []
    for e in tree.iter("*"):
        try:
            errs += _SVGelements[e.tag](e)
        except KeyError:
            errs.append("%s: unsupported tag, ignored" % e.tag)
    return _AVD_DOCTYPE + etree.tostring(tree), errs


def _SVGsvg(e):
    width = None
    height = None
    viewBox = None

    errs = []
    for a, v in e.items():
        if a == 'width':
            width = v
        elif a == 'height':
            height = v
        elif a == 'viewBox':
            viewBox = v
        else:
            errs.append("%s: unsupported attribute, it have been ignored" % a)

    e.attrib.clear()
    if width is not None:
        e.set(_ANDROID % 'width', width)
    if height is not None:
        e.set(_ANDROID % 'height', height)
    if viewBox is not None:
        viewport = viewBox.split(' ')
        if viewport[0] != "0" or viewport[1] != "0":
            errs.append("Non 0 viewBox origin is not supported, the result may not be the one expected")
        e.set(_ANDROID % 'viewportWidth', viewport[2])
        e.set(_ANDROID % 'viewportHeight', viewport[3])
    e.tag = "vector"
    return errs


def _SVGpath(e):
    fillColor = None
    strokeColor = None
    strokeWidth = None
    pathData = None

    errs = []
    for a, v in e.items():
        if a == 'fill':
            fillColor = v
        elif a == 'stroke-width':
            strokeWidth = v
        elif a == 'stroke':
            strokeColor = v
        elif a == 'd':
            pathData = v
        else:
            errs.append("%s: unsupported attribute, it have been ignored" % a)

    e.attrib.clear()
    if fillColor is not None:
        e.set(_ANDROID % 'fillColor', fillColor)
    if strokeColor is not None:
        e.set(_ANDROID % 'strokeColor', strokeColor)
    if strokeWidth is not None:
        e.set(_ANDROID % 'strokeWidth', strokeWidth)
    if pathData is not None:
        e.set(_ANDROID % 'pathData', pathData)
    return errs

_SVGelements = {
    "svg": _SVGsvg,
    "path": _SVGpath
}
