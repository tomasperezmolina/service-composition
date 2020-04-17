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

class Task(ABC):

    @abstractmethod
    def run(self, input=None):
        pass

class HTTPTaskFailure(RuntimeError):
    pass

class HTTPTask(Task):
    def __init__(self, url: str, method: HTTPMethod, **kwargs):
        self.url = url
        self.method = method
        self.kwargs = kwargs

    def run(self, input=None):
        res = requests.request(
            self.method.value,
            self.url,
            data=input,
            **self.kwargs
        )
        if res.ok:
            return res.text
        else:
            raise HTTPTaskFailure(f"HTTP task (url={self.url}, method={self.method.value}) failed with status {res.status_code}: {res.text}")

class InvalidPythonTask(RuntimeError):
    pass

class PythonTask(Task):
    def __init__(self, module_name: str):
        self.module = importlib.import_module(module_name)
        if self.module.run is None:
            raise InvalidPythonTask(f"Python module {module_name} does not have a top-level run function")

    def run(self, input=None):
        return self.module.run(input)
