from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager, SyncManager
from threading import Thread

class PNCAppManager(SyncManager): pass

def registerProxy(name, cls, proxy, manager):
    for attr in dir(cls):
        if inspect.ismethod(getattr(cls, attr)) and not attr.startswith("__"):
            proxy._exposed_ += (attr,)
            setattr(proxy, attr,
                    lambda s: object.__getattribute__(s, '_callmethod')(attr))
    manager.register(name, cls, proxy)

class TankControllerManager(BaseManager):
    def __init__(self):
        super(TankControllerManager, self).__init__()
        self.command_queue = Queue()

class TankController(Process):
    def __init__(self):
        super(TankController, self).__init__()

    def run(self):
        pass

class DeviceController(Thread):
    def __init__(self):
        super(DeviceController, self).__init__()

