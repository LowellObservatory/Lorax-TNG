"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import ABC, abstractmethod

# General Sub-Agent class, inherit from Abstract Base Class
class SubAgent(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_status_and_broadcast(self):
        pass

    @abstractmethod
    def handle_message(self):
        pass
