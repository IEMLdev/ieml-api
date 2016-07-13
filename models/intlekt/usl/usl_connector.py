from ieml.AST.propositions import Word, Morpheme
from ieml.AST.terms import Term
from models.intlekt.connector import DemoConnector
from models.intlekt.constants import COLLECTION_USL
import progressbar
import pymongo
from models.terms.terms import TermsConnector
from urllib.parse import urlencode, quote_plus
import urllib.request
from bs4 import BeautifulSoup
from collections import defaultdict


class UslConnector(DemoConnector):
    """
    Connector to add and remove usl and keywords association.
    The document are :
    {
        '_id': str(usl),
        'keywords': [str(keyword)]
    }
    """

    def __init__(self):
        super().__init__()

        self.usls = self.demo_db[COLLECTION_USL]

    def save_keyword(self, usl, keyword):
        if not self.check_usl_exists(usl):
            self.usls.insert({
                '_id': usl if isinstance(usl, str) else str(usl),
                'KEYWORDS': [keyword]
            })
        else:
            self.usls.update({
                '_id': usl if isinstance(usl, str) else str(usl)
            }, {
                '$addToSet': {'KEYWORDS': keyword}
            })

    def check_usl_exists(self, usl):
        return self.usls.find_one({
            '_id': usl if isinstance(usl, str) else str(usl)
        }) is not None


    def get_derived_terms_from_wiktionnary(self, descriptor):
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

    #Alice
    def load_collection(self):
        self.usls.create_index([('KEYWORDS.DERIVED', pymongo.TEXT)])
        terms = TermsConnector().get_all_terms()
        p = progressbar.ProgressBar(max_value=4136)
        for t in p(terms):
            w = Word(Morpheme(Term(t['_id'])))
            w.check()

            if self.check_usl_exists(str(w)): #check si l'usl existe
                continue

            total_derived_terms = defaultdict(lambda: set())
            for l in (('EN', 'english'), ('FR', 'french')):
                for e in t['TAGS'][l[0]].split('|'):
                    e = e.strip()
                    total_derived_terms[l[1]].add(e)

                    derived_terms = self.get_derived_terms_from_wiktionnary(e)
                    if not derived_terms:
                        continue

                    for key in derived_terms:
                        total_derived_terms[key] |= derived_terms[key]

            insertion = {
                '_id': str(w),  #enfin le mot de l usl avec fonction, if isinstance(usl, str) else str(usl) ???
                'KEYWORDS': [{
                                 'language': key,
                                 'DERIVED': list(total_derived_terms[key])
                             } for key in total_derived_terms]
            }

            self.usls.insert(insertion)

if __name__ == '__main__':
    UslConnector().load_collection()