import json

def translate_item(item, translator = None, exclusive = False, print_debug = False):
    """
    Translate a single json

    Parameters
    --------------
        item : dict
            Item to translate.
        translator : Dict[str, str]
            Dict specifying translation, where the key is the field name in the input and value the field name in the output.
        exclusive : bool
            Translate only the fields specified by the translator. Ignored if no translator.
        print_debug : bool
            Whether to print the resulting translation or not

    Returns
    --------------
        translation_generator : Generator[Dict]
            Generator that gives a single translated json at a time
    """

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


def translate(input_path, translator = None, exclusive = False, print_debug = False):
    """
    Generator that translates jsons read from input file.

    Parameters
    --------------
        input : str
            Input file path.
        translator : Dict[str, str]
            Dict specifying translation, where the key is the field name in the input and value the field name in the output.
        exclusive : bool
            Translate only the fields specified by the translator. Ignored if no translator.
        print_debug : bool
            Whether to print the resulting translation or not

    Returns
    --------------
        translation_generator : Generator[Dict]
            Generator that gives a single translated json at a time
    """

    with open(input_path, 'r') as file:
        if translator is None:
            for line in file:
                yield json.loads(line)
        else:
            for line in file:
                current = json.loads(line)
                yield translate_item(current, translator=translator, exclusive=exclusive, print_debug=print_debug)


def translate_all(input_path, translator = None, exclusive = False, print_debug = False):
    """
    Translate jsons read from input file.

    Parameters
    --------------
        input : str
            Input file path.
        translator : Dict[str, str]
            Dict specifying translation, where the key is the field name in the input and value the field name in the output.
        exclusive : bool
            Translate only the fields specified by the translator. Ignored if no translator.
        print_debug : bool
            Whether to print the resulting translation or not

    Returns
    --------------
        translations : List[Dict]
            List of all translated jsons in a file
    """
    result = []
    for translated in translate(input_path, translator, exclusive, print_debug):
        result.append(translated)
    return result

