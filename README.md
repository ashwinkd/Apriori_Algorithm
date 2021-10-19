# Apriori_Algorithm

Python Implementation of Apriori Algorithm

Given a set of transactions of the format

{item1, item2, item3, item4, ..., itemN1},

{item1, item2, item3, item4, ..., itemN2},

{item1, item2, item3, item4, ..., itemN3},

.

.

{item1, item2, item3, item4, ..., itemNM},

* Item1 in first transaction is not the same in other transactions. It is only used to represent different item witihin the transaction.
* Items may repeat in multiple transactions but not in the same transaction.
* Given this list of item co-occurence MS Apriori Algorithm is able to find frequent itemsets
* Frequent itemsets are set of items that have a high chance of occuring together according to the given transaction data.
* Each Frequent itemset is potentially a future transaction.
* Hence, output of MS Apriori Algorithm is similar to the format of the input transaction data. 
* The output is sorted according to the itemset length, i.e. $N1 \ge N2 \ge . . . \ge NM$
* That is, MS Apriori algorithms produce itemsets of length 1 which lead to generation of itemsets of length 2. This generation terminates when longer itemsets are not possible to generate. This is true as smaller transactions may occur frequently as well in longer transactions. Thus shorter transactions are atleast as frequent as longer transactions.
