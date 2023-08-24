import logging
import os
import shutil
import subprocess  # nosec
import tempfile
from typing import TYPE_CHECKING

import osp.dictionaries.catalyticFoam as case

from .parsers import deep_replace, run_parser, serialize
from .settings import ReaxProSettings

if TYPE_CHECKING:
    from typing import Any, Dict, List

settings = ReaxProSettings()

CASES = os.path.dirname(case.__file__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CatalyticFoamEngine:
    def __init__(self, case: str, config: dict = {}):
        case_dir = os.path.join(CASES, case)
        if not config:
            runtime = tempfile.TemporaryDirectory().name
            tar = tempfile.NamedTemporaryFile().name
            config = dict(
                commands=[
                    dict(
                        exec="catalyticPimpleTurbulentFOAM",
                        args=None,
                        bashrc=str(settings.catalyticfoam_bash),
                    )
                ],
                directory=runtime,
                filename=tar,
            )
        self._parse_files = dict()
        self._config: dict = config
        self._current_process: subprocess.Popen = None
        logger.info("Engine instanciated with the following config: `%s`.", config)
        logger.info(
            "Will copy source %s to destination %s", case_dir, config["directory"]
        )
        shutil.copytree(case_dir, config["directory"])
        self._dir0 = os.path.join(config["directory"], "0")

    def add_to_parser(self, path: "str", jsonpath: "str", value: "Any") -> None:
        split = os.path.split(path)
        self._check_file(split)
        path = os.path.join(self._config["directory"], *split)
        logger.info(
            f"Will parse {value} into under query <{jsonpath}> into file {path}."
        )
        if path not in self._parse_files.keys():
            content = run_parser(path)
        else:
            content = self._parse_files[path]
        self._parse_files[path] = deep_replace(content, jsonpath, value)

    def run(self) -> None:
        self._check_consistency()
        for path, content in self._parse_files.items():
            with open(path, "w+") as file:
                file_content = serialize(content)
                file.write(file_content)
        for command in self._config["commands"]:
            cmd = self._prepare_command(command)
            logger.info(
                "Will run the following command under `%s`: `%s`.",
                self._config["directory"],
                cmd,
            )
            self._run(cmd)
        self._make_tarball()

    def _run(self, command: dict) -> None:
        with subprocess.Popen(
            f"bash -c '{command}'",  # nosec
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=self._config["directory"],
            shell=True,  # nosec
        ) as popen:
            for stdout_line in iter(popen.stdout.readline, ""):
                logger.info(stdout_line)
            for stderr_line in iter(popen.stderr.readline, ""):
                logger.error(stderr_line)
            self._current_process = popen
        return_code = popen.returncode
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)

    def _prepare_command(self, command: dict) -> str:
        cmd = [command["exec"], command.get("args") or str()]
        if command.get("bashrc"):
            cmd = [".", command.get("bashrc"), "&&"] + cmd
        return " ".join(cmd)

    def _make_tarball(self) -> None:
        logger.info(
            "Make tarball in file `%s` of directory `%s`.",
            self.tarball,
            self._config["directory"],
        )
        shutil.make_archive(self._config["filename"], "tar", self._config["directory"])

    def _check_file(self, filename: "List[str]") -> None:
        filepath = os.path.join(self._config["directory"], *filename)
        templatepath = os.path.join(CASES, "templates", filename[-1])
        if not os.path.exists(filepath):
            logger.info(
                f"File for {filepath} does not exist yet. Will create from template"
            )
            if not os.path.exists(templatepath):
                templatepath = os.path.join(CASES, "templates", "template_chem")
                logger.info(
                    f"Specific template for {filename[-1]} does not exist. Will use {templatepath}."
                )
            shutil.copy(templatepath, filepath)

    def _check_consistency(self) -> None:
        excluded = [
            exclude.strip()
            for exclude in settings.catalyticfoam_excluded_check_files.split("|")
        ]
        logger.info(
            f"Detected to exclude the following file while checking boundary conditions: {excluded}"
        )
        for file in os.listdir(self._dir0):
            path = os.path.join(self._dir0, file)
            path0 = os.path.join("0", file)
            if (
                os.path.isfile(path)
                and path0 not in excluded
                and path not in self._parse_files.keys()
            ):
                try:
                    self._parse_files[path] = run_parser(path)
                except Exception:
                    logger.info(
                        f"{path0} does not seem to be a file which can be parsed. Will skip this file."
                    )
            else:
                logger.info(
                    f"{path0} was already parsed or is exlcuded. Will skip this file."
                )
        boundaries = self._get_defined_boundaries()
        self._check_defaults(boundaries)
        self._check_bounds(boundaries)

    def _get_defined_boundaries(self):
        boundaries = run_parser(
            os.path.join(self._config["directory"], "constant", "polyMesh", "boundary")
        )
        boundaries_def = [
            bounds
            for key, value in boundaries.items()
            if key.isnumeric()
            for bounds in value
        ]
        return {key: value for bound in boundaries_def for key, value in bound.items()}

    def _check_defaults(self, boundaries: "Dict[Any,Any]"):
        for rawpath in settings.catalyticfoam_default_files.split("|"):
            path = os.path.join(self._config["directory"], rawpath.strip())
            content = self._parse_files.get(path)
            if not content:
                raise ValueError(
                    f"{path} was not found in the buffer. Please check `excluded_check_files` in the settings."
                )
            boundaryField = content.get("boundaryField")
            if not boundaryField:
                raise ValueError(f"boundaryField not found in {path}")
            for boundary in boundaries:
                if boundary != "defaultFaces" and boundary not in boundaryField.keys():
                    default = self._find_matches(boundary)
                    if not default:
                        raise ValueError(
                            f"Needed boundary '{boundary}', was not defined in `default_bounds`. Please check the settings."
                        )
                    logger.info(
                        f"""Will place `{default}` under needed boundary `{boundary}` in file {path}`,
                        since it was not defined there yet."""
                    )
                    boundaryField[boundary] = default

    def _check_bounds(self, boundaries: "Dict[Any,Any]"):
        for path, content in self._parse_files.items():
            if "0" in path.split(os.path.sep):
                boundaryField = content.get("boundaryField")
                if not boundaryField:
                    raise ValueError(f"boundaryField not found in {path}")
                for boundary in boundaries:
                    if (
                        boundary != "defaultFaces"
                        and boundary not in boundaryField.keys()
                    ):
                        raise ValueError(f"Boundary '{boundary}', must be in {path}.")
                for key, values in boundaryField.items():
                    if "type" not in values.keys():
                        raise ValueError(
                            f"Type of boundary must be specified through 'key' in {path}/{key}/type."
                        )
                logger.info(
                    f"File {path} was validated. All boundaries are set correctly."
                )

    def _find_matches(self, key):
        for match, content in settings.catalyticfoam_default_bounds.items():
            if key.startswith(match):
                return content

    @property
    def exit_code(cls):
        return cls._current_process.returncode

    @property
    def tarball(cls):
        return f"{cls._config['filename']}.tar"
