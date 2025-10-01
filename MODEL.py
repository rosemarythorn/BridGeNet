import random
import BRIDGE
import numpy as np
import time
import multiprocessing



class Model:
    def __init__(self, lSpace, aSpace, inG, outG, lIn=None,lOut=None,bRAW=None,bCount=None):
        self.bRAW=bRAW
        self.bCount=bCount   #for generating a new model from scratch when one is not provided
        self.aSpace=aSpace
        self.lSpace=lSpace
        self.sTmem=list()
        self.outHandler=list()
        self.lIn=lIn or self.lSpace[0]
        if lOut==None:
            self.lOut=self.lSpace[1]
        else:
            self.lOut=lOut
        self.lOut=lOut or self.lSpace[1]
        self.inG=inG
        self.outG=outG
        
        if self.bRAW==None:
            shelf=self.generateBridges(lSpace=self.lSpace,aSpace=self.aSpace)
            self.bDict=shelf[0]
            self.bDictUnsorted=self.bDict
            self.bDictAddressPairs=shelf[1]
        else:
            self.bDictUnsorted=self.decomp()
            self.bDict=self.vCheck()
            self.bDictAddressPairs=self.generateAddressPairs()
        #print(self.bDictUnsorted)
        #print("bDict Unsorted Generated")
        #print(self.bDict)
        #print("bDict zoned to only include addresses within aSpace and lSpace")
        self.aDict=self.coallateAddresses()
        #print(self.aDict)
        #print("Addresses coallated")
        self.nDict=self.makeNDict()
        #print(self.nDict)
        #print("Nodes Dict generated")


    def decomp(self,bRAW=None,lSpace=None,aSpace=None):
        bRAW=bRAW or self.bRAW
        lSpace=lSpace or self.lSpace
        aSpace=aSpace or self.aSpace
        

        #Add later once i figure out the storage method for compiled bridges
        bDictUnsorted={}

        for i in range(lSpace[0],lSpace[1]+1):
            bDictUnsorted[i]=list()
            for i2 in range(0,self.bCount):
                bDictUnsorted[i].append(BRIDGE.generateRandomBridge(lSpace=lSpace,aSpace=aSpace,layer=i))
        
        
    def generateBridges(self,lSpace=None,aSpace=None):
        bDictAddressPairs={}
        bDict={}
        lSpace=lSpace or self.lSpace
        aSpace=aSpace or self.aSpace

        for i in range(lSpace[0],lSpace[1]+1):
            bDict[i]=list()
            bDictAddressPairs[i]=list()
        if self.bCount>(self.aSpace[1]-self.aSpace[0])**2:
            self.bCount=(self.aSpace[1]-self.aSpace[0])**2
            print("More bridges requested than number of valid address pair combinations within scope: bridge count lowered to prevent repeats")
        for i in range(lSpace[0],lSpace[1]): #does not generate bridges originating on the final layer, since yknow. that would cause problems.
            for i2 in range(0,self.bCount):
                actAddress=0
                passAddress=0
                keepgoing=True
                while keepgoing:
                    actAddress=random.randint(aSpace[0],aSpace[1])
                    passAddress=random.randint(aSpace[0],aSpace[1])
                    if (actAddress,passAddress) not in bDictAddressPairs[i]:
                        keepgoing=False
                    #else:
                        #print("Bridge #",i2," attempt deleted from nodes ",actAddress," to ",passAddress, " in layer ",i)
                bDict[i].append(BRIDGE.generateRandomBridge(lSpace=lSpace,aSpace=aSpace,layer=i,actAddress=actAddress,passAddress=passAddress))
                bDictAddressPairs[i].append((actAddress,passAddress))
                #print("Bridge #",i2," generated from nodes ",actAddress," to ",passAddress, " in layer ",i)
        return (bDict,bDictAddressPairs)
    
    def generateAddressPairs(self,lSpace=None,aSpace=None,bDict=None):
        bDict=bDict or self.bDict
        lSpace=lSpace or self.lSpace
        aSpace=aSpace or self.aSpace
        
        bDictAddressPairs={}
        for i in range(lSpace[0],lSpace[1]):
            bDictAddressPairs[i]=list()
            for each in bDict[i]:
                bDictAddressPairs[i].append((each.actAddress, each.passAddress))
        return bDictAddressPairs


    
    def vCheck(self, bDictUnsorted=None, aSpace=None, lSpace=None):
        bDictUnsorted=bDictUnsorted or self.bDictUnsorted
        lSpace=lSpace or self.lSpace
        aSpace=aSpace or self.aSpace
        shelf={}
        for i in range(lSpace[0],lSpace[1]+1):
            shelf[i]=list()
        for i in range(lSpace[0],lSpace[1]+1):
            for each in bDictUnsorted[i]:
                #allows for premature terminations of check if any condition is found to be false to save on performance
                if each.actAddress>=aSpace[0]:
                    if each.actAddress<=aSpace[1]:
                        if each.passAddress>=aSpace[0]:
                            if each.passAddress<=aSpace[1]:
                                if each.layer>=lSpace[0]:
                                    if each.layer<lSpace[1]:
                                        shelf[i].append(each)
        return shelf



    def coallateAddresses(self,bDict=None,lSpace=None,inG=None,outG=None,lIn=None, lOut=None):
        bDict=bDict or self.bDict
        lSpace=lSpace or self.lSpace
        inG=inG or self.inG
        outG=outG or self.outG
        lIn=lIn or self.lIn
        lOut=lOut or self.lOut
        
        shelf={}
        for i in range(lSpace[0],lSpace[1]+1):
            shelf[i]=set()
            #print(shelf)
        for i in range(lSpace[0],lSpace[1]): #does not include last layer, hence why lSpace does not have 1 added to it
            for each in bDict[i]:
                shelf[i].add(each.actAddress)
                shelf[i+1].add(each.passAddress)
        for each in outG:
            shelf[lOut].add(each)
        for each in inG:
            shelf[lIn].add(each)
        return shelf
    
    def makeNDict(self,aDict=None,lSpace=None):
        aDict=aDict or self.aDict
        lSpace=lSpace or self.lSpace
        
        nodeshopper={}
        for i in range(lSpace[0],lSpace[1]+1):
            nodeshopper[i]={}
        for i in range(lSpace[0],lSpace[1]+1):
            for each in aDict[i]:
                nodeshopper[i][each]=0
        return nodeshopper
    
    def runModel(self,inState):
        for i in range(len(inState)):
            self.nDict[self.lIn][i]=inState[i]
        for i in range(self.lSpace[0],self.lSpace[1]+1):
            for each in self.bDict[i]:
                shelf=each.executeBridgeSmall(self.nDict[i][each.actAddress])
                self.nDict[i+1][shelf[1]]=shelf[0]+self.nDict[i+1][shelf[1]]
        shelf=list()
        for each in self.outG:
            shelf.append(self.nDict[self.lOut][each])
        #print(self.nDict)
        self.outHandler.append((inState,shelf))
        
        for i in range(len(self.outHandler)):
            print("Outhandler Element ",i,": ",self.outHandler[i])

        return (inState,shelf)
    

    def sTmemPush(self,score=None,pullindex=0):
        self.sTmem.append((self.outHandler.pop(pullindex)),score)

        '''
    def runModelalt(self,inState):
        for i in range(len(inState)):
            self.nDict[self.lIn][i]=inState[i]
        for i in range(self.lSpace[0],self.lSpace[1]+1):
            for each in self.bDict[i]:
                self.nDict=each.executeBridge(self.nDict)
        shelf=list()
        for each in self.outG:
            shelf.append(self.nDict[self.lOut][each])
        return shelf
        '''
        #the above section was essentially a test version seeing whether passing the entire ndict to the bridge could execute
        #quicker than just passing a single element. predictably, it did not. additionally, for some reason I don't quite understand,
        #it causes an underflow error in sigmoid handling in the bridge, whereas in the "Small" bridge handler, it does not.
    
'''
lspacetemp=100
aspacetemp=10
bCount=10
testcount=100
nettime=0
for i in range(testcount):

    testmodel=Model((0,lspacetemp),(0,aspacetemp),(0,1,2,3),(0,1,2,3),bCount=bCount)


    start_time = time.perf_counter()

    testmodel.runModel((26,7,19,4,63,7))

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    testmodel=Model((0,lspacetemp),(0,aspacetemp),(0,1,2,3),(0,1,2,3),bCount=bCount)


    start_time = time.perf_counter()

    testmodel.runModelalt((26,7,19,4,63,7))

    end_time = time.perf_counter()

    elapsed_time2 = end_time - start_time
    print(f"Elapsed time for Short Bridge Execution: {elapsed_time} seconds")
    print(f"Elapsed time for full nDict transfer: {elapsed_time2} seconds")
    print("Difference: ",elapsed_time-elapsed_time2)
    nettime+=(elapsed_time-elapsed_time2)

#i fucking guess we go with full nDict transfer then. unless we 

print("Total time difference (Positive indicates short failure, negative indicates full failure): ",nettime)
print("Average time difference between iterations: ",nettime/testcount)###
'''