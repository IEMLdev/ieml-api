
class PathError(Exception):
    def __init__(self, message, path):
        self.message = message
        self.path = path

    def __str__(self):
        return self.message + "[%s]"%str(self.path)


class ResolveError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class IEMLObjectResolutionError(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return "Invalid ieml object definitions at:\n%s"%('\n'.join("\t[%s] %s"%(str(p), e) for p, e in self.errors))