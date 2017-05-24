import queue

from handlers.commons import exception_handler
from handlers.dictionary.client import need_login
from handlers.dictionary.commons import relation_name_table, relations_order

from ieml.exceptions import CannotParse
from ieml.ieml_objects.dictionary import RELATION_TYPES_TO_INDEX
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.tools import term
from ieml.script.operator import sc

from multiprocessing import Process, Queue, active_children

def get_relation_visibility(body):
    try:
        print("get_relation_visibility")
        _term = term(body["ieml"])
        inhibited_relations = [relation_name_table.inv[rel_name] for rel_name in _term.inhibitions]
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
    except DBException as e:
        q.put(str(e))

# relation computing process, used by computation_status to get the error message.
relation_compute_process_queue = None

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
                global relation_compute_process_queue
                relation_compute_process_queue = q
                return {'success': True}


@exception_handler
def computation_status():
    status = RelationsConnector().lock_status()
    response = {'success': True, 'free': status is None}
    if status is not None:
        response['computing_relations'] = status['role'] == RELATION_COMPUTING

    # get the error message if there is one
    global relation_compute_process_queue
    if status is None and relation_compute_process_queue is not None:
        if not relation_compute_process_queue.empty():
            try:
                response['error_message'] = relation_compute_process_queue.get_nowait()
            except queue.Empty:
                pass

        relation_compute_process_queue = None

    return response


# @exception_handler
def get_relations(body):
    t = term(body["ieml"])

    relations = list(t.relations)
    _relations = []
    for l in relations:
        if l == [] or isinstance(l[0], Term):
            _relations.append(l)
        else:
            _relations.extend(l)

    all_relations = [
        {
            "reltype": relation_name_table.inv[RELATION_TYPES_TO_INDEX.inv[i]],
            "rellist": [
                {
                    "exists": True,
                    "visible": True,
                    "ieml": str(r.script)
                } for r in reversed(rels)
            ],
            "exists": True,
            "visible": True
        } for i, rels in enumerate(_relations) if rels != []
    ]

    all_relations.append({
        "reltype": relation_name_table.inv['ROOT'],
        "rellist": [
            {
                "exists": True,
                "visible": True,
                "ieml": str(t.root.script)
            }],
        "exists": True,
        "visible": True
    })

    # for relation_type, relations in RelationsQueries.relations(script_ast, pack_ancestor=True, max_depth_child=1).items():
    #     if relations: # if there aren't any relations, we skip
    #         if relation_type != "ROOT":
    #             relations_list = sorted([{"ieml" : rel,
    #                       "exists": True,
    #                       "visible": True}
    #                      for rel in relations], key=lambda s: sc(s['ieml']), reverse=True)
    #         else:
    #             relations_list = [{"ieml": relations,
    #                   "exists": True,
    #                   "visible": True}]
    #
    #         all_relations.append({
    #             "reltype": relation_name_table.inv[relation_type],
    #             "rellist": relations_list,
    #             "exists": True,
    #             "visible": True
    #         })
    return sorted(all_relations, key=lambda rel_entry: relations_order[rel_entry['reltype']])
