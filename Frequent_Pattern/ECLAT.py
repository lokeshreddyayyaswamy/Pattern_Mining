from Frequent_Pattern import abstract as _ab
from typing import Dict, Union,Tuple,List
from pandas import DataFrame

class ECLAT(_ab._FrequentPatterns):
    """
        ECLAT algorithm to mine frequent itemsets from a transactional database.

        Inherits:
            _FrequentPatterns: Abstract class containing structure and shared attributes.

        Attributes inherited:
            _ifile (str): Input file or DataFrame.
            _minsup (int/float): Minimum support threshold.
            _sep (str): Separator for transactions.
            _final_patterns (dict): Stores final frequent patterns.
            _startTime, _endTime (float): Execution time tracking.
            _memoryUSS, _memoryRSS (float): Memory usage stats.
            _database (list): Parsed transactions.
        """

    def __init__(self, _ifile, _minsup, _sep="\t"):
        super().__init__(_ifile, _minsup, _sep)

    def database_b(self, _ifile: Union[str, DataFrame]) -> None:

        """Loads and parses the input file, URL, or DataFrame into the transaction database."""

        if isinstance(_ifile, _ab._pd.DataFrame):
            self._database = _ifile.columns.values.tolist()

            if len(self._database) == 1 and (self._database[0] == 'Transactions' or self._database[0] == 'TID'):
                self._database = _ifile[self._database[0]].values
                self._database = [x.split(self._sep) for x in self._database]
            elif len(self._database) == 2 and (self._database[1] == 'Items'):
                self._database = _ifile[self._database[1]].values
                self._database = [x.split(self._sep) for x in self._database]
            elif len(self._database) == 1 and self._sep in self._database[0]:
                self._database.extend(_ifile[self._database[0]].values.tolist())
                self._database = [x.split(self._sep) for x in self._database]
            else:
                raise Exception(
                    "your dataframe data has no columns as 'Transactions', 'TID' or 'Items' or data with specified seperator")

        if isinstance(_ifile, str):

            if _ab._validators.url(_ifile):
                data = _ab._urlopen(_ifile)
                for line in data:
                    line = line.decode("utf-8")
                    temp = [transaction.strip() for transaction in line.split(self._sep)]
                    temp = [x for x in temp if x]
                    self._database.append(temp)

            else:
                try:
                    with open(_ifile, 'r', encoding='utf-8') as file_r:

                        for line in file_r:
                            temp = [transaction.strip() for transaction in line.split(self._sep)]
                            temp = [x for x in temp if x]
                            self._database.append(temp)
                except IOError:
                    print("Check, your file is not there")

    def min_converter(self) -> int:

        """ It returns the minimum support threshold."""

        if type(self._minsup) is int:
            return self._minsup

        if type(self._minsup) is float:
            self._minsup = (self._minsup * (len(self._database)))

        if type(self._minsup) is str:
            if '.' in self._minsup:
                self._minsup = float(self._minsup)
                self._minsup = self._minsup * (len(self._database))
            else:
                self._minsup = int(self._minsup)
        else:
            raise Exception('Enter the minsup value correctly')

        return self._minsup

    def generate_sets(self) -> Tuple[Dict[Tuple[str], set], List[Tuple[str]]]:

        """Generates initial 1-itemsets and candidates with their transaction indices.

        Returns:
            Tuple containing:
                - dict of items with supporting transaction indices
                - list of candidate 1-itemsets
        """

        items = {}

        index = 0
        for transactions in self._database:
            for item in transactions:
                if tuple([item]) not in items:
                    items[tuple([item])] = [index]
                elif tuple([item]) in items:
                    items[tuple([item])].append(index)
            index += 1

        items = {tuple(item): set(ind) for item, ind in items.items() if len(ind) >= self._minsup}
        items = dict(sorted(items.items(), key=lambda x: len(x[1])))

        cands = []

        for item in items:
            if len(items[item]) >= self._minsup:
                cands.append(item)
                self._final_patterns[item] = len(items[item])
        return items, cands

    def mine(self, items, cands):

        """Performs the ECLAT mining loop to generate all frequent itemsets.

                Args:
                    items: Dictionary of 1-itemsets and their supporting transactions.
                    cands: List of candidate itemsets.

                Returns:
                    Dictionary of frequent itemsets with their support counts.
        """

        for i in range(len(cands)):

            new_cands = []

            for j in range(i + 1, len(cands)):

                if cands[i][:-1] == cands[j][:-1]:

                    new_pattern = cands[i] + tuple([cands[j][-1]])

                    freq = items[tuple([new_pattern[0]])]

                    for l in range(1, len(new_pattern)):
                        freq = (freq).intersection(items[tuple([new_pattern[l]])])

                    if len(freq) >= self._minsup:
                        self._final_patterns[tuple(new_pattern)] = len(freq)

                        new_cands.append(new_pattern)

            if (len(new_cands)) > 1:
                self.mine(items, new_cands)

    def main(self) -> None:

            """Main execution method that performs data loading, mining, and memory tracking."""
            self._startTime = _ab._time.time()
            if self._ifile is None:
                raise Exception("You have not given the file path enter the file path or file name:")

            if self._minsup is None:
                raise Exception("Enter the Minimum Support")

            self.database_b(self._ifile)

            self._minsup = self.min_converter()

            items, cands = self.generate_sets()
            self.mine(items, cands)

            print("Frequent patterns were generated successfully using ECLAT algorithm")

            self._endTime = _ab._time.time()
            process = _ab._psutil.Process(_ab._os.getpid())
            _ab._gc.collect()
            self._memoryUSS = process.memory_full_info().uss
            self._memoryRSS = process.memory_info().rss

    def getUSSMemoryConsumption(self) -> float:

            """Returns the USS (Unique Set Size) memory consumed in bytes.

            Returns:
                float: USS memory usage.
            """
            return self._memoryUSS

    def getRSSMemoryConsumption(self) -> float:

            """Returns the RSS (Resident Set Size) memory consumed in bytes.

            Returns:
                float: RSS memory usage.
            """
            return self._memoryRSS

    def getRunTime(self) -> float:

            """Returns the total runtime of the algorithm.

            Returns:
                float: Runtime in seconds.
            """
            return self._endTime - self._startTime

    def getPatternsAsDataFrame(self) -> DataFrame:

            """Converts the frequent patterns into a pandas DataFrame.

            Returns:
                DataFrame containing items and their support count.
            """

            return _ab._pd.DataFrame(list([[self._sep.join(x), y] for x, y in self._final_patterns.items()]),
                                     columns=['Items', 'Support'])

    def save(self, _ofile: str, seperator: str = "\t") -> None:

            """Saves the frequent patterns to a file.

            Args:
                _ofile: Output file path.
                seperator: Delimiter to join itemsets.

            Returns:
                None
            """
            with open(_ofile, 'w') as file_w:
                file_w.write(f"Item : Support\n")
                for x, y in self._final_patterns.items():
                    x = seperator.join(x)
                    file_w.write(f"{x} : {y}\n")

    def getFrequentPatterns(self) -> Dict[Tuple[str], int]:

            """Returns the mined frequent itemsets with their support counts.

            Returns:
                Dictionary of itemsets and support.
            """
            return self._final_patterns

    def printResults(self) -> None:

            """Prints a summary of results including pattern count, memory usage, and runtime."""

            print("Total number of Frequent Patterns:", len(self.getFrequentPatterns()))
            print("Total Memory Consumed in USS:", self.getUSSMemoryConsumption())
            print("Total Memory Consumed in RSS", self.getRSSMemoryConsumption())
            print("Total ExecutionTime in ms:", self.getRunTime())

if __name__ == "__main__":
    _ifile = _ab._sys.argv[1]
    _ofile = _ab._sys.argv[2]
    _minsup = _ab._sys.argv[3]
    if len(_ab._sys.argv) == 4:
        _eclat = ECLAT(_ifile, _minsup)
    elif len(_ab._sys.argv) == 5:
        _sep = _ab._sys.argv[4]
        _eclat = ECLAT(_ifile, _minsup, _sep)
    else:
        print("Error! Invalid number of parameters.")
        _ab._sys.exit(1)
    _eclat.main()
    print("Total number of Frequent Patterns:", len(_eclat.getFrequentPatterns()))
    _eclat.save(_ofile)
    print("Total Memory in USS:", _eclat.getUSSMemoryConsumption())
    print("Total Memory in RSS", _eclat.getRSSMemoryConsumption())
    print("Total ExecutionTime in ms:", _eclat.getRunTime())

# python -m Frequent_Pattern.ECLAT Transactional_T10I4D100K.csv patterns.txt 1000
#import Frequent_Pattern.ECLAT as alg

#ifile='/content/Transactional_T10I4D100K.csv'

#ofile='patterns.txt'

#minsup=5000

#ec = alg.ECLAT(ifile, minsup)

#ec.main()

#frequentPattern = ec.getFrequentPatterns()

#print("Total number of Frequent Patterns:", len(frequentPattern))

#ec.save(ofile)

#Df = ec.getPatternsAsDataFrame()

#memUSS = ec.getUSSMemoryConsumption()

#print("Total Memory in USS:", memUSS)

#memRSS = ec.getRSSMemoryConsumption()

#print("Total Memory in RSS", memRSS)

#run = ec.getRunTime()

#print("Total ExecutionTime in seconds:", run)