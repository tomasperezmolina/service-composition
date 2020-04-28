from yaml_parser import get_variables

variables = get_variables('test_composer.yaml')

print(variables)

assert(variables == ['PYFILE', 'ARG2', 'USERNAME'])
