from collections import defaultdict
from itertools import chain
from typing import List, Any, Dict, Type, Tuple

from ieml.dictionary.script import Script
from ieml.usl import PolyMorpheme
from ieml.usl.constants import SYNTAGMATIC_FUNCTION_SCRIPT, INDEPENDANT_QUALITY, DEPENDANT_QUALITY, ACTANTS_SCRIPTS, \
    ADDRESS_PROCESS_VALENCE_SCRIPTS, ADDRESS_SCRIPTS, ADDRESS_ACTANTS_MOTOR_SCRIPTS, INITIATOR_SCRIPT, \
    INTERACTANT_SCRIPT, RECIPIENT_SCRIPT, TIME_SCRIPT, LOCATION_SCRIPT, MANNER_SCRIPT, CAUSE_SCRIPT, INTENTION_SCRIPT, \
    check_address_script, SYNTAGMATIC_FUNCTION_PROCESS_TYPE_SCRIPT, SYNTAGMATIC_FUNCTION_ACTANT_TYPE_SCRIPT, \
    SYNTAGMATIC_FUNCTION_QUALITY_TYPE_SCRIPT, ADDRESS_SCRIPTS_ORDER, class_from_address

X = Any


class SyntagmaticRole(PolyMorpheme):
    def __init__(self, constant: List[Script]=(), groups=()):
        super().__init__(constant, groups)

        if any(e not in ADDRESS_SCRIPTS_ORDER for e in constant):
            raise ValueError("Invalid script in a syntagmatic role.")

        self.constant = tuple(sorted(constant, key=lambda e: ADDRESS_SCRIPTS_ORDER[e]))

        if len(groups):
            raise ValueError("Paradigms are not supported in syntagmatic roles.")

        # self.groups = tuple(sorted((tuple(sorted(g[0], key=lambda e: ADDRESS_SCRIPTS_ORDER[e])), g[1])
        #                            for g in groups))

        self._str = ' '.join(chain(map(str, self.constant)))
                               # ["m{}({})".format(mult, ' '.join(map(str, group))) for group, mult
                               #      in self.groups]))

    def do_lt(self, other):
        return [ADDRESS_SCRIPTS_ORDER[e] for e in self.constant] < [ADDRESS_SCRIPTS_ORDER[e] for e in other.constant]


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

    @property
    def role(self):
        return (SYNTAGMATIC_FUNCTION_SCRIPT,)

    def get(self, role: SyntagmaticRole) -> X:
        assert role.is_singular
        return self.actors[role].actor

    def get_paradigm(self, role: SyntagmaticRole) -> List[X]:
        return [self.actors[r] for r in role.singular_sequences if r in self.actors]

    def render(self, role: SyntagmaticRole=None):
        res = '['
        if role is not None:
            res += str(class_from_address(role)) + ' '

        res += " > ".join([('! ' if role is not None and address == role else '')
                                + str(address) + ' ' + str(self.actors[address].actor)
                           for address in sorted(self.actors)])
        return res + ']'

    @staticmethod
    def from_list(l: List[Tuple[List[Script], X]], type: Script) -> 'SyntagmaticFunction':
        assert all(all(s in ADDRESS_SCRIPTS for s in address) for address, _ in l), "invalid address"

        # determine witch type is
        proc_count = sum(1 if any(a in ADDRESS_PROCESS_VALENCE_SCRIPTS for a in address) else 0 for address, x in l)
        if proc_count == 1:
            return ProcessSyntagmaticFunction._from_list(l)
        elif proc_count > 1:
            raise ValueError("Invalid syntagmatic function, too many process roles")

        act_count = sum(1 if any(a in ACTANTS_SCRIPTS for a in address) else 0 for address, x in l)
        if act_count == 1:
            return ActantSyntagmaticFunction._from_list(l)
        elif act_count > 1:
            raise ValueError("Invalid syntagmatic function, too many actant roles without a process")

        dep_count = sum(1 if address == [DEPENDANT_QUALITY] else 0 for address, x in l)
        if dep_count == 1:
            return DependantQualitySyntagmaticFunction._from_list(l)
        elif dep_count > 1:
            raise ValueError(
                "Invalid syntagmatic function, too many dependant actant roles without a process nor an actant")

        indep_count = sum(1 if address == [INDEPENDANT_QUALITY] else 0 for address, x in l)
        if indep_count == 1:
            assert len(l) == 1
            address, x = l[0]
            return IndependantQualitySyntagmaticFunction(x)
        elif indep_count > 1:
            raise ValueError("Invalid syntagmatic function, too many independant actant roles without a process nor an "
                             "actant nor a dependant actant")

        if type == SYNTAGMATIC_FUNCTION_PROCESS_TYPE_SCRIPT:
            return ProcessSyntagmaticFunction._from_list(l)
        elif type == SYNTAGMATIC_FUNCTION_ACTANT_TYPE_SCRIPT:
            return DependantQualitySyntagmaticFunction._from_list(l)
        elif type == SYNTAGMATIC_FUNCTION_QUALITY_TYPE_SCRIPT:
            if len(l) != 1:
                raise ValueError("Invalid syntagmatic function, too many independant actant roles without a process nor an "
                             "actant nor a dependant actant")
            return IndependantQualitySyntagmaticFunction(l[0][1])

    def check(self, X: Type, check_X):
        if not isinstance(self.actor, X):
            raise ValueError("The process of a SyntagmaticFunction is expected to be a {}, not a {}."
                             .format(X.__name__, self.actor.__class__.__name__))

        check_X(self.actor, role=self.role)

        for address, x in self.actors.items():
            if not isinstance(address, SyntagmaticRole):
                raise ValueError("An address in a SyntagmaticFunction is expected to be a polymorpheme, not a {}."
                                 .format(address.__class__.__name__))

            check_address_script(address.constant)


class IndependantQualitySyntagmaticFunction(SyntagmaticFunction):
    def __init__(self, actor: X):
        super().__init__(actor, {self.role: self})

    @property
    def role(self):
        return (INDEPENDANT_QUALITY,)


class DependantQualitySyntagmaticFunction(SyntagmaticFunction):
    def __init__(self,
                 actor: X,
                 dependant: 'DependantQualitySyntagmaticFunction' = None,
                 independant: List[IndependantQualitySyntagmaticFunction] = (), **kwargs):

        self.dependant = dependant
        self.independant = independant

        res = {self.role: self,
            **{self.role + f.role: f for f in self.independant}}

        if dependant is not None:
            res = {**res,
                   **{self.role + address.constant: f for address, f in self.dependant.actors.items()}}

        super().__init__(actor, res)

    @property
    def role(self):
        return (DEPENDANT_QUALITY,)

    @classmethod
    def _from_list(cls, l: List[Tuple[List[Script], X]]):
        actor = None
        role = None
        _dependant = []
        independant = []

        for address, x in l:
            try:
                _role = next(iter(a for a in address if a in ACTANTS_SCRIPTS))
                if role is not None and _role != role:
                    raise ValueError("Invalid actant syntagmatic function definition, different actants roles in definition.")
                role = _role
            except StopIteration:
                try:
                    _role = next(iter(a for a in address if a == DEPENDANT_QUALITY))
                except StopIteration:
                    raise ValueError("Invalid actant syntagmatic function definition, not a dependant script.")
                role = _role

            if len(address) == 1:
                actor = x
            elif len(address) == 2 and any(a == INDEPENDANT_QUALITY for a in address):
                independant.append(IndependantQualitySyntagmaticFunction(actor=x))
            else:
                _address = list(address)
                _address.remove(role)
                _dependant.append([_address, x])

        dependant = None
        if _dependant:
            dependant = DependantQualitySyntagmaticFunction._from_list(_dependant)

        return cls(actor=actor, role=[role], dependant=dependant, independant=independant)

    def check(self, X, check_X):
        super().check(X, check_X)

        for ind in self.independant:
            if not isinstance(ind, IndependantQualitySyntagmaticFunction):
                raise ValueError("A quality is expected to be a IndependantQualitySyntagmaticFunction, not a {}."
                             .format(ind.__class__.__name__))

            ind.check(X, check_X)

        if self.dependant is not None:
            if not isinstance(self.dependant, DependantQualitySyntagmaticFunction):
                raise ValueError("An actant is expected to be a DependantQualitySyntagmaticFunction, not a {}."
                                 .format(self.dependant.__class__.__name__))

            self.dependant.check(X, check_X)

class ActantSyntagmaticFunction(DependantQualitySyntagmaticFunction):
    def __init__(self,
                 actor: X,
                 role: List[Script],
                 dependant: DependantQualitySyntagmaticFunction = None,
                 independant: List[IndependantQualitySyntagmaticFunction] = ()):

        self._role = tuple(role)
        super().__init__(actor, dependant, independant)

    @property
    def role(self):
        return self._role

class ProcessSyntagmaticFunction(SyntagmaticFunction):
    def __init__(self,
                 actor: X,
                 valence: Script,
                 actants: List[ActantSyntagmaticFunction]):
        self.actants = actants


        self.initiator = None
        self.interactant = None
        self.recipient = None

        self.time = None
        self.location = None
        self.manner = None
        self.cause = None
        self.intention = None

        for a in self.actants:
            if a.role[0] == INITIATOR_SCRIPT:
                self.initiator = a
            elif a.role[0] == INTERACTANT_SCRIPT:
                self.interactant = a
            elif a.role[0] == RECIPIENT_SCRIPT:
                self.recipient = a
            elif a.role[0] == TIME_SCRIPT:
                self.time = a
            elif a.role[0] == LOCATION_SCRIPT:
                self.location = a
            elif a.role[0] == MANNER_SCRIPT:
                self.manner = a
            elif a.role[0] == INTENTION_SCRIPT:
                self.intention = a
            elif a.role[0] == CAUSE_SCRIPT:
                self.cause = a
            else:
                raise ValueError("Invalid role : {}".format(' '.join(map(str, a.role))))

        self.valence = valence

        super().__init__(actor, {
            self.role: self,
            **{address.constant: f for actant in self.actants for address, f in actant.actors.items()}
        })

    @property
    def role(self):
        return (self.valence,)

    @staticmethod
    def _from_list(l: List[Tuple[List[Script], X]]):
        actor = None
        _actants = defaultdict(list)
        valence = None

        for address, x in l:
            if any(a in ADDRESS_PROCESS_VALENCE_SCRIPTS for a in address):
                if len(address) != 1 or actor is not None:
                    raise ValueError("Invalid process syntagmatic function, too many process roles")
                actor = x
                valence = address[0]

            elif any(a in ACTANTS_SCRIPTS for a in address):
                actant_count = sum(1 if a in ACTANTS_SCRIPTS else 0 for a in address)

                if actant_count == 1:
                    role = next(iter(a for a in address if a in ACTANTS_SCRIPTS))
                    _actants[role].append([address, x])
                elif actant_count > 1:
                    raise ValueError("Invalid syntagmatic function, too many actant roles")
            else:
                raise ValueError("Invalid address in a process syntagmatic function {}".format(' '.join(map(str, address))))

        actants = [ActantSyntagmaticFunction._from_list(l_actant) for l_actant in _actants.values()]

        return ProcessSyntagmaticFunction(actor=actor, actants=actants, valence=valence)


    def check(self, X: Type, check_X):
        super().check(X, check_X)

        for actant, role in [(self.initiator, INITIATOR_SCRIPT),
                       (self.interactant, INTERACTANT_SCRIPT),
                       (self.recipient, RECIPIENT_SCRIPT),
                       (self.time, TIME_SCRIPT),
                       (self.location, LOCATION_SCRIPT),
                       (self.intention, INTENTION_SCRIPT),
                       (self.cause, CAUSE_SCRIPT),
                       (self.manner, MANNER_SCRIPT)]:

            if actant is not None:
                if not isinstance(actant, ActantSyntagmaticFunction):
                    raise ValueError("An actant of a word is expected to be a ActantSyntagmaticFunction, not a {}."
                                     .format(actant.__class__.__name__))

                actant.check(X, check_X)
