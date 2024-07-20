from abc import ABC, abstractmethod

class ProcessInterface(ABC):
    @abstractmethod
    def thread(self):
        pass

    @abstractmethod
    def process(self):
        pass