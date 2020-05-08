import json

def translate_item(item, translator = None, exclusive = False, print_debug = False):
    if translator is None:
        return item
    translated = dict()
    for source in item:
        if source in translator:
            target = translator[source]
            if (print_debug):
                print("translating: {} [{}] to {}".format(source, item[source], target))
            translated[target] = item[source]
        elif not exclusive:
            if (print_debug):
                print("copying: {} [{}]".format(source, item[source]))
            translated[source] = item[source]
    return translated

'''
Generator that translates jsons read from input file.
input: input file path.
translator: dict specifying translation.
exclusive: translate only the fields specified by the translator. Ignored if no translator.
'''
def translate(input_path, translator = None, exclusive = False, print_debug = False):
    with open(input_path, 'r') as file:
        if translator is None:
            for line in file:
                yield json.loads(line)
        else:
            for line in file:
                current = json.loads(line)
                yield translate_item(current, translator=translator, exclusive=exclusive, print_debug=print_debug)

'''
Translates the entire file and returns an array.
See translate for parameters.
'''
def translate_all(input_path, translator = None, exclusive = False, print_debug = False):
    result = []
    for translated in translate(input_path, translator, exclusive, print_debug):
        result.append(translated)
    return result

