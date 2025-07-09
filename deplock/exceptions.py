class DepLockReaderError(Exception):
    """Raised for DepLock errors"""

class MissingPythonEnvironmentError(DepLockReaderError):
    """Raised when a packages are checked against a Python environment specification
    that has not been defined."""

class PythonVersionNotSpecifiedError(DepLockReaderError):
    """Raised when a PythonVersion does not have a major, minor, and micro version"""

class InvalidLockVersionError(DepLockReaderError):
    """Raised when the lock file version is not supported or is in an invalid format."""

class InvalidLockFileError(DepLockReaderError):
    """Raised when the lock file is malformed, corrupted, or cannot be parsed correctly."""

class PackageDistributionValidationError(DepLockReaderError):
    """Raised when a package distribution metadata fails validation checks."""

class MissingRequiredPackageFieldError(DepLockReaderError):
    """Raised when a required field is missing from a package's metadata in the lock file."""

class IncompatibleDistributionError(DepLockReaderError):
    """Raised when a package distribution metadata fails validation checks."""

class MissingLockMetadataError(DepLockReaderError):
    """Raised when a required property of the lock file object has not been set."""

class NoUVLockFileFoundError(DepLockReaderError):
    """Raised when no UV lock file can be found in the directory tree."""
    
class MissingPoetryLockFileError(DepLockReaderError):
    """Raised when no Poetry lock file can be found in the directory tree."""

class StalePoetryLockFileError(DepLockReaderError):
    """Raised when the pyproject.toml has been modified more recently
     than the Poetry lock file."""

class PoetryPyprojectMissingPythonSpecError(DepLockReaderError):
    """Raised when a poetry pyproject.toml is missing a Python specification."""