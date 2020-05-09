from typing import List

from ieml.relations.export.relations_projector import RDFRelationsProjector
from ieml.relations.graph_backend.neo4j_backend import Neo4jGraphBackend
from rdflib import Graph, Literal, RDF, URIRef, Namespace, SKOS

from ieml.usl import USL


class RDFExporter:
    def __init__(self, backend: Neo4jGraphBackend,
                       relation_projector: RDFRelationsProjector,
                       usl_namespace="https://dev.intlekt.io/api/rdf/",):
        self.usl_namespace = Namespace(usl_namespace)
        self.backend = backend
        self.relation_projector = relation_projector

    def serialize(self, usls: List[USL]):
        g = Graph()

        for s, a, m in self.backend._exec_query("""MATCH (u0:USL)-[r]->(u1:USL)
                WHERE u0.ieml IN $usls AND u1.ieml IN $usls
                RETURN u0.ieml, u1.ieml, r.name
                """):
            for subject, object, predicate in self.relation_projector.project_sam_usl(s, a, m):
                g.add((subject, predicate, object))

        for s, a, language, m in self.backend._exec_query("""MATCH (u0:USL)-[r]->(d:Descriptor)
                WHERE u0.ieml IN $usls
                RETURN u0.ieml, d.value, d.language,  r.name
                """):
            for subject, object, predicate in self.relation_projector.project_sam_descriptor(s, a, m, language=language):
                g.add((subject, predicate, object))

        for s, a, language, m in self.backend._exec_query("""MATCH (u0:USL)-[r]->(uri:URI)
                WHERE u0.ieml IN $usls
                RETURN u0.ieml, uri.uri,  r.name
                """):
            for subject, object, predicate in self.relation_projector.project_sam_uri(s, a, m):
                g.add((subject, predicate, object))






