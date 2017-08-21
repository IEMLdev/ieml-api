from ieml.dictionary import DictionaryVersion
from ieml.dictionary.version import get_available_dictionary_version


def diff(version0, version1):
    """
    Display the terms added and removed between two versions
    :param version0:
    :param version1:
    :return:
    """
    version0.load()
    version1.load()

    deleted = set(version0.terms) - set(version1.terms)
    added = set(version1.terms) - set(version0.terms)

    print("====\n\tfrom: {0}".format(str(version0)))
    print("\n".join(("-{0} -- {1}".format(str(d), version0.translations['en'][d]) for d in deleted)))

    print("====\n\tto: {0}".format(str(version1)))
    print("\n".join(("+{0} -- {1}".format(str(d), version1.translations['en'][d]) for d in added)))


def find_first_version_of_script(sc):
    last = None
    for v in get_available_dictionary_version():
        v = DictionaryVersion(v)
        v.load()
        if sc not in v.terms:
            return last

        last = v



if __name__ == '__main__':
    diff(DictionaryVersion("dictionary_2017-07-27_20:27:41"), DictionaryVersion("dictionary_2017-08-16_19:31:28"))
    # print(find_first_version_of_script("B:.S:.n.-B:S:+T:.-n.T:.A:.-+n.S:+B:.U:.-'+B:.B:.n.-B:S:+T:.-u.M:.-'"))

    {"dictionary_2017-08-03_20:42:07": {"B:.S:.n.-k.-+n.-n.S:.U:.-+n.B:.U:.-+n.T:.A:.-'+B:.B:.n.-k.-+n.-u.S:.-+u.B:.-+u.T:.-'":"B:.S:.n.-B:S:+T:.-n.T:.A:.-+n.S:+B:.U:.-'+B:.B:.n.-B:S:+T:.-u.M:.-'"}}