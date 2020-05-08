from translator import translate, translate_all

TRANSLATOR = {'name': 'tr_name', 'color': 'tr_color', 'object': 'tr_object', 'string': 'string'}

print("Translating non exclusively with {}".format(TRANSLATOR))
for translated in translate("json_test.json", TRANSLATOR, False, True):
    print(translated)

print("\n")
print("Translating all non exclusively with {}".format(TRANSLATOR))
translated = translate_all("json_test.json", TRANSLATOR, False, False)
print(translated)

print("Translating exclusively with {}".format(TRANSLATOR))
for translated in translate("json_test.json", TRANSLATOR, True, False):
    print(translated)

print("\n")
print("Translating without translator")
for translated in translate("json_test.json"):
    print(translated)
