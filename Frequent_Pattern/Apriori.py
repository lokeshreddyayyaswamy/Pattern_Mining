from Frequent_Pattern import abstract as _ab
class Apriori(_ab._FrequentPatterns):

    def database_b(self, ifile):

        if isinstance(ifile, _ab._pd.DataFrame):
            self.database = ifile.columns.values.tolist()

            if len(self.database) == 1 and (self.database[0] == 'Transactions' or self.database[0] == 'TID'):
                self.database = ifile[self.database[0]].values
                self.database = [x.split(self.sep) for x in self.database]
            elif len(self.database) == 2 and (self.database[1] == 'Items'):
                self.database = ifile[self.database[1]].values
                self.database = [x.split(self.sep) for x in self.database]
            elif len(self.database) == 1 and self.sep in self.database[0]:
                self.database.extend(ifile[self.database[0]].values.tolist())
                self.database = [x.split(self.sep) for x in self.database]
            else:
                raise Exception(
                    "your dataframe data has no columns as 'Transactions', 'TID' or 'Items' or data with specified seperator")

        if isinstance(ifile, str):

            if _ab._validators.url(ifile):
                data = _ab._urlopen(ifile)
                for line in data:
                    line = line.decode("utf-8")
                    temp = [transaction.strip() for transaction in line.split(self.sep)]
                    temp = [x for x in temp if x]
                    self.database.append(temp)

            else:
                try:
                    with open(ifile, 'r', encoding='utf-8') as file_r:

                        for line in file_r:
                            temp = [transaction.strip() for transaction in line.split(self.sep)]
                            temp = [x for x in temp if x]
                            self.database.append(temp)
                except IOError:
                    print("Check, your file is not there")

    def min_converter(self):

        if type(self.minsup) is int:
            return self.minsup

        if type(self.minsup) is float:
            self.minsup = (self.minsup * (len(self.database)))

        if type(self.minsup) is str:
            if '.' in self.minsup:
                self.minsup = float(self.minsup)
                self.minsup = self.minsup * (len(self.database))
            else:
                self.minsup = int(self.minsup)
        else:
            raise Exception('Enter the minsup value correctly')

        return self.minsup

    def generate_sets(self):

        items = {}

        index = 0
        for transactions in self.database:
            for item in transactions:
                if tuple([item]) not in items:
                    items[tuple([item])] = [index]
                elif tuple([item]) in items:
                    items[tuple([item])].append(index)
            index += 1

        items = {tuple(item): set(ind) for item, ind in items.items() if len(ind) >= self.minsup}
        items = dict(sorted(items.items(), key=lambda x: len(x[1]), reverse=True))

        cands = []

        for item in items:
            if len(items[item]) >= self.minsup:
                cands.append(item)
                self.final_patterns[item] = len(items[item])
        return items, cands

    def mine(self, items, cands):

        while cands:
            new_key = []
            for i in range(len(cands)):
                for j in range(i + 1, len(cands)):
                    if cands[i][:-1] == cands[j][:-1]:
                        n_c = cands[i] + tuple([cands[j][-1]])
                        intersection = items[tuple([n_c[0]])]
                        for k in range(1, len(n_c)):
                            intersection = intersection.intersection(items[tuple([n_c[k]])])
                        if len(intersection) >= self.minsup:
                            new_key.append(n_c)
                            self.final_patterns[n_c] = len(intersection)

            del cands
            cands = new_key
            del new_key

        return self.final_patterns

    def main(self):

        self.startTime = _ab._time.time()
        if self.ifile is None:
            raise Exception("You have not given the file path enter the file path or file name:")

        if self.minsup is None:
            raise Exception("Enter the Minimum Support")

        self.database_b(self.ifile)

        self.minsup = self.min_converter()

        items, cands = self.generate_sets()
        self.mine(items, cands)

        print("Frequent patterns were generated successfully using APRIORI algorithm")

        self.endTime = _ab._time.time()
        process = _ab._psutil.Process(_ab._os.getpid())
        _ab._gc.collect()
        self.memoryUSS = process.memory_full_info().uss
        self.memoryRSS = process.memory_info().rss

    def getUSSMemoryConsumption(self):

        return self.memoryUSS

    def getRSSMemoryConsumption(self):

        return self.memoryRSS

    def getRunTime(self):

        return self.endTime - self.startTime

    def getPatternsAsDataFrame(self):
        return _ab._pd.DataFrame(list([[self.sep.join(x), y] for x, y in self.final_patterns.items()]),
                            columns=['Patterns', 'Support'])

    def save(self, oFile,seperator="\t"):

        with open(oFile, 'w') as f:
            for x, y in self.final_patterns.items():
                x = seperator.join(x)
                f.write(f"{x}:{y}\n")

    def getFrequentPatterns(self):

        return self.final_patterns

    def printResults(self) -> None:

        print("Total number of Frequent Patterns:", len(self.getFrequentPatterns()))
        print("Total Memory Consumed in USS:", self.getUSSMemoryConsumption())
        print("Total Memory Consumed in RSS", self.getRSSMemoryConsumption())
        print("Total ExecutionTime in ms:", self.getRunTime())

if __name__ == "__main__":
    ifile="Transactional_T10I4D100K.csv"
    ap=Apriori(ifile,5000,'\t')
    ap.main()
    ap.printResults()