from lxml import objectify, etree

_DOCTYPE = '<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n'.encode("utf-8")
_ANDROID = "{http://schemas.android.com/apk/res/android}%s"

def avd2svg(contents):
    tree = etree.fromstring(contents)
    for e in tree.iter("*"):
        _elements[e.tag](e)
    objectify.deannotate(tree, cleanup_namespaces=True)
    return _DOCTYPE + etree.tostring(tree).replace(
        b'<svg',
        b'<svg xmlns="http://www.w3.org/2000/svg"'
    )


def _vector(e):
    width = None
    height = None
    viewportWidth = None
    viewportHeight = None

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
            print("%s: unsupported attribute, it have been ignored" % a)

    e.attrib.clear()
    e.set('width', width)
    e.set('height', height)
    e.set('viewBox', "0 0 {0} {1}".format(viewportWidth, viewportHeight))
    e.tag = "svg"

def _path(e):
    fill = None
    stroke = None
    strokeWidth = None
    d = None

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
            print("%s: unsupported attribute, it have been ignored" % a)

    e.attrib.clear()
    e.set('fill', fill)
    e.set('stroke', stroke)
    e.set('stroke-width', strokeWidth)
    e.set('d', d)


_elements = {
    "vector": _vector,
    "path": _path
}


def svg2avd(contents):
    print("SVG to AVD conveersion is not implemented")
