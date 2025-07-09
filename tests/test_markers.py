import pytest
from deplock.types.environment import PythonVersion
from deplock.utils.prebuilt_envs import python_env_one
from deplock.utils.markers import validate_python_version, check_markers

@pytest.fixture()
def env_3_12():
    return python_env_one(PythonVersion(major=3, minor=12, micro=5))

test_inputs_3_10_5 = [
    ("3.10.5", "==3.11", False),
    ("3.10.5", "==3.11.*", False),
    ("3.10.5", "==3.11.5", False),
    ("3.10.5", "!=3.11", True),
    ("3.10.5", "!=3.11.*", True),
    ("3.10.5", "!=3.11.5", True),
    ("3.10.5", ">3.11", False),
    ("3.10.5", ">3.11.*", False),
    ("3.10.5", ">3.11.5", False),
    ("3.10.5", "<3.11", True),
    ("3.10.5", "<3.11.*", True),
    ("3.10.5", "<3.11.5", True),
    ("3.10.5", ">=3.11", False),
    ("3.10.5", ">=3.11.*", False),
    ("3.10.5", ">=3.11.5", False),
    ("3.10.5", "<=3.11", True),
    ("3.10.5", "<=3.11.*", True),
    ("3.10.5", "<=3.11.5", True),
]

test_inputs_3_11_4 = [
    ("3.11.4", "==3.11", True),
    ("3.11.4", "==3.11.*", True),
    ("3.11.4", "==3.11.5", False),

    ("3.11.4", "!=3.11", False),
    ("3.11.4", "!=3.11.*", False),
    ("3.11.4", "!=3.11.5", True),

    ("3.11.4", ">3.11", False),
    ("3.11.4", ">3.11.*", "Error"),
    ("3.11.4", ">3.11.5", False),

    ("3.11.4", "<3.11", False),
    ("3.11.4", "<3.11.*", "Error"),
    ("3.11.4", "<3.11.5", True),

    ("3.11.4", ">=3.11", True),
    ("3.11.4", ">=3.11.*", True),
    ("3.11.4", ">=3.11.5", False),

    ("3.11.4", "<=3.11", True),
    ("3.11.4", "<=3.11.*", True),
    ("3.11.4", "<=3.11.5", True),
]

test_inputs_3_11_5 = [
    ("3.11.5", "==3.11", True),
    ("3.11.5", "==3.11.*", True),
    ("3.11.5", "==3.11.5", True),

    ("3.11.5", "!=3.11", False),
    ("3.11.5", "!=3.11.*", False),
    ("3.11.5", "!=3.11.5", False),

    ("3.11.5", ">3.11", False),
    ("3.11.5", ">3.11.*", "Error"),
    ("3.11.5", ">3.11.5", False),

    ("3.11.5", "<3.11", False),
    ("3.11.5", "<3.11.*", "Error"),
    ("3.11.5", "<3.11.5", False),

    ("3.11.5", ">=3.11", True),
    ("3.11.5", ">=3.11.*", True),
    ("3.11.5", ">=3.11.5", True),

    ("3.11.5", "<=3.11", True),
    ("3.11.5", "<=3.11.*", True),
    ("3.11.5", "<=3.11.5", True),
]

test_inputs_3_11_6 = [
    ("3.11.6", "==3.11", True),
    ("3.11.6", "==3.11.*", True),
    ("3.11.6", "==3.11.5", False),

    ("3.11.6", "!=3.11", False),
    ("3.11.6", "!=3.11.*", False),
    ("3.11.6", "!=3.11.5", True),

    ("3.11.6", ">3.11", False),
    ("3.11.6", ">3.11.*", "Error"),
    ("3.11.6", ">3.11.5", True),

    ("3.11.6", "<3.11", False),
    ("3.11.6", "<3.11.*", "Error"),
    ("3.11.6", "<3.11.5", False),

    ("3.11.6", ">=3.11", True),
    ("3.11.6", ">=3.11.*", True),
    ("3.11.6", ">=3.11.5", True),

    ("3.11.6", "<=3.11", True),
    ("3.11.6", "<=3.11.*", True),
    ("3.11.6", "<=3.11.5", False),
]

test_inputs_3_12_5 = [
    ("3.12.5", "==3.11", False),
    ("3.12.5", "==3.11.*", False),
    ("3.12.5", "==3.11.5", False),

    ("3.12.5", "!=3.11", True),
    ("3.12.5", "!=3.11.*", True),
    ("3.12.5", "!=3.11.5", True),

    ("3.12.5", ">3.11", True),
    ("3.12.5", ">3.11.*", True),
    ("3.12.5", ">3.11.5", True),

    ("3.12.5", "<3.11", False),
    ("3.12.5", "<3.11.*", False),
    ("3.12.5", "<3.11.5", False),

    ("3.12.5", ">=3.11", True),
    ("3.12.5", ">=3.11.*", True),
    ("3.12.5", ">=3.11.5", True),

    ("3.12.5", "<=3.11", False),
    ("3.12.5", "<=3.11.*", False),
    ("3.12.5", "<=3.11.5", False),
]

@pytest.mark.parametrize("input_specs", [test_inputs_3_10_5,
                                         test_inputs_3_11_4,
                                         test_inputs_3_11_5,
                                         test_inputs_3_11_6,
                                         test_inputs_3_12_5])
def test_meta_data(input_specs):
    assert len(input_specs) == 18
    assert len(set(input_specs)) == len(input_specs)


@pytest.mark.parametrize("input_3_10_5", [test_inputs_3_10_5])
def test_3_10_5(input_3_10_5):
    for py_version, requires_python, result in input_3_10_5:
        if result == "Error":
            with pytest.raises(RuntimeError):
                validate_python_version(specifier=requires_python, current_version=py_version)
        else:
            assert validate_python_version(specifier=requires_python, current_version=py_version) == result

@pytest.mark.parametrize("input_3_11_4", [test_inputs_3_11_4])
def test_3_11_4(input_3_11_4):
    for py_version, requires_python, result in input_3_11_4:
        if result == "Error":
            with pytest.raises(RuntimeError):
                validate_python_version(specifier=requires_python, current_version=py_version)
        else:
            assert validate_python_version(specifier=requires_python, current_version=py_version) == result

@pytest.mark.parametrize("input_3_11_5", [test_inputs_3_11_5])
def test_3_11_5(input_3_11_5):
    for py_version, requires_python, result in input_3_11_5:
        if result == "Error":
            with pytest.raises(RuntimeError):
                validate_python_version(specifier=requires_python, current_version=py_version)
        else:
            assert validate_python_version(specifier=requires_python, current_version=py_version) == result

@pytest.mark.parametrize("input_3_11_6", [test_inputs_3_11_6])
def test_3_11_6(input_3_11_6):
    for py_version, requires_python, result in input_3_11_6:
        if result == "Error":
            with pytest.raises(RuntimeError):
                validate_python_version(specifier=requires_python, current_version=py_version)
        else:
            assert validate_python_version(specifier=requires_python, current_version=py_version) == result

@pytest.mark.parametrize("input_3_12_5", [test_inputs_3_12_5])
def test_3_12_5(input_3_12_5):
    for py_version, requires_python, result in input_3_12_5:
        if result == "Error":
            with pytest.raises(RuntimeError):
                validate_python_version(specifier=requires_python, current_version=py_version)
        else:
            assert validate_python_version(specifier=requires_python, current_version=py_version) == result

def test_passing_double_py_marker():
    requires_python = ">=3.9, <3.11"
    assert validate_python_version(specifier=requires_python, current_version="3.10.5") is True

def test_failing_double_py_marker():
    requires_python = ">=3.9, <3.11"
    with pytest.raises(RuntimeError):
        validate_python_version(
            specifier=requires_python, current_version="3.12"
        )

def test_passing_neg_single_platform_marker(env_3_12):
    marker = "sys_platform != 'win32'"
    assert check_markers(markers=marker, environment=env_3_12) is True

def test_passing_pos_single_platform_marker(env_3_12):
    marker = "sys_platform == 'linux'"
    assert check_markers(markers=marker, environment=env_3_12) is True

def test_passing_multiple_markers_short_list(env_3_12):
    resolution_markers = [
        "python_full_version > '3.10' and sys_platform != 'win32'",
        "python_full_version > '3.10' and sys_platform == 'win32'",
    ]
    assert check_markers(markers=resolution_markers, environment=env_3_12) is True

def test_passing_multiple_markers_long_list(env_3_12):
    resolution_markers = [
        "python_full_version >= '3.10' and sys_platform != 'win32'",
        "python_full_version >= '3.10' and sys_platform == 'win32'",
        "python_full_version < '3.10' and sys_platform != 'win32'",
        "python_full_version < '3.10' and sys_platform == 'win32'",
    ]
    assert check_markers(markers=resolution_markers, environment=env_3_12) is True

def test_passing_long_marker(env_3_12):
    marker = "python_full_version >= '3.10' and sys_platform != 'emscripten' and sys_platform != 'win32'"
    assert check_markers(markers=marker, environment=env_3_12) is True
