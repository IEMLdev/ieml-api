from ieml.exceptions import InvalidPathException

class Tag:

    def __init__(self, tag_content):
        self.content = tag_content

class USL:

    def __init__(self, propositions_list):
        self.propositions = propositions_list

        self.hyperlinks_table = {} # key : a proposition, value : a USL list
        self._build_hyperlink()

        self.tags_table = {} # key : a proposition, value : a tag

    def add_hyperlink(self, path, child_USL):
        if not path in self.hyperlinks_table:
            self.hyperlinks_table[path] = []
        self.hyperlinks_table[path].append(child_USL)

    def add_tag(self, proposition, tag):
        self.tags_table[proposition].append(tag)

    def _build_hyperlink(self):
        for proposition in self.propositions:
            for hyperlink in proposition.gather_hyperlinks([]):
                self.add_hyperlink(*hyperlink)

    def __str__(self):
        return '{/' + '//'.join(map(str, self.propositions)) + '/}'

    # def __eq__(self, other):
    #     return self.propositions == other.propositions \
    #            and self.hyperlinks_table == other.hyperlinks_table

    def get_path_from_ieml(self, ieml_list):
        proposition_list = []
        childs = self.propositions
        for ieml in ieml_list:
            for elem in childs:
                if str(elem) == ieml:
                    proposition_list.append(elem)
                    if hasattr(elem, 'childs'):
                        childs = elem.childs
                    else:
                        raise InvalidPathException()
                    break
            else:
                raise InvalidPathException()




class PropositionPath:
    def __init__(self, current_path, proposition):
        self.path = current_path + [proposition]

    def __str__(self):
        return '/'.join([str(proposition) for proposition in self.path])

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.path == other.path

