import importlib
import pkgutil
from typing import Dict, Type
from agents.agent_base import AgentBase

def discover_agents() -> Dict[str, Type[AgentBase]]:
    agent_classes = {}
    package = importlib.import_module('agents')
    prefix = package.__name__ + "."
    for _, modname, _ in pkgutil.iter_modules(package.__path__, prefix):
        module = importlib.import_module(modname)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, AgentBase) and attribute is not AgentBase:
                agent_key = modname.split('.')[-1]
                agent_classes[agent_key] = attribute
    return agent_classes