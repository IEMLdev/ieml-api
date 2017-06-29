import hashlib

import bidict
import jwt
from django.utils.encoding import smart_text
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.views import APIView
from rest_framework_mongoengine import viewsets as mongoviewsets
from rest_framework import viewsets, permissions
from rest_framework import status
from rest_framework.utils import formatting
from rest_framework.decorators import detail_route, api_view
from mongoengine.queryset.visitor import Q
from rest_framework.response import Response

from ieml.commons import LANGUAGES
from ieml.exceptions import CannotParse
from ieml.ieml_objects.terms.distance import ranking_from_term
from ieml.ieml_objects.terms.tools import term
from ieml.ieml_objects.terms.version import get_available_dictionary_version, create_dictionary_version, \
    DictionaryVersion
from ieml.ieml_objects.terms import Dictionary
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS
from ieml.script.operator import sc
from ieml.script.tools import factorize
from models.logins.logins import is_user

from . import serializers
from .models import Feedback

def _build_old_model_from_term_entry(t):
    return {
        "_id": str(t.script),
        "IEML": str(t.script),
        "CLASS": t.grammatical_class,
        "EN": t.translations['en'],
        "FR": t.translations['fr'],
        "PARADIGM": "1" if t.script.paradigm else "0",
        "LAYER": t.script.layer,
        "TAILLE": t.script.cardinal,
        "ROOT_PARADIGM": t.root == t,
        "RANK": t.rank,
        "INDEX": t.index
    }


def get_modelview_description(model, html=False):
    description = model.__doc__
    description = formatting.dedent(smart_text(description))
    if html:
        return formatting.markup_description(description)
    return description


class FeedbackViewSet(mongoviewsets.ModelViewSet):
    lookup_field = 'id'
    serializer_class = serializers.FeedbackSerializer
    base_name = "feedback"

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(Feedback, html=html)

    def get_queryset(self):
        if 'term_src' in self.kwargs:
            return Feedback.objects.filter(Q(term_src=self.kwargs['term_src']) | Q(term_dest=self.kwargs['term_src']))
        else:
            return Feedback.objects.all()


@api_view(['GET'])
def get_dictionary_version(request, format=None):
    return Response(str(sorted(get_available_dictionary_version())[-1]))


@api_view(['GET'])
def all_ieml(request, format=None):
    """Returns a dump of all the terms contained in the DB, formatted for the JS client"""
    result = [{
        "_id": str(t.script),
        "IEML": str(t.script),
        "CLASS": t.grammatical_class,
        "EN": t.translations['en'],
        "FR": t.translations['fr'],
        "PARADIGM": "1" if t.script.paradigm else "0",
        "LAYER": t.script.layer,
        "TAILLE": t.script.cardinal,
        "ROOT_PARADIGM": t.root == t,
        "RANK": t.rank,
        "INDEX": t.index
    } for t in Dictionary(request.query_params.get('version', None))]

    return Response(result)

relation_name_table = bidict.bidict({
    "Crossed siblings": "crossed",
    "Associated siblings": "associated",
    "Twin siblings": "twin",
    "Opposed siblings": "opposed",

    # ancestor : Etymology
    "Ancestors in mode": "father_mode",
    "Ancestors in attribute": "father_attribute",
    "Ancestors in substance": "father_substance",

    "Descendents in mode": "child_mode",
    "Descendents in attribute": "child_attribute",
    "Descendents in substance": "child_substance",

    # Hyperonymes
    "Contained in": "contained",
    "Belongs to Paradigm": 'ROOT',
    # Hyponymes
    "Contains": "contains"
})
relations_order = {
    "Crossed siblings": 4,
    "Associated siblings": 2,
    "Twin siblings": 3,
    "Opposed siblings": 1,

    # ancestor : Etymologie
    "Ancestors in mode": 12,
    "Ancestors in attribute": 11,
    "Ancestors in substance": 10,

    "Descendents in mode": 9,
    "Descendents in attribute": 8,
    "Descendents in substance": 7,

    # Hyperonymes
    "Contained in": 6,
    "Belongs to Paradigm": 0,
    # Hyponymes
    "Contains": 5
}


@api_view(['GET'])
def rels(request, format=None):
    t = Dictionary(request.query_params.get('version', None)).terms[request.query_params.get('ieml', None)]

    all_relations = [
        {
            "reltype": rel_api,
            "rellist": [
                {
                    "exists": True,
                    "visible": True,
                    "ieml": str(r.script)
                } for r in reversed(t.relations[reltype])
            ],
            "exists": True,
            "visible": True
        } for rel_api, reltype in relation_name_table.items() if reltype != 'ROOT' and t.relations[reltype] != ()
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
    return Response(sorted(all_relations, key=lambda rel_entry: relations_order[rel_entry['reltype']]))


@api_view(['GET'])
def script_table(request, format=None):
    class_to_color = {
        AUXILIARY_CLASS: 'auxiliary',
        VERB_CLASS: 'verb',
        NOUN_CLASS: 'noun'
    }

    class_to_header_color = {k: 'header-'+class_to_color[k] for k in class_to_color}

    def _table_entry(col_size=0, ieml=None, header=False, top_header=False):
        '''
        header + ieml + !top_header = colomn and line header
        header + ieml + top_header = top header
        !ieml + top_header = gray square -_-'
        ieml + !header = cell

        :param ieml:
        :param auto_color:
        :param header:
        :param top_header:
        :return:
        '''
        if not ieml:
            color = 'black'
        elif not header:
            color = class_to_color[ieml.script_class]
        else:
            color = class_to_header_color[ieml.script_class]

        return {
            'background': color,
            'value': str(ieml) if ieml else '',
            'means': {'fr': '', 'en': ''},
            'creatable': False,
            'editable': bool(ieml),
            'span': {
                'col': col_size if header and top_header and ieml else 1,
                'row': 1
            }
        }

    def _slice_array(tab, dim):
        shape = tab.cells.shape
        if dim == 1:
            result = [
                _table_entry(1, ieml=tab.paradigm, header=True, top_header=True)
            ]
            result.extend([_table_entry(ieml=e) for e in tab.paradigm.singular_sequences])
        else:
            result = [
                _table_entry(shape[1] + 1, ieml=tab.paradigm, header=True, top_header=True),
                _table_entry(top_header=True)  # grey square
            ]

            for col in tab.columns:
                result.append(_table_entry(ieml=col, header=True))

            for i, line in enumerate(tab.cells):
                result.append(_table_entry(ieml=tab.rows[i], header=True))
                for cell in line:
                    result.append(_table_entry(ieml=cell))

        return result

    def _build_tables(tables):
        result = []
        for table in tables:
            tabs = []

            for i, tab in enumerate(table.headers):
                tabs.append({
                    'tabTitle': str(tab),
                    'slice': _slice_array(table.headers[tab], dim=table.dim)
                })

            result.append({
                'Col': len(table.headers[tab].columns) + 1 if table.dim != 1 else 1,
                'table': tabs,
                'dim': table.dim
            })

        return result

    try:
        s = sc(request.query_params.get('ieml', None))
        tables = s.tables

        if tables is None:
            raise ValueError("Not enough variable")

        return Response({
            'tree': {
                'input': str(s),
                'Tables': _build_tables(tables)
            },
            'success': True
        })
    except CannotParse:
        pass


@api_view(['GET'])
def get_ranking_from_term(request, format=None):
    _tt = term(request.query_params.get('ieml', None), dictionary=Dictionary(request.query_params.get('version', None)))

    return Response([{
        'ieml': str(t[1].script),
        'ranking': t[0],
        'relations': _tt.relations.to(t[1], relations_types=['inclusion', 'etymology', 'siblings', 'table'])
    } for t in ranking_from_term(_tt, nb_terms=30) if t[0] != 0.0])


@api_view(['GET'])
def get_rel_visibility(request, format=None):
    ieml = request.query_params.get('ieml', None)
    version = request.query_params.get('version', None)
    t = term(ieml, dictionary=version)
    return Response([relation_name_table.inv[rel] for rel in t.inhibitions])


@api_view(['GET'])
def ieml_term_exists(request, format=None):
    ieml = request.query_params.get('id', None)
    version = request.query_params.get('version', None)
    t = sc(ieml)
    if t in Dictionary(version):
        return Response([str(t)])
    else:
        return Response([])


@api_view(['GET'])
def en_tag_exists(request, format=None):
    version = request.query_params.get('version', None)
    tag_en = request.query_params.get('id', None)
    return Response([tag_en] if tag_en in Dictionary(version).translations['en'].inv else [])


@api_view(['GET'])
def fr_tag_exists(request, format=None):
    version = request.query_params.get('version', None)
    tag_fr = request.query_params.get('id', None)

    return Response([tag_fr] if tag_fr in Dictionary(version).translations['fr'].inv else [])


@api_view(['GET'])
def parse_ieml(request, format=None):
    version = request.query_params.get('version', None)
    iemltext = request.query_params.get('ieml', None)

    script_ast = sc(iemltext)
    root = Dictionary(version).get_root(script_ast)
    containsSize = len([s for s in Dictionary(version).layers[script_ast.layer] if s.script in script_ast])

    return Response({
        "factorization": str(factorize(script_ast)),
        "success" : True,
        "level" : script_ast.layer,
        "taille" : script_ast.cardinal,
        "class" : script_ast.script_class,
        "rootIntersections" : [str(root.script)] if root is not None else [],
        "containsSize": containsSize
    })


def _process_inhibits(body):
    if 'INHIBITS' in body:
        try:
            inhibits = [relation_name_table[i] for i in body['INHIBITS']]
        except KeyError as e:
            raise ValueError(e.args[0])
    else:
        inhibits = []

    return inhibits


class Terms(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        version = request.query_params.get('version', None)
        body = request.data

        script_ast = sc(body["IEML"])
        to_add = {
            'terms': [str(script_ast)],
            'roots': [str(script_ast)] if body["PARADIGM"] == "1" else [],
            'inhibitions': {str(script_ast): _process_inhibits(body)} if body["PARADIGM"] == "1" else {},
            'translations': {"fr": {str(script_ast): body["FR"]},
                             "en": {str(script_ast): body["EN"]}}
        }

        if body["PARADIGM"] == "1":
            for i, ss in enumerate(script_ast.singular_sequences):
                to_add['terms'].append(str(ss))
                to_add['translations']['fr'][str(ss)] = body["FR"] + " SS (%d)"%i
                to_add['translations']['en'][str(ss)] = body["EN"] + " SS (%d)"%i

        for j, table in enumerate(script_ast.tables):
            for i, tab in enumerate(table.tabs):
                if tab.paradigm != script_ast:
                    to_add['terms'].append(str(tab.paradigm))
                    to_add['translations']['fr'][str(tab.paradigm)] = body["FR"] + " Table (%d) Tab (%d)" % (j,i)
                    to_add['translations']['en'][str(tab.paradigm)] = body["EN"] + " Table (%d) Tab (%d)" % (j,i)

        new_version = create_dictionary_version(DictionaryVersion.from_file_name(version), add=to_add)
        new_version.upload_to_s3()

        return Response({"success" : True, "added": _build_old_model_from_term_entry(term(script_ast, dictionary=new_version))})

    def delete(self, request, format=None):
        version = request.query_params.get('version', None)
        ieml = request.query_params.get('ieml', None)

        script_ast = sc(ieml)
        if script_ast.cardinal == 1:
            raise ValueError("Can't remove %s, it is a singular sequence."%str(script_ast))

        t = term(script_ast, dictionary=Dictionary(version))
        if t.root == t:
            to_remove = [str(tt.script) for tt in t.relations.contains]
        else:
            to_remove = [script_ast]

        new_version = create_dictionary_version(DictionaryVersion(version), remove=to_remove)
        new_version.upload_to_s3()

        return Response({'success': True})

    def put(self, request, format=None):
        version = request.query_params.get('version', None)
        body = request.data

        script_ast = sc(body["ID"])
        inhibits = _process_inhibits(body)

        if body["IEML"] == body["ID"]:
            # no update on the ieml only update the translations or inhibitions
            to_update = {
                'translations': {"fr": {str(script_ast): body["FR"]},
                                 "en": {str(script_ast): body["EN"]}},
            }

            if inhibits:
                to_update['inhibitions'] =  {str(script_ast): inhibits}

            to_remove = None
            to_add = None

        else:
            t = term(script_ast, dictionary=Dictionary(version))
            if script_ast.cardinal == 1 or t.root == t:
                raise ValueError("Can only update the script of a non-root paradigm.")

            to_update = None
            to_remove = [script_ast]

            new_script = sc(body["IEML"])
            to_add = {
                'terms': [str(new_script)],
                'translations': {l: {str(new_script): t.translations[l]} for l in LANGUAGES}
            }

        new_version = create_dictionary_version(DictionaryVersion(version), remove=to_remove, add=to_add, update=to_update)
        new_version.upload_to_s3()

        return Response({"success": True, "modified": _build_old_model_from_term_entry(term(body["IEML"], dictionary=new_version))})


