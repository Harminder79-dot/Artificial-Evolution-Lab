class Gene:

    def __init__(self, name, expression=0.0, decay=0.97, threshold=0.5):

        self.name = name

        self.expression = expression

        self.previous_expression = expression

        self.decay = decay

        self.threshold = threshold

        self.incoming = []

        self.outgoing = []

    def add_incoming(self, connection):

        self.incoming.append(connection)

    def add_outgoing(self, connection):

        self.outgoing.append(connection)

    def decay_expression(self):

        self.previous_expression = self.expression

        self.expression *= self.decay