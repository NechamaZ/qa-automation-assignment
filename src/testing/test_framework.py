import uuid
from datetime import datetime
from typing import Dict

from .data_collector import DataCollector
from .result_analyzer import ResultAnalyzer
from .visualizer import DataVisualizer
from src.utils.logger import TestLogger

class AmmeterTestFramework:
    def __init__(self, config: Dict):
        self.config = config
        self.test_id = str(uuid.uuid4())
        self.logger = TestLogger(self.test_id)
        self.data_collector = DataCollector(self.config, self.logger)
        self.result_analyzer = ResultAnalyzer(self.config, self.logger)
        self.visualizer = DataVisualizer(self.config, self.logger)
        self.logger.info(f"Initialized test framework")
        
    def run_test(self, ammeter_type: str) -> Dict:
        """
        הרצת בדיקה מלאה על אמפרמטר ספציפי
        """
        if ammeter_type not in self.config["ammeters"]:
            self.logger.error(f"Unsupported ammeter type requested: {ammeter_type}")
            raise ValueError(f"Unsupported ammeter type: {ammeter_type}")
        try: 
            # איסוף נתונים
            measurements = self.data_collector.collect_measurements(
                ammeter_type=ammeter_type,
                test_id=self.test_id
            )

            # ניתוח התוצאות
            analysis_results = self.result_analyzer.analyze(measurements)

            # יצירת ויזואליזציה
            if self.config["analysis"]["visualization"]["enabled"]:
                self.visualizer.create_visualizations(
                    measurements,
                    test_id=self.test_id,
                    ammeter_type=ammeter_type
             )
            
            # הכנת המטא-דאטה
            metadata = {
                "test_id": self.test_id,
                "timestamp": datetime.now().isoformat(),
                "ammeter_type": ammeter_type,
                "test_duration": self.config["testing"]["sampling"]["total_duration_seconds"],
                "sampling_frequency": self.config["testing"]["sampling"]["sampling_frequency_hz"]
            }
        
            # שמירת התוצאות
            results = {
                "metadata": metadata,
                "measurements": measurements,
                "analysis": analysis_results
            }
        
            self._save_results(results)
            return results
        
        except Exception as e:
            # Wrap lower-level errors with clear test-level context
            raise RuntimeError(
             f"Test execution failed for ammeter '{ammeter_type}'"
            ) from e
        except Exception as e:
            self.logger.exception(f"Test execution failed for ammeter '{ammeter_type}'")
            raise RuntimeError(f"Test execution failed for ammeter '{ammeter_type}'") from e

    def _save_results(self, results: Dict) -> None:
        """
        שמירת תוצאות הבדיקה
        """
        import json
        import os
        
        save_path = self.config["result_management"]["save_path"]
        filename = f"{save_path}/{results['metadata']['test_id']}.json"
        
        os.makedirs(save_path, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4) 