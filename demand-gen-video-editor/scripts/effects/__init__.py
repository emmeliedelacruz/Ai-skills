"""Video Effect Library renderers. Importing this package registers every effect in effects.core.EFFECTS."""
import importlib
import pkgutil

from . import core  # noqa: F401

for _m in sorted(m.name for m in pkgutil.iter_modules(__path__) if m.name.startswith("set_")):
    importlib.import_module(f"{__name__}.{_m}")
