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
    """Class with a single run method, which is called once for each input item"""

    @abstractmethod
    def run(self, e=None):
        pass

class HTTPServiceFailure(RuntimeError):
    pass

class HTTPService(Service):
    """Service for making HTTP calls"""

    def __init__(self, url: str, method: HTTPMethod, serializer, **kwargs):
        """
        Parameters
        --------------
            url : str
                Endpoint url to make a call to
            method : HTTPMethod
                Method to call
            serializer : Function
                How to serialize the input to the run function in order to send it to the endpoint
            kwargs : dict
                Extra arguments to send to requests call
        """
        self.url = url
        self.method = method
        self.serializer = serializer
        self.kwargs = kwargs

    def run(self, e=None):
        res = requests.request(
            self.method.value,
            self.url,
            data=self.serializer(e),
            **self.kwargs
        )
        if res.ok:
            return res.text
        else:
            raise HTTPServiceFailure(f"HTTP service (url={self.url}, method={self.method.value}) failed with status {res.status_code}: {res.text}")

class InvalidPythonService(RuntimeError):
    pass

class PythonService(Service):
    """Service that allows executing a python file with a single run function as entrypoint"""

    def __init__(self, module_name: str, **kwargs):
        """
        Parameters
        --------------
            module_name : str
                Fully qualified name to import the required file from the working directory.
                Same as path to file but replacing "/" by ".".
                For example to run file "A/B/C.py", module_name would be "A.B.C".
            kwargs : dict
                Extra arguments to send to the run function of the imported file.
        """ 
        self.kwargs = kwargs
        self.module = importlib.import_module(module_name)
        if self.module.run is None:
            raise InvalidPythonService(f"Python module {module_name} does not have a top-level run function")

    def run(self, e=None):
        return self.module.run(e, **self.kwargs)

class FunctionService(Service):
    """Service for running a single python function"""
    def __init__(self, function):
        self.function = function

    def run(self, e=None):
        return self.function(e)
