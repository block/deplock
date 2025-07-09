import pytest
from pathlib import Path

from deplock.parser.pylock import PyLock
from deplock.types.environment import PythonVersion
from deplock.utils.prebuilt_envs import python_env_one



@pytest.fixture
def search_start_dir():
    return Path(__file__).parent / "test_project"

@pytest.fixture
def search_end_dir(search_start_dir):
    return search_start_dir.parent

@pytest.fixture
def target_environment():
    return python_env_one(PythonVersion.current_version())


def test_search_tree_for_lock_file(search_start_dir, search_end_dir):
    reader = PyLock(search_start_dir, search_end_dir)
    assert set(reader.pylock_file_paths) == {search_start_dir / "pylock.toml"}

def test_parse_pylock_file(search_start_dir, search_end_dir):
    reader = PyLock(search_start_dir, search_end_dir)
    assert reader is not None

def test_valid_pylock_file(search_start_dir, search_end_dir, target_environment):

    reader = PyLock(search_start_dir, search_end_dir)

    # add a Python environment specifier
    reader.add_target_environment_specification(target_environment)

    # validate that lock file is valid for current Python env
    reader.validate_pylock_toml()
    assert reader.pylock_toml_is_validated is True

def test_valid_packages_pylock_file(search_start_dir, search_end_dir, target_environment):

    reader = PyLock(search_start_dir, search_end_dir)

    # add a Python environment specifier
    reader.add_target_environment_specification(target_environment)

    # validate that lock file is valid for current Python env
    reader.validate_pylock_toml()

    # find the subset of packages in lock file valid for current Python env
    reader.get_valid_packages_from_lock()