import pytest
from pathlib import Path

from deplock.parser.uv import UVLock
from deplock.types.environment import PythonVersion
from deplock.utils.prebuilt_envs import python_env_one


@pytest.fixture
def target_environment():
    return python_env_one(PythonVersion.current_version())

@pytest.fixture
def uv_lock_dir():
    return Path(__file__).parent / "uv_project"


def test_find_uv_lock_file(uv_lock_dir):
    uv_lock = UVLock(base_path=uv_lock_dir
                     , uv_lock_filename="uv.lock")
    assert uv_lock is not None

def test_uv_parser(uv_lock_dir, target_environment):
    uv_lock = UVLock(base_path=uv_lock_dir, uv_lock_filename="uv.lock")
    uv_lock.add_target_environment_specification(target_environment)
    uv_lock.get_valid_packages_from_lock()
    packages = uv_lock.valid_package_list
    package_names = [i.name for i in packages]
    assert len(package_names) == len(set(package_names))
    assert len({"atomicwrites", "colorama", "pywin32-ctypes"
                }.intersection(set(package_names))) == 0

def test_uv_best_distribution(uv_lock_dir, target_environment):
    uv_lock = UVLock(base_path=uv_lock_dir, uv_lock_filename="uv.lock")
    uv_lock.add_target_environment_specification(target_environment)
    uv_lock.get_valid_packages_from_lock()
    _ = uv_lock.get_preferred_distributions()
    assert len(uv_lock.package_requirements) in [58, 56, 54]