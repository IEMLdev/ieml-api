from ieml.parsing.script.parser import ScriptParser
from .commons import terms_db

script_parser = ScriptParser()

def all_ieml():
    def _build_old_model_from_term_entry(term_db_entry):
        terms_ast = script_parser.parse(term_db_entry["_id"])
        return {"_id" : term_db_entry["_id"],
                "IEML" : term_db_entry["_id"],
                "CLASS" : "1", # TODO : cannot compute that
                "EN" : term_db_entry["TAGS.EN"],
                "FR" : term_db_entry["TAGS.FR"],
                "PARADIGM" : "1" if term_db_entry["ROOT"] else "0",
                "LAYER" : terms_ast.layer,
                "TAILLE" : terms_ast.cardinal,
                "CANONICAL" : terms_ast.canonical
                }

    return [_build_old_model_from_term_entry(entry) for entry in terms_db]


def parse_ieml(iemltext):
    pass


def script_table(iemltext):
    pass


def script_tree(iemltext):
    pass


def new_ieml_script():
    pass


def remove_ieml_script(term_id):
    pass

def update_ieml_script():
    pass

def ieml_term_exists(ieml_term):
    pass

def en_tag_exists(tag_en):
    pass

def fr_tag_exists(tag_fr):
    pass