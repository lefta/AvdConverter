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
    if tree.tag != "vector":
        svg = etree.Element("svg")
        svg.append(tree)
        tree = svg

    errs = _AVDiter(tree)
    objectify.deannotate(tree, cleanup_namespaces=True)
    return _SVG_DOCTYPE + etree.tostring(tree).replace(
        b'<svg',
        b'<svg xmlns="http://www.w3.org/2000/svg"'
    ), errs


def _AVDiter(e):
    errs = []
    try:
        errs += _AVDelements[e.tag](e)
    except KeyError:
        errs.append("%s: unsupported tag, ignored" % e.tag)

    for child in e:
        errs += _AVDiter(child)

    return errs


def _AVDsvg(e):
    # Stub to avoid an error when an svg tag is replaced
    return []

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

def _AVDshape(e):
    shape = None

    errs = []
    for a, v in e.items():
        if a == _ANDROID % 'shape':
            shape = v
        else:
            errs.append("%s: unsupported attribute, it have been ignored" % a)

    if shape is None:
        shape = "rectangle"

    e.attrib.clear()

    # Android `shape` do not have size informations, but SVG counterparts needs some
    if shape == "rectangle":
        errs += _AVDshape_rectangle(e)
    else:
        errs.append("%s: unsupported shape value, it have been ignored" % shape)
        errs += _AVDshape_rectangle(e)

    return errs

def _AVDshape_rectangle(e):
    e.tag = "rect"
    e.set("x", "0")
    e.set("y", "0")

    width = "20"
    height = "20"

    # Manually parse childs to get attributes
    errs = []
    for child in e:
        if child.tag == "corners":
            for a, v in child.items():
                if a == _ANDROID % 'radius':
                    e.set("rx", v)
                    e.set("ry", v)
                else:
                    errs.append("%s: unsupported attribute, it have been ignored" % a)
        elif child.tag == "size":
            for a, v in child.items():
                if a == _ANDROID % 'width':
                    width = v
                elif a == _ANDROID % 'height':
                    height = v
                else:
                    errs.append("%s: unsupported attribute, it have been ignored" % a)
        elif child.tag == "solid":
            for a, v in child.items():
                if a == _ANDROID % 'color':
                    e.set("fill", v)
                else:
                    errs.append("%s: unsupported attribute, it have been ignored" % a)
        elif child.tag == "stroke":
            for a, v in child.items():
                if a == _ANDROID % 'color':
                    e.set("stroke", v)
                elif a == _ANDROID % 'width':
                    e.set("stroke-width", v)
                else:
                    errs.append("%s: unsupported attribute, it have been ignored" % a)

        else:
            errs.append("%s: unsupported tag, ignored" % child.tag)
        e.remove(child)

    e.set("width", width)
    e.set("height", height)
    return errs


_AVDelements = {
    "svg": _AVDsvg,
    "vector": _AVDvector,
    "path": _AVDpath,
    "shape": _AVDshape
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
