from requests_html import HTMLSession
from fuzzywuzzy.process import extractBests
from re import sub


class AnimeEnforce:
    def __init__(self):
        self._s = HTMLSession()

    def get_list(self):
        r = self._s.get("https://www.animeforce.it/lista-anime/")
        html = getattr(r, "html")
        elements = html.find(".letter-section.animeforce > .list-item > .item-wrapper a:not(.float-right)")
        result = [Anime(element.attrs["title"], element.attrs["href"]) for element in elements]
        return result

    def search(self, text, limit=10):
        anime = self.get_list()
        return [x[0] for x in extractBests(text, anime, processor=self._search_processor, limit=limit)]

    @staticmethod
    def _search_processor(item):
        if isinstance(item, Anime):
            item = item.name
        return sub(r"[^\w\s]", " ", item).lower().strip()

    def _get_news(self):
        result = []
        r = self._s.get("https://www.animeforce.it/")
        html = getattr(r, "html")
        for anime in html.find(".anime-card.main-anime-card"):
            a = anime.find("a", first=True)
            n = anime.find(".anime-episode", first=True).text
            e = Episode(a.attrs["href"], n[3:], anime=a.attrs["title"])
            result.append(e)
        return result

    news = property(_get_news)


class Anime:
    def __init__(self, name, url):
        self._name = name
        self._url = url

    def _get_episodes(self):
        s = HTMLSession()
        r = s.get(self._url)
        html = getattr(r, "html")
        result = {}
        for tab in [x.attrs["href"] for x in html.find(".servers-container #nav-tab > a")]:
            elements = html.find(f"{tab} > div > a")
            for chunk in [x.attrs["href"] for x in html.find(f"{tab} #pills-tab a")]:
                elements_chunk = html.find(f"{tab} #pills-tabContent {chunk} > a")
                if len(elements_chunk) > 0:
                    elements += elements_chunk
            temp = []
            for index, element in enumerate(elements):
                temp.append(Episode(element.absolute_links.pop(), index+1, tab[5:].lower()))
            result[tab[5:].lower()] = temp
        return result

    def _get_info(self):
        s = HTMLSession()
        r = s.get(self._url)
        html = getattr(r, "html")
        details = html.find(".details-text > .col-md-12:not(.anime-title):not(.mt-2)")
        result = {}
        for detail in details:
            info = [sub(r"\n|^ ?: ?| ?: ?$", "", x).strip() for x in detail.xpath("//*/text()[.!='\n']")]
            result[info[0]] = info[1:]
        return result

    def __repr__(self):
        return f"<Anime object name='{self._name}' url='{self._url}'>"

    info = property(_get_info)
    episodes = property(_get_episodes)
    name = property(lambda self: self._name)
    url = property(lambda self: self._url)


class Episode:
    def __init__(self, url, number, section=None, anime=None):
        self._url = url
        self._number = int(number)
        self._section = section
        self._anime = anime

    def __repr__(self):
        return f"<Episode object url='{self._url}' number='{self._number}' section='{self._section}' " \
               f"anime='{self._anime}'>"

    def _get_download(self):
        s = HTMLSession()
        r = s.get(self._url)
        html = getattr(r, "html")
        download = html.find(".btn.btn-primary.btn-lg.btn-block", first=True)
        return download.attrs["data-href"] if download else ""

    download = property(_get_download)
    url = property(lambda self: self._url)
    number = property(lambda self: self._number)
    section = property(lambda self: self._section)
    anime = property(lambda self: self._anime)
