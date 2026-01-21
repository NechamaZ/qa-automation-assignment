import numpy as np
from typing import List, Dict
from scipy import stats

class ResultAnalyzer:
    def __init__(self, config: Dict, logger):
        self.config = config
        self.metrics = config["analysis"]["statistical_metrics"]
        self.logger = logger

    def analyze(self, measurements: List[Dict]) -> Dict:
        """
        ניתוח סטטיסטי של המדידות
        """

        values = [m["value"] for m in measurements]
        results = {}
        self.logger.info(f"Starting statistical analysis | samples={len(values)}, metrics={self.metrics}")
        if len(values) < 3:
            self.logger.warning("Not enough samples for advanced statistical analysis")


        # חישוב מדדים סטטיסטיים בסיסיים
        if "mean" in self.metrics:
            results["mean"] = float(np.mean(values))
        if "median" in self.metrics:
            results["median"] = float(np.median(values))
        if "std_dev" in self.metrics:
            results["std_dev"] = float(np.std(values))
        if "min" in self.metrics:
            results["min"] = float(np.min(values))
        if "max" in self.metrics:
            results["max"] = float(np.max(values))


        self.logger.info(f"Completed statistical analysis | {results}")

        # ניתוח מתקדם
        try:
            results.update(self._advanced_analysis(values)) 
        except Exception as e:
            self.logger.error(f"Advanced analysis failed | reason={str(e)}")

        return results
        

    def _advanced_analysis(self, values: List[float]) -> Dict:
        """
        ניתוח סטטיסטי מתקדם
        """
        self.logger.info("Starting advanced statistical analysis")
        advanced_results = {
            "skewness": float(stats.skew(values)),  # א-סימטריה
            "kurtosis": float(stats.kurtosis(values)),  # התפלגות
            "confidence_interval_95": list(stats.t.interval(
                confidence=0.95,
                df=len(values)-1,
                loc=np.mean(values),
                scale=stats.sem(values)
            )),
        }

        # בדיקת נורמליות
        _, normality_p_value = stats.normaltest(values)
        advanced_results["is_normal_distribution"] = bool(normality_p_value > 0.05)
        self.logger.info(f"Normality test | "f"is_normal={advanced_results['is_normal_distribution']}")

        # זיהוי חריגים
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        outlier_bounds = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
        outliers = [v for v in values if v < outlier_bounds[0] or v > outlier_bounds[1]]
        advanced_results["outliers_count"] = len(outliers)
        self.logger.info(f"Outlier detection | outliers_count={len(outliers)}")
        
        self.logger.info("Advanced statistical analysis completed")
        return advanced_results 