from string import ascii_lowercase

import numpy as np


def collection_define_tag(body):
    return {'success': True}


def collection_get_tags(url):
    print("url %s"%url)

    return [{'tag': ''.join(np.random.choice(list(ascii_lowercase), 8)),
             'count': np.random.randint(1, 10)} for _ in range(5)]


def collection_is_download_complete(url):
    return True


def download_collection_from_url(url):
    print(url)
    return {'success': True}