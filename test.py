#!/usr/bin/env python
#
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

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import unittest

import xon

'''tests for xon'''

class LoadTests(unittest.TestCase):

    loads = [('<e/>',                             {'e': None}),
             ('<e>text</e>',                      {'e': 'text'}),
             ('<e name="value" />',               {'e': {'@name': 'value'}}),
             ('<e name="value">text</e>',         {'e': {'@name': 'value',
                                                         '#text': 'text'}}),
             ('<e> <a>text</a> <b>text</b> </e>', {'e': {'a': 'text',
                                                         'b': 'text'}}),
             ('<e> <a>text</a> <a>text</a> </e>', {'e': {'a': ['text',
                                                               'text']}}),
             ('<e> text <a>text</a> </e>',        {'e': {'#text': 'text',
                                                         'a': 'text'}}),
             ('<e>\n'
              '  <a>some</a>\n'
              '  <b>textual</b>\n'
              '  <a>content</a>\n'
              '</e>',                             {'e': {'a': ['some',
                                                               'content'],
                                                         'b': 'textual'}}),
             ('<e>\n'
              '  some textual\n'
              '  <a>content</a>\n'
              '</e>',                             {'e': {'#text':
                                                         'some textual',
                                                         'a': 'content'}}),
             ('<e>\n'
              '  some\n'
              '  <a>textual</a>\n'
              '  content\n'
              '</e>',                             {'e': 'some '
                                                        '<a>textual</a> '
                                                        'content'}),

            ('''<ol class="xoxo">
                  <li>Subject 1
                    <ol>
                      <li>subpoint a</li>
                      <li>subpoint b</li>
                    </ol>
                  </li>
                  <li><span>Subject 2</span>
                    <ol compact="compact">
                      <li>subpoint c</li>
                      <li>subpoint d</li>
                    </ol>
                  </li>
                </ol>''',

             {'ol': {'@class': 'xoxo',
                     'li': [{'#text': 'Subject 1',
                             'ol': {'li': ['subpoint a', 'subpoint b']}},
                            {'span': 'Subject 2',
                             'ol': {'@compact': 'compact',
                                    'li': ['subpoint c', 'subpoint d']}}]}}),

            ('''<span class="vevent">
                  <a class="url" href="http://www.web2con.com/">
                    <span class="summary">Web 2.0 Conference</span>
                    <abbr class="dtstart" title="2005-10-05">October 5</abbr>
                    <abbr class="dtend" title="2005-10-08">7</abbr>
                    <span class="location">Argent Hotel, SF, CA</span>
                  </a>
                </span>''',

             {'span': {'@class': 'vevent',
                       'a': {'@class': 'url',
                             '@href': 'http://www.web2con.com/',
                             'span': [{'@class': 'summary',
                                       '#text': 'Web 2.0 Conference'},
                                      {'@class': 'location',
                                       '#text': 'Argent Hotel, SF, CA'}],
                             'abbr': [{'@class': 'dtstart',
                                       '@title': '2005-10-05',
                                       '#text': 'October 5'},
                                      {'@class': 'dtend',
                                       '@title': '2005-10-08',
                                       '#text': '7'}]}}})]

    def testloads(self):
        '''loading of XON strings to objects'''
        for xml, obj in self.loads:
            self.assertEqual(xon.loads(xml), obj)

    def testload(self):
        '''loading of XON files to objects'''
        for xml, obj in self.loads:
            fp = StringIO(xml)
            self.assertEqual(xon.load(fp), obj)

    dumps = [({'e': None},               '<e />'),
             ({'e': 'text'},             '<e>text</e>'),
             ({'e': {'@name': 'value'}}, '<e name="value" />'),
             ({'e': {'@name': 'value',
                     '#text': 'text'}},  '<e name="value">text</e>'),
             ({'e': {'a': 'text',
                     'b': 'text'}},      '<e><a>text</a><b>text</b></e>'),
             ({'e': {'a': ['text',
                           'text']}},    '<e><a>text</a><a>text</a></e>'),
             ({'e': {'#text': 'text',
                     'a': 'text'}},      '<e>text <a>text</a></e>'),
             ({'e': {'a': ['some',
                           'content'],
                     'b': 'textual'}},   '<e><a>some</a><a>content</a>'
                                         '<b>textual</b></e>'),
             ({'e': {'#text':
                     'some textual',
                     'a': 'content'}},   '<e>some textual <a>content</a></e>'),
             ({'e': 'some '
                    '<a>textual</a> '
                    'content'},          '<e>some &lt;a&gt;textual&lt;/a&gt; '
                                         'content</e>')]

    def testdumps(self):
        '''dumping of objects to XON strings'''
        for obj, xml in self.dumps:
            self.assertEqual(xon.dumps(obj), xml)

    def testdump(self):
        '''dumping of objects to XON files'''
        for obj, xml in self.dumps:
            fp = StringIO()
            xon.dump(obj, fp)
            self.assertEqual(fp.getvalue(), xml)

    def testroundtrip(self):
        '''roundtrip objects to XON and back'''
        for obj, xml in self.dumps:
            self.assertEqual(obj, xon.loads(xon.dumps(obj)))

    def testint(self):
        '''integer dump and load'''
        obj = {'int': 10}
        xml = '<int>10</int>'
        self.assertEqual(obj, xon.loads(xml, convertvalues=True))
        self.assertEqual(xml, xon.dumps(obj, convertvalues=True))

    def testfloat(self):
        '''float dump and load'''
        obj = {'float': 123.456}
        xml = '<float>123.456</float>'
        self.assertEqual(obj, xon.loads(xml, convertvalues=True))
        self.assertEqual(xml, xon.dumps(obj, convertvalues=True))

    def testboolean(self):
        '''boolean dump and load'''
        obj = {'bool': True}
        xml = '<bool>true</bool>'
        self.assertEqual(obj, xon.loads(xml, convertvalues=True))
        self.assertEqual(xml, xon.dumps(obj, convertvalues=True))

        obj = {'bool': False}
        xml = '<bool>false</bool>'
        self.assertEqual(obj, xon.loads(xml, convertvalues=True))
        self.assertEqual(xml, xon.dumps(obj, convertvalues=True))

    def testtoomanykeys(self):
        '''ValueError if obj has too many keys'''
        self.assertRaises(ValueError, xon.dumps, {'a': 'b', 'c': 'd'})

    def testunserializable(self):
        '''TypeError if obj has unserializable content'''
        class Dummy: pass
        self.assertRaises(TypeError, xon.dumps, {'a': Dummy()})
        self.assertRaises(TypeError, xon.dumps, {'b': 0})
        self.assertRaises(TypeError, xon.dumps, {'c': 0.0})
        self.assertRaises(TypeError, xon.dumps, {'d': False})

    def testunicode(self):
        '''unicode string dump and load'''
        obj = {'unicode': u'a string\u2014in Unicode'}
        xml = '<unicode>a string&#8212;in Unicode</unicode>'
        self.assertEqual(obj, xon.loads(xml))
        self.assertEqual(xml, xon.dumps(obj))

    def testwrap(self):
        '''wrap an arbitrary object in a parent tag'''
        obj = {'one': 'two', 'three': ['four', 'five']}
        xml = ('<wrapper><one>two</one>'
               '<three>four</three><three>five</three></wrapper>')
        self.assertEqual(obj, xon.loads(xml, unwrap=True))
        self.assertEqual(xml, xon.dumps(obj, wrap='wrapper'))

if __name__ == '__main__':
    unittest.main()

# vim: ft=python tabstop=8 expandtab shiftwidth=4 softtabstop=4
