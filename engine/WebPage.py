import requests
import urlparse
from bs4 import BeautifulSoup
from langdetect import detect
from robotparser import RobotFileParser
import snowballstemmer
from LANGUAGES import LANGUAGES


class WebPage(object):

    def __init__(self, url):
        self.page_url = url
        self.parsed_url = urlparse.urlparse(url)
        self.lang = ""
        self.isDownload = False
        self.title = ""
        self.text = ""
        self.soup = None
        self.robot = RobotFileParser()

    def __normalize_link__(self, link):
        if not link:
            return None
        if link.startswith('//'):
            return self.parsed_url.scheme + ':' + link
        elif link.startswith('/'):
            return self.parsed_url.scheme + '://' + self.parsed_url.hostname + link
        elif link.startswith('http://') or link.startswith('https://'):
            return link
        elif link.startswith("irc://"):
            return None
        elif link.startswith('#') or link.startswith('javascript:'):
            return None
        else:
            return urlparse.urljoin(self.page_url, link)

    def __delete_unnecessary_tags(self):
        if self.soup is None:
            return

        if self.soup.title is None:
            self.title = ""
        else:
            self.title = self.soup.title.string

        for tag in self.soup(['style', 'script', '[document]', 'head', 'title']):
            tag.decompose()

    def __get_stems(self, text):
        if self.lang in LANGUAGES:
            stemer = snowballstemmer.stemmer(LANGUAGES[self.lang])
        else:
            raise NotImplementedError("That lang not implemented")
        stems_dict = dict()

        for char in [",", ". ", "!", "?", " - ", "/n"]:
            text = text.replace(char, " ")

        for word in text.split():
            stem_word = stemer.stemWord(word.lower())
            if stem_word in stems_dict:
                stems_dict[stem_word] += 1
            else:
                stems_dict[stem_word] = 1

        return stems_dict

    def download_page(self):
        try:
            self.robot.set_url("{0}://{1}/robots.txt".format(self.parsed_url.scheme, self.parsed_url.hostname))
            self.robot.read()
            if self.robot.can_fetch("*", self.page_url):
                response = requests.get(self.page_url, verify=False)
            else:
                return False
        except requests.exceptions.InvalidSchema:
            return False
        except KeyError:
            return False
        except Exception:
            return False

        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, "html.parser")
            self.__delete_unnecessary_tags()
            self.text = "".join(self.soup.strings)
            try:
                self.lang = detect(self.text)
            except Exception:
                self.lang = "en"
            self.isDownload = True
            return True
        else:
            return False

    def get_links(self):
        if not self.isDownload:
            raise Exception("You should download page")

        def get_links_generator():
            for link in self.soup.find_all("a"):
                normalized_link = self.__normalize_link__(link.get("href"))
                if normalized_link is None:
                    continue
                else:
                    yield normalized_link

        return get_links_generator()

    def get_text_stems(self):
        if not self.isDownload:
            raise Exception("You should download page")
        return self.__get_stems(self.text)

    def get_title_stems(self):
        if not self.isDownload:
            raise Exception("You should download page")
        return self.__get_stems(self.title)

    def get_domain(self):
        return self.parsed_url.hostname


def main():
    web_page = WebPage("http://djbook.ru/rel1.9/intro/tutorial03.html")
    if not web_page.download_page():
        print "FAILED download"
        return
    print web_page.lang

    #links = web_page.get_links()
    #for link in links:
    #    print link
    #    web_page = WebPage(link)
    #    web_page.download_page()
    #    print web_page.title

    #print web_page.title
    #dct = web_page.get_title_stems()
    #for stems in dct:
    #    print u"{0} --- {1}".format(stems, dct[stems])


if __name__ == '__main__':
    main()
