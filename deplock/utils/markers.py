import logging
from packaging.markers import Marker
from typing import List, Union

from deplock.exceptions import PythonVersionNotSpecifiedError
from deplock.types.environment import PythonVersion, PythonEnvironment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _py_version_converter(py_version: str) -> PythonVersion:
    """Converts a string into the necessary Python version."""
    if not isinstance(py_version, str):
        raise TypeError("Python version must be a string")

    match py_version.count("."):
        case 0:
            raise PythonVersionNotSpecifiedError("Python version must have a major and minor specifier")
        case 1:
            major, minor = map(int, py_version.split("."))
            return PythonVersion(major=major, minor=minor, micro=None)
        case 2:
            major, minor, micro = py_version.split(".")
            try:
                micro = int(micro)
            except ValueError:
                assert micro == "*"
            return PythonVersion(major=int(major), minor=int(minor), micro=micro)
        case _:
            return PythonVersion(major=3, minor=0, micro=0)

def validate_python_version(specifier: str, current_version: str | PythonVersion) -> bool:
    # convert current version to type PythonVersion if not already
    if isinstance(current_version, str):
        current_py_version = _py_version_converter(current_version)
    else:
        current_py_version = current_version
    current_version_fully_specified = current_py_version.is_full_spec()
    if not current_version_fully_specified:
        raise RuntimeError("Runtime Python version must be fully specified "
                           "(major, minor, micro).")
    current_py_version_str = str(current_version)

    valid_ops = [">=", "<=", "==", "!=", ">", "<"]
    parts = specifier.split(",")
    markers = []
    for part in parts:
        current_part = part.strip()
        # Handle wildcard version (*)
        if current_part == '*':
            # * means any version is acceptable
            markers.append(True)
            continue

        # Handle caret (^) version specifier
        if current_part.startswith("^"):
            # ^3.10 means >= 3.10.0, < 4.0.0
            version_str = current_part[1:].strip()
            version = _py_version_converter(py_version=version_str)

            # Create >= marker
            if version.micro == "*" or version.micro is None:
                gte_marker = f"python_version >= '{version.major_minor_only_spec()}'"
            else:
                gte_marker = f"python_full_version >= '{version}'"

            # Create < marker for next major version
            lt_marker = f"python_version < '{version.major + 1}'"

            # Evaluate both markers
            if version.micro == "*" or version.micro is None:
                current_version_eval_dict = dict(python_version=current_py_version.major_minor_only_spec())
            else:
                current_version_eval_dict = dict(python_full_version=current_py_version_str)

            markers.append(Marker(gte_marker).evaluate(environment=current_version_eval_dict))
            markers.append(Marker(lt_marker).evaluate(environment=current_version_eval_dict))
            continue

        # Handle standard operators
        for op in valid_ops:
            if current_part.startswith(op):
                version = _py_version_converter(py_version=current_part[len(op):].strip())
                if (op in [">", "<"]
                        and version.minor == current_py_version.minor
                        and version.micro == "*"):
                    raise RuntimeError(f"Cannot use operator '{op}' to compare a Python "
                                       f"version that is not fully specified."
                                       f"Comparison '{current_py_version_str} {op} {version}' is not valid")
                if version.micro == "*" or version.micro is None:
                    marker = f"python_version {op} '{version.major_minor_only_spec()}'"
                else:
                    marker = f"python_full_version {op} '{version}'"
                break
        else:
            raise ValueError(f"Invalid version specifier: {current_part}")
        if version.micro == "*" or version.micro is None:
            current_version_eval_dict = dict(python_version=current_py_version.major_minor_only_spec())
        else:
            current_version_eval_dict = dict(python_full_version=current_py_version_str)
        eval_str = f'{Marker(marker)}.evaluate(environment={current_version_eval_dict})'
        logger.debug(f"Marker logic:\n{eval_str}")
        markers.append(Marker(marker).evaluate(environment=current_version_eval_dict))
    return all(markers)


def check_markers(markers: Union[List[str], str], environment: PythonEnvironment) -> bool:
    """True if the markers associated with the package meet the current environment"""
    valid_markers = []
    invalid_markers = []
    if not isinstance(markers, list):
        markers = [markers]
    for marker in markers:
        current_marker = Marker(marker)
        if environment.is_compatible_with_marker(current_marker):
            valid_markers.append(current_marker)
        else:
            invalid_markers.append(current_marker)
    if not valid_markers:
        logger.info(
            f"Environment is not compatible with any of the lock file markers: "
            f"{[f'{marker}' for marker in invalid_markers]}"
        )
        return False

    return True
