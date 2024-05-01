import importlib
import pkgutil
import subprocess
import sys
from typing import Dict, Type
from agents.agent_base import AgentBase

def install_missing_library(library_name):
    try:
        importlib.import_module(library_name)
    except ImportError:
        print(f"Installing missing library: {library_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", library_name])

def discover_agents() -> Dict[str, Type[AgentBase]]:
    agent_classes = {}
    package = importlib.import_module('agents')
    prefix = package.__name__ + "."
    for _, modname, _ in pkgutil.iter_modules(package.__path__, prefix):
        try:
            module = importlib.import_module(modname)
        except ModuleNotFoundError as e:
            missing_library = str(e).split("'")[1]
            install_missing_library(missing_library)
            module = importlib.import_module(modname)

        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, AgentBase) and attribute is not AgentBase:
                agent_key = modname.split('.')[-1]
                agent_classes[agent_key] = attribute
    return agent_classes