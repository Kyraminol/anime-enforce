#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
base_link = "http://www.animeforce.org/"


class Enforcer:
    def __init__(self):
        self._anime_list = []

    def anime_list(self, force_update=True):
        if self._anime_list and not force_update:
            return self._anime_list
        self._anime_list = self._update_info()
        return self._anime_list

    @staticmethod
    def _update_info():
        r = requests.get(base_link + "lista-anime")
        soup = BeautifulSoup(r.content, "lxml")
        div = soup.find("div", attrs={"class": "the-content"})
        uls = div.find_all("ul")
        result = []
        for ul in uls:
            lis = ul.find_all("li")
            for li in lis:
                href = li.find("a", attrs={"href": True})["href"]
                name = re.sub(r" s?u?b? ?ita.+", "", li.text, 0, re.IGNORECASE)
                result.append(Anime(name, href))
        return result


class Anime:
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self._info = None
        self._episode_list = []
        self._image_link = None

    def info(self, force_update=False):
        if not self._info or force_update:
            self._update_info()
        return self._info

    def image_link(self, force_update=False):
        if not self._image_link or force_update:
            self._update_info()
        return self._image_link

    def episode_list(self, force_update=False):
        if not self._episode_list or force_update:
            self._update_info()
        return self._episode_list

    def _update_info(self):
        r = requests.get(self.link)
        soup = BeautifulSoup(r.content, "lxml")
        img = soup.find("div", attrs={"class": "the-content"}).find("img")["src"]
        self._image_link = link_fix(img)
        tables = soup.find_all("table")
        if tables:
            info = []
            for tr in tables[0].find_all("tr"):
                tds = tr.find_all("td")
                info.append((tds[0].text, tds[1].text))
            self._info = info
            if len(tables) > 1:
                episode_list = []
                for tr in tables[1].find_all("tr"):
                    if not tr.find("th"):
                        tds = tr.find_all("td")
                        link = tds[1].find("a", attrs={"href": True})["href"]
                        img = tds[1].find("img")["src"]
                        available = True
                        if re.search(r"(nodownload|nostream)", img):
                            available = False
                        link = link_fix(link)
                        episode_list.append(Episode(tds[0].text, link, available))
                self._episode_list = episode_list

    def __repr__(self):
        return "<Anime object name='{}'>".format(self.name)


class Episode:
    def __init__(self, name, link, available=True):
        self.name = name
        self.link = link
        self.available = available
        self._download_link = None

    def download_link(self, force_update=False):
        if self._download_link and not force_update:
            return self._download_link
        r = requests.get(self.link)
        if re.search(r"d=404", r.url):
            self.available = False
            return 404
        if not re.search(r"animeforce", r.url):
            self._download_link = r.url
            return r.url
        soup = BeautifulSoup(r.content, "lxml")
        link = soup.find("source", attrs={"src": True})
        if link:
            self._download_link = link["src"]
            return link["src"]
        alternate_link = soup.find("a", text="Streaming Alternativo")
        if not alternate_link:
            self.available = False
            return -1
        alternate_link = link_fix(alternate_link["href"])
        alternate_r = requests.get(alternate_link)
        soup = BeautifulSoup(alternate_r.content, "lxml")
        scripts = soup.find_all("script", attrs={"type": "text/javascript"})
        link = None
        for script in scripts:
            rex = re.search(r"file: \"([^\"]+)\"", script.text)
            if rex:
                link = rex.group(1)
        if link:
            self._download_link = link
            return link
        else:
            self.available = False
            return -1

    def __repr__(self):
        return "<Episode object name='{}'>".format(self.nome)


def link_fix(link):
    internalre = re.search(r"(ds0?1?6?\.php\?file=.+|wp-content/.+|dl\.php\?file=.+)", link)
    if internalre:
        return base_link + internalre.group()
    externalre = re.search(r"\w+\.\w(\.?\w+)*/.+", link)
    if externalre:
        return "https://" + externalre.group()
    return "https://www.animeforce.org/ds16.php?d=404"
