from abc import ABC as _ABC, abstractmethod as _abstractmethod
import numpy as _np
import time as _time
import gc as _gc
import csv as _csv
import pandas as _pd
from itertools import combinations
import os as _os
import psutil as _psutil
import sys as _sys
import validators as _validators
from urllib.request import urlopen as _urlopen

class _FrequentPatterns(_ABC):

    def __init__(self, ifile, minsup, sep):
        self.ifile = ifile
        self.minsup = minsup
        self.sep = sep
        self.final_patterns = {}
        self.startTime = float()
        self.endTime = float()
        self.memoryUSS = float()
        self.memoryRSS = float()
        self.database = []

    @_abstractmethod
    def mine(self):

        pass

    @_abstractmethod
    def getFrequentPatterns(self):

        pass

    @_abstractmethod
    def save(self, oFile):

        pass

    @_abstractmethod
    def getPatternsAsDataFrame(self):

        pass

    @_abstractmethod
    def getUSSMemoryConsumption(self):

        pass

    @_abstractmethod
    def getRSSMemoryConsumption(self):

        pass

    @_abstractmethod
    def getRunTime(self):

        pass

    @_abstractmethod
    def printResults(self):

        pass