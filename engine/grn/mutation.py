import random


class GRNMutation:

    @staticmethod
    def mutate_connections(connections):

        for connection in connections:

            # 5% chance to mutate this connection
            if random.random() < 0.05:

                connection.weight += random.gauss(0, 0.15)

                # Keep weights bounded
                connection.weight = max(
                    -2.0,
                    min(2.0, connection.weight)
                )