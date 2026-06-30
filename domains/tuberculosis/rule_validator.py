from domains.tuberculosis.tb_rules import TB_RULES


class RuleValidator:

    def validate(self, baseline, experiment, experiment_name):

        print("\n========== RULE VALIDATION ==========\n")

        for rule in TB_RULES:

            if rule["experiment"] != experiment_name:
                continue

            baseline_value = float(baseline[rule["metric"]])
            experiment_value = float(experiment[rule["metric"]])

            passed = False

            if rule["direction"] == "increase":
                passed = experiment_value > baseline_value

            elif rule["direction"] == "decrease":
                passed = experiment_value < baseline_value

            status = "PASS" if passed else "FAIL"

            print(f"[{status}] {rule['message']}")

        print("\n=====================================")