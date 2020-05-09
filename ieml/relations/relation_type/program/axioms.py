from itertools import chain
from typing import List

from tqdm import tqdm

from ieml.dictionary import Dictionary
from ieml.relations.graph_backend.basic_backend import BasicGraphBackend
from ieml.relations.graph_backend.neo4j_backend import Neo4jGraphBackend
from ieml.relations.relation_type.program.relation_program import RelationProgram
from ieml.relations.relation_type.relation_type import *
from ieml.usl import USL, PolyMorpheme, Lexeme
from ieml.usl.usl import usl



class AxiomRelationProgram(RelationProgram):
    RELATION_TYPES = []
    def __init__(self):
        super().__init__(relation_types=self.RELATION_TYPES, dependencies=set())


class ContainsAxiomProgram(AxiomRelationProgram):
    RELATION_TYPES = [SYNTAX_RELATION_USL_PM_CONTAINS]

    def build(self, backend: Neo4jGraphBackend, usls: List[USL], dictionary: Dictionary):
        relations = set()
        for u in tqdm(filter(lambda p: p.cardinal != 1, usls), "Building USL to USL contained relationships"):
            for ss in u.singular_sequences:
                relations.add((u, ss, SYNTAX_RELATION_USL_PM_CONTAINS))

        backend.add_relations(list(relations))




class ComposedAxiomProgram(AxiomRelationProgram):
    RELATION_TYPES = [SYNTAX_RELATION_PM_CONSTANT_USL_COMPOSED,
                      SYNTAX_RELATION_PM_GROUP0_USL_COMPOSED,
                      SYNTAX_RELATION_PM_GROUP1_USL_COMPOSED,
                      SYNTAX_RELATION_PM_GROUP2_USL_COMPOSED,

                      SYNTAX_RELATION_LEX_CONTENT_USL_COMPOSED,
                      SYNTAX_RELATION_LEX_FLEXING_USL_COMPOSED,

                      SYNTAX_RELATION_SYNFUN_INITIATOR_USL_COMPOSED,
                      SYNTAX_RELATION_SYNFUN_INTERACTANT_USL_COMPOSED,
                      SYNTAX_RELATION_SYNFUN_RECEIVER_USL_COMPOSED,

                      SYNTAX_RELATION_SYNFUN_TIME_USL_COMPOSED,
                      SYNTAX_RELATION_SYNFUN_ROOT_USL_COMPOSED,
                      SYNTAX_RELATION_SYNFUN_LOCATION_USL_COMPOSED,

                      SYNTAX_RELATION_SYNFUN_MANNER_USL_COMPOSED,
                      SYNTAX_RELATION_SYNFUN_INTENTION_USL_COMPOSED,
                      SYNTAX_RELATION_SYNFUN_CAUSE_USL_COMPOSED,

                      SYNTAX_RELATION_WORD_SYNFUN_USL_COMPOSED,
                      SYNTAX_RELATION_WORD_ROLE_USL_COMPOSED,

                      SYNTAX_RELATION_MORPHEME_FATHER_SUBSTANCE_USL_COMPOSED,
                      SYNTAX_RELATION_MORPHEME_FATHER_ATTRIBUTE_USL_COMPOSED,
                      SYNTAX_RELATION_MORPHEME_FATHER_MODE_USL_COMPOSED
                      ]

    def build(self, backend: BasicGraphBackend, usls: List[USL], dictionary: Dictionary):
        relations = set()

        usls = set(filter(lambda e:e is not None,
                          set(usls) | set(chain.from_iterable(u.iter_structure(auto_promote_to_USL=True) for u in usls))))

        backend.add_nodes(list(usls))

        for u in tqdm(usls, "Building USL to USL composed relationships"):
            if isinstance(u, PolyMorpheme):
                if u.cardinal == 1 and len(u.constant) == 1:
                    pass
                else:
                    for m in u.constant:
                        relations.add((u, PolyMorpheme(constant=[m]), SYNTAX_RELATION_PM_CONSTANT_USL_COMPOSED))

                    for i, g in enumerate(u.groups):
                        reltype = [SYNTAX_RELATION_PM_GROUP0_USL_COMPOSED,
                                   SYNTAX_RELATION_PM_GROUP1_USL_COMPOSED,
                                   SYNTAX_RELATION_PM_GROUP2_USL_COMPOSED][i]
                        for m in g[0]:
                            relations.add((u, PolyMorpheme(constant=[m]), reltype))
            elif isinstance(u, Lexeme):
                if not u.pm_content.empty:
                    relations.add((u, u.pm_content, SYNTAX_RELATION_LEX_CONTENT_USL_COMPOSED))

                if not u.pm_flexion.empty:
                    relations.add((u, u.pm_flexion, SYNTAX_RELATION_LEX_FLEXING_USL_COMPOSED))
            # elif isinstance(u, SyntagmaticFunction):
            #     relations.add((u, u.actor, SYNTAX_RELATION_SYNFUN_ROOT_USL_COMPOSED))
            #
            #     if isinstance(u, ProcessSyntagmaticFunction):
            #         if u.initiator:
            #             relations.add((u, u.initiator, SYNTAX_RELATION_SYNFUN_INITIATOR_USL_COMPOSED))
            #
            #         if u.interactant:
            #             relations.add((u, u.interactant, SYNTAX_RELATION_SYNFUN_INTERACTANT_USL_COMPOSED))
            #
            #         if u.recipient:
            #             relations.add((u, u.recipient, SYNTAX_RELATION_SYNFUN_RECEIVER_USL_COMPOSED))
            #
            #         if u.time:
            #             relations.add((u, u.time, SYNTAX_RELATION_SYNFUN_TIME_USL_COMPOSED))
            #
            #         if u.location:
            #             relations.add((u, u.location, SYNTAX_RELATION_SYNFUN_LOCATION_USL_COMPOSED))
            #
            #         if u.manner:
            #             relations.add((u, u.manner, SYNTAX_RELATION_SYNFUN_MANNER_USL_COMPOSED))
            #
            #         if u.intention:
            #             relations.add((u, u.intention, SYNTAX_RELATION_SYNFUN_INTENTION_USL_COMPOSED))
            #
            #         if u.cause:
            #             relations.add((u, u.cause, SYNTAX_RELATION_SYNFUN_CAUSE_USL_COMPOSED))
            #
            # elif isinstance(u, Word):
            #     relations.add((u, u.syntagmatic_fun, SYNTAX_RELATION_WORD_SYNFUN_USL_COMPOSED))
            #     relations.add((u, u.role, SYNTAX_RELATION_WORD_ROLE_USL_COMPOSED))

        for u_s in tqdm(filter(lambda u: isinstance(u, PolyMorpheme) and u.cardinal == 1 and len(u.constant) == 1, usls), "Building Morpheme to Morpheme composed relationships"):
            s = u_s.constant[0]
            for a in dictionary.relations.object(subject=s, relation='father_substance'):
                relations.add((PolyMorpheme(constant=[s]), PolyMorpheme(constant=[a]),
                               SYNTAX_RELATION_MORPHEME_FATHER_SUBSTANCE_USL_COMPOSED))

            for a in dictionary.relations.object(subject=s, relation='father_attribute'):
                relations.add((PolyMorpheme(constant=[s]), PolyMorpheme(constant=[a]),
                               SYNTAX_RELATION_MORPHEME_FATHER_ATTRIBUTE_USL_COMPOSED))

            for a in dictionary.relations.object(subject=s, relation='father_mode'):
                relations.add((PolyMorpheme(constant=[s]), PolyMorpheme(constant=[a]),
                               SYNTAX_RELATION_MORPHEME_FATHER_MODE_USL_COMPOSED))


        backend.add_relations(relations)

