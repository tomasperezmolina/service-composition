import json

'''
Generator that translates jsons read from input file.
input: input file path.
translator: dict specifying translation.
exclusive: translate only the fields specified by the translator. Ignored if no translator.
'''
def translate(input_path, translator = None, exclusive = False, print_debug = False):
    with open(input_path, 'r') as file:
        if(translator == None):
            for line in file:
                yield json.loads(line)
        else:
            for line in file:
                translated = dict()
                current = json.loads(line)
                for source in current:
                    if source in translator:
                        target = translator[source]
                        if (print_debug):
                            print("translating: {} [{}] to {}".format(source, current[source], target))
                        translated[target] = current[source]
                    elif(not exclusive):
                        if (print_debug):
                            print("copying: {} [{}]".format(source, current[source]))
                        translated[source] = current[source]
                yield translated

'''
Translates the entire file and returns an array.
See translate for parameters.
'''
def translate_all(input_path, translator = None, exclusive = False, print_debug = False):
    result = []
    for translated in translate(input_path, translator, exclusive, print_debug):
        result.append(translated)
    return result

