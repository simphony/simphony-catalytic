from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode

from osp.core.namespaces import emmo
from osp.models.catalytic.utils import make_arcp

if TYPE_CHECKING:
    from typing import List, Union

    from osp.core.cuds import Cuds
    from osp.core.ontology import OntologyClass


def _make_internal_field(
    filepath: "str", value: "Union[int, float, List[float]]", oclass: "OntologyClass"
) -> "Cuds":
    quantity = oclass()
    # value
    path = ["internalField", "1"]
    if isinstance(value, float) or isinstance(value, int):
        value = _make_value(filepath, value, path)
    elif isinstance(value, list):
        value = _make_vector(filepath, value, path)
    else:
        raise TypeError("`value` must be type `int`, `float` or `list`.")
    quantity.add(value, rel=emmo.hasQuantityValue)
    # distribution
    iri = make_arcp(
        filepath,
        query=dict(
            jsonpath=[["internalField", "0"]],
        ),
    )
    distribution = emmo.UniformDistribution(iri=iri)
    quantity.add(distribution, rel=emmo.hasSpatialDirectPart)
    return quantity


def _make_boundary_field(
    filepath: "str",
    patch: "str",
    oclass_boundary: "OntologyClass",
    quantity: "OntologyClass" = None,
    value: "Union[int, float, List[float]]" = None,
) -> "Cuds":
    # type
    iri = make_arcp(filepath, query=dict(jsonpath=[["boundaryField", patch, "type"]]))
    bc = oclass_boundary(iri=iri)
    if value and quantity:
        quantity = quantity()
        # key
        if "gradient" in oclass_boundary.name.lower():
            key = "gradient"
        else:
            key = "value"
        # value
        path = ["boundaryField", patch, key]
        if isinstance(value, float) or isinstance(value, int):
            value = _make_value(filepath, value, path + ["1"])
        elif isinstance(value, list):
            value = _make_vector(filepath, value, path + ["1"])
        else:
            raise TypeError("`value` must be type `int`, `float` or `list`.")
        quantity.add(value, rel=emmo.hasQuantityValue)
        # distribution
        iri = make_arcp(
            filepath,
            query=dict(
                jsonpath=[
                    path + ["0"],
                ]
            ),
        )
        distribution = emmo.UniformDistribution(iri=iri)
        quantity.add(distribution, rel=emmo.hasSpatialDirectPart)
        bc.add(quantity, rel=emmo.hasSpatialDirectPart)
    return bc


def _make_value(
    filepath: "str",
    value: "Union[int, float]",
    path: "List[str]",
    oclass: "OntologyClass" = emmo.Real,
) -> "Cuds":
    iri = make_arcp(
        filepath,
        query=dict(jsonpath=[path]),
    )
    return oclass(iri=iri, hasNumericalData=value)


def _make_vector(filepath: "str", value: "List[float]", base: "List[str]") -> "Cuds":
    vector = emmo.Shape3Vector()
    components = []
    for i, val in enumerate(value):
        iri = make_arcp(
            filepath,
            query=dict(
                jsonpath=[
                    base + [str(i)],
                ]
            ),
        )
        components.append(emmo.Real(iri=iri, hasNumericalData=val))
    vector.add(components[0], rel=emmo.hasSpatialFirst)
    vector.add(components[2], rel=emmo.hasSpatialLast)
    components[0].add(components[1], rel=emmo.hasSpatialNext)
    components[1].add(components[2], rel=emmo.hasSpatialNext)
    return vector
