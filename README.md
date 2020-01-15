# IEML
[![Build Status](https://travis-ci.org/IEMLdev/ieml.svg?branch=master)](https://travis-ci.org/IEMLdev/ieml)

IEML is a regular philological language (built as a natural language), where the syntax is parallel to semantics. This means in IEML, a small change in the structure of an expression results in a semantically close expression.
For instance:
 - `[! E:S:. ()(u.A:.-) > E:.l.- (E:.-U:.s.-l.-')]` : to go up
 - `[! E:S:. ()(u.A:.-) > E:.l.- (E:.-U:.d.-l.-')]` : to go down
 
Only `E:.-U:.`**s**`.-l.-'` (up) has been changed to `E:.-U:.`**d**`.-l.-'` (down).

These properties make the semantic relationships between the different expressions of the language automatically computable by an edit distance calculation.
Therefore, there are no synonyms in the language, because by construction, the synonyms would be written identically. On the other hand, words that are written differently in IEML have different meanings.

So IEML has the perfect capabilities to uniquely identify concepts in a database, an ontology, a taxonomy, a categorization or any other documents, without having to rely on an external referential other than IEML's grammar and its dictionary of semantic primitives. 

In order to guarantee the consistency of interpretations of IEML expressions, a database of translations (en and fr), comments and tags per USL is available [here](https://github.com/IEMLdev/ieml-language "IEML database"). This database has a normative purpose concerning the interpretation of IEML expressions. It can be browsed with the [intlekt editor](https://dev.intlekt.io/ "IEML editor"). It can also be used as an educational resource for learning IEML, in addition to reading the [grammar](https://www.dropbox.com/s/875vsj0atbcts43/0-00-IEML-Manifesto-2019-fr.pdf?dl=0 "IEML grammar"). 

IEML is a regular language that is intended to serve as an easily interpretable coordinate system for the world of ideas on the internet, to improve communication and artificial intelligence.
This language has been made by the French philosopher [Pierre Levy](https://en.wikipedia.org/wiki/Pierre_L%C3%A9vy) and implemented in python by [Louis van Beurden](https://louisvanbeurden.wordpress.com/).

## Install

The library works with python 3.5+

You can install the ieml package with pip:
```bash
pip install ieml
```
If you want to install it from github:
```bash
git clone https://github.com/IEMLdev/ieml
python setup.py
```
## Quick start

### Dictionary

The IEML dictionary is a set of around ~3500 basic semantics units. 

The dictionay has its own syntax and primitives. The dictionary is organised in layers, from 0 (the most abstract) to 7 (the most specific). The words excepts the primitives are built from words of lower layers.  

The last version of the IEML dictionary is automatically downloaded and installed when instanced:
```python
from ieml.dictionary import Dictionary

dic = Dictionary()
dic.index
```
This return a list of all words defined in the dictionary.
There is an order defined on the terms of the dictionary, and d.index is the position of the words in this order.

You can access the translations of a word :
 ```python
t = dic.index[100]
t.translations.en
```
There are for the moment two languages supported: french (fr) and english (en)

The dictionaryis a graph of semantic relationships (paradigmatic) between the words.
All the relations are computed automatically from the terms definitions.
```python
t.relations.neighbours
```
This return a list of all the neighboors of term t and the type of relation they share.

You can also access the graph of relation as a numpy array of transitions :
```python
m = dic.relations_graph.connexity
```
Return a dense numpy array of boolean where `m[i, j]` is true if there is a relation 
between the term number `i` and the term number `j`.
```
from ieml.dictionary import term

t0 = term('wa.')
t1 = term('we.')
m[t0.index, t1.index]
```

The `term` function with a string argument call the dictionary parser and
return a Term if the string is a valid IEML expression of a term (defined in the dictionary).


### Syntax

A syntactic meaning unit is called an USL, for Uniform Semantic Locator. 
There is five differents types of USL :
 - Word : the basic meaning constituent, you can find all the defined words in the [IEML dictionary](https://dictionary.ieml.io).  
 - Topic: a topic aggregate Words into a root and a flexing morphem, a topic represents a subject, a process. 
 - Fact : a fact is a syntactic tree of topics, a fact symbolizes an event, a description.
 - Theory: a theory is a tree of facts, it represents a set of sentence linked together by causal, temporal, logic links etc. 
 - Text: a text is a set of Topic, Fact and Theory.

To instantiate an usl, you can use the USL parser with the `usl` function
with a string argument.

```python
from ieml.grammar import usl

usl('[([wa.])]') # topic with a single word
usl("[([t.u.-s.u.-d.u.-']+[t.u.-b.u.-'])*([b.i.-])]") # topic with two words in his root morphem and one in flexing 
```

You can also create an usl with constructors :
```python
from ieml.grammar import word, topic, fact, theory, text

w = word('wa.')
t0 = topic([w])
t1 = topic(['wa.', 'e.'])
t2 = topic(root=["t.u.-s.u.-d.u.-'", "t.u.-b.u.-'"], 
           flexing=["b.i.-"])
f = fact([(t2, t0, t1)])

t = text([t0, t1, t2, f])
```

For any usls, you can access the words, topics, facts, theories and texts defined 
in the usl by accessing the dedicated property:

```python
t.words
t.topics
t.facts
t.theories
t.texts
```
Each of these properties returns a set of USLs of the specific type.

For any couple of usl, you can compute a semantic similarity measure based on the 
relation matrix of the dictionary :
```python
from ieml.grammar.distance import dword
from ieml.grammar.tools import random_usl
u0 = random_usl(Topic)
u1 = random_usl(Text)

dword(u0, u1)
```

For the moments, only a similarity using the words of the USL is defined.

### Collection of USLs
For a list of USLs, you can compute a square matrix of relative order from each USLs :
```python
from ieml.distance.sort import square_order_matrix

usl_list = [random_usl() for _ in range(100)]

m = square_order_matrix(usl_list)

i = 20
ordered_usls = [usl_list[k] for k in m[i, :]]
```
ordered_usls is the list of usl ordered from USLs number i to the farrest USL from USL i in the collection.
This method use the semantic distance between words of the dictionary.

 
 
