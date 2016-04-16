
class Tag:

    def __init__(self, tag_content):
        self.content = tag_content

class USL:

    def __init__(self, propositions_list):
        self.propositions = propositions_list
        self.hyperlinks_table = {} # key : a proposition, value : a USL list
        self.tags_table = {} # key : a proposition, value : a tag

    def add_hyperlink(self, proposition, child_USL):
        if not proposition in self.hyperlinks_table:
            self.hyperlinks_table[proposition] = []
        self.hyperlinks_table[proposition].append(child_USL)

    def add_tag(self, proposition, tag):
        self.tags_table[proposition].append(tag)

