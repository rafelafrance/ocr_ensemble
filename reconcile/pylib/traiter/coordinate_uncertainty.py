from typing import Any

from ..base import Base
from ..darwin_core import SEP


class CoordinateUncertainty(Base):
    label = "dwc:coordinateUncertaintyInMeters"
    aliases = Base.get_aliases(label, "")

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        o_val = cls.search(other, cls.aliases)

        if isinstance(o_val, list):
            return {cls.label: SEP.join(o_val)}
        elif o_val:
            return {cls.label: o_val}
        elif t_val := traiter.get(cls.label):
            return {cls.label: t_val}
        return {}
