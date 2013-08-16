BBCODEPY
========

bbcodepy is a fast Python BBCode parser and renderer.


Usage
-----

All common BBCode tags are supported by default.

``` python
import bbcodepy
print bbcodepy.Parser().to_html('[b]Hello![/b]')
```

Easily add new tags!

``` python
import bbcodepy

class YoutubeTag(bbcodepy.Tag):
    def to_html(self):
        attributes = {
            'src': self.get_content(True).strip(),
            'width': self.params.get('width', 420),
            'height': self.params.get('height', 315)
        }

        return '<iframe %s frameborder="0" allowfullscreen></iframe>' % self.renderer.html_attributes(attributes)

parser = bbcodepy.Parser()
parser.register_tag('youtube', YoutubeTag)

print parser.to_html('[youtube width=420 height=315]http://www.youtube.com/embed/rWTa6OKgWlM[/youtube]')
```
