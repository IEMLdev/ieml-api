from typing import List

from tqdm import tqdm

from ieml.dictionary.relation import RelationsGraph
from ieml.dictionary.script import Script
from ieml.relations.graph_backend.basic_backend import BasicGraphBackend
from ieml.relations.relation_type.constants import COMPOSED_PM, CONTAINS_PM, CONTAINED_PM
from ieml.relations.relation_type.contains_contained_type import ContainsContainedRelationType
from ieml.relations.relation_type.genus_species_type import GenusSpeciesRelationType
from ieml.usl import USL, PolyMorpheme


class RelationGraph:
    def __init__(self,
                 relation_types=(GenusSpeciesRelationType, ContainsContainedRelationType),
                 backend=BasicGraphBackend):
        self.backend = backend()
        self.relation_types = [reltype() for reltype in relation_types]

    def addUSL(self, usl: USL):
        self.addManyUSLs([usl])

    def addManyUSLs(self, usls: List[USL]):
        # usls = [u for u in usls if not isinstance(u, InstancedUSL)]

        self.backend.add_nodes(usls)
        relations = set()
        for u in tqdm(self.backend.nodes, "Computing relations"):
            for reltype in self.relation_types:
                for usl in usls:
                    if usl != u:
                        rel = reltype(usl, u)
                        if rel is not None:
                            relations.add((usl, u, rel))
        print(len(relations))
        self.backend.add_relations(list(relations))


class Neo4jRelationsEngine:
    def __init__(self, backend):
        self.backend = backend

    def build(self, usls_input: List[USL]):
        usls = set()

        # build composition relationships
        # between USL -> Morpheme

        relations = set()
        for u in tqdm(usls_input, "Building USL to USL composed relationships"):
            usls.add(u)
            for uu in u.iter_structure(auto_promote_to_USL=True):
                if uu is not None:
                    usls.add(uu)
                    if not uu.empty and not (isinstance(uu, PolyMorpheme) and uu.cardinal == 1 and len(uu.constant) == 1):
                        relations.add((u, uu, COMPOSED_PM))


        usls = sorted(usls)
        self.backend.add_nodes(usls)
        self.backend.add_relations(relations)

        # build contains/contained relations
        relations = set()

        for u in tqdm(filter(lambda p:p.cardinal != 1, usls), "Building USL to USL contained relationships"):
            for ss in u.singular_sequences:
                relations.add((u, ss, CONTAINS_PM))
                relations.add((ss, u, CONTAINED_PM))

        self.backend.add_relations(relations)

    def build_dictionary_relations(self, rel_graph: RelationsGraph):
        self.backend.add_nodes([PolyMorpheme(constant=[s]) for s in rel_graph.scripts])

        for reltype, csr_mat in tqdm(rel_graph.relations.items(), "Saving dictionary relations."):
            relations = set()
            for s in rel_graph.scripts:
                attrs = rel_graph.scripts[sorted(rel_graph.relations[reltype][rel_graph.index[s]].indices)]
                relations.union([(PolyMorpheme(constant=[s]), PolyMorpheme(constant=[a]), "dic_" + reltype) for a in attrs])

            self.backend.add_relations(relations)




        #
        # for u in tqdm(usls, "Building USL to Morpheme composition relationships"):
        #     morph = [m for m in u.morphemes if not m.empty]
        #     if len(morph) != 1:
        #
