import numpy as np
import random

def sigmoid(x):
  if x>10:
      return 1
  elif x<-10:
      return -1
  else: 
      return round(((2*(1 / (1 + np.exp(-x))))-1),5)

class Bridge:
    def __init__(self,weight, bias, actvFunc, actAddress, passAddress, layer):
        self.weight=weight
        self.bias=bias
        self.actvFunc=actvFunc
        self.actAddress=actAddress
        self.passAddress=passAddress
        self.layer=layer
        self.mutAddressE=None

        '''
    def executeBridge(self,nDict):
        inVal=(nDict[self.layer][self.actAddress]*self.weight)+self.bias
        outVal=0
        if self.actvFunc==0:
            outVal=inVal
        elif self.actvFunc==1:
            outVal=sigmoid(inVal)
        elif self.actvFunc==2:
            outVal=sigmoid(inVal)
        
        nDictworking=nDict
        nDictworking[self.layer+1][self.passAddress]=nDict[self.layer+1][self.passAddress]+outVal
#if not debugging, comment out this next section
        #print("Bridge acted from address",self.layer,"x",self.actAddress," to address ",self.layer+1,"x",self.passAddress, "with weight ",self.weight," and bias ",self.bias," with activation function code ",self.actvFunc)

        return nDictworking
        '''
    
    def executeBridge(self,inVal):
        inVal=(inVal*self.weight)+self.bias
        outVal=0
        if self.actvFunc==0:
            outVal=inVal
        elif self.actvFunc==1:
            outVal=sigmoid(inVal)
        elif self.actvFunc==2:
            outVal=sigmoid(inVal)
#if not debugging, comment out this next section
        #
        #print("Bridge acted from address",self.layer,"x",self.actAddress," to address ",self.layer+1,"x",self.passAddress, "with weight ",self.weight," and bias ",self.bias," with activation function code ",self.actvFunc)
        #print("Output before activation: ",inVal,", Output after activation: ",outVal)
        return (outVal,self.passAddress)
    

    def mutateElement(self,mutAmount, mutElement=None):
        mutElement=mutElement or self.mutAddressE or random.randint(0,2)
        self.mutAddressE=mutElement
        if mutElement==0:
            self.weight+=mutAmount
        elif mutElement==1:
            self.bias+=mutAmount
        elif mutElement==2:
            self.actvFunc+=mutAmount
        return self.mutAddressE
    
    def purgeLAE(self):
        self.mutAddressE=None

    



    
def generateRandomBridge(lSpace,aSpace,layer="DEFAULT",actAddress="DEFAULT",passAddress="DEFAULT"):
    if layer=="DEFAULT":
        layer=random.randrange(lSpace[0],lSpace[1])
    if actAddress=="DEFAULT":
        actAddress=random.randrange(aSpace[0],aSpace[1])
    if passAddress=="DEFAULT":
        passAddress=random.randrange(aSpace[0],aSpace[1])
        
    return Bridge(random.randrange(-10,10),random.randrange(-10,10),random.randrange(1,2),actAddress,passAddress,layer)
#for i in range(0,100):    
#    testaSpace=[0,3]
#    testlSpace=[0,9]
#    test=generateRandomBridge(testlSpace,testaSpace)
#    testNDict=testfunctions.generateexampleNDict()
#    testfunctions.printNDict(testNDict)
#    test2=test.executebridge(testNDict)
#    testfunctions.printNDict(test2)