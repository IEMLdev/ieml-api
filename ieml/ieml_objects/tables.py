

class Table:
    def __init__(self, s):
        """"""
        super().__init__()

        self.cells = None
        self.headers = None

    @staticmethod
    def from_script(s):
        r = Table()