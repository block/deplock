"""
This module provides example functions for setting up Python environments.

The functions within this module return configured `PythonEnvironment`
objects that are compatible with the respective base images.

To determine the supported platform tags (compatible wheels/PEP 600 tags)
for a Python interpreter within a container image:

1. Install the `packaging` library in the target Python environment.
2. Use the following code to enumerate the supported platform tags:

   ```python
   import packaging.tags
   print(list(packaging.tags.platform_tags()))
"""

from deplock.types.environment import EnvironmentMarkers, PythonEnvironment, PythonVersion


def python_env_one(python_version: PythonVersion) -> PythonEnvironment:
    """
    This function configures a second test Python environment.

    Args:
        python_version (PythonVersion): The version of Python available in the Hermit
            base image.

    Returns:
        PythonEnvironment: An object encapsulating configurations appropriate
            for block-python base images, ensuring installed packages are compatible
            with the underlying system.
    """
    return PythonEnvironment(
        python_version=python_version,
        platforms=(
            "manylinux_2_36_x86_64",
            "manylinux_2_35_x86_64",
            "manylinux_2_34_x86_64",
            "manylinux_2_33_x86_64",
            "manylinux_2_32_x86_64",
            "manylinux_2_31_x86_64",
            "manylinux_2_30_x86_64",
            "manylinux_2_29_x86_64",
            "manylinux_2_28_x86_64",
            "manylinux_2_27_x86_64",
            "manylinux_2_26_x86_64",
            "manylinux_2_25_x86_64",
            "manylinux_2_24_x86_64",
            "manylinux_2_23_x86_64",
            "manylinux_2_22_x86_64",
            "manylinux_2_21_x86_64",
            "manylinux_2_20_x86_64",
            "manylinux_2_19_x86_64",
            "manylinux_2_18_x86_64",
            "manylinux_2_17_x86_64",
            "manylinux2014_x86_64",
            "manylinux_2_16_x86_64",
            "manylinux_2_15_x86_64",
            "manylinux_2_14_x86_64",
            "manylinux_2_13_x86_64",
            "manylinux_2_12_x86_64",
            "manylinux2010_x86_64",
            "manylinux_2_11_x86_64",
            "manylinux_2_10_x86_64",
            "manylinux_2_9_x86_64",
            "manylinux_2_8_x86_64",
            "manylinux_2_7_x86_64",
            "manylinux_2_6_x86_64",
            "manylinux_2_5_x86_64",
            "manylinux1_x86_64",
            "linux_x86_64",
        ),
        environment_location="/opt/TEST/venv",
        environment_markers=EnvironmentMarkers(
            os_name="posix",
            sys_platform="linux",
            platform_machine="x86_64",
            platform_python_implementation="CPython",
            platform_release="6.6.22-linuxkit",
            platform_system="Linux",
            platform_version="#1 SMP Fri Mar 29 12:21:27 UTC 2024",
            implementation_name="cpython",
        ),
    )


def python_env_two(python_version: PythonVersion) -> PythonEnvironment:
    """
    This function configures a second test Python environment.

    Args:
        python_version (PythonVersion): The version of Python available in the Hermit
            base image.

    Returns:
        PythonEnvironment: An object encapsulating configurations appropriate
            for Hermit base images, ensuring installed packages are compatible
            with the underlying system.
    """
    return PythonEnvironment(
        python_version=python_version,
        platforms=(
            "manylinux_2_35_x86_64",
            "manylinux_2_34_x86_64",
            "manylinux_2_33_x86_64",
            "manylinux_2_32_x86_64",
            "manylinux_2_31_x86_64",
            "manylinux_2_30_x86_64",
            "manylinux_2_29_x86_64",
            "manylinux_2_28_x86_64",
            "manylinux_2_27_x86_64",
            "manylinux_2_26_x86_64",
            "manylinux_2_25_x86_64",
            "manylinux_2_24_x86_64",
            "manylinux_2_23_x86_64",
            "manylinux_2_22_x86_64",
            "manylinux_2_21_x86_64",
            "manylinux_2_20_x86_64",
            "manylinux_2_19_x86_64",
            "manylinux_2_18_x86_64",
            "manylinux_2_17_x86_64",
            "manylinux2014_x86_64",
            "manylinux_2_16_x86_64",
            "manylinux_2_15_x86_64",
            "manylinux_2_14_x86_64",
            "manylinux_2_13_x86_64",
            "manylinux_2_12_x86_64",
            "manylinux2010_x86_64",
            "manylinux_2_11_x86_64",
            "manylinux_2_10_x86_64",
            "manylinux_2_9_x86_64",
            "manylinux_2_8_x86_64",
            "manylinux_2_7_x86_64",
            "manylinux_2_6_x86_64",
            "manylinux_2_5_x86_64",
            "manylinux1_x86_64",
            "linux_x86_64",
        ),
        environment_location="/opt/TEST/venv",
        environment_markers=EnvironmentMarkers(
            os_name="posix",
            sys_platform="linux",
            platform_machine="x86_64",
            platform_python_implementation="CPython",
            platform_release="6.6.22-linuxkit",
            platform_system="Linux",
            platform_version="#1 SMP Fri Mar 29 12:21:27 UTC 2024",
            implementation_name="cpython",
        ),
    )
