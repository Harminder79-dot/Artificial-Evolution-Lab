class Comparator:

    @staticmethod
    def compare(baseline, experiment, experiment_name):

        print("\n========== EXPERIMENT COMPARISON ==========\n")

        metrics = [

            ("Population", "Population"),
            ("Active", "Active%"),
            ("Dormant", "Dormant%"),
            ("Stress", "Stress%"),
            ("Fitness", "AverageFitness"),
            ("ATP", "AverageATP"),
            ("Growth", "AverageGrowth"),
            ("DosR", "AverageDosR")

        ]

        for name, column in metrics:

            baseline_value = float(baseline[column])
            experiment_value = float(experiment[column])

            difference = experiment_value - baseline_value

            print(f"{name}")

            print(f"  Baseline : {baseline_value:.2f}")
            print(f"  {experiment_name} : {experiment_value:.2f}")
            print(f"  Difference : {difference:+.2f}")

            print()