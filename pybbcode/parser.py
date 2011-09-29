from .tags import BUILTIN_TAGS, Tag
from .renderer import Renderer
import re

_WHITESPACE = ' '
_TOKEN_RE = re.compile(r'(\[/?.+?\])')
_START_NEWLINE_RE = re.compile(r'^\r?\n')

class Parser(object):
    def __init__(self, allowed_tags=None):
        if allowed_tags is None:
            self.tags = BUILTIN_TAGS.copy()
        else:
            self.tags = {}

            for tag in allowed_tags:
                if tag in BUILTIN_TAGS:
                    self.tags[tag] = BUILTIN_TAGS[tag]

        self.renderer = Renderer()

    def register_tag(self, name, tag):
        self.tags[name] = tag

    def _parse_params(self, token):
        params = []

        if token:
            target = key = []
            value = []
            terminate = _WHITESPACE
            skip_next = False

            for c in token:
                if skip_next:
                    skip_next = False
                elif target == key and c == '=':
                    target = value
                elif not value and c == '"':
                    terminate = c
                elif c != terminate:
                    target.append(c)
                else:
                    params.append((''.join(key).lower(), ''.join(value)))

                    if not terminate.isspace():
                        skip_next = True

                    target = key = []
                    value = []
                    terminate = _WHITESPACE

            params.append((''.join(key).lower(), ''.join(value)))
            
        return params
    
    def _create_text_node(self, parent, text):
        if parent.children and parent.children[-1].STRIP_OUTER:
            text = _START_NEWLINE_RE.sub('', text, 1)

        Tag(self.renderer, text=text, parent=parent)

    def parse(self, bbcode):
        current = root = Tag(self.renderer)

        tokens = _TOKEN_RE.split(bbcode)

        while tokens:
            token = tokens.pop(0)

            if re.match(_TOKEN_RE, token):
                params = self._parse_params(token[1:-1])
                tag_name = params[0][0]

                if tag_name in current.CLOSED_BY:
                    tokens.insert(0, token)
                    tag_name = '/' + current.name
                    params = []

                if tag_name[0] == '/':
                    tag_name = tag_name[1:]

                    if tag_name not in self.tags:
                        self._create_text_node(current, token)
                        continue

                    if current.name == tag_name:
                        current = current.parent
                else:
                    cls = self.tags.get(tag_name)

                    if cls is None:
                        self._create_text_node(current, token)
                        continue
                    
                    tag = cls(self.renderer, tag_name, parent=current, params=params)

                    if not tag.SELF_CLOSE and (tag_name not in cls.CLOSED_BY or current.name != tag_name):
                        current = tag
            else:
                self._create_text_node(current, token)

        return root

    def to_html(self, bbcode, prettify=False):
        html = self.parse(bbcode).to_html()

        if prettify:
            from BeautifulSoup import BeautifulSoup
            html = BeautifulSoup(html).prettify()

        return html