import json
from typing import List
from hashlib import sha256


class TxOutput:
    def __init__(self, value = None, pubkey = None, outputJsonObj = None):
        if outputJsonObj:
            self.__getWithJson(outputJsonObj)
            return
        self.value = value
        self.pubkey = pubkey
        
    def isEqual(self, txOutput) :
        return txOutput.value == self.value and txOutput.pubkey == self.pubkey    
    
    
    def __getWithJson(self, jsonObj):
        self.value = int(jsonObj['value'])
        self.pubkey = jsonObj['pubkey'].encode('utf-8')

    def toString(self):
        outputList = [str(self.value), str(self.pubkey)]
        return ''.join(outputList)

class TxInput:
    def __init__(self, number = None, output : TxOutput = None, inputJsonObj = None):
        if inputJsonObj:
            self.__getWithJson(inputJsonObj)
            return
        self.number = number
        self.output = TxOutput(output.value, output.pubkey)
        
    def isEqual(self, txInput):
        return self.number == txInput.number and self.output.isEqual(txInput.output)       

    def __getWithJson(self, jsonObj):
        self.number = jsonObj['number']
        self.output = TxOutput(outputJsonObj=jsonObj['output'])
    
    def toString(self):
        outputList = [str(self.number), str(self.output.value), str(self.output.pubkey)]
        return ''.join(outputList)


class Transaction:
    def __init__(self, txNumber = None, inputList : List[TxInput] = None, outputList : List[TxOutput] = None, sig = None, jsonObj = None):
        if jsonObj:
            self.__getTxWithJson(jsonObj)
            return
        self.txNumber = txNumber
        self.inputList = inputList
        self.outputList = outputList
        self.sig = sig

    def __getTxWithJson(self, jsonObj):
        jsonObj = jsonObj
        self.txNumber = jsonObj['number']
        self.inputList = []
        self.outputList = []
        self.sig = jsonObj['sig']

        for txInput in jsonObj['input']:
            self.inputList.append(TxInput(inputJsonObj=txInput))

        for txOutput in jsonObj['output']:
            self.outputList.append(TxOutput(outputJsonObj=txOutput))
        
    def hashingTxNumber(self):
        hashList = []
        for tx in self.inputList:
            hashList.append(tx.toString())
        for tx in self.outputList:
            hashList.append(tx.toString())
        hashList.append(self.sig)
    
        return sha256(''.join(hashList).encode('utf-8')).hexdigest()

    def toString(self):
        resList = [str(self.txNumber)]
        for tx in self.inputList:
            resList.append(tx.toString())
        for tx in self.outputList:
            resList.append(tx.toString())
        resList.append(self.sig)
        return ''.join(resList)

    def getJson(self):
        jsonOut = {"number": self.txNumber}

        inputList = []
        for txInput in self.inputList:
            TxInputObj = {"number": txInput.number, "output": {"value": txInput.output.value, "pubkey": txInput.output.pubkey.decode('utf-8')}}
            inputList.append(TxInputObj)
        jsonOut["input"] = inputList

        outputList = []
        for txOutput in self.outputList:
            TxOutputObj = {"value": txOutput.value, "pubkey": txOutput.pubkey.decode('utf-8')}
            outputList.append(TxOutputObj)
        jsonOut["output"] = outputList
        jsonOut["sig"] = self.sig
        return jsonOut







