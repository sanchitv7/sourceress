def hello() -> str:
    return "Hello from sourceress!"

# Semantic version of the package
__version__ = "0.1.0"

# Re-export major submodules for convenience
from . import agents, models, workflows  # noqa: F401
