from .tags import BUILTIN_TAGS, Tag
import re

TOKEN_RE = re.compile(r'(\[/?.+?\])')

class Parser(object):
    def __init__(self, allowed_tags=None):
        if allowed_tags is None:
            self.tags = BUILTIN_TAGS.copy()
        else:
            self.tags = {}

            for tag in allowed_tags:
                if tag in BUILTIN_TAGS:
                    self.tags[tag] = BUILTIN_TAGS[tag]

    def register_tag(self, name, tag):
        self.tags[name] = tag

    def parse(self, bbcode):
        current = root = Tag(self)

        tokens = TOKEN_RE.split(bbcode)

        while tokens:
            token = tokens.pop(0)

            if re.match(TOKEN_RE, token):
                params = [argument.partition('=') for argument in token[1:-1].split()]
                tag_name = params[0][0].lower()

                if tag_name in current.CLOSED_BY:
                    tokens.insert(0, token)
                    tag_name = '/' + current.name
                    params = []

                if tag_name[0] == '/':
                    tag_name = tag_name[1:]

                    if tag_name not in self.tags:
                        Tag(self, text=token, parent=current)
                        continue

                    if current.name == tag_name:
                        current = current.parent
                else:
                    cls = self.tags.get(tag_name)

                    if cls is None:
                        Tag(self, text=token, parent=current)
                        continue
                    
                    tag = cls(self, tag_name, parent=current, params=params)

                    if not tag.SELF_CLOSE and (tag_name not in cls.CLOSED_BY or current.name != tag_name):
                        current = tag
            else:
                Tag(self, text=token, parent=current)

        return root

    def to_html(self, bbcode, prettify=False):
        html = self.parse(bbcode).to_html()

        if prettify:
            from BeautifulSoup import BeautifulSoup
            html = BeautifulSoup(html).prettify()

        return html