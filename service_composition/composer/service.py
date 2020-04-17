import requests
import importlib
from enum import Enum
from abc import ABC, abstractmethod

class HTTPMethod(Enum):
    GET = 'get'
    POST = 'post'
    HEAD = 'head'
    PUT = 'put'
    PATCH = 'patch'
    DELETE = 'delete'

class Service(ABC):

    @abstractmethod
    def run(self, e=None):
        pass

class HTTPServiceFailure(RuntimeError):
    pass

class HTTPService(Service):
    def __init__(self, url: str, method: HTTPMethod, **kwargs):
        self.url = url
        self.method = method
        self.kwargs = kwargs

    def run(self, e=None):
        res = requests.request(
            self.method.value,
            self.url,
            data=e,
            **self.kwargs
        )
        if res.ok:
            return res.text
        else:
            raise HTTPServiceFailure(f"HTTP service (url={self.url}, method={self.method.value}) failed with status {res.status_code}: {res.text}")

class InvalidPythonService(RuntimeError):
    pass

class PythonService(Service):
    def __init__(self, module_name: str):
        self.module = importlib.import_module(module_name)
        if self.module.run is None:
            raise InvalidPythonService(f"Python module {module_name} does not have a top-level run function")

    def run(self, e=None):
        return self.module.run(e)
