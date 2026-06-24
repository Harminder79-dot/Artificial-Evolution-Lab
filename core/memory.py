class Memory:

    def __init__(self):

        self.storage = {}


    def remember(

        self,

        key,

        value,

        confidence=1.0

    ):

        self.storage[key] = {

            "value": value,

            "confidence": confidence

        }


    def recall(

        self,

        key

    ):

        data = self.storage.get(key)

        if data:

            return data["value"]

        return None


    def get_confidence(

        self,

        key

    ):

        data = self.storage.get(key)

        if data:

            return data["confidence"]

        return 0


    def strengthen(

        self,

        key,

        amount=0.1

    ):

        if key in self.storage:

            self.storage[key]["confidence"] = min(

                1,

                self.storage[key]["confidence"]

                +

                amount

            )


    def weaken(

        self,

        key,

        amount=0.05

    ):

        if key in self.storage:

            self.storage[key]["confidence"] -= amount


            if (

                self.storage[key]["confidence"]

                <=

                0

            ):

                del self.storage[key]