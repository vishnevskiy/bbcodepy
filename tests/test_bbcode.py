import inspect
import os
import unittest
import bbcodepy

class TestBBCodeParser(unittest.TestCase):
    def _to_html(self, bbcode, prettify=True):
        return bbcodepy.Parser().to_html(bbcode, prettify)

    def _read_file(self, name):
        with open(os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'static', name)) as f:
            return f.read()

    def _assertEqual(self, name):
        self.assertEqual(self._to_html(self._read_file(name + '.bbcode')), self._read_file(name + '.html'))

    def test_simple_tag(self):
        tests= [
            ('[b]Hello[/b]', "<strong>Hello</strong>"),
            ('[i]Italic[/i]', "<em>Italic</em>"),
            ('[s]Strike[/s]', "<strike>Strike</strike>"),
            ('[u]underlined[/u]', "<u>underlined</u>"),
        ]

        for test, result in tests:
            self.assertEqual(self._to_html(test, False), result)

    def test_links(self):
        tests= [
            ('[link=http://guildwork.com]link1[/link]', '<a href="http://guildwork.com" target="_blank">link1</a>'),
            ('[link="http://guildwork.com"]link2[/link]', '<a href="http://guildwork.com" target="_blank">link2</a>'),
            ('[link]http://guildwork.com[/link]', '<a href="http://guildwork.com" target="_blank">http://guildwork.com</a>')
        ]
 
        for test, result in tests:
            self.assertEqual(self._to_html(test, False), result)

    def test_equal_sign_in_attributes(self):
        self.assertEqual(self._to_html('[url="http://mysite.com?page=home"]Home[/url]', False), '<a href="http://mysite.com?page=home" target="_blank">Home</a>')

    def test_document1(self):
        self._assertEqual('document1')

    def test_document2(self):
        self._assertEqual('document2')

    def test_document3(self):
#        import time
#
#        st = time.time()
#
#        code = '[link wow=2 meow="asdsa\\" asda" disabled]asdsada[/link]'
#
#        for _ in xrange(1000):
#            self._to_html(code, False)
#
#        print '%.2fms' % (time.time() - st)


        print self._to_html(self._read_file('document2.bbcode'))

if __name__ == '__main__':
    unittest.main()