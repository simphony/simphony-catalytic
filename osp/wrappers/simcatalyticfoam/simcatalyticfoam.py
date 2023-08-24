import logging
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

from osp.core.namespaces import emmo
from osp.core.session import SimWrapperSession
from osp.models.catalytic.utils import check_arcp, wrap_arcp

from .catalyticfoam_engine import CatalyticFoamEngine, settings

if TYPE_CHECKING:
    from typing import Any, List

    from osp.core.cuds import Cuds
    from osp.core.ontology import OntologyClass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SimCatalyticFoamSession(SimWrapperSession):
    def __init__(
        self, case: "str" = "laminar_2D_ML", config: "dict" = {}, *args, **kwargs
    ):
        engine = CatalyticFoamEngine(case, config=config)
        super().__init__(engine=engine)

    def __str__(self):
        return "CatalyticFoamSession"

    # OVERRIDE
    def _run(self, root_object) -> None:
        self._engine.run()

    # OVERRIDE
    def _apply_added(self, root_object, buffer) -> None:
        for obj in buffer.values():
            self._wrap(obj)

    # OVERRIDE
    def _wrap(self, cuds: "Cuds") -> None:
        if cuds.is_a(emmo.ChemicalComposition):
            logger.info(f"Found a {emmo.ChemicalComposition}.")
            self._make_new_chemical(cuds)
            self._check_quantity(cuds, emmo.MassFraction)
            self._check_for_boundaries(cuds)
        elif (
            cuds.is_a(emmo.Pressure)
            or cuds.is_a(emmo.ThermodynamicTemperature)
            or cuds.is_a(emmo.Velocity)
        ):
            logger.info(f"Found a {cuds.oclass}.")
            self._check_for_value(cuds)
            self._check_for_boundaries(cuds)
        elif cuds.is_a(emmo.CatalystAmount):
            self._check_for_value(cuds)
        elif (
            cuds.is_a(emmo.EnergyEquation)
            or cuds.is_a(emmo.DiffusivityModel)
            or cuds.is_a(emmo.ProbabilityDistribution)
        ):
            self._wrap_with_label(cuds)
        elif cuds.is_a(emmo.TurbulentModel) or cuds.is_a(emmo.LaminarModel):
            self._check_turbulent_model(cuds)
        elif cuds.is_a(emmo.SimulationTime) and not cuds.is_a(
            emmo.AdjustableSimulationTimeStep
        ):
            self._check_for_value(cuds)
        elif cuds.is_a(emmo.AdjustableSimulationTimeStep):
            self._wrap_arcp(cuds, "yes")

    def _make_new_chemical(self, composition: "Cuds") -> None:
        species = composition.get(oclass=emmo.ChemicalSpecies)
        if species:
            symbol = species.pop().get(oclass=emmo.Symbol)
        if symbol:
            symbol = symbol.pop()
        if check_arcp(symbol):
            logger.info(
                f"Found a {emmo.ChemicalSpecies} for <{composition}> with a {emmo.Symbol}: {symbol.hasSymbolData}."
            )
            self._wrap_arcp(symbol, symbol.hasSymbolData)

    def _check_for_boundaries(self, cuds: "Cuds") -> None:
        boundaries = cuds.get(rel=emmo.hasBoundaryField)
        for obj in boundaries:
            if check_arcp(obj):
                self._wrap_with_label(obj)
            for value in obj.get(rel=emmo.hasSpatialDirectPart):
                self._check_for_value(value)

    def _check_turbulent_model(self, cuds: "Cuds") -> None:
        self._wrap_with_label(cuds)
        if cuds.is_a(emmo.ReynoldsAveragedSimulationModel):
            stype = "RAS"
        elif cuds.is_a(emmo.LargeEddySimulationModel):
            stype = "LES"
        elif cuds.is_a(emmo.LaminarModel):
            stype = None
        else:
            raise TypeError(
                f"""
            Turbulence model `{cuds}` not understood.
            Must be a subclass of `{emmo.ReynoldsAveragedSimulationModel}`,
            `{emmo.LargeEddySimulationModel}` or `{emmo.LaminarModel}`."""
            )
        if stype:
            self.add_to_parser("constant/turbulenceProperties", "simulationType", stype)
            self.add_to_parser(
                "constant/turbulenceProperties", f"{stype}.turbulence", "on"
            )
            self.add_to_parser(
                "constant/turbulenceProperties", f"{stype}.printCoeffs", "on"
            )

    def _wrap_with_label(self, entity: "Cuds") -> None:
        label = self._get_label(entity)
        logger.info(
            f"Found <{entity}> with {label} by annotation {settings.catalyticfoam_label_iri}."
        )
        self._wrap_arcp(entity, label)

    def _get_label(self, obj: "Cuds") -> "str":
        labels = [
            str(o)
            for s, p, o in obj.oclass.get_triples()
            if s == obj.oclass.iri and str(p) == settings.catalyticfoam_label_iri
        ]
        if len(labels) > 1:
            raise ValueError(
                f"More than one OpemFOAM-label for {obj} detected: {labels}. Please check ontology-class."
            )
        elif len(labels) == 0:
            raise ValueError(
                f"No OpemFOAM-label for {obj} detected. Please check ontology-class."
            )
        return labels.pop()

    def _wrap_arcp(self, value: "Cuds", data: "str") -> None:
        result = wrap_arcp(value)
        path = result.path[1:]
        for query in parse_qs(result.query).get("jsonpath"):
            self.add_to_parser(path, query, data)

    def _check_quantity(self, cuds: "Cuds", oclass: "OntologyClass") -> None:
        cuds_list = cuds.get(oclass=oclass)
        logger.info(f"Check <{cuds}> for a related <{oclass}>.")
        if cuds_list:
            self._check_for_value(cuds_list.pop())

    def _check_for_value(self, quantity: "Cuds") -> None:
        value = quantity.get(rel=emmo.hasQuantityValue)
        if value:
            value = value.pop()
            if value.is_a(emmo.Number):
                self._check_number(quantity, value)
            elif value.is_a(emmo.Shape3Vector):
                self._check_vector(quantity, value)

    def _check_number(self, quantity: "Cuds", value: "Cuds") -> None:
        if check_arcp(value):
            logger.info(
                f"Found quantity <{quantity}> with <{value}> valued {value.hasNumericalData}."
            )
            self._wrap_arcp(value, value.hasNumericalData)

    def _check_vector(self, quantity: "Cuds", vector: "Cuds") -> None:
        first = vector.get(rel=emmo.hasSpatialFirst)
        if first:
            first = first.pop()
            self._check_number(quantity, first)
            sec = first.get(rel=emmo.hasSpatialNext)
            if sec:
                sec = sec.pop()
                self._check_number(quantity, sec)
                third = sec.get(rel=emmo.hasSpatialNext)
                if third:
                    third = third.pop()
                    self._check_number(quantity, third)

    @property
    def parse_files(self) -> "dict":
        return self._engine._parse_files

    def add_to_parser(self, path: "str", query: "str", data: "Any") -> None:
        self._engine.add_to_parser(path, query, data)

    @property
    def tarball(cls):
        return cls._engine.tarball

    # OVERRIDE
    def _load_from_backend(self, uids, expired=None) -> "Cuds":
        for uid in uids:
            if uid in self._registry:
                yield self._registry.get(uid)
            else:
                yield None

    # OVERRIDE
    def _apply_added(self, root_object, buffer) -> None:
        for obj in buffer.values():
            self._wrap(obj)

    # OVERRIDE
    def _apply_updated(self, root_object, buffer) -> None:
        pass

    # OVERRIDE
    def _apply_deleted(self, root_object, buffer) -> None:
        pass

    @property
    def config(self) -> dict:
        return self._engine._config

    @property
    def exit_code(self) -> int:
        return self._engine.exit_code
