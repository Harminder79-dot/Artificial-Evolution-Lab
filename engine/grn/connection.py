class Connection:

    def __init__(self, source, target, weight):

        self.source = source

        self.target = target

        self.weight = weight

        self.original_weight = weight

        self.enabled = True