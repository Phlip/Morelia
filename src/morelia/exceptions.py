class MoreliaError(Exception):
    pass


class MissingStepError(MoreliaError):

    def __init__(self, predicate, suggest, method_name, docstring, *args, **kwargs):
        self.predicate = predicate
        self.suggest = suggest
        self.method_name = method_name
        self.docstring = docstring
