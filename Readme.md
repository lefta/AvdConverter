# AvdConverter

Easily preview and convert Android Vector Drawable files to / from SVG

### Preface

While playing with Substratum, I found that there is very little support for Android Vector Drawable files (unless you use the bloated Android Studio, which is a little overkill for some assets editing IMO).

I decided to remedy that and here is the result.


### Android Vector What?

No it's not some kind of food. This is the android version of SVG, which supports only a subset of the SVG specification, and renaming everything by the way. This way, they create the need for specific tools to support their assets format.

Like SVG, these are vectorial files, which means they draw shapes, not pixels. This means that an AVD asset is resizable at the infinite without quality loss. This way, one drawable deserves all 6 standard Android definitions (ldpi, mdpi, hdpi, xhdpi, xxhdpi and xxxhdpi). Lighter, cleaner, better.


### The project

AvdConverter is released under the MIT license, which means you may do whatever you want with it. The only restriction is to keep my name in the license text.

The GUI and the converter are separated from each other, so if Qt is a too big dependency for you, you may easily write a command line wrapper for the converter. If you do so, please send a Pull Request, I would be glad to integrate it.


### Dependencies

* Python 3: This tool is developped with Python 3.6, but any minor version *should* work
* lxml
* PyQt5: Yeah, I know, quite a big dependency.


### Current status

At the moment, AvdConverter only supports the `vector` and `path` tags, but better support for AVD file format is planned.


### Plans for the future (a.k.a. TODO)

* Full support for AVD file format
* Better support for SVG features not supported by AVD (convert when possible)
* Batch open / directory open
* Batch convert
* CLI support (without the Qt dependency)
