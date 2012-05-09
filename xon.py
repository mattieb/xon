# Copyright (c) 2012 Matt Behrens.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''read and write XML Object Notation (XON)

XML Object Notation (XON) is a way to represent the same vocabulary as
JSON using XML, based on the approach proposed by Stefan Goessner in
"Converting Between XML and JSON"
<http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html>.

'''

try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

def tailedchildren(elem):
    '''check for non-whitespace tails on an Element's children'''
    for child in elem.getchildren():
        if child.tail:
            if child.tail.strip():
                return True

def parsevalue(s):
    '''try to convert a string to an int, float, or bool'''
    try:
        return float(s)
    except ValueError:
        pass

    try:
        return int(s)
    except ValueError:
        pass

    if s.lower() == 'true':
        return True
    if s.lower() == 'false':
        return False

    return s

def loade(elem, unwrap=True, convertvalues=False):
    '''load XON from an Element
  
    unwrap -- if True, only the value part of the XON object is
    returned

    convertvalues -- if True, convert ints, floats, and bools from
    string representations to their native types

    '''
    value = {}

    for attr in elem.keys():
        value['@' + attr] = elem.get(attr)

    if tailedchildren(elem):
        text = elem.text + ''.join([ET.tostring(child)
                                    for child in elem.getchildren()])
        value['#text'] = ' '.join(text.split())

    else:
        if elem.text:
            text = elem.text.strip()
        else:
            text = None
        if not text:
            text = None

        if text:
            if convertvalues:
                text = parsevalue(text)
            value['#text'] = text

        for child in elem.getchildren():
            tag = child.tag

            if tag in value:
                if type(value[tag]) != list:
                    value[tag] = [value[tag]]
                value[tag].append(loade(child, unwrap=True,
                                        convertvalues=convertvalues))

            else:
                value[tag] = loade(child, unwrap=True,
                                   convertvalues=convertvalues)

    keys = value.keys()
    if len(keys):
        if value.keys() == ['#text']:
            value = value['#text']

    else:
        value = None

    if unwrap:
        return value
    else:
        return {elem.tag: value}

def loads(s, unwrap=False, convertvalues=False):
    '''load XON from a string
  
    unwrap -- if True, only the value part of the XON object is
    returned

    convertvalues -- if True, convert ints, floats, and bools from
    string representations to their native types

    '''
    return loade(ET.XML(s), unwrap, convertvalues)

def load(fp, unwrap=False, convertvalues=False):
    '''load XON from a file
  
    unwrap -- if False, only the value part of the XON object is
    returned

    convertvalues -- if True, convert ints, floats, and bools from
    string representations to their native types

    '''
    return loade(ET.parse(fp).getroot(), unwrap, convertvalues)

def stringify(v):
    '''stringify an int, float or bool'''
    if type(v) in [int, float, bool]:
        return str(v).lower()
    return v

def dumpe(obj, convertvalues=False, wrap=None):
    '''dump object to an Element
   
    convertvalues -- if True, convert ints, floats and bools to string
    representations.  TypeError will be raised otherwise

    wrap -- if not None, name of a parent tag to wrap the object in
    
    '''
    if wrap is not None:
        obj = {wrap: obj}

    if len(obj.keys()) > 1:
        raise ValueError, 'obj has more than one key'

    tag = obj.keys()[0]
    value = obj[tag]

    elem = ET.Element(tag)

    if type(value) != dict:
        value = {'#text': value}

    hastext = False
    hassubobjs = False

    for k in value:
        v = value[k]

        if k.startswith('@'):
            if convertvalues:
                v = stringify(v)
            elem.set(k[1:], v)

        elif k == '#text':
            hastext = True
            if convertvalues:
                v = stringify(v)
            else:
                if v is not None and type(v) not in (str, unicode):
                    raise TypeError, 'value %r is unserializable' % v
            elem.text = v

        else:
            hassubobjs = True

            if type(v) != list:
                v = [v]

            for subobj in v:
                elem.append(dumpe({k: subobj}, convertvalues))

    if hastext and hassubobjs:
        elem.text = elem.text + ' '

    return elem

def dumps(obj, convertvalues=False, wrap=None, encoding=None):
    '''dump object to an XON string
   
    convertvalues -- if True, convert ints, floats and bools to string
    representations.  TypeError will be raised otherwise

    wrap -- if not None, name of a parent tag to wrap the object in

    encoding -- see ElementTree.tostring
    
    '''
    return ET.tostring(dumpe(obj, convertvalues, wrap), encoding=encoding)

def dump(obj, fp, convertvalues=False, wrap=None, encoding=None):
    '''dump object to a file
   
    convertvalues -- if True, convert ints, floats and bools to string
    representations.  TypeError will be raised otherwise
    
    wrap -- if not None, name of a parent tag to wrap the object in

    encoding -- see ElementTree.tostring
    
    '''
    fp.write(dumps(obj, convertvalues, wrap, encoding))

# vim: ft=python tabstop=8 expandtab shiftwidth=4 softtabstop=4
