# Minimum-Viable-Blockchain

## Running the program
To run our program, simply run the `driver.py` by using `python3 driver.py`. If want to test different cases, change the file names in __readTxFromFile() function in `driver.py`. Example: with `open("./transactions/xxxxxx.json")` --> replace xxxxxx with file name from transactions folder. Remember to include all required modules mentioned in the `requirement.txt.`


## Code structure overview

`Block.py`

- *Block* class and *BlockLinkedNode* class are implemented. *Block* class represents the basic structure of a block in the Blockchain. *BlockLinkedNode* class is used to represent a node in the Chain, which facilitates finding the previous block and current block.


`BlockChain.py`

- *BlockChain* class are implemented. *BlockChain* class represents the basic structure of a BlockChain, in which some functions, such as createGenesisBlock(), addBlock(), retrieveForking() are included.

`Node.py`

- The *Node* class is implemented in this file. Each object of this class is a blockchain network node,  with ability to do verifications. Verifications include to verify transaction is validly structured and the transaction is not already on the blockchain, etc. This class also includes broadcasting mined blocks, mining blocks from Tx pools and managing files.

`Transaction.py`

- 3 classes related to transactions are implemented, including *TxInput*, *TxOutput* and *Transaction*, which represent the operations over transaction stream.

`Driver.py`

- Creates an object of calls on all the test methods. Driver of testing all bad cases .


## Design of tests

### Json files for test input
We design 7 main different json files, each of which contains multiple transactions and these transactions will be used by different test methods in our `Driver.py` to cover different cases.

`GenesisTx.json`

- contains the genesis transaction with 15 initial outputs

`ValidTestTx.json`

- contains 15 valid transactions.

`DoubleSpendTestTx.json`

- contains 2 transactions with the same input (so the first is valid but the second one is invalid)

`InputOutputSumTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has different input sum and output sum

`SigVerifyTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has the wrong signature  

`NumberHashTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has the wrong number hash

`TxInputsExistTestTx.json`

- contains 2 transactions, the first is valid while the second transaction has non-exist input  


## Files generated
- `Nodex.json`
    - This json file records the ledger in node X. Each node should have their own copy of the blockchain ledger, so in this task we have 8 nodes and thus 8 node-x.json, each of which is essentially the same, except for those nodes who are inhonest.

