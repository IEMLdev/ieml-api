from typing import Union

from sqlalchemy.util import NoneType

from ieml.usl import USL


class RelationType:
    def __call__(self, arg0: USL, arg1: USL) -> Union[USL,NoneType]:
        raise NotImplementedError()

    # def iter_relations(self, arg0: USL):
    #     raise NotImplementedError()

