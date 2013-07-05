from contextlib import contextmanager
import re

_ESCAPE_RE = re.compile('[&<>"]')
_ESCAPE_DICT = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}

_URL_RE = re.compile(ur'''\b((?:([\w-]+):(/{1,3})|www[.])(?:(?:(?:[^\s&()]|&amp;|&quot;)*(?:[^!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\s]))|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)''')

_COSMETIC_DICT = {
    u'--': u'&ndash;',
    u'---': u'&mdash;',
    u'...': u'&#8230;',
    u'(c)': u'&copy;',
    u'(reg)': u'&reg;',
    u'(tm)': u'&trade;',
}
_COSMETIC_RE = re.compile(u'|'.join(re.escape(key) for key in _COSMETIC_DICT.keys()))

class Renderer(object):
    def __init__(self):
        self._contexts = []
        self.options = {
            'linkify': True
        }

    @contextmanager
    def __call__(self, **context):
        options = self.options.copy()
        options.update(context)

        self._contexts.append(self.options)
        self.options = options
        yield
        self.options = self._contexts.pop()

    def escape(self, value):
        """Escapes a string so it is valid within XML or XHTML."""
        return _ESCAPE_RE.sub(lambda match: _ESCAPE_DICT[match.group(0)], value)

    def linkify(self, text):
        def make_link(m):
            url = m.group(1)
            proto = m.group(2)

            if proto and proto not in ['http', 'https']:
                return url # bad protocol, no linkify

            href = m.group(1)

            if not proto:
                href = 'http://' + href # no proto specified, use http

            html = self.process_link(href)

            if html:
                return html

            return u'<a href="%s" target="_blank">%s</a>' % (href, url)

        return _URL_RE.sub(make_link, text)
    
    def process_link(self, href):
        pass

    def cosmetic_replace(self, s):
        def repl(match):
            item = match.group(0)
            return _COSMETIC_DICT.get(item, item)

        return _COSMETIC_RE.sub(repl, s)

    def html_attributes(self, attributes):
        if not attributes:
            return u''

        return u' '.join(u'%s="%s"' % item for item in attributes.items())
