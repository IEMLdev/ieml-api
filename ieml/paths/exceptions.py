
class PathError(Exception):
    def __init__(self, message, path):
        self.message = message
        self.path = path

    def __str__(self):
        return self.message + "[%s]"%str(self.path)