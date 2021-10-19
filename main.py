import os
import re
from collections import OrderedDict


class MSApriori:
    def __init__(self, data_file, parameter_file, output_filename):
        self.data_file = f"{os.path.dirname(os.path.abspath(__file__))}\\{data_file}"
        self.parameter_file = f"{os.path.dirname(os.path.abspath(__file__))}\\{parameter_file}"
        self.output_filename = f"{os.path.dirname(os.path.abspath(__file__))}\\{output_filename}"
        self.default_MIS = None
        self.F = []

    def get_transactions(self):
        """
        Read self.data_file to produce a list of transactions
        :return: transactions is a list of transactions
        transactions = [[item1, item2, ...],
                        [item1, item3, ...]
                        ]
        """
        transactions = []
        file = open(self.data_file, "r")
        for transaction in file.readlines():
            transaction = re.sub("[^0-9,]", "", transaction)
            if not transaction:
                continue
            transaction = transaction.split(",")
            transaction = [int(i) for i in transaction if i]
            transactions.append(transaction)
        return transactions

    def get_min_support(self):
        """
        Read self.parameter_file to produce MIS and SDC
        :return:MIS is a dictionary with key to value mapping as follows
        item_i --> user defined MIS of item_i
        SDC is a float value between 0.0 and 1.0
        """
        MIS = OrderedDict()
        SDC = 1.0
        file = open(self.parameter_file, "r")
        for line in file.readlines():

            if line.startswith("MIS"):
                # Either has MIS value
                # Clean up text part
                line = line.replace("MIS(", "")
                line = line.replace(")", "")
                # item and value are separated
                item, item_MIS_value = line.split("=")
                item_MIS_value = float(item_MIS_value)
                if item.strip() != "rest":
                    # not the default MIS value
                    item = int(item)
                    MIS[item] = item_MIS_value
                else:
                    # the default MIS value
                    self.default_MIS = item_MIS_value
            elif line.startswith("SDC"):
                # or has SDC value
                line = line.replace("SDC", "")
                line = line.replace("=", "")
                SDC = float(line)
        return MIS, SDC

    def sort_items(self, transactions, MIS):
        """
        Creates list of items I and M
        :param transactions: are the list of lists. Each transaction is a list of item_num
        :param MIS: is a dictionary mapping from item_num to user defined MIS values
        :return: I is a dictionary mapping from item_num to user defined MIS values
        such that item_num is present in transactions
        M is sorted version of I according to it's MIS values.
        """
        I = OrderedDict()
        for transaction in transactions:
            for item in transaction:
                I[item] = MIS.get(item, self.default_MIS)
        M = {k: v for k, v in sorted(I.items(), key=lambda item: item[1])}
        return I, M

    def init_pass(self, M, transactions):
        """
        Creates the seeds L and Frequent 1-itemsets
        :param M: is a dictionary mapping from item_num to user defined MIS values
        sorted according to its MIS values
        :param transactions: are the list of lists. Each transaction is a list of item_num
        :return:
        L: seeds
        F1: Frequest 1-itemsets
        n: number of transactions
        """
        # get support count of each item in transactions
        support_count = OrderedDict()
        n = len(transactions)
        for item, MIS in M.items():
            support_count[item] = 0
            for transaction in transactions:
                if item in transaction:
                    support_count[item] += 1
        i = None
        L = []
        F1 = []
        for item, MIS in M.items():
            if i is None:
                if support_count[item] / n >= MIS:
                    i = item
                    L.append(item)
                    F1.append([item])
            else:
                if support_count[item] / n >= M[i]:
                    L.append(item)
                    if support_count[item] / n >= MIS:
                        F1.append([item])
        return support_count, L, F1, n

    def is_in_lexicographic_order(self, val1, val2):
        arr = [str(val1), str(val2)]
        arr2 = sorted(arr)
        if arr == arr2:
            return True
        return False

    def k_1_subset(self, c):
        s = [[c[j] for j in range(len(c)) if j != i] for i in range(len(c))]
        return s

    def level2_candidate_gen(self, L, support_count, n, SDC, MIS):
        """
        Builds candidate set at level k = 2
        :param L: Seeds
        :param support_count: Actual count of items in given transactions
        :param n: Number of transactions
        :param SDC: Support Difference Constraint
        :param MIS: User defined MIS values
        :return: C2 Candidate set at level k=2
        """
        C2 = {}
        for i, l in enumerate(L):
            if support_count[l] / n >= MIS.get(l, self.default_MIS):
                for h in L[i + 1:]:
                    if (support_count[h] / n >= MIS.get(l, self.default_MIS)) and (
                            abs((support_count[h] / n) - (support_count[l] / n)) <= SDC):
                        cset = [l, h]
                        ckey = "#".join([str(elem) for elem in cset])
                        C2[ckey] = cset
        return C2

    def MS_candidate_gen(self, Fk_1, support_count, n, SDC, MIS):
        """
        Builds candidate set at k
        :param Fk_1: k-1 frequent itemsets
        :param support_count: Actual count of items in given transactions
        :param n: Number of transactions
        :param SDC: Support Difference Constraint
        :param MIS: User defined MIS values
        :return: Ck  Candidate set at level = k
        """
        Ck = []
        for f1 in Fk_1:
            for f2 in Fk_1:
                if f1[:-1] == f2[:-1] and f1[-1] != f2[-1]:
                    if self.is_in_lexicographic_order(f1[-1], f2[-1]):
                        if abs((support_count[f1[-1]] / n) - (support_count[f2[-1]] / n)) <= SDC:
                            c = f1 + [f2[-1]]
                            Ck.append(c)
                            for s in self.k_1_subset(c):
                                if (c[0] in s) or (MIS.get(c[1], self.default_MIS) == MIS.get(c[0], self.default_MIS)):
                                    if s not in Fk_1:
                                        if c in Ck:
                                            Ck.remove(c)
        _Ck = {}
        for cset in Ck:
            ckey = "#".join([str(elem) for elem in cset])
            _Ck[ckey] = cset
        return _Ck

    def save_to_file(self):
        """
        Reformat results in self.F to required structure and save to a file.
        :return: void
        """
        total_output = []
        for i, Fk in enumerate(self.F):
            length = i + 1
            Fk_string = []
            for itemset in Fk:
                itemset_string = " ".join([str(item) for item in itemset])
                itemset_string = f"\t\t({itemset_string})"
                Fk_string.append(itemset_string)
            Fk_string = "\n".join(Fk_string)
            output = f"(Length-{length} {len(Fk)}\n{Fk_string})"
            total_output.append(output)
        total_output = "\n".join(total_output)
        total_output = f"51 98\n{total_output}"
        print(total_output)
        fp = open(self.output_filename, "w")
        fp.write(total_output)
        fp.close()

    def apriori(self):
        """
        Implementation of Apriori Algorithm
        Saves the list of Frequent k-itemsets in self.F
        :return: void
        """
        transactions = self.get_transactions()
        MIS, SDC = self.get_min_support()
        I, M = self.sort_items(transactions, MIS)
        support_count, L, F1, n = self.init_pass(M, transactions)
        itemset_count = OrderedDict()
        Fk_1 = F1.copy()
        Fset = [F1.copy()]
        k = 2
        while Fk_1:
            if k == 2:
                Ck = self.level2_candidate_gen(L, support_count, n, SDC, MIS)
            else:
                Ck = self.MS_candidate_gen(Fk_1, support_count, n, SDC, MIS)
            for t in transactions:
                for (ckey, cset) in Ck.items():
                    if ckey not in itemset_count:
                        itemset_count[ckey] = 0
                    if set(cset).issubset(set(t)):
                        itemset_count[ckey] += 1
                    new_cset = cset[1:]
                    if set(new_cset).issubset(set(t)):
                        new_ckey = "#".join([str(item) for item in new_cset])
                        if new_ckey not in itemset_count:
                            itemset_count[new_ckey] = 0
                        itemset_count[new_ckey] += 1
            Fk = []
            for (ckey, cset) in Ck.items():
                if itemset_count[ckey] / n >= MIS.get(cset[0], self.default_MIS):
                    Fk.append(cset)
            if Fk:
                Fset.append(Fk.copy())
            Fk_1 = Fk.copy()
            k += 1
        self.F = Fset


def main():
    problem_num = 2
    data_file = f"data-{problem_num}\\data-{problem_num}.txt"
    parameter_file = f"data-{problem_num}\\para-{problem_num}.txt"
    ms_obj = MSApriori(data_file, parameter_file, f"data-{problem_num}\\result{problem_num}.txt")
    ms_obj.apriori()
    ms_obj.save_to_file()


if __name__ == '__main__':
    main()
    #51
    #98
