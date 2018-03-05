# IEML
[![Build Status](https://travis-ci.org/IEMLdev/ieml.svg?branch=master)](https://travis-ci.org/IEMLdev/ieml)


IEML is an artificial natural language created by the french philosopher Pierre Levy [blog](https://pierrelevyblog.com/).
It is a regular language that can efficiently manipulated algorithmically.


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

The IEML dictionary is a set of basic semantics units. There is 5000 terms defined in the dictionary with 
3500 words. Statistical algorithms have difficulties to manage big vocabularies where there is few examples 
for a lot of symbols. This is the often the case in NLP applications with natural languages.

However, with the finite set dictionary, this problem does not happen in IEML.   

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

The dictionary defines the paradigmatics relations between the terms,
and the grammar defined the syntactics and textual relations between the terms.


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
Each of these properties returns a frozen set of USLs.

For any couple of usl, you can compute a semantic similarity measure based on the 
relation matrix of the dictionary :
```python
from ieml.grammar.distance import dword
from ieml.grammar.tools import random_usl
u0 = random_usl(Topic)
u1 = random_usl(Text)

dword(u0, u1)
```

For the moments, only the distance on words is supported.

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

 
 
