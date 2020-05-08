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

class ServiceType(Enum):
    PYTHON = 'python'
    HTTP   = 'HTTP'
    OTHER  = 'other'

class ServiceData:
    def __init__(self, name, extra_args, type: ServiceType=ServiceType.OTHER, translator = None, translator_exclusive = False):
        self.name = name
        self.extra_args = extra_args
        self.type = type
        self.translator = translator
        self.translator_exclusive = translator_exclusive

    def __str__(self):
        return 'Service: {}\n\ttype: {}\n\textra_args: {}\n\ttranslator (ex: {}): {}'.format(self.name, self.type, self.extra_args, self.translator_exclusive, self.translator)

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
    def __init__(self, name, file, extra_args, translator, translator_exclusive):
        super().__init__(name, extra_args, ServiceType.PYTHON, translator, translator_exclusive)
        self.file = file

    def __str__(self):
        return 'Python Service: {}\n\ttype: {}\n\tfile: {}\n\textra_args: {}\n\ttranslator (ex: {}): {}'.format(self.name, self.type, self.file, self.extra_args, self.translator_exclusive, self.translator)

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
    def __init__(self, name, url, method, auth, extra_args, translator, translator_exclusive):
        super().__init__(name, extra_args, ServiceType.HTTP, translator, translator_exclusive)
        self.url = url
        self.method = method 
        self.auth = auth

    def __str__(self):
        return 'HTTP Service: {}\n\ttype: {}\n\turl: {}\n\tmethod: {}\n\tauth: {}\n\textra_args: {}\n\ttranslator (ex: {}): {}'.format(self.name, self.type, self.url, self.method, self.auth, self.extra_args, self.translator_exclusive, self.translator)

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
        type = _check_var_arg(args['type'], variables_dict)

        extra_args = None
        if 'args' in args:
            extra_args = _merge_list_to_dict(args['args'])
            for _arg in extra_args:
                extra_args[_arg] = _check_var_arg(extra_args[_arg], variables_dict)

        translator = None
        if 'translator' in args:
            translator = _merge_list_to_dict(args['translator'])
        translator_exclusive = False
        if 'translator-exclusive' in args:
            translator_exclusive = _check_var_arg(args['translator-exclusive'], variables_dict)

        if(type == 'HTTP'):
            if not ('url' in args and 'method' in args):
                raise Exception('HTTP service requires \"url\" and \"method\" values')

            url = _check_var_arg(args['url'], variables_dict)
            method = _check_var_arg(args['method'], variables_dict)
            auth = None
            if 'auth' in args:
                auth = _merge_list_to_dict(args['auth'])
                for _arg in auth:
                    auth[_arg] = _check_var_arg(auth[_arg], variables_dict)
            res = HTTPServiceData(name, url, method, auth, extra_args, translator, translator_exclusive)

        elif(type == 'python'):
            if not 'file' in args:
                raise Exception('Python service requires a \"file\" value')
            file = _check_var_arg(args['file'], variables_dict)
            res = PythonServiceData(name, file, extra_args, translator, translator_exclusive)

        else:
            res = ServiceData(name, extra_args, translator=translator, translator_exclusive=translator_exclusive)

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

