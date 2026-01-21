import sys
import os
from src.testing.accuracy_evaluator import AccuracyEvaluator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.config import load_config

import unittest
from src.testing.test_framework import AmmeterTestFramework
import threading
import time
from src.ammeters.main import (
    run_greenlee_emulator,
    run_entes_emulator,
    run_circutor_emulator
)

class TestAmmeterFramework(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        הפעלת האמפרמטרים לפני הבדיקות
        """
        cls.threads = [
            threading.Thread(target=run_greenlee_emulator, daemon=True),
            threading.Thread(target=run_entes_emulator, daemon=True),
            threading.Thread(target=run_circutor_emulator, daemon=True)
        ]
        
        for thread in cls.threads:
            thread.start()
            
        time.sleep(5)  # המתנה להפעלת השרתים

        # טעינת קונפיג פעם אחת
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "config", "test_config.yaml")
        cls.config = load_config(config_path)
        
    def setUp(self):
        # create framework for each test
        self.framework = AmmeterTestFramework(self.config)

    def test_greenlee_measurements(self):
        """
        בדיקת מדידות של Greenlee
        """
        results = self.framework.run_test("greenlee")
        self.assertIn("metadata", results)
        self.assertIn("measurements", results)
        self.assertIn("analysis", results)
        
        # בדיקת טווח המדידות
        for measurement in results["measurements"]:
            self.assertGreater(measurement["value"], 0)
            self.assertLess(measurement["value"], 100)

    def test_entes_measurements(self):
        """
        בדיקת מדידות של ENTES
        """
        results = self.framework.run_test("entes")
        self.assertIn("analysis", results)
        
        # בדיקת הניתוח הסטטיסטי
        analysis = results["analysis"]
        self.assertIn("mean", analysis)
        self.assertIn("std_dev", analysis)
        self.assertIn("outliers_count", analysis)

    def test_circutor_measurements(self):
        """
        בדיקת מדידות של CIRCUTOR
        """
        results = self.framework.run_test("circutor")
        
        # בדיקת המטא-דאטה
        metadata = results["metadata"]
        self.assertEqual(metadata["ammeter_type"], "circutor")
        self.assertIn("test_id", metadata)
        self.assertIn("timestamp", metadata)

    def test_invalid_ammeter_type(self):
        """
        בדיקת טיפול בסוג אמפרמטר לא חוקי
        """
        with self.assertRaises(ValueError):
            self.framework.run_test("invalid_type")

    def test_accuracy_comparison(self):
        """
        Bonus test:
        Compare accuracy across ammeter types and identify the most reliable one
        """
        results = {}

        for ammeter in ["greenlee", "entes", "circutor"]:
            results[ammeter] = self.framework.run_test(ammeter)

        evaluator = AccuracyEvaluator(logger=self.framework.logger)
        accuracy_report = evaluator.evaluate(results)

        # Basic sanity checks
        self.assertIn("most_reliable", accuracy_report)
        self.assertIn(
            accuracy_report["most_reliable"],
            ["greenlee", "entes", "circutor"]
        )

        # Ensure all ammeters were evaluated
        for ammeter in ["greenlee", "entes", "circutor"]:
            self.assertIn("accuracy_score", accuracy_report[ammeter])

if __name__ == '__main__':
    unittest.main() 