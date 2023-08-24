"""Full multiscale workflow from atomistic to continuum."""

import tempfile
import warnings

from pydantic import Field
from pydantic.dataclasses import dataclass

from osp.core.namespaces import crystallography, emmo
from osp.core.session import CoreSession
from osp.core.utils import export_cuds
from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel
from osp.models.multiscale.co_pt111_meso import (
    BindingSite,
    COMolarFractionRange,
    PESExploration,
    ZGBModel,
)
from osp.models.utils.general import _get_example_json, get_upload
from osp.models.zacros.co_pyzacros import COpyZacrosModel

STANDARD_XYZ = [
    ("4442d5c3-4b61-4b13-9bbb-fdf942776ca6", "CO_ads+Pt111.xyz"),
]


@dataclass
class ContinuumModel(COCatalyticFOAMModel):
    """Continuum model for full multiscale workflow."""

    class Config:
        """Pydantic model."""

        exclude = {"species_from_upload"}


@dataclass
class ZacrosModel(COpyZacrosModel):
    """Continuum model for full multiscale workflow."""

    class Config:
        """Pydantic model."""

        exclude = {"apd"}


@dataclass
class COPt111FullscaleModel:
    """Pydantic model describing the Full scale for CO oxidation."""

    pes_exploration: PESExploration = Field(
        ..., description="AMS data model for PESExploration."
    )
    binding_site: BindingSite = Field(
        ...,
        description="""data model for binding site calculation
        based on the previous PESExploraion.""",
    )
    zgb_model: ZGBModel = Field(..., description="ZGB model for mesoscopic scale.")

    adp: COMolarFractionRange = Field(
        ...,
        description="""Molar fractions of CO
        for the adaptive design procedure""",
    )

    catalyticfoam: ContinuumModel = Field(
        ..., description="Data model for continuum scale."
    )

    def __post_init_post_parse__(self):
        with CoreSession() as session:
            workflow = emmo.Workflow()
            apd = emmo.AdaptiveDesignProcedure()
            apd.add(self.adp.cuds, rel=emmo.hasInput)
            for oclass in [
                emmo.ForceFieldIdentifierString,
                emmo.Solver,
                emmo.FixedRegion,
                emmo.MaximumEnergy,
                emmo.NeighborCutoff,
                emmo.ReferenceRegion,
                emmo.RandomSeed,
                emmo.MolecularGeometry,
                crystallography.UnitCell,
            ]:
                input_cuds = self.pes_exploration.cuds.get(
                    oclass=oclass, rel=emmo.hasInput
                )
                self.binding_site.cuds.add(input_cuds.pop(), rel=emmo.hasInput)
            self.pes_exploration.cuds.add(
                self.binding_site.cuds, rel=emmo.hasSpatialNext
            )
            self.binding_site.cuds.add(self.zgb_model.cuds, rel=emmo.hasSpatialNext)
            self.zgb_model.cuds.add(apd, rel=emmo.hasSpatialNext)
            apd.add(self.catalyticfoam.cuds, rel=emmo.hasSpatialNext)
            workflow.add(self.pes_exploration.cuds, rel=emmo.hasSpatialFirst)
            workflow.add(self.binding_site.cuds, rel=emmo.hasSpatialDirectPart)
            workflow.add(self.zgb_model.cuds, rel=emmo.hasSpatialDirectPart)
            workflow.add(apd, rel=emmo.hasSpatialDirectPart)
            workflow.add(self.catalyticfoam.cuds, rel=emmo.hasSpatialLast)

        file = tempfile.NamedTemporaryFile(suffix=".ttl", delete=False)
        export_cuds(session, file.name)
        self._file = file.name
        try:
            self._uuid = get_upload(file)
        except Exception as error:
            self._uuid = None
            message = (
                message
            ) = f"The graph of the model could not be stored at the minio-instance: {error.args}"
            warnings.warn(message)
        self._session = session

    @property
    def session(self) -> "CoreSession":
        return self._session

    @property
    def cuds(cls):
        return cls._session.load(cls._session.root).first()

    @property
    def uuid(cls):
        return cls._uuid

    @property
    def file(cls):
        return cls._file

    class Config:
        """Pydantic Config"""

        schema_extra = {
            "example": _get_example_json("co_pt111_full.json", STANDARD_XYZ)
        }


@dataclass
class COPt111FromMesoScaleModel:
    """Pydantic model describing data model for
    CO oxidation beginning on the mescoscopic scale."""

    zgb_model: ZacrosModel = Field(..., description="ZGB model for mesoscopic scale.")

    adp: COMolarFractionRange = Field(
        ...,
        description="""Molar fractions of CO
        for the adaptive design procedure""",
    )

    catalyticfoam: ContinuumModel = Field(
        ..., description="Data model for continuum scale."
    )

    def __post_init_post_parse__(self):
        with CoreSession() as session:
            workflow = emmo.Workflow()
            self.zgb_model.cuds.add(apd, rel=emmo.hasSpatialNext)
            apd.add(self.catalyticfoam.cuds, rel=emmo.hasSpatialNext)
            apd = emmo.AdaptiveDesignProcedure()
            apd.add(self.adp.cuds, rel=emmo.hasInput)
            workflow.add(self.zgb_model.cuds, rel=emmo.hasSpatialFirst)
            workflow.add(apd, rel=emmo.hasSpatialDirectPart)
            workflow.add(self.catalyticfoam.cuds, rel=emmo.hasSpatialLast)

        file = tempfile.NamedTemporaryFile(suffix=".ttl", delete=False)
        export_cuds(session, file.name)
        self._file = file.name
        try:
            self._uuid = get_upload(file)
        except Exception as error:
            self._uuid = None
            message = (
                message
            ) = f"The graph of the model could not be stored at the minio-instance: {error.args}"
            warnings.warn(message)
        self._session = session

    @property
    def session(self) -> "CoreSession":
        return self._session

    @property
    def cuds(cls):
        return cls._session.load(cls._session.root).first()

    @property
    def uuid(cls):
        return cls._uuid

    @property
    def file(cls):
        return cls._file

    class Config:
        """Pydantic Config"""

        schema_extra = {
            "example": _get_example_json("co_pt111_from_meso.json", STANDARD_XYZ)
        }
