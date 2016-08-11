import os
import queue

from bidict import bidict

from handlers.dictionary.client import need_login
from handlers.dictionary.commons import terms_db, exception_handler, relation_name_table
from ieml.exceptions import CannotParse
from ieml.operator import sc
from models.constants import RELATION_COMPUTING
from models.exceptions import CollectionAlreadyLocked
from models.relations.relations import RelationsConnector
from models.relations.relations_queries import RelationsQueries
from multiprocessing import Process, Queue, active_children

def get_relation_visibility(body):
    try:
        script_ast = sc(body["ieml"])
        term_db_entry = terms_db().get_term(script_ast)
        inhibited_relations = [relation_name_table.inv[rel_name] for rel_name in term_db_entry["INHIBITS"]]
        return {"viz": inhibited_relations}
    except CannotParse:
        pass


def _compute_relations(q):
    try:
        terms_db().recompute_relations(all_delete=True)
    except CollectionAlreadyLocked as e:
        if e.role == RELATION_COMPUTING:
            q.put("The relation computation of the database is already performing.")
        else:
            q.put("The relation collection is used by another process, retry later.")


@need_login
@exception_handler
def update_relations(body):
    q = Queue()
    # no effect just join terminated proccess.
    active_children()

    p = Process(target=_compute_relations, args=(q,))
    p.start()
    while True:
        try:
            error_message = q.get(timeout=1)
            p.join()
            return {'success': False, 'message': error_message}
        except queue.Empty:
            lock_status = RelationsConnector().lock_status()
            if lock_status is not None and lock_status['pid'] == p.pid:
                return {'success': True}

@exception_handler
def computation_status():
    status = RelationsConnector().lock_status()
    response = {'success': True, 'free': status is None}
    if status is not None:
        response['computing_relations'] = status['role'] == RELATION_COMPUTING

    return response


@exception_handler
def get_relations(term):
    script_ast = sc(term["ieml"])
    all_relations = []
    for relation_type, relations in RelationsQueries.relations(script_ast, pack_ancestor=True, max_depth_child=1).items():
        if relations: # if there aren't any relations, we skip
            all_relations.append({
                "reltype" : relation_name_table.inv[relation_type],
                "rellist" :
                    [{"ieml" : rel,
                      "exists": True,
                      "visible": True}
                     for rel in relations]
                    if relation_type != "ROOT" else
                    [{"ieml": relations,
                      "exists": True,
                      "visible": True}],
                "exists" : True,
                "visible" : True
            })
    return all_relations