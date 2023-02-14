import json
from Block import *
from Transaction import *
from typing import List
from hashlib import sha256
from BlockChain import *
from queue import Queue
import numpy as np

from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

logging.basicConfig(filename='main.log', filemode='w', level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("my-logger")
logger.handlers = []

class Node:
    def __init__(self, genesisBlock: Block = None, nodeID = None):
        self.id = nodeID
        self.miningNodeList = []
        self.blockChain = BlockChain(genesisBlock)
        self.blockQueue = Queue()
        self.globalUnverifiedTxPool : List[Transaction] = []
        self.alreadyMinedTx : List[Transaction] = []
        self.miningDifficulty = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    
    def miningBlock(self, tx : Transaction):
        if self.verifyTranscation(tx):
            nonce = 0
            blockPOW = str(self.miningDifficulty + 1)
            #TODO: Check if prev is the pow
            prevBlockNode = self.blockChain.last_block
            prevHashing = prevBlockNode.curBlockNode.hashing()
            txAndPrevBeforeHash = tx.toString() + prevHashing
            while int(blockPOW, 16) > self.miningDifficulty:
                blockInfo = txAndPrevBeforeHash + str(nonce)
                blockPOW = sha256(blockInfo.encode('utf-8')).hexdigest()
                nonce += 1
            nonce -= 1

            # add to the longest chain
            newBlock = Block(tx, prevHashing, nonce, blockPOW)
            newBlockLinkedNode = BlockLinkedNode(prevBlockNode, newBlock, prevBlockNode.height + 1)
            self.broadCastBlock(newBlock)
            txBroadcastList = self.addBlockToChain(newBlockLinkedNode)
            if txBroadcastList:
                self.__broadcastTx(txBroadcastList)

    def addBroadcastBlock(self):
        if self.blockQueue.empty():
            return
        while not self.blockQueue.empty():
            newBlock = self.blockQueue.get()
            if not self.__verifyBlockPOW(newBlock):
                logger.error("Verification Failed! Block POW not match for blocks from other node")
                continue
            if not self.verifyTranscation(newBlock.tx):
                # logger.error("Verification Failed! Transcation not valid for blocks from other node")
                continue
            for blockLinkedNode in self.blockChain.chain:
                if blockLinkedNode.hashing() == newBlock.prev:
                    foundPrevBlock = blockLinkedNode
                    break
            if not foundPrevBlock:
                logger.error("Verification Failed! Prev hash not match for blocks from other node")
                continue
            
            newBlockLinkedNode = BlockLinkedNode(foundPrevBlock, newBlock, foundPrevBlock.height + 1)
            self.blockChain.addBlock(newBlockLinkedNode)
            

    def __verifyBlockPOW(self, newBlock):
        blockInfo = newBlock.tx.toString() + newBlock.prev + str(newBlock.nonce)
        blockPOW = sha256(blockInfo.encode('utf-8')).hexdigest()

        if str(blockPOW) != newBlock.proofOfWork:
            logger.error("In Node " + str(self.id) + " :" + "POW does not match")
            return false
        return True


    def verifyTranscation(self, tx: Transaction) :  # verify a Tx
        """
            1. Ensure the transaction is not already on the blockchain (included in an existing valid block)
            2. Ensure the transaction is validly structured
        """
        return self.verifyTxNotAlreadyOnBlockchain(tx) and self.verifyTxValidStruct(tx)

    def verifyTxNotAlreadyOnBlockchain(self, tx: Transaction):
        #  Ensure the transaction is not already on the blockchain (included in an existing valid block)
        prevBlock = self.blockChain.last_block
        while prevBlock:
            if tx.txNumber == prevBlock.curBlockNode.tx.txNumber:
                logger.error("Verification Failed! Tx is already on the blockchain")
                return False
            prevBlock = prevBlock.prevBlockNode
        return True

    def verifyTxValidStruct(self, tx: Transaction):
        """
            Ensure the transaction is validly structured
        """
        TxNumHash = self.verifyTxNumberHash(tx) # number hash is correct
        TxInNum = self.verifyTxInputsNumber(tx) # each number in the input exists as a transaction already on the blockchain, each output in the input actually exists in the named transaction
        TxPKsig = self.verifyTxPubKeyAndSig(tx) # each output in the input has the same public key, and that key can verify the signature on this transaction
        TxDS = self.verifyTxDoubleSpend(tx) # that public key is the most recent recipient of that output (i.e. not a double-spend)
        TxIOSum = self.verifyTxInOutSum(tx) # the sum of the input and output values are equal
        return TxNumHash and TxInNum and TxPKsig and TxDS and TxIOSum

    def verifyTxNumberHash(self, tx: Transaction):
        #  Ensure number hash is correct
        num_Hash = tx.txNumber
        now_Hash = tx.hashingTxNumber()
        if tx.txNumber != '' and now_Hash == num_Hash:
            return True
        else:
            logger.error("In Node " + str(self.id) + " :" + "Tx Verification Failed! Number hash is not correct")

    def verifyTxInputsNumber(self, tx: Transaction):
        #  each number in the input exists as a transaction already on the blockchain
        #  each output in the input actually exists in the named transaction
        validInput_count= 0
        for Input in tx.inputList:
            num_Exist = False
            outputright = False
            prevBlock = self.blockChain.last_block
            while prevBlock:
                if Input.number == prevBlock.curBlockNode.tx.txNumber: # find that old transaction in the current block
                    num_Exist = True
                    for pBlockTxOutput in prevBlock.curBlockNode.tx.outputList:
                        if Input.output.isEqual(pBlockTxOutput):  # verify the output content
                            outputright = True
                            break
                    break
                prevBlock = prevBlock.prevBlockNode
            if num_Exist and outputright:
                validInput_count += 1
        if validInput_count == len(tx.inputList):
            return True
        else:
            logger.error("Node " + str(self.id) + " :" + "Tx Verification Failed! Inputs are not correct")

    def verifyTxPubKeyAndSig(self, tx: Transaction):
        #  each output in the input has the same public key, and that key can be used to verify the signature of the transaction
        if not tx.inputList:
            return False
        sender_PublicKey: bytes = tx.inputList[0].output.pubkey
        for Input in tx.inputList:
            if Input.output.pubkey != sender_PublicKey:
                logger.error("In Node " + str(self.id) + " :" + "Tx Verification Failed! Input pubkey is not unique")
                return False

        verifyKey = VerifyKey(sender_PublicKey, HexEncoder)
        try:
            verifyKey.verify(tx.sig.encode('utf-8'), encoder=HexEncoder)
            return True
        except BadSignatureError:
            logger.error("In Node " + str(self.id) + " :" + "Tx Verification Failed! Signature verification failed")
            return False
        # return True
    
    def verifyTxDoubleSpend(self, tx:Transaction):
        # that public key is the most recent recipient of that output (i.e. not a double-spend)
        for Input in tx.inputList:
            prevBlock = self.blockChain.last_block
            while prevBlock:
                for pBlockTxInput in prevBlock.curBlockNode.tx.inputList:
                    if Input.isEqual(pBlockTxInput):
                        logger.error("In Node " + str(self.id) + " :" + "Tx Verification Failed! Double spend detected")
                        return False
                prevBlock = prevBlock.prevBlockNode
            return True

    def verifyTxInOutSum(self, tx: Transaction) :
        #  the sum of the input and output values are equal
        inSum, outSum = 0, 0
        inSum = np.sum([x.output.value for x in tx.inputList])
        outSum = np.sum([y.value for y in tx.outputList])
        if not inSum == outSum:
            logger.error("In Node " + str(self.id) + " :" + "Tx Verification Failed! Tx Inputs val sum is not equal to outputs sum")
        return bool(inSum == outSum)

    def broadCastBlock(self, newBlock):
        for tempNode in self.miningNodeList:
            if tempNode != self:
                tempNode.blockQueue.put(newBlock)
    
    def addBlockToChain(self, newBlockLinkedNode : BlockLinkedNode):
        self.blockChain.addBlock(newBlockLinkedNode)

    def __broadcastTx(self, txBroadcastList):
        for tempNode in self.miningNodeList:
            if tempNode != self:
                for tx in txBroadcastList:
                    tempNode.globalUnverifiedTxPool.append(tx)
                    tempNode.alreadyMinedTx.remove(tx)
    
    def getJson(self):
        jsonOut = {"Blocks": []}
        for linkedBlockNode in self.blockChain.chain:
            jsonOut["Blocks"].append(linkedBlockNode.curBlockNode.getJson())
        return json.dumps(jsonOut, indent=4, sort_keys=True, separators=(',', ':'))

    def writeToFile(self):
        nodeJson = self.getJson()
        with open("./nodeOutputs/Node" + str(self.id) + '.json', 'w', encoding='utf-8') as f:
            f.write(nodeJson)
