import io

import boto3
from ieml.dictionary.dictionary import Dictionary

from ieml.dictionary.tools import term
from ieml.dictionary.version import get_available_dictionary_version, create_dictionary_version, \
    DictionaryVersion, latest_dictionary_version
from ieml.dictionary.script import script, m, NullScript, AdditiveScript

from ieml.dictionary.script.tools import factorize


def find_and_add_script_to_current_version(to_find):
    t = reversed(get_available_dictionary_version())
    for version in t:
        version.load()
        if to_find in version.terms:
            version = create_dictionary_version(merge=[version])
            version.upload_to_s3()
            break

"""
s.-S:.U:.-'l.-S:.O:.-'n.-S:.U:.-',+M:.-'M:.-'n.-S:.U:.-',  => n.-S:.U:.-'s.-S:.U:.-'l.-S:.O:.-',+n.-S:.U:.-‘M:.-‘M:.-‘,   (continents)
M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_    =>     n.-S:.U:.-’S:.-’B:.-‘,M:.-‘,M:.-‘,_   (Pays Européens)
M:.-',M:.-',S:.-'S:.-'n.-S:.U:.-',_    =>     n.-S:.U:.-’S:.-’S:.-‘,M:.-‘,M:.-‘,_   (Pays d’Amérique du Nord)
M:.-',M:.-',B:.-'S:.-'n.-S:.U:.-',_    =>     n.-S:.U:.-’B:.-’S:.-‘,M:.-‘,M:.-‘,_  (Pays d’Amérique centrale et des Caraïbes)
M:.-',M:.-',T:.-'S:.-'n.-S:.U:.-',_    =>     n.-S:.U:.-’T:.-’S:.-‘,M:.-‘,M:.-‘,_   (Pays d’Amérique du Sud)
1 Comment

Pour avoir le VIDE en substance et donner une étymologie aux auxiliaires qui n’en n’ont pas
E:O:.M:O:.-  => E:.O:.M:O:.- (pour récupérer l’étymologie avec le vide en substance)
E:M:.M:O:.-  => E:.M:.M:O:.-  (idem)
E:F:.O:O:.- => E:.F:.O:O:.- (idem)
E:F:.O:M:.t.- => E:.-F:.O:M:.-t.-‘  (changement de couche)
E:F:.M:M:.l.- => E:.-F:.M:M:.-l.-‘   (changement de couche)
E:O:.-M:O:.-t.o.-' => E:.-O:.M:O:.-t.o.-‘
Pour donner une étymologie aux verbes qui n’en n’ont pas
O:O:.O:O:.-  => O:O:.O:O:.t.-
O:O:.F:.- => O:O:.f.F:.-
noms
i.B:.-+u.M:.-O:.-' => i.f.B:.-+u.f.M:.-O:.-‘  (pour tenir compte du changement précédent)
M:.-O:.-'M:.-wa.e.-'t.x.-s.y.-',  => M:.-O:.-'M:.-wa.e.-'t.-x.-s.y.-', (Pour réparer une erreur)
"""


def _rotate_sc(s):
    subst, attr, mode = s
    return m(mode, subst, attr)


def _rotate_sc_additive(s):
    """
    s.-S:.U:.-'l.-S:.O:.-'n.-S:.U:.-',+M:.-'M:.-'n.-S:.U:.-',  =>
    n.-S:.U:.-'s.-S:.U:.-'l.-S:.O:.-',+n.-S:.U:.-‘M:.-‘M:.-‘,"""

    if isinstance(s, AdditiveScript):
        return AdditiveScript([_rotate_sc(_s) for _s in s])
    else:
        return _rotate_sc(s)


def _double_rotate(s):
    subst, attr, mode = s
    mode = _rotate_sc(mode)
    return m(mode, subst, attr)


def _split_subst(s):
    subst, attr, mode = s
    assert isinstance(mode, NullScript)
    subst0, subst1, mode = subst
    assert isinstance(mode, NullScript)

    return m(m(subst0), m(subst1), attr)

def _promote_and_split(s):
    """
    E:F:.O:M:.t.- => E:.-F:.O:M:.-t.-‘
    E:F:.M:M:.l.- => E:.-F:.M:M:.-l.-‘
    """
    subst, attr, mode = s
    subst0, subst1, _mode = subst
    assert isinstance(_mode, NullScript)

    return m(m(m(subst0)) ,m(m(subst1), attr) ,m(mode))

def _transfer_substance(s):
    """
    E:O:.-M:O:.-t.o.-' => E:.-O:.M:O:.-t.o.-‘
    """
    subst, attr, mode = s
    attr0, attr1, attr2 = attr
    assert isinstance(attr1, NullScript) and isinstance(attr2, NullScript)
    subst, subst1, subst2 = subst
    assert isinstance(subst1, NullScript) and isinstance(subst2, NullScript)

    subst0, subst1, subst2 = subst
    assert isinstance(subst2, NullScript)
    return m(m(m(subst0)), m(m(subst1), attr0), mode)

"""
 (Pour réparer une erreur)
"""
def _add_mode_t(s):
    """
O:O:.O:O:.-  => O:O:.O:O:.t.-
    """
    subst, attr, mode = s
    assert isinstance(mode, NullScript)
    return m(subst, attr, script('t.'))

def _insert_attr_f(s):
    """O:O:.F:.- => O:O:.f.F:.-"""
    subst, attr, mode = s
    assert isinstance(mode, NullScript)
    return m(subst, script('f.'), attr)

def _insert_f_additive(s):
    """i.B:.-+u.M:.-O:.-' => i.f.B:.-+u.f.M:.-O:.-'"""
    subst, attr, mode = s
    assert isinstance(mode, NullScript)

    if isinstance(subst, AdditiveScript):
        subst = AdditiveScript([_insert_attr_f(_s) for _s in subst])
    else:
        subst = _insert_attr_f(subst)

    return m(subst ,attr)

def _fix_typo(s):
    """M:.-O:.-'M:.-wa.e.-'t.x.-s.y.-',  => M:.-O:.-'M:.-wa.e.-'t.-x.-s.y.-',"""
    subst, attr, mode = s
    return m(subst, attr, script("t.-x.-s.y.-'"))

to_translate = {
    "s.-S:.U:.-'l.-S:.O:.-'n.-S:.U:.-',+M:.-'M:.-'n.-S:.U:.-',": _rotate_sc_additive,
    "M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_": _double_rotate,
    "M:.-',M:.-',S:.-'S:.-'n.-S:.U:.-',_": _double_rotate,
    "M:.-',M:.-',B:.-'S:.-'n.-S:.U:.-',_": _double_rotate,
    "M:.-',M:.-',T:.-'S:.-'n.-S:.U:.-',_": _double_rotate,
    "E:O:.M:O:.-": _split_subst,
    "E:M:.M:O:.-": _split_subst,
    "E:F:.O:O:.-": _split_subst,
    "E:F:.O:M:.t.-": _promote_and_split,
    "E:F:.M:M:.l.-": _promote_and_split,
    "E:O:.-M:O:.-t.o.-'": _transfer_substance,
    "O:O:.O:O:.-": _add_mode_t,
    "O:O:.F:.-": _insert_attr_f,
    "i.B:.-+u.M:.-O:.-'":_insert_f_additive,
    "M:.-O:.-'M:.-wa.e.-'t.x.-s.y.-',":_fix_typo
}

result = {
    "s.-S:.U:.-'l.-S:.O:.-'n.-S:.U:.-',+M:.-'M:.-'n.-S:.U:.-',": "n.-S:.U:.-'s.-S:.U:.-'l.-S:.O:.-',+n.-S:.U:.-'M:.-'M:.-',",
    "M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_": "n.-S:.U:.-'S:.-'B:.-',M:.-',M:.-',_",
    "M:.-',M:.-',S:.-'S:.-'n.-S:.U:.-',_": "n.-S:.U:.-'S:.-'S:.-',M:.-',M:.-',_",
    "M:.-',M:.-',B:.-'S:.-'n.-S:.U:.-',_": "n.-S:.U:.-'B:.-'S:.-',M:.-',M:.-',_",
    "M:.-',M:.-',T:.-'S:.-'n.-S:.U:.-',_": "n.-S:.U:.-'T:.-'S:.-',M:.-',M:.-',_",
    "E:O:.M:O:.-": "E:.O:.M:O:.-",
    "E:M:.M:O:.-": "E:.M:.M:O:.-",
    "E:F:.O:O:.-": "E:.F:.O:O:.-",
    "E:F:.O:M:.t.-": "E:.-F:.O:M:.-t.-'",
    "E:F:.M:M:.l.-": "E:.-F:.M:M:.-l.-'",
    "E:O:.-M:O:.-t.o.-'": "E:.-O:.M:O:.-t.o.-'",
    "O:O:.O:O:.-": "O:O:.O:O:.t.-",
    "O:O:.F:.-": "O:O:.f.F:.-",
    "i.B:.-+u.M:.-O:.-'": "i.f.B:.-+u.f.M:.-O:.-'",
    "M:.-O:.-'M:.-wa.e.-'t.x.-s.y.-',": "M:.-O:.-'M:.-wa.e.-'t.-x.-s.y.-',"
}


# def _test_rules():
#     for s, r in to_translate.items():
#         if str(r(script(s))) != result[s]:
#             print("error for %s != %s"%(str(r(script(s))), result[s]))


def translate_script(to_translate):
    """
    translate the root paradigms in key in argument, with the function in value
    :param to_translate:
    :return:
    """
    version = DictionaryVersion(latest_dictionary_version())
    version.load()
    to_remove = []
    to_add = {
        'terms': [],
        'roots': [],
        'inhibitions': {},
        'translations': {l: {} for l in LANGUAGES}
    }

    for root, func in to_translate.items():
        root = script(root)
        terms = list(filter(lambda s: s in root, map(script, version.terms)))

        new_root = func(root)
        new_terms = [func(s) for s in terms]

        to_add['terms'].extend(map(str, new_terms))
        to_add['roots'].append(str(new_root))
        to_add['inhibitions'].update({str(new_root): version.inhibitions[root]})
        for l in LANGUAGES:
            to_add['translations'][l].update({str(func(s)): version.translations[l][s] for s in terms})

        to_remove.extend(map(str, terms))

    return create_dictionary_version(version, add=to_add, remove=to_remove)

"""
s.-S:.U:.-'l.-S:.O:.-'n.-T:.A:.-',+M:.-'M:.-'n.-T:.A:.-',
s.-S:.U:.-'n.-T:.A:.-'l.-S:.O:.-',+n.-T:.A:.-'M:.-'M:.-',
"""
def translate_ocean(s):
    if s in script("M:.-'M:.-'n.-T:.A:.-',"):
        return _rotate_sc(s)
    elif s in script("s.-S:.U:.-'l.-S:.O:.-'n.-T:.A:.-',"):
        subst, attr, mode = s
        return m(subst, mode, attr)
    elif isinstance(s, AdditiveScript):
        return AdditiveScript(children=[translate_ocean(c) for c in s])


def translate_body_parts(s):
    def _level_3(s):
        s2, a2, m2 = s
        s1, a1, m1 = a2
        return m(s2, m(s1, m(a1.children[0], m1.children[0])), m2)

    s4, a4, _ = s
    s3, a3, _ = a4
    return m(s4, m(_level_3(s3), _level_3(a3)))


body_parts = {
    "f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:.T:.-l.-'E:.-A:.M:.T:.-l.-',_" : "f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:.T:.-l.-'E:.-A:.M:.T:.-l.-',_" : "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
}
to_translate_body = {
        "f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:.T:.-l.-'E:.-A:.M:.T:.-l.-',_": translate_body_parts,
        "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:.T:.-l.-'E:.-A:.M:.T:.-l.-',_": translate_body_parts
    }


body_parts_root = factorize(list(map(script, [
    "f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_"
])))


def upload_to_s3(dictionary_version):
    s3 = boto3.resource('s3')
    bucket_name = 'ieml-dictionary-versions'
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object("%s.json" % str(dictionary_version))

    obj.upload_fileobj(io.BytesIO(bytes(dictionary_version.json(), 'utf-8')))
    obj.Acl().put(ACL='public-read')

    assert dictionary_version in get_available_dictionary_version()

animals_and_vegetebals = {"B:.S:.n.-k.-+n.-n.S:.U:.-+n.B:.U:.-+n.T:.A:.-'+B:.B:.n.-k.-+n.-u.S:.-+u.B:.-+u.T:.-'":
                          "B:.S:.n.-B:S:+T:.-n.T:.A:.-+n.S:+B:.U:.-'+     B:.B:.n.-B:S:+T:.-u.M:.-'"}

def factorize_root(root):
    factorized_root = factorize(root.script)

    to_remove = []
    to_add = {
        'terms': [],
        'roots': [str(factorized_root)],
        'inhibitions': {
            str(factorized_root): root.inhibitions
        },
        'translations': {
            'fr': {},
            'en': {}
        }
    }

    for t in Dictionary().roots[root]:
        to_remove.append(str(t.script))
        s = factorize(t.script)
        to_add['terms'].append(str(s))
        to_add['translations']['fr'][str(s)] = t.translations.fr
        to_add['translations']['en'][str(s)] = t.translations.en

    return to_remove, to_add

def _remove_attr_f(s):
    """O:O:.f.F:.- -> O:O:.F:.- """
    subst, attr, mode = s
    return m(subst, mode)


def translate_mouvements_et_milieux(s):
    """i.f.B:.-+u.f.M:.-O:.-' -> i.B:.-+u.M:.-O:.-'"""
    subst, attr, mode = s
    assert isinstance(mode, NullScript)

    if isinstance(subst, AdditiveScript):
        subst = AdditiveScript([_remove_attr_f(_s) for _s in subst])
    else:
        subst = _remove_attr_f(subst)

    return m(subst, attr)


def translate_competence_en_curr_data(s):
    """M:.-O:.-'M:.-wa.e.-'t.-x.-s.y.-',  => t.-x.-s.y.-' wa.e.-', M:M:.-',O:.-',_"""
    subst, attr, mode = s
    attr_s, attr_a, attr_m = attr
    assert isinstance(attr_m, NullScript)

    subst_s, subst_a, subst_m = subst
    assert isinstance(subst_m, NullScript)
    first_M = subst_s.children[0].children[0]

    return m(m(mode, m(attr_a)), m(m(m(m(first_M, attr_s.children[0].children[0])))), m(m(subst_a)))

def get_competence_en_curr_data_diff():
    update = {}
    remove = []
    for t in term("M:.-O:.-'M:.-wa.e.-'t.-x.-s.y.-',").relations.contains:
        if len(t) == 1 or len(t) == 2 or len(t) == 18:
            update[str(t.script)] = str(translate_competence_en_curr_data(t.script))
        else:
            remove.append(str(t.script))
    return update, remove

def translate_noetic(s):
    """M:.O:.-O:.O:.-B:.T:.n.-' => s.M:O:.O:O:.-"""
    subst, attr, mode = s
    return m(script('s.'),
             m(subst.children[0].children[0], subst.children[1].children[0]),
             m(attr.children[0].children[0], attr.children[1].children[0]))


def translate_tisse_intl_col(s):
    """O:M:.-O:M:.-we.h.-' => O:M:.-'O:M:.-'s.o.-k.o.-',"""
    subst, attr, mode = s
    return m(m(subst), m(attr), script("s.o.-k.o.-'"))


def translate_formes_visuelles(s):
    """s.u.-'O:M:.-'O:.-',+s.u.-'M:O:.-O:.-'M:.-', => b.-S:.U:.-'O:M:.-'O:.-', + b.-S:.U:.-'M:O:.-O:.-'M:.-',"""

    def set_bSU_subst(s):
        subst, attr, mode = s
        return m(script("b.-S:.U:.-'"), attr, mode)

    if isinstance(s, AdditiveScript):
        return AdditiveScript([set_bSU_subst(i) for i in s.children])
    else:
        return set_bSU_subst(s)


def translate_update(root, f):
    update = {'terms':
                  {str(s.script): str(f(s.script)) for s in term(root).relations.contains}
              }
    version = create_dictionary_version(latest_dictionary_version(), update=update)
    upload_to_s3(version)
    print(version)


def translate_ecosystem_intl_col(s):
    """O:.M:.- => s.o.-k.o.-'M:O:.-',"""
    subst, attr, mode = s

    return m(script("s.o.-k.o.-'"), m(m(m(attr.children[0], subst.children[0]))))


def translate_ecosystem_intl_col_tern(s):
    """O:.M:.-M:.-' => s.o.-k.o.-‘M:O:.-‘,M:.-',_"""
    subst, attr, mode = s

    return m(translate_ecosystem_intl_col(subst), m(m(attr)))

if __name__ == "__main__":
    # to_add = {
    #     'terms': ["f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    #               "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    #               "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_",
    #               "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_+f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    #               "f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_"
    #              ],
    #     'roots': ["f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_+f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_"],
    #     'inhibitions': {
    #          "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_+f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": ['father_mode']
    #     },
    #     'translations': {
    #         'fr': {
    #             "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_+f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "Parties du corps",
    #             "f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "Parties du corps: le tronc",
    #             "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "Parties du corps: la tête",
    #             "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_": "Parties du corps: membres",
    #             "f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "Parties du corps: la tête et le tronc"
    #         },
    #         'en': {
    #             "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_+f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "body parts",
    #             "f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "Body parts: trunk",
    #             "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "Body parts: head",
    #             "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_": "body parts: limbs",
    #             "f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_": "Body parts: head and trunk"
    #
    #         }
    #     }
    # }
    # to_remove = ["f.o.-f.o.-'E:.-U:.n.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    #               "f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_",
    #               "f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_"
    # ]

    # to_remove, to_add = factorize_root(term("b.i.-n.i.-'l.i.-n.i.-'+m.+l.i.-f.i.-'+wu.f.A:.-+a.S:.-+i.U:.-+e.O:.-+S:+T:T:.i.-'n.o.-n.o.-'+f.o.-f.o.-'+n.-B:.A:.-+S:+B:.U:.-',"))
    #
    #
    # version = create_dictionary_version(latest_dictionary_version(),
    #                           add=to_add, remove=to_remove)
    # upload_to_s3(version)
    # print(version)
    # update = {str(s.script): str(translate_mouvements_et_milieux(s.script)) for s in term("i.f.B:.-+u.f.M:.-O:.-'").relations.contains}
    # version = create_dictionary_version(latest_dictionary_version(), update=update)
    # upload_to_s3(version)
    # print(version)
    # _up, _rem = get_competence_en_curr_data_diff()
    # update = {'terms': {
    #         **{str(s.script): str(translate_mouvements_et_milieux(s.script)) for s in term("i.f.B:.-+u.f.M:.-O:.-'").relations.contains},
    #         **_up
    #     },
    #     'remove': {
    #         *_rem
    #     }
    # }
    # print('\n'.join("{} => {}".format(a, b) for a, b in _up.items()))
    # version = create_dictionary_version(latest_dictionary_version(), update=update, remove=_rem)
    # upload_to_s3(version)
    # print(version)

    root = "O:.M:.-M:.-'"
    translator = translate_ecosystem_intl_col_tern
    "dictionary_2018-06-08_17:07:06"
    print(str(translator(script(root))))

    d = Dictionary("dictionary_2018-06-08_17:07:06")
    # translate_update("s.u.-'O:M:.-'O:.-',+s.u.-'M:O:.-O:.-'M:.-',", translate_formes_visuelles)
    diff = {
        **{str(s.script): str(translate_competence_en_curr_data(s.script)) for s in term("M:.-O:.-'M:.-wa.e.-'t.-x.-s.y.-',", d).relations.contains},
        # **{str(s.script): str(translate_ecosystem_intl_col_tern(s.script)) for s in term("O:.M:.-M:.-'", d).relations.contains},
    }
    import json
    print(json.dumps(diff, indent=True))

    version = create_dictionary_version(None, diff=diff)
    # upload_to_s3(version)
    print(version)