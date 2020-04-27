from collections import defaultdict
from itertools import chain, product
from typing import List, Any, Dict, Type, Tuple, Union

from ieml.dictionary.script import Script
from ieml.usl import PolyMorpheme
from ieml.usl.constants import SYNTAGMATIC_FUNCTION_SCRIPT, INDEPENDANT_QUALITY, DEPENDANT_QUALITY, ACTANTS_SCRIPTS, \
    ADDRESS_PROCESS_VALENCE_SCRIPTS, ADDRESS_SCRIPTS, ADDRESS_ACTANTS_MOTOR_SCRIPTS, INITIATOR_SCRIPT, \
    INTERACTANT_SCRIPT, RECIPIENT_SCRIPT, TIME_SCRIPT, LOCATION_SCRIPT, MANNER_SCRIPT, CAUSE_SCRIPT, INTENTION_SCRIPT, \
    check_address_script, SYNTAGMATIC_FUNCTION_PROCESS_TYPE_SCRIPT, SYNTAGMATIC_FUNCTION_ACTANT_TYPE_SCRIPT, \
    SYNTAGMATIC_FUNCTION_QUALITY_TYPE_SCRIPT, ADDRESS_SCRIPTS_ORDER, class_from_address, \
    JUNCTION_INDEX, JUNCTION_SCRIPTS, ADDRESS_ROLE_IN_PROCESS

X = Any


class SyntagmaticRole:
    def __init__(self, constant: List[Script]=()):

        self.constant = tuple(constant)

        self._str = ' '.join(chain(map(str, self.constant)))

        if any(e not in ADDRESS_SCRIPTS for e in constant):
            raise ValueError("Invalid script in a syntagmatic role: " +\
                             ' '.join(map(str, filter(lambda e: e not in ADDRESS_SCRIPTS, constant))))

    def __str__(self):
        return self._str

    def __lt__(self, other):
        return self.__class__ == other.__class__ and (
                (all(s in ADDRESS_SCRIPTS for s in chain(self.constant, other.constant)) and \
                 [ADDRESS_SCRIPTS_ORDER[s] for s in self.constant] < [ADDRESS_SCRIPTS_ORDER[s] for s in other.constant]) or \
                (any(s not in ADDRESS_SCRIPTS for s in chain(self.constant, other.constant)) and (\
                 len(self.constant) < len(other.constant) or self.constant < other.constant))
        )

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        """Since the IEML string for a script is its definition, it can be used as a hash"""
        return self._str.__hash__()

    def is_junction_prefix(self, role: 'SyntagmaticRole'):
        """ if self is the junction prefix of the role"""
        return list(self.constant) == list(role.constant[:len(self.constant) - 3]) and \
                 len(role.constant) == len(self.constant) + 2


class SyntagmaticFunction:
    def __init__(self, actor: X, _actors: Dict[List[Script], 'SyntagmaticFunction']):
        self.actor = actor
        self.actors = {SyntagmaticRole(constant=role): f for role, f in _actors.items()}

    def __eq__(self, other):
        s_actors = sorted([(p, a.actor) for p, a in self.actors.items()], key=lambda e: e[0])
        o_actors = sorted([(p, a.actor) for p, a in other.actors.items()], key=lambda e: e[0])
        return s_actors == o_actors

    def __lt__(self, other):
        s_actors = sorted([(p, a.actor) for p, a in self.actors.items()], key=lambda e: e[0])
        o_actors = sorted([(p, a.actor) for p, a in other.actors.items()], key=lambda e: e[0])
        return s_actors < o_actors

    # @property
    # def role(self):
    #     return (SYNTAGMATIC_FUNCTION_SCRIPT,)

    def role_in(self, tgt: 'SyntagmaticFunction'):
        """ return the role of the tgt syntagmatic function occupy in self."""
        for role, node in self.actors.items():
            if node == tgt:
                return role
        else:
            raise KeyError("Node not contained")

    @property
    def empty(self):
        return self.actor.empty and len(self.actors) == 0

    def get(self, role: SyntagmaticRole, ignore_prefix=False, ignore_process_valence=False) -> X:
        # UNUSED ?
        # assert role.is_singular
        if ignore_prefix and role.constant[0] not in ADDRESS_ROLE_IN_PROCESS:
            # in the case of a process syntagm, we do not ignore the prefix
            role = SyntagmaticRole(list(role.constant)[1:])

        if ignore_process_valence and role.constant and role.constant[0] in ADDRESS_PROCESS_VALENCE_SCRIPTS:
            for valence in ADDRESS_PROCESS_VALENCE_SCRIPTS:
                if valence in self.actors:
                    break
            else:
                raise KeyError("Not a process")

            role = SyntagmaticRole([valence] + list(role.constant)[1:])

        return self.actors[role].actor

    def get_paradigm(self, role: SyntagmaticRole) -> List[X]:
        # UNUSED ?
        return [self.actors[r] for r in role.constant if r in self.actors]

    def iter_structure(self):
        for sfun in self.actors.values():
            yield sfun.actor
            if sfun.actor is not None:
                yield from sfun.actor.iter_structure()

    def iter_structure_path(self, context, focus_role=None):
        from ieml.usl.decoration.path import RolePath

        for l, lex in self.as_list(context):
            has_focus = (SyntagmaticRole(constant=l) == focus_role)
            yield (RolePath(SyntagmaticRole(l), has_focus=has_focus, child=None), lex)

            for child, x in lex.iter_structure_path():
                yield (RolePath(SyntagmaticRole(l), has_focus=has_focus, child=child), x)

    def role_is_junction(self, role: SyntagmaticRole=None):
        try:
            return isinstance(self.actors[role], JunctionSyntagmaticFunction)
        except KeyError:
            return False

    @staticmethod
    def get_context_role_prefix(context):
        if context in [ProcessSyntagmaticFunction, JunctionSyntagmaticFunction]:
            return tuple()
        elif context == DependantQualitySyntagmaticFunction:
            return (DEPENDANT_QUALITY,)
        elif context == IndependantQualitySyntagmaticFunction:
            return (INDEPENDANT_QUALITY,)
        else:
            return None

    def render_with_context(self, role: SyntagmaticRole=None, context=None):
        prefix = tuple()
        if context is not None:
            prefix = self.get_context_role_prefix(context)
            if prefix is None:
                raise ValueError("Invalid context to render a syntagmatic function \"{}\", expected [{}]".format(
                    str(context),
                    ','
                ))

        main_roles_expansion = self.get_role_expansion(role, ignore_prefix=prefix)

        res = '['

        res += " > ".join([
            ('! ' if address in main_roles_expansion else '')
                + ((str(prefix[0]) + ' ') if prefix else '')
                + str(address) + ' '
                + str(self.actors[address].actor)
            for address in sorted(self.actors) if not isinstance(self.actors[address], JunctionSyntagmaticFunction)
        ])
        return res + ']'

    def get_role_expansion(self, role: SyntagmaticRole, ignore_prefix=()):

        def _expand_junction(role):
            try:
                node = self.actors[SyntagmaticRole(role)]
            except KeyError:
                pass
            if not isinstance(node, JunctionSyntagmaticFunction):
                return [role]
            return list(chain.from_iterable(map(_expand_junction,
                                                [role + (node.junction_link, JUNCTION_INDEX[i]) for i, _ in enumerate(node.children)])))

        _ignore_prefix = lambda e : SyntagmaticRole(constant=e.constant[len(ignore_prefix):])

        return sorted(SyntagmaticRole(r) for r in _expand_junction(_ignore_prefix(role).constant))

    def as_list(self, context_type) -> List[Tuple[List[Script], X]]:
        prefix = self.get_context_role_prefix(context_type)
        if prefix is None:
            raise ValueError("Invalid syntagmatic function \"{}\" type".format(str(context_type)))
        prefix = list(prefix)

        return [(prefix + list(role.constant), sfun.actor) for role, sfun in self.actors.items()
                    if not isinstance(sfun, JunctionSyntagmaticFunction)]

    @staticmethod
    def from_list(l: List[Tuple[List[Script], X]]) -> Tuple[Type['SyntagmaticFunction'], 'SyntagmaticFunction']:

        # assert all(all(s in ADDRESS_SCRIPTS for s in address) for address, _ in l), "invalid address"
        if not l:
            raise ValueError("Empty syntagmatic function")

        roles = [address[0] for address, _ in l]
        children_l = [(address[1:], x) for address, x in l]

        # determine witch type is
        proc_count = sum(1 if a in ADDRESS_PROCESS_VALENCE_SCRIPTS else 0 for a in roles)
        if proc_count == 1:
            return ProcessSyntagmaticFunction, ProcessSyntagmaticFunction._from_list(l)
        elif proc_count > 1:
            raise ValueError("Invalid syntagmatic function, too many process roles")

        roles = set(roles)
        if len(roles) != 1:
            raise ValueError("Invalid syntagmatic function, too many different actant roles ")

        role = next(iter(roles))

        # role in ACTANTS_SCRIPTS or
        if role == DEPENDANT_QUALITY:
            return DependantQualitySyntagmaticFunction, DependantQualitySyntagmaticFunction._from_list(children_l)

        if role == INDEPENDANT_QUALITY:
            return IndependantQualitySyntagmaticFunction, IndependantQualitySyntagmaticFunction._from_list(children_l)

        raise ValueError("Invalid syntagmatic function, unknown function.")

    def check(self, X: Type, check_X, sfun_type):
        if not isinstance(self, JunctionSyntagmaticFunction):
            if not isinstance(self.actor, X):
                raise ValueError("The process of a SyntagmaticFunction is expected to be a {}, not a {}."
                                 .format(X.__name__, self.actor.__class__.__name__))

            check_X(self.actor, sfun=self)

        for address, x in self.actors.items():
            if not isinstance(address, SyntagmaticRole):
                raise ValueError("An address in a SyntagmaticFunction is expected to be a polymorpheme, not a {}."
                                 .format(address.__class__.__name__))

            check_address_script(address.constant, sfun_type=sfun_type)

    def singular_sequences(self, context_type):
        sfun_l = self.as_list(context_type)

        res = []
        roles, x_l = zip(*sfun_l)
        for x_l_ss in product(*[x.singular_sequences for x in x_l]):
            ctx, sfun = self.from_list(list(zip(roles, x_l_ss)))
            res.append(sfun)

        return res


class JunctionSyntagmaticFunction(SyntagmaticFunction):
    def __init__(self, junction_link: Script, children: List[SyntagmaticFunction]):
        self.junction_link = junction_link

        # if self.junction_link in JUNCTION_SYMMETRICAL:
        #     self.children = sorted(children)

        self.children = tuple(children)

        res = {
            tuple(): self,
            **{(self.junction_link, JUNCTION_INDEX[i], *role.constant): sfun for i, f
                in enumerate(self.children) for role, sfun in f.actors.items()}
        }

        super().__init__(None, res)

    @classmethod
    def _from_list(cls, l: List[Tuple[List[Script], X]], context: Type[SyntagmaticFunction]):

        junctions = {address[0] for address, _ in l}

        links = junctions & set(JUNCTION_SCRIPTS)
        if len(links) != 1:
            raise ValueError("No links defined in the junction")
        link = next(iter(links))

        # anchors = junctions & JUNCTION_ANCHOR_TO_LINKS.keys()
        # try:
        #     anchor = next(iter(anchors))
        #
        #     if any(j not in {anchor, *JUNCTION_ANCHOR_TO_LINKS[anchor]} for j in junctions):
        #         raise ValueError("multiple different anchor are taken togethers")
        # except StopIteration:
        #     pass

        # if any(link not in {j, anchor} for j in junctions):
        #     raise ValueError("multiple different links are taken togethers")

        _groups = defaultdict(list)
        for address, x in l:
            idx = JUNCTION_INDEX.index(address[1])
            _groups[idx].append((address[2:], x))

        groups = [[] for _ in range(len(_groups))]
        for i in _groups:
            if i > len(groups):
                raise ValueError("Invalid junction syntagmatic function definition, incoherent indexing.")
            groups[i] = _groups[i]

        return cls(junction_link=link, children=[context._from_list(g_v) for g_v in groups])

    def check(self, X: Type, check_X, sfun_type):
        super().check(X, check_X, sfun_type)

        for c in self.children:
            c.check(X, check_X, sfun_type)


class IndependantQualitySyntagmaticFunction(SyntagmaticFunction):
    def __init__(self, actor: X):
        super().__init__(actor, {tuple(): self})

    @classmethod
    def _from_list(cls, l: List[Tuple[List[Script], X]]):
        if len(l) == 1 and len(l[0][0]) == 0: # no role, only a unique lexeme
            return cls(actor=l[0][1])

        # _junction = None
        # for address, x in l:
        #     role = next(iter(address))
        #     if role in JUNCTION_SCRIPTS:
        #         _junction = role
        #     elif _junction is not None:
        #         raise ValueError("Invalid actant syntagmatic function definition, if a junction is present, all children must be a junction")

            # if len(address) != 2:
            #     raise ValueError("Invalid quality syntagmatic function definition, expected a jonction not \"{}\" role.".format(' '.join(map(str, address))))
        #
        # if _junction:
        #     return JunctionSyntagmaticFunction._from_list(l, DependantQualitySyntagmaticFunction)


        return JunctionSyntagmaticFunction._from_list( l, context=IndependantQualitySyntagmaticFunction)


class DependantQualitySyntagmaticFunction(SyntagmaticFunction):
    def __init__(self,
                 actor: X,
                 dependant: Union['DependantQualitySyntagmaticFunction',JunctionSyntagmaticFunction] = None,
                 independant: Union[IndependantQualitySyntagmaticFunction,JunctionSyntagmaticFunction] = None,
                 **kwargs):

        self.dependant = dependant
        self.independant = independant

        res = {
                tuple(): self,
                **({(INDEPENDANT_QUALITY, *role.constant): f for role, f in self.independant.actors.items()} if self.independant is not None else {}),
                **({(DEPENDANT_QUALITY, *role.constant): f for role, f in self.dependant.actors.items()} if self.dependant is not None else {}),
            }

        super().__init__(actor, res)

    @classmethod
    def _from_list(cls, l: List[Tuple[List[Script], X]]):
        actor = None
        _dependant = []
        _independant = []

        _junction = None

        for address, x in l:
            if len(address) == 0:
                if actor is not None:
                    raise ValueError(
                        "Invalid actant syntagmatic function definition, there is two lexemes for the same role.")
                actor = x
            else:
                role = next(iter(address))
                if role in JUNCTION_SCRIPTS:
                    _junction = role
                elif _junction is not None:
                    raise ValueError("Invalid actant syntagmatic function definition, if a junction is present, all children must be a junction")
                elif address[0] == INDEPENDANT_QUALITY:
                    _independant.append((address[1:], x))
                elif address[0] == DEPENDANT_QUALITY:
                    _dependant.append((address[1:], x))
                else:
                    raise ValueError("Invalid actant syntagmatic function definition, the role \"{}\" is not valid in this context."
                                         .format(str(address[0])))

        if _junction:
            return JunctionSyntagmaticFunction._from_list(l, DependantQualitySyntagmaticFunction)

        dependant = None
        if _dependant:
            dependant = DependantQualitySyntagmaticFunction._from_list(_dependant)

        independant = None
        if _independant:
            independant = IndependantQualitySyntagmaticFunction._from_list(_independant)

        return cls(actor=actor, dependant=dependant, independant=independant)

    def check(self, X, check_X, sfun_type):
        super().check(X, check_X, sfun_type)

        if self.independant is not None:
            if not isinstance(self.independant, (IndependantQualitySyntagmaticFunction, JunctionSyntagmaticFunction)):
                raise ValueError("A quality is expected to be a IndependantQualitySyntagmaticFunction or a JunctionSyntagmaticFunction, not a {}."
                             .format(self.independant.__class__.__name__))

            self.independant.check(X, check_X, sfun_type)

        if self.dependant is not None:
            if not isinstance(self.dependant, (DependantQualitySyntagmaticFunction, JunctionSyntagmaticFunction)):
                raise ValueError("An actant is expected to be a DependantQualitySyntagmaticFunction or a JunctionSyntagmaticFunction, not a {}."
                                 .format(self.dependant.__class__.__name__))

            self.dependant.check(X, check_X, sfun_type)


class ProcessSyntagmaticFunction(SyntagmaticFunction):
    def __init__(self,
                 actor: X,
                 valence: Script,
                 actants: Dict[Script, DependantQualitySyntagmaticFunction]):
        self.actants = actants

        self.initiator = self.actants.get(INITIATOR_SCRIPT, None)
        self.interactant = self.actants.get(INTERACTANT_SCRIPT, None)
        self.recipient = self.actants.get(RECIPIENT_SCRIPT, None)

        self.time = self.actants.get(TIME_SCRIPT, None)
        self.location = self.actants.get(LOCATION_SCRIPT, None)
        self.manner = self.actants.get(MANNER_SCRIPT, None)
        self.cause = self.actants.get(CAUSE_SCRIPT, None)
        self.intention = self.actants.get(INTENTION_SCRIPT, None)

        for role, a in self.actants.items():
            if role not in ACTANTS_SCRIPTS:
                raise ValueError("Invalid role : {}".format(' '.join(str(role))))

        self.valence = valence

        super().__init__(actor, {
            (self.valence,): self,
            **{(role, *role_sub.constant): f for role, actant in self.actants.items() for role_sub, f in actant.actors.items()}
        })

    @staticmethod
    def _from_list(l: List[Tuple[List[Script], X]]):
        actor = None
        _actants = defaultdict(list)
        valence = None

        for address, x in l:
            role = next(iter(address))

            if role in ADDRESS_PROCESS_VALENCE_SCRIPTS:
                if len(address) != 1 or actor is not None:
                    raise ValueError("Invalid process syntagmatic function, too many process roles")
                actor = x
                valence = role
            elif role in ACTANTS_SCRIPTS:
                actant_count = sum(1 if a in ACTANTS_SCRIPTS else 0 for a in address)

                if actant_count == 1:
                    _actants[role].append([address[1:], x])
                elif actant_count > 1:
                    raise ValueError("Invalid syntagmatic function, too many actant roles")
            else:
                raise ValueError("Invalid address in a process syntagmatic function {}".format(' '.join(map(str, address))))

        actants = {}
        for r, l_actant in _actants.items():
            # if all(l[0][0] in JUNCTION_SCRIPTS for l in l_actant):
            #     actants[r] = JunctionSyntagmaticFunction._from_list(l_actant, DependantQualitySyntagmaticFunction)
            # else:
            actants[r] = DependantQualitySyntagmaticFunction._from_list(l_actant)

        return ProcessSyntagmaticFunction(actor=actor, actants=actants, valence=valence)

    def check(self, X: Type, check_X, sfun_type):
        super().check(X, check_X, sfun_type)

        for actant, role in [(self.initiator, INITIATOR_SCRIPT),
                       (self.interactant, INTERACTANT_SCRIPT),
                       (self.recipient, RECIPIENT_SCRIPT),
                       (self.time, TIME_SCRIPT),
                       (self.location, LOCATION_SCRIPT),
                       (self.intention, INTENTION_SCRIPT),
                       (self.cause, CAUSE_SCRIPT),
                       (self.manner, MANNER_SCRIPT)]:

            if actant is not None:
                if not isinstance(actant, (DependantQualitySyntagmaticFunction, JunctionSyntagmaticFunction)):
                    raise ValueError("An actant of a word is expected to be a ActantSyntagmaticFunction or a JunctionSyntagmaticFunction, not a {}."
                                     .format(actant.__class__.__name__))

                actant.check(X, check_X, sfun_type)
