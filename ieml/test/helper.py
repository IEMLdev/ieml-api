from ieml.dictionary import term
from ieml.grammar import fact, topic
from ieml.grammar.word import word


def get_test_word_instance():
    morpheme_subst = [term("a.i.-"), term("i.i.-")]
    morpheme_attr = [term("E:A:T:."), term("E:S:.wa.-"),term("E:S:.o.-")]
    return word(morpheme_subst, morpheme_attr)

def get_test_morpheme_instance():
    morpheme = [term("E:A:T:."), term("E:S:.wa.-"),term("E:S:.o.-")]
    return morpheme

def get_topics_list():
    #this list is already sorted
    terms_list = [term("E:A:T:."), term("E:.S:.wa.-"), term("E:.-S:.o.-t.-'"), term("a.i.-"), term("i.i.-"),  term("u.M:M:.-")]

    # a small yield to check the word before returning it :-°
    for t in terms_list:
        word_obj = topic([t])
        yield word_obj

def get_test_sentence():
    a, b, c, d, e, f = tuple(get_topics_list())
    clause_a, clause_b, clause_c, clause_d = (a,b,f), (a,c,f), (b,d,f), (b,e,f)
    sentence = fact([clause_b, clause_a, clause_d, clause_c])
    return sentence

