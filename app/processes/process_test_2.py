from processes.process_base import ProcessBase

class Process2(ProcessBase):
    def process(self):
        print("Hello from Process TWO!")

        # Use a sleep to simulate a long-running process
        #time.sleep(6)