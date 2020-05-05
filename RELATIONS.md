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
 - `(:USL {ieml: "...", cardinal: 1})` : n'importe quel usl de la base de données
    attributs:
     - `ieml`: la chaine IEML
     - `cardinal`: le nombre de ss de l'USL
     
Les types qui suivent sont des sous-types de `:USL` 
 - `(:Morpheme)` : un polymorpheme simple
 - `(:PolyMorpheme)`
 - `(:Lexeme)`
 - `(:SyntagmaticFunction)`
 - `(:Word)`

- `(:Relation {name: "..."})` 
    attributs:
     - `name`: la chaine arbitraire utilisé pour identifié la relation


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

- `(:USL)-[:composed]->(:USL)`

##### Structure des `(:PolyMorpheme)`
- `(:PolyMorpheme)-[:composed_pm]->(:Morpheme)`
- `(:PolyMorpheme)-[:composed_pm_constant]->(:Morpheme)`
- `(:PolyMorpheme)-[:composed_pm_group0]->(:Morpheme)`
- `(:PolyMorpheme)-[:composed_pm_group1]->(:Morpheme)`
- `(:PolyMorpheme)-[:composed_pm_group2]->(:Morpheme)`

##### Structure des `(:Lexeme)`
- `(:Lexeme)-[:composed_lex]->(:PolyMorpheme)`
- `(:Lexeme)-[:composed_lex_content]->(:PolyMorpheme)`
- `(:Lexeme)-[:composed_lex_flexion]->(:PolyMorpheme)`

##### Structure des `(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_root]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_initiator]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_interactant]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_receiver]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_time]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_location]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_manner]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_intention]->(:Lexeme)|(:SyntagmaticFunction)`
- `(:SyntagmaticFunction)-[:composed_synfun_cause]->(:Lexeme)|(:SyntagmaticFunction)`

##### Structure des `(:Word)`
- `(:Word)-[:composed_word]->(:SyntagmaticFunction)`
- `(:Word)-[:composed_word_synfun]->(:SyntagmaticFunction)`
- `(:Word)-[:composed_word_role]->(:PolyMorpheme)` : the address of the !

#### Structure des `(:Morpheme)`

- `(:Morpheme)-[:composed_morpheme]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_father]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_father_substance]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_father_attribute]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_father_mode]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_child]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_child_substance]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_child_attribute]->(:Morpheme)`
- `(:Morpheme)-[:composed_morpheme_child_mode]->(:Morpheme)`


#### Inclusions paradigmatiques

Relation racine:

 - `(:USL)-[:contains]->(:USL)`
 
 



### Relations quantitifiées
Il peut y avoir plusieurs fois la même relations entre deux noeuds.
Donc pour deux noeuds, on peut en mesurer le poids de ce type de relation : le nombre de cette relation qui relie les deux mêmes noeuds

ce type de relation peut être utile pour calculer les proximités sémantiques.


### Query Language

Le language de query est le language CYPHER de neo4j.


### Définition de relations:
Plusieurs relations peuvent être définies ensemble.

 Relations:
  - nom0
  - USL0
  
  - nom1
  - USL1 
  ...
  
  Query: "..." 



### Exemples de requêtes :

 1) Créer les relations `contained` (x est une ss de y) à partir de la relation `contains` (x à y pour ss)
 
    ```
    MATCH (a:USL), (b:USL)
    WHERE (a) -[:contains]-> (b)
    MERGE (b)-[:contained]->(a)  
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
 3) Genre/espece pour les polymorphemes (relation quantifiable)
 
    Relations:
     - name: `:genus_pm`
     - USL: ``
     
     - name: `:species_pm`
     - USL: ``
     
     Query:
     ```
        MATCH (a:PolyMorpheme), (b:PolyMorpheme)
        WHERE (a)-[:contained]->(:USL {ieml: "M:O:.-'U:.-'k.o.-t.o.-'"})
        CREATE (b)-[:part_of]->(a)
        CREATE (a)-[:species_pm]->(b)```
