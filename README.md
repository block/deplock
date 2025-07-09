# DepLock

## Introduction

A simple Python package used to parse lock files, useful when writing code that must 
interpret the requirements of a lock file and process or manipulate these requirements.

### Background
With the acceptance of [Pep 751](https://peps.python.org/pep-0751/) in March 2025, Python
has agreed upon a universal lock file specification, known as the `pylock.toml`.  The 
PEP describes the projects as:

"_[A] new file format for specifying dependencies to enable reproducible installation in a 
Python environment. The format is designed to be human-readable and machine-generated. 
Installers consuming the file should be able to calculate what to install without the 
need for dependency resolution at install-time._"

There are many use cases where a Python API that parses the lock file specifications into 
Python objects are useful and necessary to build on top of.

### How To Use
Import the package and get started!

```python
from deplock.parser.pylock import PyLock
from deplock.types.environment import PythonVersion
from deplock.utils.prebuilt_envs import python_env_one

# create the config
config = PyLock()
py_env = python_env_one(PythonVersion.current_version())

# add a Python environment specifier
config.add_target_environment_specification(py_env)

# validate that lock file is valid for current Python env
config.validate_pylock_toml()

# find the subset of packages in lock file valid for current Python env
config.get_valid_packages_from_lock()
```

Simply change the configuration class if to parse `uv.lock` files!
```python
from deplock.parser.uv import UVLock
from deplock.types.environment import PythonVersion
from deplock.utils.prebuilt_envs import python_env_one

# create the config
config = UVLock()
py_env = python_env_one(PythonVersion.current_version())

# add a Python environment specifier
config.add_target_environment_specification(py_env)

# validate that lock file is valid for current Python env
config.validate_uv_lock()

# find the subset of packages in lock file valid for current Python env
config.get_valid_packages_from_lock()

# find the preferred distribution of each valid package
config.get_preferred_distributions()
```

### Notes
Unlike some lock files, the metadata contained in `[[package.dependencies]]` is 
purposefully not used to determine if a package is required in the current installation 
environment.  The PEP confirms this, stating "_Tools MUST NOT use this information when 
doing installation; it is purely informational for auditing purposes._"

More Open Source and usage information can be found here:
* [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
* [GOVERNANCE.md](./GOVERNANCE.md)
* [LICENSE](./LICENSE)

## Project Resources

| Resource                                   | Description                                                                    |
| ------------------------------------------ | ------------------------------------------------------------------------------ |
| [CODEOWNERS](./CODEOWNERS)                 | Outlines the project lead(s)                                                   |
| [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) | Expected behavior for project contributors, promoting a welcoming environment |
| [CONTRIBUTING.md](./CONTRIBUTING.md)       | Developer guide to build, test, run, access CI, chat, discuss, file issues     |
| [GOVERNANCE.md](./GOVERNANCE.md)           | Project governance                                                             |
| [LICENSE](./LICENSE)                       | Apache License, Version 2.0                                                    |

Authors:
* Tyler Zupan
* Josh Hamet