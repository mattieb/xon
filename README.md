`xon`
-----

`xon` is a Python implementation of something I've come to call "XML Object
Notation", or XON.  It generally conforms to the [`pickle`][1] protocol,
which means you interact with it using `load` and `dump` functions.

XON arose out of a need to support XML in web-based APIs that already
support [JSON][2], and supports the same vocabulary that JSON does.
It is based on--and, in fact, the test cases come from--Stefan Goessner's
["Converting Between XML and JSON"][3].  If you don't use any of `xon`'s
extra options, it is intended to work exactly like Goessner describes
therein:

    >>> import xon
    >>> xon.dumps({'foo': {'bar': ['baz', 'quux']}})
    '<foo><bar>baz</bar><bar>quux</bar></foo>'
    >>> xon.loads('<foo><bar>baz</bar><bar>quux</bar></foo>')
    {'foo': {'bar': ['baz', 'quux']}}

Additional options include `convertvalues`, which will convert `int`s,
`float`s, and `bool`s in addition to the default behavior of handling
strings only, and `wrap`/`unwrap`, which deals with the root tag so that
the `load` result and `dump` parameters are more like typical JSON
objects.

[1]: http://docs.python.org/library/pickle.html
[2]: http://json.org/
[3]: http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html

