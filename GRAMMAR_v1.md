# IEML grammar v1

## Goals

 - unification of the syntax : how far do we want to go ? should we only have different layers of Words ? 
 - first implementation of relations


## IEML grammar v0.* issues

### Interlayer
 - Simple Polymorphemes don't have the same code with the Morpheme
 - Simple Lexemes don't have the same code with the Polymorpheme
 - Simple Words don't have the same code with the Lexeme
 
### Variations

NOTE: difference with the dictionary: there is many paradigms that have the same singulars sequences, it implies that for
a set of singulars sequences, there is multiple valid factorizations

 - All the USL paradigm should be expressed by the additive operation

 
 

#### Polymorphemes

 - The Polymorphemes groups should be written with as an USL paradigm of Simple Polymorphemes 
 (= Morpheme seen as PM, distinction irrevelant in V1)

 ISSUE : the position in the group is lost with the ss of the PM paradigm
    => multiple possible factorization

   
 
#### Lexeme   
  - We should remove the enclosing parenthesis for the content
  - the flexing should be related to relations
#### Word

  - remove the enclosing bracket
  - The root should not be prefixed by an address
  - unify the syntagmatics structures

### Literals
 - the literals should be embedded in the USL, not at the end of the code.
 
 
## New features
### Relations
   - Each relation is defined by an USL, cf doc Pierre.
   - (+) Equivalency between sub-graph and Word (new kind of factorization ?) 

### Descriptors
  - (+) Use the literal fonctionality with the relationship to store the descriptors informations
  



    