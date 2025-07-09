import pytest
from pathlib import Path

from deplock.parser.poetry_class import PoetryLock
from deplock.types.environment import PythonVersion
from deplock.utils.prebuilt_envs import python_env_one
from deplock.exceptions import MissingPoetryLockFileError


@pytest.fixture
def target_environment():
    return python_env_one(PythonVersion.current_version())


@pytest.fixture
def poetry_lock_dir():
    return Path(__file__).parent / "poetry_project"


def test_find_poetry_lock_file(poetry_lock_dir):
    poetry_lock = PoetryLock(base_path=poetry_lock_dir,
                         poetry_lock_filename="poetry.lock")
    assert poetry_lock.poetry_lock_path.exists()
    assert poetry_lock.poetry_lock_path.name == "poetry.lock"


def test_find_nonexistent_poetry_lock_file(poetry_lock_dir):
    with pytest.raises(MissingPoetryLockFileError):
        PoetryLock(base_path=poetry_lock_dir,
                poetry_lock_filename="nonexistent.lock")


def test_poetry_parser(poetry_lock_dir, target_environment):
    poetry_lock = PoetryLock(base_path=poetry_lock_dir, 
                         poetry_lock_filename="poetry.lock")
    poetry_lock.add_target_environment_specification(target_environment)
    poetry_lock.validate_poetry_lock()
    assert poetry_lock.poetry_lock_is_validated is True
    
    valid_packages = poetry_lock.get_valid_packages_from_lock()
    package_names = [i for i in valid_packages]
    assert len(package_names) == len(set(package_names)), "Package names should be unique"
    assert len(package_names) > 0, "Should have found packages in the poetry.lock file"


def test_poetry_best_distribution(poetry_lock_dir, target_environment):
    poetry_lock = PoetryLock(base_path=poetry_lock_dir, 
                         poetry_lock_filename="poetry.lock")
    poetry_lock.add_target_environment_specification(target_environment)
    poetry_lock.validate_poetry_lock()
    poetry_lock.get_valid_packages_from_lock()
    requirements = poetry_lock.get_preferred_distributions()
    
    assert len(requirements) > 0, "Should have found package requirements"
    assert len(poetry_lock.package_requirements) == len(requirements)
    
    # Basic validation of requirements format
    for req in requirements:
        assert req.name, "Package should have a name"
        assert req.version, "Package should have a version"
        assert req.fingerprint, "Package should have a fingerprint (hash)"