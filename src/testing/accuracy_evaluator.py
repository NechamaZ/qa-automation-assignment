import numpy as np
from typing import Dict

class AccuracyEvaluator:
    def __init__(self, logger):
        self.logger = logger

    def evaluate(self, results: Dict[str, Dict]) -> Dict:
        """
        Compare accuracy and reliability across different ammeter types.

        Method:
        - For each ammeter, calculate mean and standard deviation
        - Use Coefficient of Variation (CV = std / mean) as accuracy score
        - Lower CV => more stable and reliable measurement
        """

        self.logger.info("=" * 60)
        self.logger.info("Starting Accuracy Comparison Test")
        self.logger.info("=" * 60)

        accuracy_scores = {}

        for ammeter_type, result in results.items():
            values = [m["value"] for m in result["measurements"]]

            self.logger.info(f"Evaluating ammeter={ammeter_type} | samples={len(values)}")

            mean = float(np.mean(values))
            std_dev = float(np.std(values))
            cv = std_dev / mean if mean != 0 else float("inf")

            accuracy_scores[ammeter_type] = {
                "mean": mean,
                "std_dev": std_dev,
                "cv": cv
            }

            self.logger.info(
                f"Ammeter summary | "
                f"type={ammeter_type}, "
                f"mean={mean:.4f}, "
                f"std_dev={std_dev:.4f}, "
                f"cv={cv:.4f}"
            )

        # Lower CV = more reliable measurement
        most_reliable = min(
            accuracy_scores,
            key=lambda k: accuracy_scores[k]["cv"]
        )

        self.logger.info("=" * 60)
        self.logger.info("Accuracy Evaluation Summary")
        self.logger.info("=" * 60)
        self.logger.info(f"Most reliable ammeter: {most_reliable}")
        self.logger.info(f"Accuracy scores: {accuracy_scores}")

        # Build final report
        report = {}

        for ammeter, metrics in accuracy_scores.items():
            report[ammeter] = {
                **metrics,
                "accuracy_score": metrics["cv"]
            }

        report["most_reliable"] = most_reliable

        return report
