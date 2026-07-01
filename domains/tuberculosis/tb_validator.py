class TBValidator:

    def __init__(self):

        self.results = []

    def check(self, condition, success, failure

    ):

        if condition:

            self.results.append(

                ("PASS", success)

            )

        else:

            self.results.append(

                ("FAIL", failure)

            )

    def report(self):

        print()

        print("=" * 45)

        print("TB VALIDATION REPORT")

        print("=" * 45)

        for status, message in self.results:

            print(f"[{status}] {message}")

        print("=" * 45)

    def latest(self, history, key, default=0.0):

        values = history.get(key, [])

        if values:
            return values[-1]

        return default