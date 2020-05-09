from rdflib import Namespace, SKOS, Literal, URIRef

from ieml.relations.relation_type.relation_type import RelationType, ALIGNMENT_RELATION_USL_MATCH_EXACT, \
    ALIGNMENT_RELATION_USL_MATCH_CLOSE, DESCRIPTOR_RELATION_USL_TRANSLATION, DESCRIPTOR_RELATION_USL_COMMENT, \
    SYNTAX_RELATION_USL
from ieml.usl import USL


class RDFRelationsProjector:
    def __init__(self, usl_namespace,
                       mapping_usl_to_usl,
                       mapping_usl_to_descriptor,
                       mapping_usl_to_uri
                 ):
        self.usl_namespace = Namespace(usl_namespace)
        self.mapping_usl_to_usl = mapping_usl_to_usl
        self.mapping_usl_to_descriptor = mapping_usl_to_descriptor
        self.mapping_usl_to_uri = mapping_usl_to_uri

    def project_sam_usl(self, s: USL, a: USL, m: RelationType):
        for reltype in self.mapping_usl_to_usl:
            if m in reltype:
                yield (self.usl_namespace[str(s)], self.usl_namespace[str(a)], self.mapping_usl_to_usl[reltype])

    def project_sam_descriptor(self, s: USL, a: str, m: RelationType, language: str):
        for reltype in self.mapping_usl_to_descriptor:
            if m in reltype:
                yield (self.usl_namespace[str(s)], Literal(a, lang=language), self.mapping_usl_to_descriptor[reltype])

    def project_sam_uri(self, s: USL, a: str, m: RelationType):
        for reltype in self.mapping_usl_to_uri:
            if m in reltype:
                yield (self.usl_namespace[str(s)], URIRef(a), self.mapping_usl_to_uri[reltype])


SKOS_ISIDORE_RELATIONS_PROJECTOR = RDFRelationsProjector(
    mapping_usl_to_usl={
        SYNTAX_RELATION_USL: SKOS.semanticRelation
    },
    mapping_usl_to_descriptor={
        DESCRIPTOR_RELATION_USL_TRANSLATION: SKOS.prefLabel,
        DESCRIPTOR_RELATION_USL_COMMENT: SKOS.editorialNote,

        # 'altLabel', 'hiddenLabel', 'prefLabel', 'notation', 'changeNote',
        #         'definition', 'editorialNote', 'example', 'historyNote', 'note',
        #         'scopeNote'
    },
    mapping_usl_to_uri={
        ALIGNMENT_RELATION_USL_MATCH_EXACT: SKOS.exactMatch,
        ALIGNMENT_RELATION_USL_MATCH_CLOSE: SKOS.closeMatch,
        # 'broadMatch', 'closeMatch', 'exactMatch', 'mappingRelation',
    },
    usl_namespace="https://dev.intlekt.io/usls/")