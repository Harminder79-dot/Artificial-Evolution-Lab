from pathlib import Path
import json
import shutil
import time
import platform
import hashlib
import sys
from datetime import datetime


class ExperimentManager:

    def __init__(self, config = None):

        self.config = config

        self.name = config["experiment"]["name"]

        self.root = (

            Path("experiments")

            /

            self.name

        )

    def prepare(self):

        if self.root.exists():

            shutil.rmtree(

                self.root

            )

        self.root.mkdir(

            parents=True,

            exist_ok=True

        )

    def path(self, filename):

        return self.root / filename
    
    def save_config(self):

        with open(

            self.path(

                "config.json"

            ),

            "w"

        ) as f:

            json.dump(

                self.config.data,

                f,

                indent=4

            )

    def save_metadata(self):

        metadata = {

            "experiment":

                self.name,

            "timestamp":

                datetime.now().isoformat(),

            "configuration_hash":

                self.configuration_hash()

        }

        with open(

            self.path(

                "metadata.json"

            ),

            "w"

        ) as f:

            json.dump(

                metadata,

                f,

                indent=4

            )

    def log_path(self):

        return self.path("tb_log.txt")
    
    def plots_path(self):

        folder = self.path(

            "plots"

        )

        folder.mkdir(

            exist_ok=True

        )

        return folder
    
    def configuration_hash(self):

        encoded = json.dumps(

            self.config.data,

            sort_keys=True

        ).encode()

        return hashlib.sha256(

            encoded

        ).hexdigest()
    
    def save_environment(self):

        environment = {

            "python":

                sys.version,

            "platform":

                platform.platform(),

            "architecture":

                platform.machine()

        }

        with open(

            self.path(

                "environment.json"

            ),

            "w"

        ) as f:

            json.dump(

                environment,

                f,

                indent=4

            )

    