from threading import Thread
import HAL

class TemperatureController(Thread):
    def __init__(self, sample_rate = 1):
        self.sample_rate = sample_rate

def InitializeComms():
    HAL.InitializeI2C(1)
    HAL.Initialize1Wire()
    HAL.InitializeUART()

class MainStateMachine():
    def __init__(self):