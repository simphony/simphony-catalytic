import os
import shutil
import tempfile

from osp.core.namespaces import cuba, emmo
from osp.models.catalytic.utils import make_arcp
from osp.wrappers.simcatalyticfoam.parsers import run_parser
from osp.wrappers.simcatalyticfoam.simcatalyticfoam import SimCatalyticFoamSession
from osp.wrappers.simcatalyticfoam.utils import (
    _make_boundary_field,
    _make_internal_field,
)

p_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "p",
    },
    "dimensions": [1, -1, -2, 0, 0, 0, 0],
    "internalField": ["uniform", 100000],
    "boundaryField": {
        "inlet": {"type": "zeroGradient"},
        "outlet": {"type": "fixedValue", "value": ["uniform", 100000]},
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
    "internalField": ["uniform", 9.45945945945946e-06],
    "boundaryField": {
        "inlet": {"type": "fixedValue", "value": ["uniform", 9.45945945945946e-06]},
        "outlet": {"type": "zeroGradient"},
        "inertWall": {
            "type": "zeroGradient",
        },
        "reactingWall": {
            "type": "catalyticWall",
            "value": ["uniform", 9.45945945945946e-06],
        },
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
}


n2_expected = {
    "FoamFile": {
        "version": 2.0,
        "format": "binary",
        "class": "volScalarField",
        "location": '"0"',
        "object": "N2",
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
        "inertWall": {"type": "fixedValue", "value uniform": [0, 0, 1]},
        "inlet": {"type": "fixedValue", "value uniform": [0, 0, 1]},
        "outlet": {"type": "zeroGradient"},
        "reactingWall": {"type": "fixedValue", "value uniform": [0, 0, 1]},
        "wedge1": {"type": "wedge"},
        "wedge2": {"type": "wedge"},
        "wedge3": {"type": "wedge"},
        "wedge4": {"type": "wedge"},
    },
    "dimensions": [0, 1, -1, 0, 0, 0, 0],
    "internalField": ["uniform", [0, 0, 1]],
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
    "internalField": ["uniform", 900],
    "boundaryField": {
        "inlet": {"type": "fixedValue", "value": ["uniform", 900]},
        "outlet": {"type": "zeroGradient"},
        "inertWall": {"type": "zeroGradient"},
        "reactingWall": {"type": "catalyticWall", "value": ["uniform", 900]},
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
    "simulationType": "laminar",
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


def test_foam():
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

    #############################################################################################

    #                                   CO

    ############################################################################################

    CO_composition = emmo.ChemicalComposition()

    CO = emmo.ChemicalSpecies()

    iri = make_arcp("0/CO", query=dict(jsonpath=[["FoamFile", "object"]]))
    CO_symbol = emmo.Symbol(iri=iri, hasSymbolData="CO")

    CO.add(CO_symbol)  # Check alternative relation

    CO_composition.add(CO, rel=emmo.hasSpatialDirectPart)

    val = 9.45945945945946e-06

    ###### internalField

    mass_fraction = _make_internal_field("0/CO", val, emmo.MassFraction)

    CO_composition.add(mass_fraction, rel=emmo.hasSpatialDirectPart)

    ###### BoundaryField

    ### reactingwall
    bc = _make_boundary_field(
        "0/CO",
        "reactingWall",
        emmo.CatalyticWall,
        quantity=emmo.MassFraction,
        value=val,
    )
    CO_composition.add(bc, rel=emmo.hasBoundaryField)

    ### inlet
    bc = _make_boundary_field(
        "0/CO", "inlet", emmo.FixedValue, quantity=emmo.MassFraction, value=val
    )
    CO_composition.add(bc, rel=emmo.hasBoundaryField)

    ### inertWall, outlet, wedges
    for patch, condition in [
        ("inertWall", emmo.ZeroGradient),
        ("outlet", emmo.ZeroGradient),
        ("wedge1", emmo.Wedge),
        ("wedge2", emmo.Wedge),
        ("wedge3", emmo.Wedge),
        ("wedge4", emmo.Wedge),
    ]:
        bc = _make_boundary_field("0/CO", patch, condition)
        CO_composition.add(bc, rel=emmo.hasBoundaryField)

    ######################################################################################

    #                                   Nitrogen

    ######################################################################################

    n2_composition = emmo.ChemicalComposition()

    n2 = emmo.ChemicalSpecies()

    iri = make_arcp("0/N2", query=dict(jsonpath=[["FoamFile", "object"]]))
    n2_symbol = emmo.Symbol(iri=iri, hasSymbolData="N2")

    n2.add(n2_symbol)  # Check alternative relation

    n2_composition.add(n2, rel=emmo.hasSpatialDirectPart)

    val = 0.567558108108108

    ###### internalField

    mass_fraction = _make_internal_field("0/N2", val, emmo.MassFraction)
    n2_composition.add(mass_fraction, rel=emmo.hasSpatialDirectPart)

    ###### BoundaryField

    ### reactingwall
    bc = _make_boundary_field(
        "0/N2",
        "reactingWall",
        emmo.CatalyticWall,
        value=val,
        quantity=emmo.MassFraction,
    )
    n2_composition.add(bc, rel=emmo.hasBoundaryField)

    ### inlet
    bc = _make_boundary_field(
        "0/N2", "inlet", emmo.FixedValue, value=val, quantity=emmo.MassFraction
    )
    n2_composition.add(bc, rel=emmo.hasBoundaryField)

    ### inertWall, outlet, wedges
    for patch, condition in [
        ("inertWall", emmo.ZeroGradient),
        ("outlet", emmo.ZeroGradient),
        ("wedge1", emmo.Wedge),
        ("wedge2", emmo.Wedge),
        ("wedge3", emmo.Wedge),
        ("wedge4", emmo.Wedge),
    ]:
        bc = _make_boundary_field("0/N2", patch, condition)
        n2_composition.add(bc, rel=emmo.hasBoundaryField)

    ######################################################################################

    #                                   Oxygen

    ######################################################################################

    O2_composition = emmo.ChemicalComposition()

    O2 = emmo.ChemicalSpecies()

    iri = make_arcp("0/O2", query=dict(jsonpath=[["FoamFile", "object"]]))
    O2_symbol = emmo.Symbol(iri=iri, hasSymbolData="O2")

    O2.add(O2_symbol)  # Check alternative relation

    O2_composition.add(CO, rel=emmo.hasSpatialDirectPart)

    ###### internalField

    val = 0.432432432432432

    mass_fraction = _make_internal_field("0/O2", val, emmo.MassFraction)

    O2_composition.add(mass_fraction, rel=emmo.hasSpatialDirectPart)

    ###### BoundaryField

    ### reactingwall
    bc = _make_boundary_field(
        "0/O2",
        "reactingWall",
        emmo.CatalyticWall,
        value=val,
        quantity=emmo.MassFraction,
    )
    O2_composition.add(bc, rel=emmo.hasBoundaryField)

    ### inlet
    bc = _make_boundary_field(
        "0/O2", "inlet", emmo.FixedValue, value=val, quantity=emmo.MassFraction
    )
    O2_composition.add(bc, rel=emmo.hasBoundaryField)

    # inertwall, outlet, wedges
    for patch, condition in [
        ("inertWall", emmo.ZeroGradient),
        ("outlet", emmo.ZeroGradient),
        ("wedge1", emmo.Wedge),
        ("wedge2", emmo.Wedge),
        ("wedge3", emmo.Wedge),
        ("wedge4", emmo.Wedge),
    ]:
        bc = _make_boundary_field("0/O2", patch, condition)
        O2_composition.add(bc, rel=emmo.hasBoundaryField)

    ######################################################################################

    #                                   Pressure

    ######################################################################################

    val = 100000

    ##### internalField

    pressure = _make_internal_field("0/p", val, emmo.Pressure)

    ##### BoundaryField

    ### outlet
    bc = _make_boundary_field(
        "0/p", "outlet", emmo.FixedValue, value=val, quantity=emmo.Pressure
    )
    pressure.add(bc, rel=emmo.hasBoundaryField)

    ### reactingWall, inertwall, inlet, wedges
    for patch, condition in [
        ("inertWall", emmo.ZeroGradient),
        ("reactingWall", emmo.ZeroGradient),
        ("inlet", emmo.ZeroGradient),
        ("wedge1", emmo.Wedge),
        ("wedge2", emmo.Wedge),
        ("wedge3", emmo.Wedge),
        ("wedge4", emmo.Wedge),
    ]:
        bc = _make_boundary_field("0/p", patch, condition)
        pressure.add(bc, rel=emmo.hasBoundaryField)

    ######################################################################################

    #                                   Temperature

    ######################################################################################

    val = 900

    ###### internalField

    temperature = _make_internal_field("0/T", val, emmo.ThermodynamicTemperature)

    ###### boundaryField

    ### reactingwall
    bc = _make_boundary_field(
        "0/T",
        "reactingWall",
        emmo.CatalyticWall,
        value=val,
        quantity=emmo.ThermodynamicTemperature,
    )
    temperature.add(bc, rel=emmo.hasBoundaryField)

    ### inlet
    bc = _make_boundary_field(
        "0/T",
        "inlet",
        emmo.FixedValue,
        value=val,
        quantity=emmo.ThermodynamicTemperature,
    )
    temperature.add(bc, rel=emmo.hasBoundaryField)

    ### inertwall, outlet, wedges
    for patch, condition in [
        ("inertWall", emmo.ZeroGradient),
        ("outlet", emmo.ZeroGradient),
        ("wedge1", emmo.Wedge),
        ("wedge2", emmo.Wedge),
        ("wedge3", emmo.Wedge),
        ("wedge4", emmo.Wedge),
    ]:
        bc = _make_boundary_field("0/T", patch, condition)
        temperature.add(bc, rel=emmo.hasBoundaryField)

    ######################################################################################

    #                                   Velocity

    ######################################################################################

    val = [0, 0, 1]

    ###### internalField

    velocity = _make_internal_field("0/U", val, emmo.Velocity)

    ###### boundaryField

    # reactingWall, inlet, inertWall, wedges
    for patch in ["reactingWall", "inlet", "inertWall"]:
        bc = _make_boundary_field(
            "0/U", patch, emmo.FixedValue, value=val, quantity=emmo.Velocity
        )
        velocity.add(bc, rel=emmo.hasBoundaryField)

    # outlet, wedges
    for patch, condition in [
        ("outlet", emmo.ZeroGradient),
        ("wedge1", emmo.Wedge),
        ("wedge2", emmo.Wedge),
        ("wedge3", emmo.Wedge),
        ("wedge4", emmo.Wedge),
    ]:
        bc = _make_boundary_field("0/U", patch, condition)
        velocity.add(bc, rel=emmo.hasBoundaryField)

    ######################################################################################

    # Create calculation

    calc = emmo.ContinuumCalculation()

    # Solver options

    iri = make_arcp(
        "constant/solverOptions",
        query=dict(jsonpath=[["PhysicalModel", "alfaCatalyst"]]),
    )
    catalyst_amount = emmo.CatalystAmount()
    catalyst_amount_value = emmo.Real(iri=iri, hasNumericalData=1.5e-5)
    catalyst_amount.add(catalyst_amount_value, rel=emmo.hasQuantityValue)

    iri = make_arcp(
        "constant/solverOptions",
        query=dict(jsonpath=[["PhysicalModel", "energyEquation"]]),
    )
    energy_eq = emmo.EnergyEquation(iri=iri)

    iri = make_arcp(
        "constant/solverOptions",
        query=dict(jsonpath=[["PhysicalModel", "diffusivityModel"]]),
    )
    diffusivity_model = emmo.FicksDiffusion(iri=iri)

    iri = make_arcp(
        "constant/turbulenceProperties", query=dict(jsonpath=[["simulationType"]])
    )
    turbulent_model = emmo.LaminarModel(iri=iri)

    model = emmo.ContinuumModel()
    model.add(
        energy_eq,
        diffusivity_model,
        turbulent_model,
        rel=emmo.hasSpatialDirectPart,
    )

    calc.add(
        CO_composition,
        n2_composition,
        O2_composition,
        pressure,
        temperature,
        velocity,
        model,
        catalyst_amount,
        rel=emmo.hasCalculationInput,
    )

    session = SimCatalyticFoamSession(config=config)
    wrapper = cuba.Wrapper(session=session)
    wrapper.add(calc, rel=cuba.relationship)
    session.run()

    p = run_parser(os.path.join(session.config["directory"], "0", "p"))
    T = run_parser(os.path.join(session.config["directory"], "0", "T"))
    U = run_parser(os.path.join(session.config["directory"], "0", "U"))
    CO = run_parser(os.path.join(session.config["directory"], "0", "CO"))
    n2 = run_parser(os.path.join(session.config["directory"], "0", "N2"))
    y = run_parser(os.path.join(session.config["directory"], "0", "Ydefault"))
    theta = run_parser(os.path.join(session.config["directory"], "0", "thetaDefault"))
    turbulence = run_parser(
        os.path.join(session.config["directory"], "constant", "turbulenceProperties")
    )
    solver = run_parser(
        os.path.join(session.config["directory"], "constant", "solverOptions")
    )

    assert p == p_expected

    assert U == U_expected

    assert T == T_expected

    assert CO == CO_expected

    assert n2 == n2_expected

    assert theta == theta_expected

    assert y == y_expected

    assert solver == solver_expected

    assert turbulence == turbulence_expected

    assert session.exit_code == 0
