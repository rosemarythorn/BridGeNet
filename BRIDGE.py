import numpy as np
import random
import algs

class Bridge:
    def __init__(self,weight, bias, actvFunc, startAddress, endAddress, layer):
        self.weight=weight
        self.bias=bias
        self.actvFunc=actvFunc
        self.startAddress=startAddress
        self.endAddress=endAddress
        self.layer=layer
        self.adjPointerE=None

        
    def bridgeActivate (self,inVal):
        if self.actvFunc==0:
            outVal=inVal
        elif self.actvFunc==1:
            outVal=algs.sigmoid(inVal)
        elif self.actvFunc==2:
            outVal=algs.leakyReLU(inVal)
        return outVal
    
   

    def executeBridgeDependent(self,nDict):
        inVal=(nDict[self.layer-1][self.startAddress]*self.weight)+self.bias
        outVal=0
        outVal=self.bridgeActivate(inVal)        
        nDict[self.layer][self.endAddress]+=outVal
#if not debugging, comment out this next section
        #print("Input Layer: ",nDict[self.layer-1])
        #print("Bridge acted from address",self.layer-1,"x",self.startAddress," to address ",self.layer,"x",self.endAddress, "with weight ",self.weight," and bias ",self.bias," with activation function code ",self.actvFunc)
        #print("Input before Bridge Operations: ",nDict[self.layer-1][self.startAddress], "From address ",self.startAddress, "Output before activation: ",inVal,", Output after activation: ",outVal)
        #print("Output Layer: ",nDict[self.layer])
        #print()
        #print()
        
    
    def executeBridgeMixed(self,inVal):
        inVal=(inVal*self.weight)+self.bias
        outVal=0
        outVal=self.bridgeActivate(inVal)
#if not debugging, comment out this next section
        #
        #print("Bridge acted from address",self.layer-1,"x",self.startAddress," to address ",self.layer,"x",self.endAddress, "with weight ",self.weight," and bias ",self.bias," with activation function code ",self.actvFunc)
        #print("Output before activation: ",inVal,", Output after activation: ",outVal)
        return (outVal,self.endAddress)
    
    def executeBridgeIndependent(self,inVal):
        inVal=(inVal*self.weight)+self.bias
        outVal=0
        outVal=self.bridgeActivate(inVal)
#if not debugging, comment out this next section
        #
        #print("Bridge acted from address",self.layer-1,"x",self.startAddress," to address ",self.layer,"x",self.endAddress, "with weight ",self.weight," and bias ",self.bias," with activation function code ",self.actvFunc)
        #print("Output before activation: ",inVal,", Output after activation: ",outVal)
        return outVal
    

    def adjustElement(self,adjAmount, idealE=None):
        adjElement=self.adjPointerE or idealE or random.randint(1,2)
        self.adjPointerE=adjElement
        oV=0
        if adjElement==1:
            oV=self.weight
            self.weight+=adjAmount
        elif adjElement==2:
            oV=self.bias
            self.bias+=adjAmount
        elif adjElement==3:
            oV=self.actvFunc
            self.actvFunc+=adjAmount
        #print("Adjusted element ",adjElement, " saved address ", self.adjPointerE)
        return oV
    
    
    def purgeLAE(self):
        self.adjPointerE=None

    



    
def generateRandomBridge(lSpace,aSpace,layer=None,startAddress=None,endAddress=None):
    layer=layer or random.randrange(lSpace[0],lSpace[1])
    startAddress=startAddress or random.randrange(aSpace[0],aSpace[1])
    endAddress=endAddress or random.randrange(aSpace[0],aSpace[1])
        
    return Bridge(random.randrange(-1000,1000)/1000,random.randrange(-1000,1000)/1000,0,startAddress,endAddress,layer)
#for i in range(0,100):    
#    testaSpace=[0,3]
#    testlSpace=[0,9]
#    test=generateRandomBridge(testlSpace,testaSpace)
#    testNDict=testfunctions.generateexampleNDict()
#    testfunctions.printNDict(testNDict)
#    test2=test.executebridge(testNDict)
#    testfunctions.printNDict(test2)