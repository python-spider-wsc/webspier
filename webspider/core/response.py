from lxml import etree
from requests.models import Response
import re

class MyResponse(Response):
    def __init__(self, response):
        super(Response, self).__init__()
        self.__dict__.update(response.__dict__)
        self.json_cache = None
        self.selector = None
        self._cached_text = None
        self.model = None

    @property
    def text(self): # 重写text，主要解决编码问题
        if self._cached_text is None:
            self._cached_text = self.content.decode(self.apparent_encoding if self.apparent_encoding else "utf-8")

        return self._cached_text
    
    def save_as_file(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.html)

    def xpath(self, path, first=False):
        if self.model is None:
            self.model = etree.HTML(self.text)
        res = self.model.xpath(path)
        return res[0] if first else res

    def re(self, regex, first=True):
        res = re.findall(regex, self.text)
        return res[0] if first else res

    def compress(self):
        # 去除style标签
        nodes = self.xpath('//style')
        for bad in nodes:
            bad.getparent().remove(bad)
        # 去除link标签
        nodes = self.xpath('//link')
        for bad in nodes:
            bad.getparent().remove(bad)
        # 去除外部js
        nodes = self.xpath('//script[(@src)]')
        for bad in nodes:
            bad.getparent().remove(bad)
        return etree.tounicode(self.model)
