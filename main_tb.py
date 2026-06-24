import sys

log_file = open("tb_log.txt", "w")

sys.stdout = log_file

from domains.tuberculosis.tb_world import TBWorld

def main():

    world = TBWorld()

    world.run()


if __name__ == "__main__":

    main()