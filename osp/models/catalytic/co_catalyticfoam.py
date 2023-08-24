import tempfile
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, confloat, root_validator
from pydantic.dataclasses import dataclass
from pydantic.error_wrappers import ValidationError

from osp.core.cuds import Cuds
from osp.core.namespaces import emmo
from osp.core.session import CoreSession
from osp.core.utils import export_cuds
from osp.models.utils.general import _get_example, get_download, get_upload
from osp.wrappers.simcatalyticfoam.utils import (
    _make_boundary_field,
    _make_internal_field,
    _make_value,
)

from .utils import _import_from_pkl, _read_patches, make_arcp

if TYPE_CHECKING:
    from typing import List, Union

    from osp.core.cuds import Cuds
    from osp.core.ontology import OntologyClass


class Boundary(str, Enum):
    """Model with a chosen set of boundary types."""

    fixedValue = "FixedValue"
    fixedGradient = "FixedGradient"
    catalyticWall = "CatalyticWall"
    empty = "Empty"
    zeroGradient = "ZeroGradient"
    processor = "Processor"
    patch = "Patch"
    SymmetryPlane = "SymmetryPlane"
    wedge = "Wedge"
    wall = "Wall"


class TurbulenceModel(str, Enum):
    """Turblence model of the CFD-calculation."""

    kOmegaSST = "KOmegaSST"
    kEpsilon = "KEpsilon"
    laminar = "LaminarModel"
    smagorinsky = "SmagorinskyTurbulenceModel"
    kinetic_energy_equation = "KineticEnergyEquation"


class DiffusivityModel(str, Enum):
    ficks_diffusion = "FicksDiffusion"
    maxwell_diffusion = "MaxwellStefanDiffusion"


class ChemicalComposition(str):
    """Chemical composition of the species."""

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(standard_species=_import_from_pkl())


class Patch(str):
    """Available patches in the regarded use case."""

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(standard_patches=_read_patches())


class BoundaryCondition(BaseModel):
    """Patch and boundary type definition."""

    boundary_type: Boundary = Field(
        Boundary.zeroGradient.value,
        description="Boundary types available in OpenFOAM (most popular ones)",
    )
    patch: Patch = Field(
        ..., description="Patch in the mesh available from the use case."
    )
    value: Optional[Union[float, int, List[confloat(allow_inf_nan=False)]]] = Field(
        None,
        description="""Fixed value (Dirichlet-condition),
        fixed gradient (von-Neumann-condition) or field value at reacting catalyst wall.
        Field will be ignored for other conditions.""",
    )

    @root_validator
    def validate_all(cls, values):
        if values.get("boundary_type") in [
            Boundary.fixedValue,
            Boundary.fixedGradient,
            Boundary.catalyticWall,
        ] and not values.get("value"):
            raise ValidationError(
                """If `boundary` is set to `fixedValue`, `fixedGradient` or `catalyticWall`,
                `value`-field must be set as well."""
            )
        return values

    class Config:
        use_enum_values = True


class BaseQuantity(BaseModel):
    """BaseQuantity for vector and scalar fields."""

    boundaries: List[BoundaryCondition] = Field(
        ...,
        description="""Mapping between available patches and boundary condition.
        NOTE: All patches in the mesh must be defined!""",
    )

    class Config:
        use_enum_values = True


class SolverOptions(BaseModel):
    """Solver options model for diffusivity and turbulence properties."""

    diffusivity_model: DiffusivityModel = Field(
        DiffusivityModel.ficks_diffusion.value,
        description="Diffusivity of the mixture: Fick's multi component diffusion or Maxwell Stefan diffusion.",
    )
    turbulence_model: TurbulenceModel = Field(
        TurbulenceModel.laminar.value,
        description="Turbulence model of the mixture: laminar, RAS or LES.",
    )
    use_energy_equation: bool = Field(
        False, description="Whether the energy equation should be regarded or not."
    )

    class Config:
        use_enum_values = True


class Velocity(BaseQuantity):
    """Velocity model of the mixture."""

    value: List[confloat(allow_inf_nan=False)] = Field(
        ..., description="Velocity vector in m/s.", min_items=3, max_items=3
    )


class Temperature(BaseQuantity):
    """Temperature model of the mixture."""

    value: confloat(allow_inf_nan=False) = Field(
        ..., description="Temperature value of the mixture in K."
    )


class Pressure(BaseQuantity):
    """Pressure model of the mixture."""

    value: confloat(allow_inf_nan=False) = Field(
        ..., description="Pressure value of the mixture in Pa."
    )


class ChemicalSpecies(BaseQuantity):
    """A chemical species with defined properties."""

    composition: ChemicalComposition = Field(
        ...,
        description="""Chemical composition of the species.
        Available subset is forwarded from the standard surrogate model.""",
    )

    mass_fraction: confloat(ge=0, le=1, allow_inf_nan=False) = Field(
        ...,
        description="""Mass fraction of the species within the composition.
        Sum of all mass fractions must be 1.""",
    )


@dataclass
class COCatalyticFOAMModel:
    chemical_species: List[ChemicalSpecies] = Field(
        ..., description="List of chemical species involed into the reaction."
    )
    species_from_upload: Optional[UUID] = Field(
        None,
        description="UUID of the PKL in the cache to be used instead of the standard model",
    )
    patches_from_upload: Optional[UUID] = Field(
        None,
        description="If defined, UUID of the use case tar-ball in the cache to be used instead of the standard use case",
    )
    fraction_sum_error: Optional[int] = Field(
        3,
        description="""Number of decimal places which shall be
    used while rounding sum of mass fractions.
    E.g. the test passes when CO=0.4468 and O2=0.5531 with an error 3 digits,
    but fails for 4 digits.""",
    )
    velocity: Velocity = Field(..., description="Velocity model of the mixture.")
    pressure: Pressure = Field(..., description="Pressure model of the mixture.")
    temperature: Temperature = Field(
        ..., description="Temperature model of the mixture."
    )
    catalyst_amount: confloat(ge=0, le=1, allow_inf_nan=False) = Field(
        ..., description="Amount fraction of catalyst in the reactive wall patch."
    )
    solver_options: SolverOptions = Field(
        SolverOptions(),
        description="Solver options including turbulence and diffusion properties.",
    )

    maxtime: confloat(allow_inf_nan=False) = Field(
        1e-7,
        description="Maximum simulation time in seconds until the simulation should run.",
    )
    delta_t: confloat(allow_inf_nan=False) = Field(
        1e-8,
        description="""Inital time step length in seconds.
    Will be adjusted by the solver when `adjustable_timestep` is set to `True`.
    IMPORTANT: For simplicity, the delta_t is going to be the `writeInterval` of the output files!""",
    )
    adjustable_timestep: bool = Field(
        True,
        description="""Whether the time step should be adjusted according to the Courant–Friedrichs–Lewy-condition
                                     in order to keep the stability of the simulation.""",
    )

    @property
    def session(self) -> CoreSession:
        return self._session

    def __post_init_post_parse__(self):
        with CoreSession() as session:
            calc = emmo.ContinuumCalculation()
            mappings = [
                ("0/p", "pressure", emmo.Pressure),
                ("0/T", "temperature", emmo.ThermodynamicTemperature),
                ("0/U", "velocity", emmo.Velocity),
            ]
            for path, attr, oclass in mappings:
                model = getattr(self, attr)
                quantity = self._make_quantity(path, model, oclass)
                calc.add(quantity, rel=emmo.hasCalculationInput)
            for species in self.chemical_species:
                calc.add(self._make_species(species), rel=emmo.hasCalculationInput)
            calc.add(self._make_continuum_model(), rel=emmo.hasCalculationInput)
            calc.add(self._make_catalyist_amount(), rel=emmo.hasCalculationInput)
        file = tempfile.NamedTemporaryFile(suffix=".ttl")
        export_cuds(session, file.name)
        self._uuid = get_upload(file)
        self._session = session

    def _make_time_constraints(self) -> List[Cuds]:
        if self.maxtime < self.delta_t:
            raise ValueError("`maxtime` must be larger equal `delta_t`!")
        quantities = []
        for oclass, attr, key in [
            (emmo.MaximumSimulationTime, "maxtime", "endTime"),
            (emmo.DeltaSimulationTime, "delta_t", "deltaT"),
            (emmo.SimulationWriteOutputInterval, "delta_t", "writeInterval"),
        ]:
            quantity = oclass()
            value = _make_value("system/controlDict", getattr(self, attr), [key])
            quantity.add(value, rel=emmo.hasQuantityValue)
            quantities.append(quantity)
        return quantities

    def _make_species(self, species: ChemicalSpecies) -> Cuds:
        path = f"0/{species.composition}"
        oclass = emmo.MassFraction
        composition = emmo.ChemicalComposition()
        cspecies = emmo.ChemicalSpecies()
        iri = make_arcp(path, query=dict(jsonpath=[["FoamFile", "object"]]))
        symbol = emmo.Symbol(iri=iri, hasSymbolData=species.composition)
        cspecies.add(symbol)
        mass_fraction = _make_internal_field(path, species.mass_fraction, oclass)
        composition.add(mass_fraction, cspecies, rel=emmo.hasSpatialDirectPart)
        for boundary in species.boundaries:
            bc = _make_boundary_field(
                path,
                boundary.patch,
                emmo[boundary.boundary_type],
                value=boundary.value,
                quantity=oclass,
            )
            composition.add(bc, rel=emmo.hasBoundaryField)
        return composition

    def _make_quantity(
        self, path: "str", quantitymodel: "BaseQuantity", oclass: "OntologyClass"
    ) -> "Cuds":
        quantity = _make_internal_field(path, quantitymodel.value, oclass)
        for boundary in quantitymodel.boundaries:
            bc = _make_boundary_field(
                path,
                boundary.patch,
                emmo[boundary.boundary_type],
                value=boundary.value,
                quantity=oclass,
            )
            quantity.add(bc, rel=emmo.hasBoundaryField)
        return quantity

    def _make_continuum_model(self) -> "Cuds":
        model = emmo.ContinuumModel()

        if self.solver_options.use_energy_equation:
            iri = make_arcp(
                "constant/solverOptions",
                query=dict(jsonpath=[["PhysicalModel", "energyEquation"]]),
            )
            energy_eq = emmo.EnergyEquation(iri=iri)
            model.add(energy_eq, rel=emmo.hasSpatialDirectPart)

        iri = make_arcp(
            "constant/solverOptions",
            query=dict(jsonpath=[["PhysicalModel", "diffusivityModel"]]),
        )
        diffusivity_model = emmo[self.solver_options.diffusivity_model](iri=iri)
        model.add(diffusivity_model, rel=emmo.hasSpatialDirectPart)

        model.add(self._make_turbulent_model(), rel=emmo.hasSpatialDirectPart)
        model.add(*self._make_time_constraints(), rel=emmo.hasSpatialDirectPart)

        if self.adjustable_timestep:
            iri = make_arcp(
                "system/controlDict",
                query=dict(jsonpath=[["adjustTimeStep"]]),
            )
            adjust = emmo.AdjustableSimulationTimeStep(iri=iri)
            model.add(adjust, rel=emmo.hasSpatialDirectPart)
        return model

    def _make_turbulent_model(self) -> "List[Cuds]":
        oclass = emmo[self.solver_options.turbulence_model]
        if oclass.is_subclass_of(emmo.ReynoldsAveragedSimulationModel):
            path = ["RAS", "RASModel"]
        elif oclass.is_subclass_of(emmo.LargeEddySimulationModel):
            path = ["LES", "LESModel"]
        elif oclass.is_subclass_of(emmo.LaminarModel):
            path = ["simulationType"]
        else:
            raise TypeError(
                f"""
            Turbulence model `{oclass}` not understood.
            Must be a subclass of `{emmo.ReynoldsAveragedSimulationModel}`,
            `{emmo.LargeEddySimulationModel}` or `{emmo.LaminarModel}`."""
            )
        iri = make_arcp("constant/turbulenceProperties", query=dict(jsonpath=[path]))
        return oclass(iri=iri)

    def _make_catalyist_amount(self) -> "Cuds":
        iri = make_arcp(
            "constant/solverOptions",
            query=dict(jsonpath=[["PhysicalModel", "alfaCatalyst"]]),
        )
        catalyst_amount = emmo.CatalystAmount()
        catalyst_amount_value = emmo.Real(
            iri=iri, hasNumericalData=self.catalyst_amount
        )
        catalyst_amount.add(catalyst_amount_value, rel=emmo.hasQuantityValue)
        return catalyst_amount

    @root_validator
    def validate_all(cls, values):
        if not values.get("chemical_species"):
            raise ValidationError("`chemical_species` is a mandatory field.")
        species_upload = values.get("species_from_upload")
        patches_upload = values.get("patches_from_upload")
        if not species_upload:
            compositions = _import_from_pkl()
        else:
            compositions = cls._get_species_from_upload(species_upload)
        if not patches_upload:
            patches = _read_patches()
        else:
            patches = cls._get_patches_from_upload(patches_upload)
        cls._validate_species(values, compositions)
        quantities = [
            values.get(key) for key in ["temperature", "pressure", "velocity"]
        ]
        species = [species for species in values.get("chemical_species")]
        cls._check_bounds(species + quantities, patches)
        return values

    @classmethod
    def _validate_species(
        self, values: "Dict[Any, Any]", compositions: "List[str]"
    ) -> None:
        sum_species = 0
        for species in values.get("chemical_species"):
            if species.composition not in compositions:
                raise ValueError(
                    f"Invalid composition `{species.composition}`. Please choose from {compositions}"
                )
            sum_species += species.mass_fraction
        error = values.get("fraction_sum_error")
        rounded = round(sum_species, error)
        if rounded != 1.0:
            raise ArithmeticError(
                f"""The sum of `composition` of `chemical_species` must be `1.0`,
            but it was {rounded}, according to an error of `sum_fraction_error`={error}
            (true unrounded sum is: `{sum_species}`).
            Please decrease of your `sum_fraction_error` or
            check the `composition`-values of your `chemical_species`."""
            )

    @classmethod
    def _check_bounds(self, quantities: "List[Any]", patches: "List[str]") -> None:
        for quantity in quantities:
            list_patches = []
            if quantity:
                for condition in quantity.boundaries:
                    list_patches += [condition.patch]
                    if condition.patch not in patches:
                        raise ValueError(
                            f"Invalid patch `{condition.patch}`. Please choose from: `{patches}`"
                        )
            if sorted(patches) != sorted(list_patches):
                raise ValueError(
                    f"""The provided patches for the species `{quantity}` are inconsistent with
                    the list of required patches from the use case: `{patches}`. Your provided
                    patches were: `{list_patches}`. Please complete the boundary conditions with
                    the needed patches.
                    """
                )

    @classmethod
    def _get_species_from_upload(cls, uuid: UUID) -> List[str]:
        file_path = get_download(uuid, as_file=True)
        return _import_from_pkl(file_path)

    @classmethod
    def _get_patches_from_upload(cls, uuid: UUID) -> List[str]:
        file_path = get_download(uuid, as_file=True)
        return _read_patches(case_path=file_path)

    @property
    def cuds(cls):
        return cls._session.load(cls._session.root).first()

    @property
    def uuid(cls):
        return cls._uuid

    class Config:
        """Pydantic config class for CO catalytic FOAM"""

        schema_extra = {"example": _get_example("catalyticFoam", "COModel.json")}
