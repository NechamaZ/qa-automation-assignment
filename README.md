# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

- `Ammeters/`
  - `main.py`: Main script to start the ammeter emulators and request current measurements.
  - `Circutor_Ammeter.py`: Emulator for the CIRCUTOR ammeter.
  - `Entes_Ammeter.py`: Emulator for the ENTES ammeter.
  - `Greenlee_Ammeter.py`: Emulator for the Greenlee ammeter.
  - `base_ammeter.py`: Base class for all ammeter emulators.
  - `client.py`: Client to request current measurements from the ammeter emulators.
- `Utiles/`
  - `Utils.py`: Utility functions, including `generate_random_float`.

## Usage

# Ammeter Emulators

## Greenlee Ammeter

- **Port**: 5001
- **Command**: `MEASURE_GREENLEE -get_measurement`
- **Measurement Logic**: Calculates current using voltage (1V - 10V) and (0.1Ω - 100Ω).
- **Measurement method** : Ohm's Law: I = V / R

## ENTES Ammeter

- **Port**: 5002
- **Command**: `MEASURE_ENTES -get_data`
- **Measurement Logic**: Calculates current using magnetic field strength (0.01T - 0.1T) and calibration factor (500 - 2000).
- **Measurement method** : Hall Effect: I = B * K

## CIRCUTOR Ammeter

- **Port**: 5003
- **Command**: `MEASURE_CIRCUTOR -get_measurement -current`
- **Measurement Logic**: Calculates current using voltage values (0.1V - 1.0V) over a number of samples and a random time step (0.001s - 0.01s).
- **Measurement method** : Rogowski Coil Integration: I = ∫V dt


-------------------------------------------------------------------------------------------------------------------------

## Virtual Environment Setup
The provided virtual environment (.venv) was recreated locally, as it referenced
a Python interpreter path that was not available on my current system.
A new `.venv` was generated to ensure compatibility and consistent execution.

## Environment Verification
First, I verified the emulator environment by running main.py
The output I got:
"CircutorAmmeter is running on port 5003
 EntesAmmeter is running on port 5002   
 GreenleeAmmeter is running on port 5001"
A mismatch was identified between the port numbers documented in the original README and the actual ports used by the running ammeter emulators.

## Resolution
The issue was resolved by updating the project documentation.
No code changes were applied, as the ammeter emulators were functioning correctly and listening on valid, non-conflicting ports.

The README was corrected to match the ports reported during execution:
- Greenlee Ammeter: 5001
- ENTES Ammeter: 5002
- CIRCUTOR Ammeter: 5003

## Client Command Fix
Fixing the commented out section on `main.py`.
The issue was resolved by updating the client requests to use the correct
command strings as defined in the emulator documentation:

Greenlee: `MEASURE_GREENLEE -get_measurement`
ENTES: `MEASURE_ENTES -get_data`
CIRCUTOR: `MEASURE_CIRCUTOR -get_measurement`

## Client Validation
After fixing the client command formats,
executing `main.py` and issuing direct measurement requests to all running
ammeter emulators.

## Observed Results
Greenlee Ammeter: Successfully returned a current measurement value.
ENTES Ammeter: Successfully returned a current measurement value.
CIRCUTOR Ammeter: A TCP connection was successfully established; however, no measurement data was returned.

## CIRCUTOR Command Fix
Investigation of the emulator implementation revealed that the CIRCUTOR ammeter
expects an extended command format that includes the `-current` flag in order
to trigger the integration-based measurement logic.

The client request was updated to use the correct command:
`MEASURE_CIRCUTOR -get_measurement -current`.

After applying this fix, the CIRCUTOR ammeter successfully returned a calculated
current value. This confirmed that the previous behavior was caused by a command
mismatch rather than a functional defect in the emulator.
The documentation of the original README was updated to reflect the correct command format.

## Data Collection and Sampling
The client interface was updated to return numeric (`float`) measurement values
instead of only printing them, enabling automated sampling, statistical analysis,
and result persistence.

I added this import to data_collector.py:
`from Ammeters.client import request_current_from_ammeter`

removed  `request_current_from_ammeter()` from main.py, called at data_collector.py
main.py is responsible only for starting ammeter emulation servers, while all client-side communication is handled by the testing and data collection layers.

## Environment Setup
import issue for the `yaml`, `numpy`, `scipy`, `matplotlib`, `seaborn` modules was encountered.
The issue was resolved by:
1. Installing the required dependency inside the virtual environment:
   `pip install pyyaml`
   `pip install numpy`
   `pip install scipy`
   `pip install matplotlib`
   `pip install seaborn`
2. Selecting the correct Python interpreter (`.venv`) in VS Code.

## Config Management
Configuration is loaded once at a single entry point
(`run_tests.py` and in setUpClass() method at `test_cases.py`) and injected into the testing framework.
This approach ensures a single source of truth for configuration data and keeps
the framework decoupled from file system concerns.

Configuration mismatch between emulator server
ports (main.py) and client connection settings was detected and resolved in test_config.yaml.

## Client–Server Separation
Manual client request calls were removed from the emulator startup code (main.py) to
preserve separation between server emulation and test execution.

## API change in SciPy
A breaking API change in SciPy was handled to ensure compatibility with recent
library versions.
The confidence interval calculation was updated to use the
modern `confidence` parameter instead of the deprecated `alpha` argument.

## Small Fixes
- A command mismatch was identified between the CIRCUTOR ammeter emulator and the
  test configuration. The emulator expected a command including the `-current`
  flag, while the configuration sent a different command format.

- A missing emulator initialization in the test-facing startup module `src/ammeters/main.py` was
  identified and fixed to ensure proper emulator availability during test runs.

- Unit tests were updated (test_cases.py) to explicitly load and pass the test configuration to
  the testing framework, ensuring consistency between test and runtime behavior.
 
- Resolved a runtime serialization issue where NumPy boolean types produced by SciPy statistics caused JSON export failure
  in result_analyzer.py converted NumPy boolean results to native Python bool: `bool(normality_p_value > 0.05)`

## Running tests
*manual testing:
  `python main.py`

*automated testing:
  `python -m unittest tests.test_cases`

## Emulator Startup – Manual vs Automated
The ammeter emulators can be started either manually via `main.py` for debugging and development, or automatically inside the test suite (`test_cases.py`).


## Test Results and Outputs
Each test run generates a unique test ID and produces:
- A JSON file containing metadata, raw measurements, and statistical analysis
- Visualization plots including time series, histogram, and box plot

All outputs are stored under the `results/` directory, with plots organized
by test ID to allow easy comparison between test runs.

All unit tests passed successfully, and the framework was validated end-to-end
using the provided ammeter emulators.

## Cleaning code
removing unused imports from `test_framework.py`:
`import time`
`from typing import List, Optional`

## Error handling
at `test_framework.py` in run_test():
validate unsupported ammeter type to fail fast.
adding try/except to fail fast and clearly.

## Logging enablement
enabling logger at init once per test run inside AmmeterTestFramework 
`self.logger = TestLogger(self.test_id)`
adding import
`from src.utils.logger import TestLogger`
now we can see the logs in the results folder.
logs are easier to read for debug instaed of just prints in console.
adding logger.exception method to logger.
adding `self.logger.info("....")` and other types (error, exception, warning...) in all relavent places to have info in the log.

## Accuracy Evaluation (Bonus)
`accuracy_evaluator.py` was implemented to compare measurement accuracy and consistency across different ammeter types.
The evaluator uses statistical metrics such as mean, standard deviation, and coefficient of variation to assess relative precision and identify the most reliable ammeter.

I added a dedicated unit test that validates the accuracy comparison logic.