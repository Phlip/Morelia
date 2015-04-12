class MoreliaError(Exception):
    pass


class MissingStepError(MoreliaError):

    def __init__(self, predicate, suggest, *args, **kwargs):
        self.predicate = predicate
        self.suggest = suggest
