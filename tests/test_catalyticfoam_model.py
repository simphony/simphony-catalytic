"""Pytest for the catalyticFOAM with the Pydantic CO-model"""

p_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "p",
    },
    "dimensions": [1, -1, -2, 0, 0, 0, 0],
    "internalField": ["uniform", 100000.0],
    "boundaryField": {
        "inlet": {"type": "zeroGradient"},
        "outlet": {"type": "fixedValue", "value": ["uniform", 100000.0]},
        "inertWall": {"type": "zeroGradient"},
        "reactingWall": {"type": "zeroGradient"},
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}

CO_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "CO",
    },
    "dimensions": [0, 0, 0, 0, 0, 0, 0],
    "internalField": ["uniform", 0.00000945945945945946],
    "boundaryField": {
        "inlet": {"type": "fixedValue", "value": ["uniform", 0.00000945945945945946]},
        "outlet": {"type": "zeroGradient"},
        "inertWall": {
            "type": "zeroGradient",
        },
        "reactingWall": {
            "type": "catalyticWall",
            "value": ["uniform", 0.00000945945945945946],
        },
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}


co2_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "CO2",
    },
    "dimensions": [0, 0, 0, 0, 0, 0, 0],
    "internalField": ["uniform", 0.567558108108108],
    "boundaryField": {
        "inlet": {"type": "fixedValue", "value": ["uniform", 0.567558108108108]},
        "outlet": {"type": "zeroGradient"},
        "inertWall": {
            "type": "zeroGradient",
        },
        "reactingWall": {
            "type": "catalyticWall",
            "value": ["uniform", 0.567558108108108],
        },
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}


O2_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "O2",
    },
    "dimensions": [0, 0, 0, 0, 0, 0, 0],
    "internalField": ["uniform", 0.432432432432432],
    "boundaryField": {
        "inlet": {"type": "fixedValue", "value": ["uniform", 0.432432432432432]},
        "outlet": {"type": "zeroGradient"},
        "inertWall": {
            "type": "zeroGradient",
        },
        "reactingWall": {
            "type": "catalyticWall",
            "value": ["uniform", 0.4324324324324328],
        },
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}

U_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volVectorField",
        "location": '"0"',
        "object": "U",
    },
    "boundaryField": {
        "inertWall": {"type": "fixedValue", "value uniform": [0.0, 0.0, 1.0]},
        "inlet": {"type": "fixedValue", "value uniform": [0.0, 0.0, 1.0]},
        "outlet": {"type": "zeroGradient"},
        "reactingWall": {"type": "fixedValue", "value uniform": [0.0, 0.0, 1.0]},
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
    "dimensions": [0, 1, -1, 0, 0, 0, 0],
    "internalField": ["uniform", [0.0, 0.0, 1.0]],
}

T_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "T",
    },
    "dimensions": [0, 0, 0, 1, 0, 0, 0],
    "internalField": ["uniform", 900.0],
    "boundaryField": {
        "inlet": {"type": "fixedValue", "value": ["uniform", 900.0]},
        "outlet": {"type": "zeroGradient"},
        "inertWall": {"type": "zeroGradient"},
        "reactingWall": {"type": "catalyticWall", "value": ["uniform", 900.0]},
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}


theta_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "thetaDefault",
    },
    "dimensions": [0, 0, 0, 0, 0, 0, 0],
    "internalField": ["uniform", 0],
    "boundaryField": {
        "inlet": {"type": "zeroGradient"},
        "outlet": {"type": "zeroGradient"},
        "inertWall": {"type": "zeroGradient"},
        "reactingWall": {"type": "fixedValue", "value": ["uniform", 0]},
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}

y_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "ascii",
        "class": "volScalarField",
        "location": '"1"',
        "object": "Ydefault",
    },
    "dimensions": [0, 0, 0, 0, 0, 0, 0],
    "internalField": ["uniform", 0],
    "boundaryField": {
        "reactingWall": {"type": "catalyticWall", "value": ["uniform", 0]},
        "inertWall": {"type": "zeroGradient"},
        "inlet": {"type": "fixedValue", "value": ["uniform", 0]},
        "outlet": {"type": "zeroGradient"},
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}

turbulence_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "ascii",
        "class": "dictionary",
        "location": '"constant"',
        "object": "turbulenceProperties",
    },
    "simulationType": "RAS",
    "RAS": {"RASModel": "kEpsilon", "turbulence": "on", "printCoeffs": "on"},
}

solver_expected = {
    "FoamFile": {
        "version": 2.3,
        "format": "binary",
        "class": "dictionary",
        "location": '"constant"',
        "object": "solverOptions",
    },
    "MachineLearning": {
        "MLSurrogate": "on",
        "MachineLearningFile": '"ml_ExtraTrees_forCFD.pkl"',
    },
    "PhysicalModel": {
        "strangAlgorithm": '"TransportReactionMomentum"',
        "homogeneousReactions": "off",
        "heterogeneousReactions": "on",
        "alfaCatalyst": 1.5e-05,
        "Sct": 0.7,
        "Prt": 0.7,
        "catalyticWalls": ["reactingWall"],
        "energyEquation": "on",
        "reactionHeatFromHeterogeneousReactions": "on",
        "constPressureBatchReactor": True,
        "massDiffusionInEnergyEquation": "on",
        "diffusivityModel": "fick-multi-component",
        "includeDpDt": "off",
        "soretEffect": "off",
    },
    "OdeHomogeneous": {
        "odeSolver": '"OpenSMOKE"',
        "relTolerance": 1e-07,
        "absTolerance": 1e-12,
        "maximumOrder": 5,
        "fullPivoting": False,
    },
    "OdeHeterogeneous": {
        "odeSolver": '"OpenSMOKE"',
        "relTolerance": 1e-07,
        "absTolerance": 1e-12,
        "maximumOrder": 5,
        "fullPivoting": False,
    },
    "LewisNumbers": {"O2": 1.0, "H2": 1.1, "H2O": 1.2, "N2": 1.3},
    "#include": '"isatOptions"',
}

control_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "ascii",
        "class": "dictionary",
        "location": '"system"',
        "object": "controlDict",
    },
    "application": "catalyticFoam",
    "startFrom": "startTime",
    "startTime": 0,
    "stopAt": "endTime",
    "endTime": 1e-07,
    "deltaT": 1e-08,
    "writeControl": "adjustableRunTime",
    "writeInterval": 1e-08,
    "purgeWrite": 0,
    "writeFormat": "ascii",
    "writePrecision": 18,
    "writeCompression": "uncompressed",
    "timeFormat": "general",
    "timePrecision": 6,
    "runTimeModifiable": "yes",
    "adjustTimeStep": "yes",
    "maxCo": 0.1,
    "libs": ['"libCatalyticWall.so"'],
}


def test_foam_model():
    import os
    import tempfile

    from osp.core.namespaces import cuba
    from osp.core.utils import import_cuds
    from osp.models.catalytic.co_catalyticfoam import (
        COCatalyticFOAMModel,
        TurbulenceModel,
    )
    from osp.wrappers.simcatalyticfoam.parsers import run_parser
    from osp.wrappers.simcatalyticfoam.simcatalyticfoam import SimCatalyticFoamSession

    from .conftest import return_file
    from .utils import chem_bounds, p_bounds, t_bounds, u_bounds

    config = {
        "chemical_species": [
            {
                "composition": "O2",
                "mass_fraction": 0.432432432432432,
                "boundaries": chem_bounds(0.432432432432432),
            },
            {
                "composition": "CO",
                "mass_fraction": 0.00000945945945945946,
                "boundaries": chem_bounds(0.00000945945945945946),
            },
            {
                "composition": "CO2",
                "mass_fraction": 0.567558108108108,
                "boundaries": chem_bounds(0.567558108108108),
            },
        ],
        "velocity": {
            "value": [0.0, 0.0, 1.0],
            "boundaries": u_bounds([0.0, 0.0, 1.0]),
        },
        "temperature": {"value": 900.0, "boundaries": t_bounds(900.0)},
        "pressure": {"value": 100000.0, "boundaries": p_bounds(100000.0)},
        "catalyst_amount": 1.5e-05,
        "solver_options": {
            "use_energy_equation": True,
            "turbulence_model": TurbulenceModel.kEpsilon,
        },
    }
    model = COCatalyticFOAMModel(**config)
    cuds_file = return_file(model.uuid)

    # check if catalyticFoam is installed
    config = dict(
        commands=[
            dict(
                exec="echo",
                args="hello world",
            )
        ],
        directory=tempfile.TemporaryDirectory().name,
        filename=f"{tempfile.NamedTemporaryFile().name}.tar",
    )

    session = SimCatalyticFoamSession(config=config)
    wrapper = cuba.Wrapper(session=session)
    cuds = import_cuds(cuds_file, session=session)
    wrapper.add(*cuds, rel=cuba.relationship)
    session.run()

    p = run_parser(os.path.join(session.config["directory"], "0", "p"))
    T = run_parser(os.path.join(session.config["directory"], "0", "T"))
    U = run_parser(os.path.join(session.config["directory"], "0", "U"))
    CO = run_parser(os.path.join(session.config["directory"], "0", "CO"))
    co2 = run_parser(os.path.join(session.config["directory"], "0", "CO2"))
    y = run_parser(os.path.join(session.config["directory"], "0", "Ydefault"))
    theta = run_parser(os.path.join(session.config["directory"], "0", "thetaDefault"))
    turbulence = run_parser(
        os.path.join(session.config["directory"], "constant", "turbulenceProperties")
    )
    solver = run_parser(
        os.path.join(session.config["directory"], "constant", "solverOptions")
    )
    control = run_parser(
        os.path.join(session.config["directory"], "system", "controlDict")
    )

    assert p == p_expected

    assert T == T_expected

    assert CO == CO_expected

    assert co2 == co2_expected

    assert theta == theta_expected

    assert y == y_expected

    assert U == U_expected

    assert solver == solver_expected

    assert turbulence == turbulence_expected

    assert control == control_expected

    assert session.exit_code == 0
