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
    """
    Abstract base class for mining frequent patterns from transactional data.

    Attributes:
        ifile (str): Input file path or data.
        minsup (int): Minimum support threshold.
        sep (str): Separator used in the input file.
        final_patterns (dict): Stores mined frequent patterns.
        startTime (float): Start time of mining.
        endTime (float): End time of mining.
        memoryUSS (float): Unique Set Size memory used during execution.
        memoryRSS (float): Resident Set Size memory used during execution.
        database (list): Internal representation of the input database.
    """

    def __init__(self, ifile, minsup, sep):
        """
        Initializes the FrequentPatterns base class.

        Args:
            ifile (str): Path to input file or input data.
            minsup (int): Minimum support threshold.
            sep (str): Delimiter used in the input file.
        """
        self._ifile = ifile
        self._minsup = minsup
        self._sep = sep
        self._final_patterns = {}
        self._ofile = str()
        self._startTime = float()
        self._endTime = float()
        self._memoryUSS = float()
        self._memoryRSS = float()
        self._database = []

    @_abstractmethod
    def mine(self):
        """
        Abstract method to perform the mining of frequent patterns.
        Must be implemented in derived classes.
        """
        pass

    @_abstractmethod
    def getFrequentPatterns(self):
        """
        Abstract method to return the mined frequent patterns.
        Returns:
            dict: Dictionary of frequent patterns with support values.
        """
        pass

    @_abstractmethod
    def save(self, oFile):
        """
        Abstract method to save the frequent patterns to a file.

        Args:
            oFile (str): Output file path to save results.
        """
        pass

    @_abstractmethod
    def getPatternsAsDataFrame(self):
        """
        Abstract method to convert frequent patterns to a pandas DataFrame.

        Returns:
            pandas.DataFrame: DataFrame of frequent patterns.
        """
        pass

    @_abstractmethod
    def getUSSMemoryConsumption(self):
        """
        Abstract method to get the USS memory consumed during mining.

        Returns:
            float: USS memory usage in Bytes.
        """
        pass

    @_abstractmethod
    def getRSSMemoryConsumption(self):
        """
        Abstract method to get the RSS memory consumed during mining.

        Returns:
            float: RSS memory usage in Bytes.
        """
        pass

    @_abstractmethod
    def getRunTime(self):
        """
        Abstract method to get the total runtime of the mining process.

        Returns:
            float: Runtime in seconds.
        """
        pass

    @_abstractmethod
    def printResults(self):
        """
        Abstract method to print the final results.
        """
        pass
