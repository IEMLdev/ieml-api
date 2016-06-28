from ieml.exceptions import CannotParse
from ieml.script.script import MultiplicativeScript, NullScript
from ieml.script.tools import old_canonical
from .commons import terms_db, script_parser


def all_ieml():
    """Returns a dump of all the terms contained in the DB, formatted for the JS client"""
    def _build_old_model_from_term_entry(term_db_entry):
        terms_ast = script_parser.parse(term_db_entry["_id"])
        return {"_id" : term_db_entry["_id"],
                "IEML" : term_db_entry["_id"],
                "CLASS" : "1", # TODO : cannot compute that yet
                "EN" : term_db_entry["TAGS"]["EN"],
                "FR" : term_db_entry["TAGS"]["FR"],
                "PARADIGM" : "1" if term_db_entry["ROOT"] else "0",
                "LAYER" : terms_ast.layer,
                "TAILLE" : terms_ast.cardinal,
                "CANONICAL" : old_canonical(terms_ast)
                }

    return [_build_old_model_from_term_entry(entry) for entry in terms_db.get_all_terms()]


def parse_ieml(iemltext):
    try:
        script_ast = script_parser.parse(iemltext)
        return {
            "success" : True,
            "level" : script_ast.layer,
            "taille" : script_ast.cardinal,
            "class" : 1, # TODO : change it to the actual value
            "canonical" : old_canonical(script_ast)
        }
    except CannotParse:
        return {"success" : False}


def script_table(iemltext):
    pass


def script_tree(iemltext):
    def _tree_entry(script):
        if script.layer == 0:
            return {
                'op': 'none',
                'name': str(script),
                'children': []
            }

        if isinstance(script, NullScript):
            n = NullScript(script.layer - 1)
            return {
                'op': '*',
                'name': str(script),
                'children': [
                    _tree_entry(n) for i in range(3)
                ]
            }
        return {
            'op': '*' if isinstance(script, MultiplicativeScript) else '+',
            'name': str(script),
            'children': [
                _tree_entry(s) for s in script
            ]
        }

    try:
        script = script_parser.parse(iemltext)
        return {
            'level': script.layer,
            'tree': _tree_entry(script),
            'taille': script.cardinal,
            'success': True,
            'canonical': old_canonical(script)
        }
    except CannotParse:
        pass


def new_ieml_script(body):
    try:
        script_ast = script_parser.parse(body["IEML"])
        terms_db.add_term(script_ast,  # the ieml script's ast
                          {"FR": body["FR"], "EN": body["EN"]},  # the
                          root=body["PARADIGM"] == "1")
    except CannotParse:
        pass # TODO ; maybe define an error for this case


def remove_ieml_script(term_id):
    try:
        script_ast = script_parser.parse(term_id)
        terms_db.remove_term(script_ast)
    except CannotParse:
        pass  # TODO ; maybe define an error for this case


def update_ieml_script(body):
    """Updates an IEML Term's properties (mainly the tags, and the paradigm). If the IEML is changed,
    a new term is created"""
    try:
        script_ast = script_parser.parse(body["ID"])
        if body["IEML"] == body["ID"]:
            terms_db.update_term(script_ast,
                                 tags={ "FR" : body["FR"], "EN" : body["EN"]},
                                 root= body["PARADIGM"] == "1")
        else:
            terms_db.remove_term(script_ast)
            terms_db.add_term(script_ast,  # the ieml script's ast
                              {"FR": body["FR"], "EN": body["EN"]},  # the
                              root=body["PARADIGM"] == "1")
    except CannotParse:
        pass  # TODO ; maybe define an error for this case


def ieml_term_exists(ieml_term):
    """Tries to dig a term from the database"""
    return terms_db.get_term(ieml_term)


def en_tag_exists(tag_en):
    return list(terms_db.search_by_tag(tag_en, "EN"))


def fr_tag_exists(tag_fr):
    return list(terms_db.search_by_tag(tag_fr, "FR"))
