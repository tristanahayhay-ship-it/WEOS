"""
WEOS
World Economic Operating System
Version 0.1.0
"""

from datetime import datetime


class WEOS:
    def __init__(self):
        self.name = "WEOS"
        self.version = "0.1.0"
        self.created = datetime.now()

    def info(self):
        return f"""
=========================================
WORLD ECONOMIC OPERATING SYSTEM
=========================================
Project : {self.name}
Version : {self.version}
Created : {self.created}
=========================================
"""


weos = WEOS()
print(weos.info())
