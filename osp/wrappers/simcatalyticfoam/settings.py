import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseSettings, Field

import osp.dictionaries.catalyticFoam as case

CASES = os.path.dirname(case.__file__)
STANDARD_CASE = os.path.join(CASES, "laminar_2D_ML")
DEFAULT_PKL = os.path.join(STANDARD_CASE, "ml_ExtraTrees_forCFD.pkl")


class ModelSettings(BaseSettings):
    catalyticfoam_standard_pkl: Path = Field(
        DEFAULT_PKL,
        description="Path to standard PKL-file with the trained surrogate model.",
    )

    catalyticfoam_standard_case: Path = Field(
        STANDARD_CASE, description="Path to standard case."
    )

    download_timeout: int = Field(
        10,
        description="Timeout when a file is downloaded by the pydantic model from a static url.",
    )


class CatalyticFoamSettings(BaseSettings):
    catalyticfoam_excluded_check_files: str = Field(
        "0/Rh_s_",
        description="Files to be excluded during the consistency-check of boundaries",
    )
    catalyticfoam_bash: Path = Field(
        "/opt/openfoam8/etc/bashrc",
        description="Bashrc to be sourced while launching the catalyticFOAM-solver.",
    )
    catalyticfoam_default_files: str = Field(
        "0/Ydefault | 0/thetaDefault",
        description="""Files holding default values for boundaryFields of chemical species,
        which were not defined by the user.""",
    )
    catalyticfoam_default_bounds: Dict[Any, Any] = Field(
        {"wedge": {"type": "wedge"}},
        description="""Python-dict setting the default data for bounaries in the `default_files`.
        The primary keys are string-matching with the patches available in the `constant/polyMesh/boundary`-file.""",
    )

    catalyticfoam_label_iri: str = Field(
        "http://emmo.info/emmo#EMMO_5d181bad_b072_4b33_82a8_774c20ca577d",
        description="""IRI for the annotation property to detect the OpenFOAM-syntax of a property.
        E.g. `fixedValue` for a Dirichlet boundary condition.""",
    )


class ReaxProSettings(ModelSettings, CatalyticFoamSettings):
    """General Reaxpro wrapper settings"""

    class Config:
        """Config-class for the general wrapper settings."""

        env_prefix = "REAXPRO_"
