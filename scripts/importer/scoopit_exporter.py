import json
import urllib
import codecs
from itertools import count
from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen

import progressbar
import pymongo
from bs4 import BeautifulSoup
import os.path

from config import DB_ADDRESS

DIR = 'scoop_it/'
os.makedirs(DIR, exist_ok=True)

TOPICS_FILE = DIR + 'topics.html'
TOPICS_URL = 'http://www.scoop.it/u/pierre-levy/ajaxGetUserCuratedThemes?followContext=CuratorProfile&nbItemsPerPage=12&view=json&listId=curatedTopicsTab'
RELOAD_BACKUP = False


def save_topics():
    if RELOAD_BACKUP or not os.path.isfile(TOPICS_FILE):
        with open(TOPICS_FILE, 'w') as e:
            r = urllib.request.urlopen(TOPICS_URL)
            r = json.load(codecs.getreader('utf-8')(r))
            e.write(r['js_inner_replace']['html'])


def save_theme(theme_url, theme_file):
    if RELOAD_BACKUP or not os.path.isfile(theme_file):
        with open(theme_file, 'w') as e:
            r = urllib.request.urlopen(theme_url)
            r = codecs.getreader('utf-8')(r)
            e.write(r.read())


def title_lnk(a):
    return a.contents[0].replace('\n', '').replace('\t', '').strip()


def retrieve_tags(base_url, base_file):
    tags = []
    url = base_url
    file = "%s" % base_file
    save_theme(url, file)
    with open(file) as theme_fp:
        th_html = BeautifulSoup(theme_fp, "lxml")
        # [e.select('.topic-tags-item-name')[0].contents[0] for e in
         # th_html.select('#tagListWrapper .topic-tags-list .topic-tags-item > a')]
        for tag in th_html.select('.topic-tags-list > .topic-tags-item > a'):
            tags.append({
                'title': tag.select('.topic-tags-item-name')[0].contents[0],
                'count': tag.select('.topic-tags-item-count')[0].contents[0],
                'url': "http://%s%s"%(urlparse(url).netloc, tag['href'])
            })

    return tags


def retrieve_posts_for_tag(tag, name):
    result = []
    for page in count(1):
        url = '%s&page=%d' % (tag['url'], page)
        dir = DIR + "%s/%s/"%(name, tag['title'])
        file = dir + "%d.html"%page

        os.makedirs(dir, exist_ok=True)
        save_theme(url, file)

        with open(file) as theme_fp:
            th_html = BeautifulSoup(theme_fp, "lxml")
            if th_html.select("#noScoopYet"):
                break

            for div in th_html.select('div[id^=post_]'):
                a = div.select('h2 > a')
                if not a:
                    # result.append({
                    #     'id': div['data-lid'],
                    #     'type': 'post'
                    # })
                    print("Malformed article at %s on tag %s at page %d (id:%s)."%
                          (name, tag['title'], page, div['data-lid']))
                else:
                    a = a[0]
                    result.append({
                        'type': 'link',
                        'id': div['data-lid'],
                        'title': title_lnk(a),
                        'url': a['href']
                    })
    return result

def scrap_scoopit():
    save_topics()
    datas = []
    with open(TOPICS_FILE) as r:
        s = BeautifulSoup(r, "lxml")

        for a in s.select('.theme-title > a'):
            title = title_lnk(a)
            datas.append({
                'title': title,
                'url': a['href'],
                'file': DIR + title.lower().replace(' ', '_'),
                'posts': {}
            })

        for theme in datas:
            theme['tags'] = retrieve_tags(theme['url'], theme['file'])
            print(theme['title'] + '\n---------', flush=True)

            p = progressbar.ProgressBar(redirect_stdout = True)

            for tag in p(theme['tags']):
                posts = retrieve_posts_for_tag(tag, theme['title'])

                tag['posts'] = [p['id'] for p in posts]
                for p in posts:
                    if p['id'] not in theme['posts']:
                        theme['posts'][p['id']] = p

                if len(tag['posts']) != int(tag['count']):
                    print('Missing some tags ... in %s for tag %s. (post:%d vs tag_count:%d)'%
                          (theme['title'], tag['title'], len(tag['posts']), int(tag['count'])))

            theme['posts'] = list(theme.values())
    return datas


def save_datas(datas):
    with open('scoopit-datas.json', 'w') as f:
        json.dump(datas, f,indent=True)


def load_datas():
    with open('/home/louis/code/ieml/propositions-restful-server/scripts/scoopit-datas.json') as f:
        return json.load(f)

def mongo_save_datas(datas):
    collection = pymongo.MongoClient(DB_ADDRESS)['data']['scoopit']
    collection.drop()

    datas = [
        {**theme, 'posts':
            {id: {**theme['posts'][id],
                  'tags': []} for id in theme['posts']}
         } for theme in datas]

    for theme in datas:
        for tag in theme['tags']:
            for p in tag['posts']:
                theme['posts'][p]['tags'].append({
                    'type': 'taxonomic',
                    'title': tag['title']
                })

        for post_id in theme['posts']:
            post = theme['posts'][post_id]
            insertion = {
                '_id': post_id,
                'type': post['type'],
                'tags': post['tags'] + [{
                    'type': 'sentence',
                    'title': theme['title']
                }]
            }
            if post['type'] == 'link':
                insertion['title'] = post['title']
                insertion['url'] = post['url']
                insertion['tags'].append({
                    'type': 'sentence',
                    'title': post['title']
                })

            collection.insert(insertion)

def scoopit_login(username, password):
    import requests
    r = requests.post('http://www.scoop.it/login', data={
        'email': 'test',
        'password': 'test',
        'remenberMe': True})

    # request = Request(, data=bytes(urlencode(
    # }), 'utf-8'))

    print(str(r))
    # response = urlopen(request)
    # print(response.read().decode('utf-8'))


# save_datas(scrap_scoopit())
# datas = scrap_scoopit()
# save_datas(datas)
data = load_datas()
save_datas(data)
mongo_save_datas(data)
# scoopit_login('pierre.levy@mac.me', '1plotin')