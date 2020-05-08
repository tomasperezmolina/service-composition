import yaml
from enum import Enum

#if the argument value is a variable, replaces it with the provided value in the dict. If its not present in the dict, just returns the string.
def _check_var_arg(arg, variables_dict):
    if (not isinstance(arg, str) or not arg[0] == '$'):
        return arg
    else:
        _var_name = arg[1:]
        if not _var_name in variables_dict:
            #we keep going with the argument value
            print("[YAML parser]: {} value not specified".format(arg))
            return arg
        else:
            return variables_dict[_var_name]

def _merge_list_to_dict(lst):
    result = dict()
    for e in lst:
        result.update(e)
    return result

def _pipeline_names(pipeline):
    res = []
    for s in pipeline:
        if isinstance(s, str):
            res.append(s)
        elif isinstance(s, dict):
            res.append(list(s.keys())[0])
        else:
            raise RuntimeError(f"Parsed service as a {type(s)}, unrecognized type")
    return res

def _pipeline_connection_args(pipeline, i):
    s = pipeline[i]
    if isinstance(s, str):
        return dict()
    elif isinstance(s, dict):
        return s[list(s.keys())[0]]
    else:
        raise RuntimeError(f"Parsed service as a {type(s)}, unrecognized type")

class ServiceType(Enum):
    PYTHON = 'python'
    HTTP   = 'HTTP'
    OTHER  = 'other'

class ServiceData:
    def __init__(self, name, threads, connection_args, extra_args, type: ServiceType=ServiceType.OTHER):
        self.name = name
        self.threads = threads
        self.connection_args = connection_args
        self.extra_args = extra_args
        self.type = type

    def __str__(self):
        return 'Service: {}\n\ttype: {}\n\tthreads: {}\n\tconnection_args: {}\n\textra_args: {}'.format(self.name, self.type, self.threads, self.connection_args, self.extra_args)

''' Example:
services:
    - Print:
        type: python
        file: printer.py
        args:
            - arg1 = 'hello'
            - arg2 = 3
        translator:
            - arg1: var1
            - arg2: var2
'''
class PythonServiceData(ServiceData):
    def __init__(self, name, threads, file, connection_args, extra_args):
        super().__init__(name, threads, connection_args, extra_args, ServiceType.PYTHON)
        self.file = file

    def __str__(self):
        return 'Python Service: {}\n\ttype: {}\n\tthreads: {}\n\tfile: {}\n\tconnection_args: {}\n\textra_args: {}'.format(self.name, self.type, self.threads, self.file, self.connection_args, self.extra_args)

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
    def __init__(self, name, threads, url, method, auth, content_type, connection_args, extra_args):
        super().__init__(name, threads, connection_args, extra_args, ServiceType.HTTP)
        self.url = url
        self.method = method 
        self.auth = auth
        self.content_type = content_type

    def __str__(self):
        return 'HTTP Service: {}\n\ttype: {}\n\tthreads: {}\n\turl: {}\n\tmethod: {}\n\tauth: {}\n\tcontent_type: {}\n\tconnection_args: {}\n\textra_args: {}'.format(self.name, self.type, self.threads, self.url, self.method, self.auth, self.content_type, self.connection_args, self.extra_args)

'''
Returns an array of ServiceData objects in pipeline order
'''
def parse_composition(path, variables_dict, print_debug=False):
    if print_debug:
        print('[YAML parser]:')
    loaded = yaml.safe_load(open(path, 'r'))

    #get pipeline and services
    if not ('pipeline' in loaded and 'services' in loaded):
        raise Exception('The composer requires \"pipeline\" and \"services\" values')
    pipeline = loaded['pipeline']
    service_list = _merge_list_to_dict(loaded['services'])

    service_names = _pipeline_names(pipeline)

    #check if all services in the pipeline are specified
    for name in service_names:
        if not name in service_list:
            raise Exception('Service {} is undeclared'.format(name))

    #parse services
    services = []
    res = None
    for (i, name) in enumerate(service_names):
        args = service_list[name]

        if not 'type' in args:
            raise Exception('Service requires a \"type\" value')
        type = _check_var_arg(args['type'], variables_dict)

        if not 'threads' in args:
            threads = 1
        else:
            threads = _check_var_arg(args['threads'], variables_dict)

        connection_args = _pipeline_connection_args(pipeline, i)

        extra_args = dict()
        if 'args' in args:
            extra_args = _merge_list_to_dict(args['args'])
            for _arg in extra_args:
                extra_args[_arg] = _check_var_arg(extra_args[_arg], variables_dict)
        
        if type == 'HTTP':
            if not ('url' in args and 'method' in args):
                raise Exception('HTTP service requires \"url\" and \"method\" values')

            url = _check_var_arg(args['url'], variables_dict)
            method = _check_var_arg(args['method'], variables_dict)
            if 'content-type' in args:
                content_type = _check_var_arg(args['content-type'], variables_dict)
            else:
                content_type = None
            auth = None
            if 'auth' in args:
                auth = _merge_list_to_dict(args['auth'])
                for _arg in auth:
                    auth[_arg] = _check_var_arg(auth[_arg], variables_dict)
            res = HTTPServiceData(name, threads, url, method, auth, content_type, connection_args, extra_args)

        elif type == 'python':
            if not 'file' in args:
                raise Exception('Python service requires a \"file\" value')
            file = _check_var_arg(args['file'], variables_dict)
            res = PythonServiceData(name, threads, file, connection_args, extra_args)

        else:
            res = ServiceData(name, threads, connection_args, extra_args)

        services.append(res)
        if print_debug:
            print(res)

    return services


def _get_variables(current, acc):
    for key in current:
        curr = current[key]
        if isinstance(curr, dict):
            _get_variables(curr, acc)
        elif isinstance(curr, str) and curr[0] == '$':
            name = curr[1:]
            if not name in acc:
                acc.append(name)
        elif isinstance(curr, list) and isinstance(curr[0], dict):
            _get_variables(_merge_list_to_dict(curr), acc)

def get_variables(path):
    loaded = yaml.safe_load(open(path, 'r'))
    acc = []
    _get_variables(loaded, acc)
    return acc

