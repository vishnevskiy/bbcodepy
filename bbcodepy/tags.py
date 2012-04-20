import re

_NEWLINE_RE = re.compile(r'\r?\n')
_LINE_BREAK = u'<br />'

class Tag(object):
    CLOSED_BY = []
    SELF_CLOSE = False
    STRIP_INNER = False
    STRIP_OUTER = False
    DISCARD_TEXT = False

    def __init__(self, renderer, name=None, parent=None, text=u'', params=None):
        self.renderer = renderer

        self.name = name
        self.text = text

        self.parent = parent

        if parent:
            parent.children.append(self)

        self._raw_params = params or []
        self._params = None

        self.children = []

    @property
    def params(self):
        if self._params is None:
            self._params = {}

            if self._raw_params:
                for key, value in self._raw_params:
                    if value:
                        self.params[key] = value

        return self._params

    def get_content(self, raw=False):
        pieces = []

        if self.text:
            text = self.renderer.escape(self.text)

            if not raw:
                if self.renderer.options['linkify']:
                    text = self.renderer.linkify(text)

                text = self.renderer.cosmetic_replace(_NEWLINE_RE.sub(_LINE_BREAK, text))

            pieces.append(text)

        children = self.children

        for child in children:
            if raw:
                pieces.append(child.to_text())
            else:
                if self.DISCARD_TEXT and child.name is None:
                    continue

                pieces.append(child.to_html())

        content = ''.join(pieces)

        if not raw and self.STRIP_INNER:
            content = content.strip()

            while content.startswith(_LINE_BREAK):
                content = content[len(_LINE_BREAK):]

            while content.endswith(_LINE_BREAK):
                content = content[:-len(_LINE_BREAK)]

            content = content.strip()

        return content

    def to_text(self, content_as_html=False):
        pieces = []

        if self.name is not None:
            if self.params:
                params = ' '.join(u'='.join(item) for item in self.params.items())

                if self.name in self.params:
                    pieces.append(u'[%s]' % params)
                else:
                    pieces.append(u'[%s %s]' % (self.name, params))
            else:
                pieces.append(u'[%s]' % self.name)

        pieces.append(self.get_content(not content_as_html))

        if self.name is not None and self.name not in self.CLOSED_BY:
            pieces.append(u'[/%s]' % self.name)

        return ''.join(pieces)

    def _to_html(self):
        return self.to_text(True),

    def to_html(self):
        return ''.join(self._to_html())

class CodeTag(Tag):
    STRIP_INNER = True

    def __init__(self, *args, **kwargs):
        Tag.__init__(self, *args, **kwargs)
        self._inline = self.params.get('code') == 'inline'

        if not self._inline:
            self.STRIP_OUTER = True

    def _to_html(self):
        if self._inline:
            return u'<code>', self.get_content(True), u'</code>'

        content = self.get_content(True)

        lang = self.params.get('lang') or self.params.get(self.name)

        if lang:
            return u'<pre class="prettyprint lang-%s linenums">' % lang, content, u'</pre>',
        else:
            return u'<pre class="prettyprint linenums">', content, u'</pre>',

class ImageTag(Tag):
    def _to_html(self):
        attributes = {
            'src': self.get_content(True).strip(),
        }

        if 'width' in self.params:
            attributes['width'] = self.params['width']

        if 'height' in self.params:
            attributes['height'] = self.params['height']

        if 'width' not in attributes and 'height' not in attributes:
            attributes['class'] = 'bbcode'

        return u'<img %s />' % self.renderer.html_attributes(attributes),

class SizeTag(Tag):
    def _to_html(self):
        size = self.params.get('size')

        try:
            size = int(size)
        except (TypeError, ValueError):
            size = None

        if size is None:
            return self.get_content()

        return u'<span style="font-size:%spx">' % size, self.get_content(), u'</span>',

class ColorTag(Tag):
    def _to_html(self):
        color = self.params.get('color')

        if not color:
            return self.get_content()

        return u'<span style="color:%s">' % color, self.get_content(), u'</span>',

class CenterTag(Tag):
    def _to_html(self):
        return u'<div style="text-align:center;">', self.get_content(), u'</div>',

class RightTag(Tag):
    def _to_html(self):
        return u'<div style="float:right;">', self.get_content(), u'</div>',

class HorizontalRuleTag(Tag):
    SELF_CLOSE = True
    STRIP_OUTER = True

    def _to_html(self):
        return u'<hr />',

class ListTag(Tag):
    STRIP_INNER = True
    STRIP_OUTER = True

    def _to_html(self):
        list_type = self.params.get('list')

        if list_type == '1':
            return u'<ol>', self.get_content(), u'</ol>',
        elif list_type == 'a':
            return u'<ol style="list-style-type:lower-alpha;">', self.get_content(), u'</ol>',
        elif list_type == 'A':
            return u'<ol style="list-style-type:upper-alpha;">', self.get_content(), u'</ol>',
        else:
            return u'<ul>', self.get_content(), u'</ul>',

class ListItemTag(Tag):
    CLOSED_BY = ['*', '/list']
    STRIP_INNER = True

    def _to_html(self):
        return u'<li>', self.get_content(), u'</li>',

class QuoteTag(Tag):
    STRIP_INNER = True
    STRIP_OUTER = True

    def _to_html(self):
        pieces = [u'<blockquote>', self.get_content()]

        citation = self.params.get('quote')

        if citation:
            pieces.append(u'<small>')
            pieces.append(citation)
            pieces.append(u'</small>')

        pieces.append(u'</blockquote>')

        return pieces

class LinkTag(Tag):
    SAFE_CHARS = frozenset(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'abcdefghijklmnopqrstuvwxyz'
        '0123456789'
        '_.-=/&?:%&#'
    )

    def _to_html(self):
        url = (self.params.get(self.name) or self.get_content(True)).strip()

        if u'javascript:' in url.lower():
            url = u''
        elif u':' not in url:
            url = u'http://' + url

        url = ''.join([c if c in LinkTag.SAFE_CHARS else '%%%02X' % ord(c) for c in url])

        if url:
            with self.renderer(linkify=False):
                return u'<a href="%s" target="_blank">%s</a>' % (url, self.get_content())
        else:
            return self.get_content()

def create_simple_tag(name, **attributes):
    def _to_html(self):
        html_attributes = self.renderer.html_attributes(self.params)

        if html_attributes:
            html_attributes = ' ' + html_attributes

        return u'<%s%s>' % (name, html_attributes), self.get_content(), u'</%s>' % name,

    attributes['_to_html'] = _to_html

    return type('%sTag' % name.title(), (Tag,), attributes)

BUILTIN_TAGS = {
    'b': create_simple_tag('strong'),
    'i': create_simple_tag('em'),
    'u': create_simple_tag('u'),
    's': create_simple_tag('strike'),
    'h1': create_simple_tag('h1', STRIP_OUTER=True),
    'h2': create_simple_tag('h2', STRIP_OUTER=True),
    'h3': create_simple_tag('h3', STRIP_OUTER=True),
    'h4': create_simple_tag('h4', STRIP_OUTER=True),
    'h5': create_simple_tag('h5', STRIP_OUTER=True),
    'h6': create_simple_tag('h6', STRIP_OUTER=True),
    'pre': create_simple_tag('pre'),
    'table': create_simple_tag('table', DISCARD_TEXT=True),
    'thead': create_simple_tag('thead', DISCARD_TEXT=True),
    'tbody': create_simple_tag('tbody', DISCARD_TEXT=True),
    'tr': create_simple_tag('tr', DISCARD_TEXT=True),
    'th': create_simple_tag('th'),
    'td': create_simple_tag('td'),
    'code': CodeTag,
    'hr': HorizontalRuleTag,
    'img': ImageTag,
    'size': SizeTag,
    'center': CenterTag,
    'right': RightTag,
    'color': ColorTag,
    'list': ListTag,
    '*': ListItemTag,
    'quote': QuoteTag,
    'url': LinkTag,
    'link': LinkTag,
}
