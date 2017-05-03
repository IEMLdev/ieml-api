import urllib.request
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from models.intlekt.collections.sources import SourcesConnector

SCOOPIT_URL="www.scoop.it"


def _check_is_scoopit_url(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc == SCOOPIT_URL


def import_tags(url):
    if not _check_is_scoopit_url(url):
        raise ValueError("Not a scoopit url: %s"%url)

    tags = scrap_tags(url)
    SourcesConnector().save_sources(url, tags)


def scrap_tags(theme_url):
    r = urllib.request.urlopen(theme_url).read()
    th_html = BeautifulSoup(r, "lxml")
    tags = []

    for tag in th_html.select('.topic-tags-list > .topic-tags-item > a'):
        tags.append({
            'title': tag.select('.topic-tags-item-name')[0].contents[0],
            'count': int(tag.select('.topic-tags-item-count')[0].contents[0]),
            'link': "http://%s%s" % (urlparse(theme_url).netloc, tag['href'])
        })

    return tags




if __name__ == '__main__':
    import_tags("http://www.scoop.it/t/big-data-cloud-and-social-everything")
