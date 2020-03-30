import csv
import enum
import json
import operator
from io import StringIO
from typing import Dict, List

import pandas
from collections import defaultdict
from functools import reduce

from ieml.constants import LANGUAGES, STRUCTURE_KEYS, INHIBITABLE_RELATIONS, DESCRIPTORS_CLASS
from ieml.usl.parser import USLParser


def normalize_key(ieml, key, value, parse_ieml=False, partial=False, structure=False):
    if not (partial or (ieml is not None and key and (structure or value))):
        raise ValueError("IEML and Key can't be null")

    if ieml:
        ieml = str(ieml)
        if parse_ieml:
            parsed = USLParser().parse(str(ieml))
            ieml = str(parsed)
            # if ieml != str(parsed):
            #     raise ValueError("IEML is not normalized: {}".format(ieml))

            # if len(parsed) == 1 and structure:
            #     raise ValueError("Only paradigms can have a structure: {}".format(ieml))

    if structure:
        if key:
            key = str(key)
            if key not in STRUCTURE_KEYS:
                raise ValueError("Unsupported structure key: '{}'".format(str(key)))

        if value:
            if key and key == 'inhibition':
                value = str(value)
                if value not in INHIBITABLE_RELATIONS:
                    raise ValueError("Unsupported inhibition: {}".format(value))

            if key and key in ['is_root', 'is_ignored']:
                value = json.loads(str(value).lower())
                if not isinstance(value, bool):
                    raise ValueError("is_root or is_ignored field only accept boolean, not {}".format(value))
                value = str(value)
    else:
        if key:
            key = str(key)
            if key not in LANGUAGES:
                raise ValueError("Unsupported language: '{}'".format(str(key)))

        if value:
            value = str(value)
            if value not in DESCRIPTORS_CLASS:
                raise ValueError("Unsupported descriptor: '{}'".format(str(value)))

    return ieml, key, value


class Languages(enum.Enum):
    FR = 'fr'
    EN = 'en'

class DescriptorsType(enum.Enum):
    TRANSLATIONS = 'translations'
    TAGS = 'tags'
    COMMENTS = 'comments'


Descriptor = Dict[DescriptorsType, Dict[Languages, List[str]]]

class Descriptors:
    def __init__(self, df):
        assert list(df.columns) == ['ieml', 'language', 'descriptor', 'value']
        self.df = df.set_index(['ieml', 'language', 'descriptor']).sort_index()

    # @monitor_decorator('get_values')
    def get_values(self, ieml, language, descriptor):
        ieml, language, descriptor = normalize_key(ieml, language, descriptor,
                                                   parse_ieml=False, partial=False)
        try:
            res = self.df.loc(axis=0)[(str(ieml), language, descriptor)]
            if isinstance(res, pandas.Series):
                return res.to_list()
            else:
                return res.to_dict('list')['value']
        except KeyError:
            return []

    # @monitor_decorator('get_values_partial')
    def get_values_partial(self, ieml, language=None, descriptor=None):
        ieml, language, descriptor = normalize_key(ieml, language, descriptor,
                                                   parse_ieml=False, partial=True)

        key = {'ieml': ieml, 'language': language, 'descriptor': descriptor}
        key = reduce(operator.and_,
                     [self.df.index.get_level_values(k) == v for k, v in key.items() if v is not None],
                     True)

        res = defaultdict(list)
        for k, (v,) in self.df[key].iterrows():
            res[k].append(v)

        return dict(res)

    def get_descriptor(self, ieml) -> Descriptor:
        res = {d : {l: [] for l in LANGUAGES} for d in DESCRIPTORS_CLASS}

        for (_ieml, lang, desc), value in self.get_values_partial(ieml).items():
            assert ieml == _ieml
            res[desc][lang] = value

        return res

    @staticmethod
    def from_csv_string(s, assert_unique_ieml=False):
        ours_data = StringIO(s)
        csv_reader = csv.reader(ours_data, delimiter=' ', quotechar='"')
        desc = defaultdict(lambda :{d: {l: [] for l in LANGUAGES} for d in DESCRIPTORS_CLASS})
        for (_ieml, _lang, _desc, value) in csv_reader:
            desc[_ieml][_desc][_lang].append(value)

        if assert_unique_ieml and len(desc) != 1:
            raise ValueError("Multiple IEML in csv string")

        return dict(desc)