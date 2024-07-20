from abc import ABC, abstractmethod
from threading import Thread, Lock

class ProcessBase:
    _thread_lock = Lock()
    _thread_running = False

    def __init__(self):
        # Define the lock as an instance variable
        self.lock = Lock()  

    @abstractmethod
    def process(self):
        pass

    def thread(self):
        with self._thread_lock:
            if not ProcessBase._thread_running:
                self._thread_running = True
                t = Thread(target=self._process_wrapper)
                t.daemon = True  
                t.start()
                return t

    def _process_wrapper(self):
        try:
            # Use the instance-level lock
            with self.lock:  
                # Call the abstract method
                self.process() 
        finally:
            self._thread_finished()

    
    def _thread_finished(self):
        ProcessBase._thread_running = False