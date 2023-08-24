"""Conftest for simphony-catalytic"""
import os
import tempfile
from typing import TextIO, Union
from uuid import uuid4

import pytest

PATH = os.path.dirname(__file__)
TEST_PATH = os.path.join(PATH, "test_files")


def return_file(key: str, as_file=False) -> str:
    """Mocker function for returning test files."""
    tempdir = tempfile.gettempdir()
    path = os.path.join(tempdir, f"{key}.ttl")
    if not os.path.exists(path):
        raise ValueError(f"Key `{key}` does not exist in cache.")
    if as_file:
        return open(path, "rb")
    else:
        return path


def store_file(file: Union[TextIO, str], uuid: str = None) -> str:
    """Mocker for uploading files."""
    tempdir = tempfile.gettempdir()
    if not uuid:
        uuid = str(uuid4())
    path = os.path.join(tempdir, f"{uuid}.ttl")
    with open(path, "wb") as temp:
        temp.write(file.read())
    return uuid


@pytest.fixture
def prepare_env():
    os.environ["REAXPRO_MINIO_USER"] = "foo"
    os.environ["REAXPRO_MINIO_PASSWORD"] = "bar"


@pytest.fixture(autouse=True)
@pytest.mark.usefixtures("mocker")
def mock_download(mocker, prepare_env):
    """Sending request to mock-minio."""
    function = "osp.models.utils.general.get_download"
    patch = mocker.patch(function, new=return_file)
    return patch


@pytest.fixture(autouse=True)
@pytest.mark.usefixtures("mocker")
def mock_upload(mocker, prepare_env):
    """Sending request to mock-minio."""
    function = "osp.models.utils.general.get_upload"
    patch = mocker.patch(function, new=store_file)
    return patch
