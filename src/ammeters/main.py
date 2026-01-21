from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Circutor_Ammeter import CircutorAmmeter

def run_greenlee_emulator():
    GreenleeAmmeter(5001).start_server()

def run_entes_emulator():
    EntesAmmeter(5002).start_server()

def run_circutor_emulator():
    CircutorAmmeter(5003).start_server()
