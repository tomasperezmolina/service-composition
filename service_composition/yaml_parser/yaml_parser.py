import yaml
from enum import Enum

class ServiceType(Enum):
    PYTHON = 'python'
    HTTP   = 'HTTP'
    OTHER  = 'other'

def _merge_list_to_dict(lst):
    result = dict()
    for e in lst:
        result.update(e)
    return result

class ServiceData:
    def __init__(self, name, extra_args, type: ServiceType=ServiceType.OTHER):
        self.name = name
        self.extra_args = extra_args
        self.type = type

    def __str__(self):
        return 'Service: {}\n\ttype: {}\n\textra_args: {}'.format(self.name, self.type, self.extra_args)

''' Example:
services:
    - Print:
        type: python
        file: printer.py
        args:
            - arg1 = 'hello'
            - arg2 = 3
'''
class PythonServiceData(ServiceData):
    def __init__(self, name, file, extra_args):
        super().__init__(name, extra_args, ServiceType.PYTHON)
        self.file = file

    def __str__(self):
        return 'Python Service: {}\n\ttype: {}\n\tfile: {}\n\textra_args: {}'.format(self.name, self.type, self.file, self.extra_args)

''' Example:
services:
    - Crawler:
        url: http://131.175.120.108:20007/e2mc/CIME/v1.0/tweet/twitter_json
        method: POST
        auth:
            - type: BASIC
            - user: $USERNAME
            - password: $USERNAME
        args:
            - arg1 = 'hello'
            - arg2 = 3
'''
class HTTPServiceData(ServiceData):
    def __init__(self, name, url, method, auth, extra_args):
        super().__init__(name, extra_args, ServiceType.HTTP)
        self.url = url
        self.method = method 
        self.auth = auth

    def __str__(self):
        return 'HTTP Service: {}\n\ttype: {}\n\turl: {}\n\tmethod: {}\n\tauth: {}\n\textra_args: {}'.format(self.name, self.type, self.url, self.method, self.auth, self.extra_args)

'''
Returns an array of ServiceData objects in pipeline order
'''
def parse_composition(path, print_debug=False):
    if print_debug:
        print('[YAML parser]:')
    loaded = yaml.safe_load(open(path, 'r'))

    #get pipeline and services
    if not ('pipeline' in loaded and 'services' in loaded):
        raise Exception('The composer requires \"pipeline\" and \"services\" values')
    pipeline = loaded['pipeline']
    service_list = _merge_list_to_dict(loaded['services'])

    #check if all services in the pipeline are specified
    for name in pipeline:
        if not name in service_list:
            raise Exception('Service {} is undeclared'.format(name))

    #parse services
    services = []
    res = None
    for name in pipeline:
        args = service_list[name]
        if not 'type' in args:
            raise Exception('Service requires a \"type\" value')
        type = args['type']
        extra_args = None
        if 'args' in args:
            extra_args = _merge_list_to_dict(args['args'])
        if(type == 'HTTP'):
            if not ('url' in args and 'method' in args):
                raise Exception('HTTP service requires \"url\" and \"method\" values')

            url = args['url']
            method = args['method']
            auth = None
            if 'auth' in args:
                auth = _merge_list_to_dict(args['auth'])
            res = HTTPServiceData(name, url, method, auth, extra_args)

        elif(type == 'python'):
            if not 'file' in args:
                raise Exception('Python service requires a \"file\" value')
            file = args['file']
            res = PythonServiceData(name, file, extra_args)

        else:
            res = ServiceData(name, extra_args)

        services.append(res)
        if print_debug:
            print(res)

    return services
