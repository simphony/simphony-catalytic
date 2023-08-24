import json
import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote, urlencode

import joblib
import requests
from arcp import arcp_random, is_arcp_uri
from arcp.parse import ARCPParseResult, parse_arcp

import osp.dictionaries as cases
from osp.core.cuds import Cuds
from osp.models.utils.general import get_download, get_upload
from osp.wrappers.simcatalyticfoam.parsers import run_parser
from osp.wrappers.simcatalyticfoam.settings import ReaxProSettings

CASES = os.path.dirname(cases.__file__)
settings = ReaxProSettings()


def make_arcp(*args, **kwargs):
    if kwargs.get("query"):
        query = kwargs.pop("query")
        for key, value in query.items():
            query[key] = [quote(".".join(item)) for item in value]
        query = urlencode(query, doseq=True)
    return arcp_random(*args, **kwargs, query=query)


def check_arcp(cuds: Cuds) -> bool:
    return is_arcp_uri(cuds.iri)


def wrap_arcp(cuds: Cuds) -> ARCPParseResult:
    return parse_arcp(cuds.iri)


def _import_from_pkl(
    file_path: Path = settings.catalyticfoam_standard_pkl,
) -> List[str]:
    _, _, _, tabVarParam = joblib.load(file_path)
    return tabVarParam["names"]


def _read_from_case(
    rel_file_path: Path, case_path: Path = settings.catalyticfoam_standard_case
) -> Dict[Any, Any]:
    file_path = os.path.join(case_path, rel_file_path)
    return run_parser(file_path)


def _read_patches(case_path: Path = settings.catalyticfoam_standard_case) -> List[str]:
    path = os.path.join("constant", "polyMesh", "boundary")
    boundaries = _read_from_case(path, case_path=case_path)
    boundaries_def = [
        bounds
        for key, value in boundaries.items()
        if key.isnumeric()
        for bounds in value
    ]
    return [
        key for bound in boundaries_def for key in bound.keys() if key != "defaultFaces"
    ]
