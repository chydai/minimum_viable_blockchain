import json
import hashlib
from Transaction import *

class Block:
    def __init__(self,tx = None, prev = None, nonce = None, proofOfWork = None):
        self.tx = tx
        self.prev = prev
        self.nonce = nonce
        self.proofOfWork = proofOfWork

    def hashing(self):
        blockInfo = self.toString()
        return sha256(blockInfo.encode('utf-8')).hexdigest()
 
    def toString(self):
        outputList = [self.tx.toString()]
        outputList.append(str(self.prev))
        outputList.append(str(self.nonce))
        outputList.append(str(self.proofOfWork))
        return ''.join(outputList)

    def getJson(self):
        jsonOut = {"tx": self.tx.getJson(), "prev": str(self.prev), "nonce": str(self.nonce), "pow": str(self.proofOfWork)}
        return jsonOut

class BlockLinkedNode:
    def __init__(self, prevBlockNode, curBlockNode, height):
        self.prevBlockNode = prevBlockNode
        self.curBlockNode = curBlockNode
        self.height = height
