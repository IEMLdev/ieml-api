from ieml.ieml_objects.terms.version import get_available_dictionary_version, create_dictionary_version, \
    DictionaryVersion

to_find = "M:.-',M:.-',S:.-'S:.-'n.-S:.U:.-',_"

t = reversed(get_available_dictionary_version())
for version in t:
    version.load()
    if to_find in version.terms:
        version = create_dictionary_version(merge=[version])
        version.upload_to_s3()
        break


