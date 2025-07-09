import datetime
from datetime import datetime as DateTime
import pytest

from deplock.configs.packages import Package
from deplock.exceptions import PackageDistributionValidationError

package_list = [
    {
        "name": "attrs",
        "version": "25.1.0",
        "requires-python": ">=3.8",
        "wheels": [
            {
                "name": "attrs-25.1.0-py3-none-any.whl",
                "upload-time": DateTime(
                    2025,
                    1,
                    25,
                    11,
                    30,
                    10,
                    164985,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/fc/30/d4986a882011f9df997a55e6becd864812ccfcd821d64aac8570ee39f719/attrs-25.1.0-py3-none-any.whl",
                "size": 63152,
                "hashes": {
                    "sha256": "c75a69e28a550a7e93789579c22aa26b0f5b83b75dc4e08fe092980051e1090a"
                },
            }
        ],
        "attestation-identities": [
            {
                "environment": "release-pypi",
                "kind": "GitHub",
                "repository": "python-attrs/attrs",
                "workflow": "pypi-package.yml",
            }
        ],
    },
    {
        "name": "cattrs",
        "version": "24.1.2",
        "requires-python": ">=3.8",
        "dependencies": [{"name": "attrs"}],
        "wheels": [
            {
                "name": "cattrs-24.1.2-py3-none-any.whl",
                "upload-time": DateTime(
                    2024,
                    9,
                    22,
                    14,
                    58,
                    34,
                    812643,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/c8/d5/867e75361fc45f6de75fe277dd085627a9db5ebb511a87f27dc1396b5351/cattrs-24.1.2-py3-none-any.whl",
                "size": 66446,
                "hashes": {
                    "sha256": "67c7495b760168d931a10233f979b28dc04daf853b30752246f4f8471c6d68d0"
                },
            }
        ],
    },
    {
        "name": "numpy",
        "version": "2.2.3",
        "requires-python": ">=3.10",
        "wheels": [
            {
                "name": "numpy-2.2.3-cp312-cp312-win_amd64.whl",
                "upload-time": DateTime(
                    2025,
                    2,
                    13,
                    16,
                    51,
                    21,
                    821880,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/42/6e/55580a538116d16ae7c9aa17d4edd56e83f42126cb1dfe7a684da7925d2c/numpy-2.2.3-cp312-cp312-win_amd64.whl",
                "size": 12626357,
                "hashes": {
                    "sha256": "83807d445817326b4bcdaaaf8e8e9f1753da04341eceec705c001ff342002e5d"
                },
            },
            {
                "name": "numpy-2.2.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                "upload-time": DateTime(
                    2025,
                    2,
                    13,
                    16,
                    50,
                    0,
                    79662,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/39/04/78d2e7402fb479d893953fb78fa7045f7deb635ec095b6b4f0260223091a/numpy-2.2.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                "size": 16116679,
                "hashes": {
                    "sha256": "3b787adbf04b0db1967798dba8da1af07e387908ed1553a0d6e74c084d1ceafe"
                },
            },
        ],
        "sdist": [
            {
                "name": "numpy-2.2.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                "upload-time": DateTime(
                    2025,
                    2,
                    13,
                    16,
                    50,
                    0,
                    79662,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/39/04/78d2e7402fb479d893953fb78fa7045f7deb635ec095b6b4f0260223091a/numpy-2.2.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                "size": 16116679,
                "hashes": {
                    "sha256": "3b787adbf04b0db1967798dba8da1af07e387908ed1553a0d6e74c084d1ceafe"
                },
            }
        ],
    },
    {
        "name": "numpy",
        "version": "2.2.3",
        "requires-python": ">=3.10",
        "wheels": [
            {
                "name": "numpy-2.2.3-cp312-cp312-win_amd64.whl",
                "upload-time": DateTime(
                    2025,
                    2,
                    13,
                    16,
                    51,
                    21,
                    821880,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/42/6e/55580a538116d16ae7c9aa17d4edd56e83f42126cb1dfe7a684da7925d2c/numpy-2.2.3-cp312-cp312-win_amd64.whl",
                "size": 12626357,
                "hashes": {
                    "sha256": "83807d445817326b4bcdaaaf8e8e9f1753da04341eceec705c001ff342002e5d"
                },
            },
            {
                "name": "numpy-2.2.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                "upload-time": DateTime(
                    2025,
                    2,
                    13,
                    16,
                    50,
                    0,
                    79662,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/39/04/78d2e7402fb479d893953fb78fa7045f7deb635ec095b6b4f0260223091a/numpy-2.2.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                "size": 16116679,
                "hashes": {
                    "sha256": "3b787adbf04b0db1967798dba8da1af07e387908ed1553a0d6e74c084d1ceafe"
                },
            },
        ],
        "archive": [
            {
                "upload-time": DateTime(
                    2025,
                    2,
                    13,
                    16,
                    50,
                    0,
                    79662,
                    tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
                ),
                "url": "https://files.pythonhosted.org/packages/39/04/78d2e7402fb479d893953fb78fa7045f7deb635ec095b6b4f0260223091a/numpy-2.2.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                "size": 16116679,
                "hashes": {
                    "sha256": "3b787adbf04b0db1967798dba8da1af07e387908ed1553a0d6e74c084d1ceafe"
                },
            }
        ],
    },
]

def test_base_package():
    test_package = package_list[0]
    package_config = Package.model_validate(test_package)
    assert package_config.name == 'attrs'
    assert package_config.requires_python == '>=3.8'
    assert package_config.version == '25.1.0'
    assert package_config.dependencies is None
    package_info = package_config.wheels_info
    assert len(package_info) == 1

def test_package_w_deps():
    test_package = package_list[1]
    package_config = Package.model_validate(test_package)
    assert package_config.dependencies == [{'name': 'attrs'}]

def test_package_w_dists():
    test_package = package_list[2]
    package_config = Package.model_validate(test_package)
    package_wheel_info = package_config.wheels_info
    assert len(package_wheel_info) == 2

    package_sdist_info = package_config.sdist_info
    assert len(package_sdist_info) == 1

def test_package_w_extra_dists():
    test_package = package_list[3]
    with pytest.raises(PackageDistributionValidationError) as e:
        package_config = Package.model_validate(test_package)
        assert package_config is not None
        print(e.value)

