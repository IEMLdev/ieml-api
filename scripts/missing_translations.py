import urllib.request
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
# from models.intlekt.old.constants import LANGUAGES
# from models.intlekt.old.usl_connector import UslConnector

#faire les champs Spanish et portuguese même vide pour ne retourner qu'un seul objet python : JSON
# connector = UslConnector()

# usls_ieml = list(connector.usls.find())
#
# to_translate = []
#
# for el in usls_ieml:
#     l_to_trans = set(LANGUAGES) - set(k['language'] for k in el['KEYWORDS'])
#     keywords = el['KEYWORDS']
#     keywords.extend([{
#         'language': l,
#         'DERIVED':'write here the %s translation'%l
#     } for l in l_to_trans])
#
#     to_translate.append({
#         '_id': el['_id'],
#         'KEYWORDS': keywords
#     })
#
# import json
# with open("missing_translations.txt", 'w') as fp:
#     json.dump(to_translate, fp=fp, ensure_ascii=False, indent=True)
#


def get_derived_terms_from_wiktionnary(descriptor):
    """

    :param descriptor:
    :return: a dict language -> set of str representing the drived t$erm in that language
    """
    result = {}

    try:
        response = urllib.request.urlopen('https://en.wiktionary.org/w/index.php?title=' \
                                          + quote_plus(descriptor.rstrip('\n\r')) + '&printable=yes')
    except IOError:
        return result
    else:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        for language in ("English","French","Portuguese","Spanish"):
            titles_list = [el.attrs["title"] for el in soup.select('ul li span a[href$="#%s"]'%language) \
                           if "title" in el.attrs]
            if titles_list:  # checks if the list is empty
                result[language.lower()] = set(titles_list)
    return result

if __name__ == '__main__':
    print(get_derived_terms_from_wiktionnary('manger'))