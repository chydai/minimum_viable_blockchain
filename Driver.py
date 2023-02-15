from Block import Block
from BlockChain import BlockChain
from Node import *
from Transaction import *
from threading import Thread
import random
from time import *
import json


class Driver:
    def __init__(self):
        self.nodeList = []
        self.globalUnverifiedTxPool : Transaction = []
        myMVB = BlockChain(None)
        # create genesis Block via static method
        self.genesisBlock = BlockChain.createGenesisBlock(BlockChain)
        self.__startNodesThread(8)
        self.__readTxFromFile()

    def __startNodesThread(self, count):
        for id in range(1, count + 1):
            node = Node(self.genesisBlock, id)
            self.nodeList.append(node)
            nodeThread = Thread(target=self.nodeMining, args=(node,))
            nodeThread.start()
        for node in self.nodeList:
            node.miningNodeList += self.nodeList

    def nodeMining(self, node):
        while True:
            node.addBroadcastBlock()
            sleep(1)
            for tx in self.globalUnverifiedTxPool:
                if tx in node.alreadyMinedTx:
                    continue
                node.globalUnverifiedTxPool.append(tx)
                # self.globalUnverifiedTxPool.remove(tx)
            for tx in node.globalUnverifiedTxPool:
                print(tx.txNumber)
                node.miningBlock(tx)
                node.alreadyMinedTx.append(tx)
                if node.globalUnverifiedTxPool:
                    node.globalUnverifiedTxPool.remove(tx)
            if len(node.globalUnverifiedTxPool) == 0:
                sleep(1)
                if len(node.globalUnverifiedTxPool) == 0:
                    break
            
        node.writeToFile()
            
    
    # TODO: make the file name modifiable
    def __readTxFromFile(self):
        with open("./transactions/ValidTestTx.json") as f:
            jsonObj = json.load(f)
        for obj in jsonObj['txList']:
            sleep(random.uniform(0, 0.5))
            self.globalUnverifiedTxPool.append(Transaction(jsonObj=obj))

if __name__ == "__main__":
    testDriver = Driver()
