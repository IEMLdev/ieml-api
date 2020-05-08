# RELATIONS

Représentation du graphe de la bdd :
 - `()` : noeud
 - `(:node_type)` : un noeud de type `:node_type`
 - `(:node_type {clef0: "valeur0", clef1: "valeur1"})` : un noeud de type `:node_type` avec deux attributs (propriété du neoud), clef0 et clef1 avec les valeurs valeur0 et valeur1 respéctivement.

 - `()-->()` : 2 noeuds et une relation dirigée entre eux
 - `()--()` : 2 noeuds et une relation non dirigée entre eux
 - `()-[:rel_type]->()` : 2 noeuds et une relation de type `:rel_type` dirigée entre eux



## Types des noeuds
 - `()` : n'importe quel noeud de la bdd

### Noeuds URIs
 - `(:URI)` : un URI,
    attribut:
       - `uri`: l'URI 

### Noeuds USLs
Les types qui suivent sont des sous-types de `:URI` 

 - `(:USL {ieml: "...", cardinal: 1})` : n'importe quel usl de la base de données,
    attributs:
     - `ieml`: la chaine IEML
     - `cardinal`: le nombre de ss de l'USL
     
Les types qui suivent sont des sous-types de `:URI:USL` 
 - `(:Morpheme)` : un polymorpheme simple
 - `(:PolyMorpheme)`
 - `(:Lexeme)`
 - `(:SyntagmaticFunction)`
 - `(:Word)`

- `(:Relation {name: "..."})` 
    attributs:
     - `name`: la chaine arbitraire utilisée pour identifier la relation

### Noeuds descripteurs
 - `(:Descriptor)` : une description en langue naturelle,
  attributs:
   - `language` : la langue du descripteur
   - `value`: la valeur du descripteur
   
Les types qui suivent sont des sous-types de `:Descriptor` 

 - `(:Translation)` : une traduction
 - `(:Tag)` : un tag
 - `(:Comment)` : un commentaire
    
### Autres

 - `(:ExternalRDFRepository)`: un référentiel de concepts RDF externe,
    attributs:
     - `namespace` : le prefix des concepts contenus dans le referentiel
     - `sparql_enpoint`: le endpoint sparql pour intéroger la base
     - `list_all_concepts_sparql_query`: la query list()
     - `list_predicat_object_for_subject_sparql_query`: la query get(URI)


### Types de relations binaires (présente/absente)


Dans la base de données, je ne peux pas enregistrer la chaine IEML comme identifiant de la relation.
Il faut utiliser une chaine de charactères alphanumériques : 
Il y a plusieurs possibilités d'identifiants pour identifier les relations:
    - id unique
    - nom arbitraire 
    - descripteur (1ère traduction en anglais)

Charactères authorisés peut utiliser les charactères `[0-9a-zA-Z]` et `_`.

Pour chaques types de relations dans la bdd, il y a un noeud `(:Relation)` associés
Exemple de requête pour seléctionner un noeud de relations:
 - par nom de relation (ou id): `MATCH (relation_usl:Relation {name: "contains"})`
 - par ieml: `MATCH (relation_usl:Relation {ieml: "E:U:S:."})`



#### Composition (relations syntaxiques)
Relation racine:

- `(:USL)-[:syntax_composed]->(:USL)`

##### Structure des `(:PolyMorpheme)`
- `(:PolyMorpheme)-[:syntax_composed_pm]->(:Morpheme)`
- `(:PolyMorpheme)-[:syntax_composed_pm_constant]->(:Morpheme)`
- `(:PolyMorpheme)-[:syntax_composed_pm_group0]->(:Morpheme)`
- `(:PolyMorpheme)-[:syntax_composed_pm_group1]->(:Morpheme)`
- `(:PolyMorpheme)-[:syntax_composed_pm_group2]->(:Morpheme)`

##### Structure des `(:Lexeme)`
- `(:Lexeme)-[:syntax_composed_lex]->(:PolyMorpheme)`
- `(:Lexeme)-[:syntax_composed_lex_content]->(:PolyMorpheme)`
- `(:Lexeme)-[:syntax_composed_lex_flexion]->(:PolyMorpheme)`

##### Structure des `(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_root]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_initiator]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_interactant]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_receiver]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_time]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_location]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_manner]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_intention]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:syntax_composed_synfun_cause]->(:Lexeme)|(:SyntagmaticFunction)`

##### Structure des `(:Word)`
- `(:Word)-[:syntax_composed_word]->(:SyntagmaticFunction)`
- `(:Word)-[:syntax_composed_word_synfun]->(:SyntagmaticFunction)`
- `(:Word)-[:syntax_composed_word_role]->(:PolyMorpheme)` : the address of the !

#### Structure des `(:Morpheme)`

- `(:Morpheme)-[:syntax_composed_morpheme]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_father]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_father_substance]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_father_attribute]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_father_mode]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_child]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_child_substance]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_child_attribute]->(:Morpheme)`
- `(:Morpheme)-[:syntax_composed_morpheme_child_mode]->(:Morpheme)`


#### Inclusions paradigmatiques

Relation racine:

 - `(:USL)-[:syntax_contains]->(:USL)`
 
 
#### Descripteurs

Relation racine:
 - `(:USL)-[:descriptor]->(:Descriptor)`
 
Sous relations:
 - `(:USL)-[:descriptor_translation]->(:Descriptor)`
 - `(:USL)-[:descriptor_comment]->(:Descriptor)`
 - `(:USL)-[:descriptor_tag]->(:Descriptor)`
 
 #### Référentiels RDFs
 
 Alignement avec un référentiel externe:

 - `(:USL)-[:alignment_match]-(:URI)`
 - `(:USL)-[:alignment_match_exact]-(:URI)`
 - `(:USL)-[:alignment_match_close]-(:URI)`

 
 Inclusion d'une URI externe dans un référentiel externe:
 - `(:ExternalRDFRepository)-[:rdf_repository_defines]->(:URI)`

### Relations quantitifiées
Il peut y avoir plusieurs fois la même relations entre deux noeuds.
Donc pour deux noeuds, on peut en mesurer le poids de ce type de relation : le nombre de cette relation qui relie les deux mêmes noeuds

ce type de relation peut être utile pour calculer les proximités sémantiques.


### Query Language

Le language de query est le language CYPHER de neo4j.


### Définition des relations:


Toutes les relations sont définie par la structure suivante:
 - Définition d'un type de relation:
   - `name` : nom utilisé pour identifier la relation dans la base de données
   - `usl`  : USL utilisé pour représenter la relation
   
   
Il y deux types de calcul de relations:
 - le calcul axiomatique : ce sont les relations qui découlent de la syntax
 - le calcul génératif : on calcul de nouvelles relations à partir de celles présentes dans la base de données.
 
Le calcul axiomatique est implémenté dans les librairies IEML, le calcul génératif est enregistrer dans la base de données de la langue (ieml-language)
Un programme de calcul génératif de relation est spécifié par :
 - Un ensemble de définition de types relations
 - Un ensemble de type de relations dont le calcul dépend
 - Une requete de création dans le language CYPHER

### Exemples de requêtes :

 1) Créer les relations `contained` (x est une ss de y) à partir de la relation `contains` (x à y pour ss)
 
    ```
    MATCH (a:USL), (b:USL)
    WHERE (a) -[:syntax_contains]-> (b)
    MERGE (b)-[:syntax_contained]->(a)  
      ```

    NB: `MERGE` signifie: créer la relation si elle n'existe pas déjà dans la bdd.
 2) Relation parties/tous pour l'oralité primaire:
    
    Relations:
     - name: `:part_of`
     - USL: `E:S:.p.- t.wo.-`
     
     - name: `:whole_from`
     - USL: `E:S:.p.- t.wo.-`
     
    Query:
    ```
    MATCH (a:USL), (b:USL {ieml: "S:.-'U:.-'k.o.-t.o.-'"})
    WHERE (a)-[:contained]->(:USL {ieml: "M:O:.-'U:.-'k.o.-t.o.-'"})
    MERGE (b)-[:part_of]->(a)
    MERGE (a)-[:whole_from]->(b)
    ```
 3) Genre/espece pour les polymorphemes
 
    Relations:
     - name: `:genus_pm`
     - USL: ``
     
     - name: `:species_pm`
     - USL: ``  
   
    Query:
       ```
    MATCH (a:PolyMorpheme)-[:syntax_composed_pm_constant]->(m:Morpheme)<-[:syntax_composed_pm_constant]-(b:PolyMorpheme)
    WHERE a != b
    WITH a, b, count(m) as commonsMorphCount
    MATCH (a)-[:syntax_composed_pm_constant]->(ma:Morpheme)
    WHERE commonsMorphCount > 0
    WITH a, b, commonsMorphCount, count(ma) as MorphACount
    WHERE MorphACount <= commonsMorphCount
    MERGE (b)-[:genus_pm]->(a)
    MERGE (a)-[:species_pm]->(b)```

        
  
### TODO

 - bdd git pour enregistrer les relations génératives (save/load)
 - definition des USLs des relations (Pierre)
 - projection des relations en SKOS/RDF
 - export graphe en SKOS/RDF
 - endpoint RDF
 
 