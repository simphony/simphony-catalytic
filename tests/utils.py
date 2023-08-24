"""Utilities for pytests for Reaxpro wrappers."""

from osp.models.catalytic.co_catalyticfoam import Boundary


def chem_bounds(value: "float") -> "Dict[Any, Any]":
    return [
        {"patch": "wedge1", "boundary_type": Boundary.wedge},
        {"patch": "wedge2", "boundary_type": Boundary.wedge},
        {"patch": "wedge3", "boundary_type": Boundary.wedge},
        {"patch": "wedge4", "boundary_type": Boundary.wedge},
        {"patch": "inlet", "boundary_type": Boundary.fixedValue, "value": value},
        {"patch": "outlet", "boundary_type": Boundary.zeroGradient},
        {"patch": "inertWall", "boundary_type": Boundary.zeroGradient},
        {
            "patch": "reactingWall",
            "boundary_type": Boundary.catalyticWall,
            "value": value,
        },
    ]


def u_bounds(value: "float") -> "Dict[Any, Any]":
    return [
        {"patch": "inlet", "boundary_type": Boundary.fixedValue, "value": value},
        {"patch": "outlet", "boundary_type": Boundary.zeroGradient},
        {"patch": "inertWall", "boundary_type": Boundary.fixedValue, "value": value},
        {"patch": "reactingWall", "boundary_type": Boundary.fixedValue, "value": value},
        {"patch": "wedge1", "boundary_type": Boundary.wedge},
        {"patch": "wedge2", "boundary_type": Boundary.wedge},
        {"patch": "wedge3", "boundary_type": Boundary.wedge},
        {"patch": "wedge4", "boundary_type": Boundary.wedge},
    ]


def t_bounds(value: "float") -> "Dict[Any, Any]":
    return [
        {"patch": "inlet", "boundary_type": Boundary.fixedValue, "value": value},
        {"patch": "outlet", "boundary_type": Boundary.zeroGradient},
        {"patch": "inertWall", "boundary_type": Boundary.zeroGradient},
        {
            "patch": "reactingWall",
            "boundary_type": Boundary.catalyticWall,
            "value": value,
        },
        {"patch": "wedge1", "boundary_type": Boundary.wedge},
        {"patch": "wedge2", "boundary_type": Boundary.wedge},
        {"patch": "wedge3", "boundary_type": Boundary.wedge},
        {"patch": "wedge4", "boundary_type": Boundary.wedge},
    ]


def p_bounds(value: "float") -> "Dict[Any, Any]":
    return [
        {"patch": "inlet", "boundary_type": Boundary.zeroGradient},
        {"patch": "outlet", "boundary_type": Boundary.fixedValue, "value": value},
        {"patch": "inertWall", "boundary_type": Boundary.zeroGradient},
        {"patch": "reactingWall", "boundary_type": Boundary.zeroGradient},
        {"patch": "wedge1", "boundary_type": Boundary.wedge},
        {"patch": "wedge2", "boundary_type": Boundary.wedge},
        {"patch": "wedge3", "boundary_type": Boundary.wedge},
        {"patch": "wedge4", "boundary_type": Boundary.wedge},
    ]
