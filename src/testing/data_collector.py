import time
from typing import List, Dict
import threading
import queue
from Ammeters.client import request_current_from_ammeter
import time

class DataCollector:
    def __init__(self, config: Dict, logger):
        self.config = config
        self.measurement_queue = queue.Queue()
        self.logger = logger
        
    def collect_measurements(self, ammeter_type: str, test_id: str) -> List[Dict]:
        """
        איסוף מדידות מהאמפרמטר
        """
        self.logger.info(f"Starting data collection for ammeter={ammeter_type}")
        measurements = []
        sampling_config = self.config["testing"]["sampling"]
        
        # חישוב מרווח הזמן בין דגימות
        interval = 1.0 / sampling_config["sampling_frequency_hz"]
        total_measurements = sampling_config["measurements_count"]
        self.logger.info(f"samples={total_measurements}, interval={interval:.3f}s, test_id={test_id}")

        # הפעלת תהליכון נפרד לדגימה
        sampling_thread = threading.Thread(
            target=self._sampling_worker,
            args=(ammeter_type, interval, total_measurements)
        )
        sampling_thread.start()
        
        # איסוף התוצאות
        for _ in range(total_measurements):
            measurement = self.measurement_queue.get()
            measurements.append({
                "timestamp": time.time(),
                "value": measurement,
                "test_id": test_id
            })
            
        sampling_thread.join()
        self.logger.info(
            f"Completed data collection, "
            f"samples_collected={len(measurements)}"
        )
        return measurements
        
    def _sampling_worker(self, ammeter_type: str, interval: float, total_measurements: int):
        """
        עובד שאוסף את המדידות בתהליכון נפרד
        """
        # Normalize ammeter identifier to match configuration keys
        ammeter_type = ammeter_type.lower()
        ammeter_config = self.config["ammeters"][ammeter_type]
        
        for _ in range(total_measurements):
            start_time = time.time()
            
            # קבלת מדידה מהאמפרמטר
            # כאן צריך להשתמש בקוד הקיים של האמפרמטרים
            measurement = self._get_measurement(ammeter_type, ammeter_config)
            
            self.measurement_queue.put(measurement)
            
            # המתנה עד לדגימה הבאה
            elapsed = time.time() - start_time
            if elapsed < interval:
                time.sleep(interval - elapsed)

    def _get_measurement(self, ammeter_type: str, config: Dict) -> float:
        for attempt in range(3):
            try:
                # Encode command from string to bytes to match socket communication protocol
                return request_current_from_ammeter(port=config["port"], command=config["command"].encode())
            except ConnectionRefusedError:
                self.logger.warning(
                    f"Connection refused | ammeter={ammeter_type}, "
                    f"port={config['port']}, retry={attempt + 1}/3"
                    )
                time.sleep(0.5)
        self.logger.error(
            f"Failed to get measurement after retries | "
            f"ammeter={ammeter_type}, port={config['port']}"
        )
        raise RuntimeError(
            f"Measurement failed after {attempt + 1} retries | "
            f"ammeter={ammeter_type}, port={config['port']}"
        )
