from Frequent_Pattern import abstract as _ab
from typing import Dict, Union,Tuple
from pandas import DataFrame
from itertools import combinations

_ab._sys.setrecursionlimit(20000)
class FPNode:

  def __init__(self,item,count,parent):
    self.item=item
    self.children={}
    self.count=count
    self.parent=parent

  def addchild(self,item,count=1):
    if item not in self.children:
      self.children[item]=FPNode(item,count,self)
    else:
      self.children[item].count+=count
    return self.children[item]

  def get_prefix_path(self):
    transactions=[]
    count=self.count
    node=self.parent
    while node.parent is not None:
      transactions.append(node.item)
      node=node.parent
    return transactions[::-1],count

class FPGrowth(_ab._FrequentPatterns):

    def __init__(self, _ifile, _minsup, _sep="\t"):
        super().__init__(_ifile, _minsup, _sep)
        self.__uniqueitemset = {}

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
                    quit()

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

    def itemset(self):

        for items in self._database:
            for item in items:
                if item not in self.__uniqueitemset:
                    self.__uniqueitemset[item] = 1
                else:
                    self.__uniqueitemset[item] += 1

    def all_combinations(self, arr):

        for i in range(1, len(arr) + 1):
            for combo in combinations(arr, i):
                yield combo

    def FPtree(self):

        headerdict = {}

        self.__uniqueitemset = {i: c for i, c in self.__uniqueitemset.items() if c >= self._minsup}

        root = FPNode([], 0, None)
        for items in self._database:
            currnode = root
            items = sorted([item for item in items if item in self.__uniqueitemset], key=lambda x: self.__uniqueitemset[x],
                           reverse=True)

            for item in items:
                currnode = currnode.addchild(item)

                if item not in headerdict:
                    headerdict[item] = [set([currnode]), 1]
                else:
                    headerdict[item][0].add(currnode)
                    headerdict[item][1] += 1

        return root, headerdict

    def recursive_pattern(self, root, headerdict):

        headerdict = {i: c for i, c in sorted(headerdict.items(), key=lambda v: v[1][1])}

        for item in headerdict:

            newroot = FPNode(root.item + [item], 0, None)
            if headerdict[item][1] >= self._minsup:
                self._final_patterns[tuple(newroot.item)] = headerdict[item][1]

            if len(headerdict[item][0]) == 1:
                transactions, count = headerdict[item][0].pop().get_prefix_path()
                if len(transactions) == 0:
                    continue

                combos = self.all_combinations(transactions)
                for c in combos:
                    self._final_patterns[tuple(list(c) + newroot.item)] = count

            if len(headerdict[item][0]) > 1:

                new_transactions = {}
                itemcount = {}

                for node in headerdict[item][0]:
                    transactions, count = node.get_prefix_path()

                    if len(transactions) == 0:
                        continue

                    if tuple(transactions) not in new_transactions:
                        new_transactions[tuple(transactions)] = count
                    else:
                        new_transactions[tuple(transactions)] += count

                    for t_item in transactions:
                        if t_item not in itemcount:
                            itemcount[t_item] = count
                        else:
                            itemcount[t_item] += count

                itemcount = {i: c for i, c in itemcount.items() if c >= self._minsup}

                if len(itemcount) == 0:
                    continue

                prefixheaderdict = {}

                for transactions, count in new_transactions.items():

                    currnode = newroot

                    transactions = sorted([transaction for transaction in transactions if transaction in itemcount],
                                          key=lambda x: itemcount[x], reverse=True)

                    for item_p in transactions:
                        currnode = currnode.addchild(item_p, count)

                        if item_p not in prefixheaderdict:
                            prefixheaderdict[item_p] = [set([currnode]), count]
                        else:
                            prefixheaderdict[item_p][0].add(currnode)
                            prefixheaderdict[item_p][1] += count

                if len(prefixheaderdict) == 0:
                    continue

                self.recursive_pattern(newroot, prefixheaderdict)

    def mine(self) -> None:

            """Main execution method that performs data loading, mining, and memory tracking."""
            self._startTime = _ab._time.time()
            if self._ifile is None:
                raise Exception("You have not given the file path enter the file path or file name:")

            if self._minsup is None:
                raise Exception("Enter the Minimum Support")

            self.database_b(self._ifile)

            self.itemset()

            self._minsup = self.min_converter()

            root, headerdict = self.FPtree()

            self.recursive_pattern(root, headerdict)

            print("Frequent patterns were generated successfully using FP-Growth algorithm")

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
        _fp = FPGrowth(_ifile, _minsup)
    elif len(_ab._sys.argv) == 5:
        _sep = _ab._sys.argv[4]
        _fp = FPGrowth(_ifile, _minsup, _sep)
    else:
        print("Error! Invalid number of parameters.")
        _ab._sys.exit(1)
    _fp.mine()
    print("Total number of Frequent Patterns:", len(_fp.getFrequentPatterns()))
    _fp.save(_ofile)
    print("Total Memory in USS:", _fp.getUSSMemoryConsumption())
    print("Total Memory in RSS", _fp.getRSSMemoryConsumption())
    print("Total ExecutionTime in ms:", _fp.getRunTime())

#import Frequent_Pattern.FPGrowth as alg

#ifile='/content/Transactional_T10I4D100K.csv'

#ofile='patterns.txt'

#minsup=5000

#fp = alg.FPGrowth(ifile, minsup)

#fp.mine()

#frequentPattern = fp.getFrequentPatterns()

#print("Total number of Frequent Patterns:", len(frequentPattern))

#fp.save(ofile)

#Df = fp.getPatternsAsDataFrame()

#memUSS = fp.getUSSMemoryConsumption()

#print("Total Memory in USS:", memUSS)

#memRSS = fp.getRSSMemoryConsumption()

#print("Total Memory in RSS", memRSS)

#run = fp.getRunTime()

#print("Total ExecutionTime in seconds:", run)