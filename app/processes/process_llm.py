from processes.process_base import ProcessBase
from db.db import Database
from llm.llm_tools import get_full_debate
from llm.llm_manager import LlmManager

class ProcessLlm(ProcessBase):

    def __init__(self):
        super().__init__() 
        # self.collection = collection


    def process(self):

        self.db = Database()
        
        did = 450

        full_debate = get_full_debate(did)

        llm_manager = LlmManager()
        llm_manager.test(full_debate)
        
       

 

 