from __future__ import annotations
import importlib
import inspect
import pkgutil
from typing import Type

import Entities
from Entities.boats import Boat


def load_boats() -> dict[str, Type[Boat]]:
    boat_registry = {}
    # Search through all .py files in root/Entities
    for module_info in pkgutil.iter_modules(Entities.__path__):
        module_name = module_info.name
        # Skip Private files
        if module_name.startswith("_"):
            continue
        # Import the module
        module = importlib.import_module(f"Entities.{module_name}")
        # Get all Boat classes in it
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue

            if issubclass(obj, Boat) and obj is not Boat:
                # Use class name as Key
                boat_registry[name] = obj

    return boat_registry
