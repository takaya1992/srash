import requests
import lxml.html

class SearchEngine:
    def __init__(self):
        pass

class SearchEngineFactory:
    @classmethod
    def create(cls, engine_name):
        # TODO: 大文字小文字の違いを許容する
        if engine_name == 'Google':
            return GoogleSearch()
        elif engine_name == 'Yahoo':
            return YahooSearch()
        elif engine_name == 'Bing':
            return BingSearch()
        else:
            return None


class SearchEnginePager:

    _count = 1

    def __init__(self, search_word):
        self.search_word = search_word

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration()


class SearchEnginePage:

    DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'

    def __init__(self, params):
        self._params = params
        headers = {'User-Agent': self.DEFAULT_USER_AGENT}
        self._r = requests.get(self.SEARCH_ENDPOINT, params=params, headers=headers)
        self._dom = None


class SearchEngineEntry:
    def __init__(self, *, uri, title, description, index):
        self.uri = uri
        self.title = title
        self.description = description
        self.index = index

    def to_dict(self):
        return {
            'uri': self.uri,
            'title': self.title,
            'description': self.description,
            'index': self.index
        }


class GoogleSearch(SearchEngine):
    def search(self, search_word):
        return GoogleSearchPager(search_word)
    

class GoogleSearchPager(SearchEnginePager):

    MAX_COUNT = 3

    def __next__(self):
        if self._count > self.MAX_COUNT:
            raise StopIteration()
        params = {'q': self.search_word, 'start': (self._count - 1) * 10}
        if self._count == 3:
            params['start'] = 0
            params['num'] = 100
        page = GoogleSearchPage(params)
        self._count += 1
        return page


class GoogleSearchPage(SearchEnginePage):

    SEARCH_ENDPOINT = 'https://www.google.com/search'
    COUNT_PATH = 'count(//div[@class="rc"])'
    BASE_PATH = '//div[@class="g"][%i]//div[@class="rc"]/h3/a[starts-with(@href, "http://%s") or starts-with(@href, "https://%s")]'

    def find_entry(self, domain):
        if self._dom is None:
            self._dom = lxml.html.fromstring(self._r.content)
        rc_count = int(self._dom.xpath(self.COUNT_PATH))
        position = None
        for i in range(rc_count):
            element = self._dom.xpath(self.BASE_PATH % (i, domain, domain))
            if len(element) >= 1:
                position = i
                break
        if position is None:
            return None
        base_path = self.BASE_PATH % (position, domain, domain)
        uri = ''.join(self._dom.xpath(base_path + '/@href'))
        title = ''.join(self._dom.xpath(base_path + '/text()'))
        description = ''.join(self._dom.xpath(base_path + '/../../div[@class="s"]/div/span[@class="st"]//text()'))
        index = self._params['start'] + position
        return SearchEngineEntry(uri=uri, title=title, description=description, index=index)


class YahooSearch(SearchEngine):
    def search(self, search_word):
        return YahooSearchPager(search_word)


class YahooSearchPager(SearchEnginePager):

    MAX_COUNT = 5

    def __next__(self):
        if self._count > self.MAX_COUNT:
            raise StopIteration()
        params = {'p': self.search_word, 'b': (self._count - 1) * 10 + 1}
        page = YahooSearchPage(params)
        self._count += 1
        return page


class YahooSearchPage(SearchEnginePage):

    SEARCH_ENDPOINT = 'http://search.yahoo.co.jp/search'
    COUNT_PATH = 'count(//div[@id="WS2m"]/div[@class="w"])'
    BASE_PATH = '//div[@id="WS2m"]/div[@class="w"][%i]//h3/a[starts-with(@href, "http://%s") or starts-with(@href, "https://%s")]'

    def find_entry(self, domain):
        if self._dom is None:
            self._dom = lxml.html.fromstring(self._r.content)
        rc_count = int(self._dom.xpath(self.COUNT_PATH))
        position = None
        for i in range(rc_count):
            element = self._dom.xpath(self.BASE_PATH % (i, domain, domain))
            if len(element) >= 1:
                position = i
                break
        if position is None:
            return None
        base_path = self.BASE_PATH % (position, domain, domain)
        uri = ''.join(self._dom.xpath(base_path + '/@href'))
        title = ''.join(self._dom.xpath(base_path + '//text()'))
        description = ''.join(self._dom.xpath(base_path + '/../../../div[@class="bd"]/p//text()'))
        index = self._params['b'] + position - 1
        return SearchEngineEntry(uri=uri, title=title, description=description, index=index)


class BingSearch(SearchEngine):
    def search(self, search_word):
        return BingSearchPager(search_word)


class BingSearchPager(SearchEnginePager):

    MAX_COUNT = 5

    def __next__(self):
        if self._count > self.MAX_COUNT:
            raise StopIteration()
        params = {'q': self.search_word, 'first': (self._count - 1) * 10}
        page = BingSearchPage(params)
        self._count += 1
        return page


class BingSearchPage(SearchEnginePage):

    SEARCH_ENDPOINT = 'https://www.bing.com/search'
    OFFSET_PARAM_NAME = 'first'
    COUNT_PATH = 'count(//li[@class="b_algo"])'
    BASE_PATH = '//li[@class="b_algo"][%i]//h2/a[starts-with(@href, "http://%s") or starts-with(@href, "https://%s")]'

    def find_entry(self, domain):
        if self._dom is None:
            self._dom = lxml.html.fromstring(self._r.text)
        rc_count = int(self._dom.xpath(self.COUNT_PATH))
        position = None
        for i in range(rc_count):
            element = self._dom.xpath(self.BASE_PATH % (i, domain, domain))
            if len(element) >= 1:
                position = i
                break
        if position is None:
            return None
        base_path = self.BASE_PATH % (position, domain, domain)
        uri = ''.join(self._dom.xpath(base_path + '/@href'))
        title = ''.join(self._dom.xpath(base_path + '//text()'))
        description = ''.join(self._dom.xpath('//li[@class="b_algo"][%i]/div[@class="b_caption"]//p/text()' % (position)))
        index = self._params[self.OFFSET_PARAM_NAME] + position
        return SearchEngineEntry(uri=uri, title=title, description=description, index=index)
