
class APIException(Exception):
    pass

class MissingField(APIException):

    def __init__(self, field_name):
        super().__init__()
        self.field_name = field_name
