import os
from io import BytesIO
from typing import List
from uuid import uuid4

import pytest

PATH = os.path.dirname(__file__)
TEST_PATH = os.path.join(PATH, "test_files")


def test_co():
    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1, "boundaries": chem_bounds(1)}
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    model = COCatalyticFOAMModel(**config)
    assert model.chemical_species[0].composition == "CO"
    assert model.velocity.value[0] == 0.1
    assert model.velocity.value[1] == 0.1
    assert model.velocity.value[2] == 0.1
    assert model.velocity.value[2] == 0.1


def test_wrong_velocity_vec():
    from pydantic.error_wrappers import ValidationError

    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config_error = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1, "boundaries": chem_bounds(1)},
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(
        ValidationError, match="ensure this value has at most 3 items"
    ) as err:
        COCatalyticFOAMModel(**config_error)


def test_velocity_vec_too_short():
    from pydantic.error_wrappers import ValidationError

    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config_error = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1, "boundaries": chem_bounds(1)},
        ],
        "velocity": {
            "value": [0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(
        ValidationError, match="ensure this value has at least 3 items"
    ) as err:
        COCatalyticFOAMModel(**config_error)


def test_wrong_composition():
    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config_error = {
        "chemical_species": [
            {"composition": "COA", "mass_fraction": 1, "boundaries": chem_bounds(1)},
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(ValueError, match="Invalid composition") as err:
        COCatalyticFOAMModel(**config_error)


def test_co_from_pkl():
    from pydantic.error_wrappers import ValidationError

    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel
    from osp.wrappers.simcatalyticfoam.settings import ReaxProSettings

    settings = ReaxProSettings()

    from .conftest import store_file
    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    pkl = os.path.join(TEST_PATH, "test.pkl")
    with open(pkl, "rb") as file:
        key = str(store_file(file))

    config = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1, "boundaries": chem_bounds(1)}
        ],
        "species_from_upload": key,
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    model = COCatalyticFOAMModel(**config)
    assert model.chemical_species[0].composition == "CO"

    config_error = {
        "chemical_species": [
            {"composition": "COA", "mass_fraction": 1, "boundaries": chem_bounds(1)}
        ],
        "species_from_upload": key,
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(ValueError, match="Invalid composition") as err:
        COCatalyticFOAMModel(**config_error)


def test_wrong_co_from_pkl_cache():
    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    invalid_uuid = str(uuid4())
    config_error = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1, "boundaries": chem_bounds(1)}
        ],
        "species_from_upload": invalid_uuid,
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(
        ValueError, match=f"Key `{invalid_uuid}` does not exist in cache."
    ) as err:
        COCatalyticFOAMModel(**config_error)


def test_mass_fraction_co():
    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 0.5, "boundaries": chem_bounds(0.5)},
            {"composition": "O2", "mass_fraction": 0.5, "boundaries": chem_bounds(0.5)},
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    model = COCatalyticFOAMModel(**config)
    assert model.chemical_species[0].composition == "CO"
    assert model.chemical_species[0].mass_fraction == 0.5
    assert model.chemical_species[1].composition == "O2"
    assert model.chemical_species[1].mass_fraction == 0.5
    assert model.velocity.value[0] == 0.1
    assert model.velocity.value[1] == 0.1
    assert model.velocity.value[2] == 0.1


def test_invalid_patch():
    from osp.models.catalytic.co_catalyticfoam import Boundary, COCatalyticFOAMModel

    from .utils import p_bounds, t_bounds, u_bounds

    invalid_bounds = [
        {"patch": "foo", "boundary_type": Boundary.wedge},
        {"patch": "wedge2", "boundary_type": Boundary.wedge},
        {"patch": "wedge3", "boundary_type": Boundary.wedge},
        {"patch": "wedge4", "boundary_type": Boundary.wedge},
        {"patch": "inlet", "boundary_type": Boundary.zeroGradient},
        {"patch": "outlet", "boundary_type": Boundary.fixedValue, "value": 1},
        {"patch": "inertWall", "boundary_type": Boundary.zeroGradient},
    ]
    config_error = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1, "boundaries": invalid_bounds},
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(ValueError, match="Invalid patch") as err:
        COCatalyticFOAMModel(**config_error)


def test_invalid_patch_list_match():
    from osp.models.catalytic.co_catalyticfoam import Boundary, COCatalyticFOAMModel

    from .utils import p_bounds, t_bounds, u_bounds

    invalid_bounds = [
        {"patch": "wedge1", "boundary_type": Boundary.wedge},
        {"patch": "wedge2", "boundary_type": Boundary.wedge},
        {"patch": "wedge3", "boundary_type": Boundary.wedge},
        {"patch": "wedge4", "boundary_type": Boundary.wedge},
        {"patch": "inlet", "boundary_type": Boundary.zeroGradient},
        {"patch": "outlet", "boundary_type": Boundary.fixedValue, "value": 1},
        {"patch": "inertWall", "boundary_type": Boundary.zeroGradient},
    ]
    config_error = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1, "boundaries": invalid_bounds},
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(ValueError, match="The provided patches for the species") as err:
        COCatalyticFOAMModel(**config_error)


def test_wrong_mass_co_upper():
    from pydantic.error_wrappers import ValidationError

    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config_error = {
        "chemical_species": [
            {"composition": "CO", "mass_fraction": 1.3, "boundaries": chem_bounds(1.3)},
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(
        ValidationError, match="ensure this value is less than or equal to 1"
    ) as err:
        COCatalyticFOAMModel(**config_error)


def test_wrong_mass_co_lower():
    from pydantic.error_wrappers import ValidationError

    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config_error = {
        "chemical_species": [
            {
                "composition": "CO",
                "mass_fraction": -0.1,
                "boundaries": chem_bounds(-0.1),
            },
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(ValidationError, match="ensure this value ") as err:
        COCatalyticFOAMModel(**config_error)


def test_wrong_mass_sum():
    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config_error = {
        "chemical_species": [
            {
                "composition": "CO",
                "mass_fraction": 0.1,
                "boundaries": chem_bounds(0.1),
            },
            {
                "composition": "O2",
                "mass_fraction": 0.1,
                "boundaries": chem_bounds(0.1),
            },
            {
                "composition": "CO2",
                "mass_fraction": 0.3333,
                "boundaries": chem_bounds(0.3333),
            },
        ],
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    with pytest.raises(
        ArithmeticError,
        match="The sum of `composition` of `chemical_species` must be `1.0`",
    ) as err:
        COCatalyticFOAMModel(**config_error)


def test_mass_sum():
    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel

    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config = {
        "chemical_species": [
            {
                "composition": "CO",
                "mass_fraction": 0.3333,
                "boundaries": chem_bounds(0.3333),
            },
            {
                "composition": "O2",
                "mass_fraction": 0.3333,
                "boundaries": chem_bounds(0.3333),
            },
            {
                "composition": "CO2",
                "mass_fraction": 0.3333,
                "boundaries": chem_bounds(0.3333),
            },
        ],
        "sum_fraction_error": 4,
        "velocity": {
            "value": [0.1, 0.1, 0.1],
            "boundaries": u_bounds([0.1, 0.1, 0.1]),
        },
        "temperature": {"value": 300.0, "boundaries": t_bounds(300.0)},
        "pressure": {"value": 1000.0, "boundaries": p_bounds(1000.0)},
        "catalyst_amount": 1.5e-5,
    }
    model = COCatalyticFOAMModel(**config)
    assert model.chemical_species[0].composition == "CO"
    assert model.chemical_species[0].mass_fraction == 0.3333
    assert model.chemical_species[1].composition == "O2"
    assert model.chemical_species[1].mass_fraction == 0.3333
    assert model.chemical_species[2].composition == "CO2"
    assert model.chemical_species[2].mass_fraction == 0.3333
    assert model.velocity.value[0] == 0.1
    assert model.velocity.value[1] == 0.1
    assert model.velocity.value[2] == 0.1


def test_example_model():
    from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel
    from osp.models.utils.general import _get_example

    example = _get_example("catalyticFoam", "COModel.json")
    assert isinstance(example, dict)
    assert example != {}
    assert example == COCatalyticFOAMModel.Config.schema_extra["example"]
