from ieml.parsing.parser import PropositionsParser
from models.intlekt.usl.usl_connector import UslConnector
from models.terms.terms import TermsConnector

connector = UslConnector()
e = list(connector.usls.find({'KEYWORDS.language':{'$nin':['spanish']}}))
connector_term = TermsConnector()

zord = PropositionsParser().parse(e)
zord.subst[0]

k = 'e.'
t = connector_term.terms.find_one({'_id':k})