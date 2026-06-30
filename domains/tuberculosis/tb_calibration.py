class TBCalibration:

    @staticmethod
    def report(world):

        print("\n========== CALIBRATION ==========\n")

        print(f"Population : {world.debug_stats['population']}")

        print(f"Active     : {world.debug_stats['active_percent']:.1f}%")

        print(f"Dormant    : {world.debug_stats['dormant_percent']:.1f}%")

        print(f"Stress     : {world.debug_stats['stressed_percent']:.1f}%")

        print(f"Fitness    : {world.debug_stats['average_fitness']:.2f}")

        print(f"Generation : {world.debug_stats['max_generation']}")

        print(f"Lineages   : {world.debug_stats['living_lineages']}")

        ratio = (world.total_births / max(1, world.total_deaths))

        print(f"Total Births : " f"{world.total_births}")

        print(f"Total Deaths : " f"{world.total_deaths}")

        print(f"Birth/Death Ratio : " f"{ratio:.2f}")

        print(f"First Dormancy Tick : " f"{world.first_dormancy_tick}")

        print("\n=================================\n")