# IEML
[![Build Status](https://travis-ci.org/IEMLdev/ieml.svg?branch=master)](https://travis-ci.org/IEMLdev/ieml)



IEML is an artificial language built to allow algorithmic manipulation of meaning.
It is constituted of a [dictionary of elementary meaning units and their semantic relations](https://intlekt.io/?comments=I%3A "IEML dictionary") and a syntax that defines nested structures with explicit meaning-composition rules. The grammar is regular, and the semantic relations are explicit (can be automatically computed at every syntactic level).

This language is the theory of the last 20 years of the French philosopher Pierre Levy [blog](https://pierrelevyblog.com/) to empower collective intelligence in the digital media. This language is to be seen as classification system for the Internet librarian.

and is made to overcome certain limitation of the natural language for natural langage processing :
    - polysemie of signs : in IEML, the meaning of a sign is embedded in the sign itself. So different meaning will writes with different signs. It also ensure that there is no synonyms.
    - out-of-vocabularies : every proposition in IEML is build from the ~3500 basic meaning units (called words) of the dictionary.
    - interlingua : IEML doesn't use any existing natural language at his core semantics. It doesn't rely on English or French to defines his primitives units.
    - semantic similarity : we can automatically compute a semantic graph between two IEML propositions.


## Install

You can install the ieml package with pip:
```bash
pip install ieml
```
The library has been developed with python3.5, but it should work with any python3 versions.

If you want to install it from github:
```bash
git clone https://github.com/IEMLdev/ieml
pip install -r requirements.txt
python setup.py
```
## Quick start

### Dictionary

The IEML dictionary is a set of around ~3500 basic semantics units.
The dictionary is made of 6 layers of words build on top of each others. The words in the low layers are more abstract and general, while the higher layers are more particular and specific.


The last version of the IEML dictionary is automatically downloaded and installed when instanced:
```python
from ieml.dictionary import Dictionary

dic = Dictionary()
dic.index
```
This return a list of all terms defined in the dictionary.
There is an order defined on the terms of the dictionary, and d.index is
sorted with this order. 

You can access the translations of a term in to natural languages:
 ```python
t = dic.index[100]
t.translations.en
```
There is actually two languages supported: french (fr) and english (en)


The dictionary is a dense graph of semantic relations between the terms.
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
return a Term if the string is a valid IEML term (valid syntax and defined in the dictionary).


### Grammar



A syntactic meaning unit is called an USL, for Uniform Semantic Locator. 
There is five differents types of USL :
 - Word : the basic meaning constituent, you can find all the defined words in the [IEML dictionary](https://dictionary.ieml.io).  
 - Topic: a topic aggregate Words into a root and a flexing morphem, a topic represents a subject, a process. 
 - Fact : a fact is a syntactic tree of topics, a fact symbolizes an event, a description.
 - Theory: a theory is a tree of facts, it represents a set of sentence linked together by causal, temporal, logic links. 
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

For the moments, only a similarity on words is defined.

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

## Learning more

Check the [documentation](http://ieml.readthedocs.io/en/latest/index.html) (to be there soon) for more detail on the library usage

 
 
