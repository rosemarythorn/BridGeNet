import random
import BRIDGE
import numpy as np
import time
import multiprocessing
import algs

#Note: add submodel support into initialize functions
#bDict elements should be able to be initialized as the same thing, right?
#We should probably code ztuff such that models stored in bDict are indexes to mDict


class Model:
    def __init__(self, lSpace, aSpace, inG, outG, lIn=None,lOut=None,bRAW=None,bCount=None,mdlDict=None):
        self.bRAW=bRAW
        self.mdlDict=mdlDict
        self.bCount=bCount   #for generating a new model from scratch when one is not provided
        self.aSpace=aSpace
        self.lSpace=lSpace     #lSpace[0] should never have elements to run on it.lSpace[1] is final layer, and thus should be included in calculations before export
        self.outHandler=list()
        self.lIn=lIn or self.lSpace[0]
        if lOut==None:
            self.lOut=self.lSpace[1]
        else:
            self.lOut=lOut
        self.lOut=lOut or self.lSpace[1]
        self.inG=inG
        self.outG=outG

        self.adjustPointerLB=(None,None)
        
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

        for i in range(lSpace[0]+1,lSpace[1]+1):
            bDictUnsorted[i]=list()
            for i2 in range(0,self.bCount):
                bDictUnsorted[i].append(BRIDGE.generateRandomBridge(lSpace=lSpace,aSpace=aSpace,layer=i))
        
        
    def generateBridges(self,lSpace=None,aSpace=None):
        bDictAddressPairs={}
        bDict={}
        lSpace=lSpace or self.lSpace
        aSpace=aSpace or self.aSpace

        #Initializes empty lists for all Valid operative Addresses
        for i in range(lSpace[0]+1,lSpace[1]+1):  #goes from 1 layer above lSpace[0] to final element lSpace[1]+1
            bDict[i]=list()
            bDictAddressPairs[i]=list()
        
        bCountMax=(self.aSpace[1]-self.aSpace[0])**2
        if self.bCount>bCountMax:
            self.bCount=bCountMax
            print("More bridges requested than number of valid address pair combinations within scope: bridge count lowered to prevent repeats")
        
        for i in range(lSpace[0]+1,lSpace[1]+1): #does not generate bridges originating on the first layer, since yknow. that would cause problems.
            for i2 in range(0,self.bCount):
                startAddress=0
                endAddress=0
                keepgoing=True
                while keepgoing:
                    startAddress=random.randint(aSpace[0],aSpace[1])
                    endAddress=random.randint(aSpace[0],aSpace[1])
                    if (startAddress,endAddress) not in bDictAddressPairs[i]:
                        keepgoing=False
                    #else:
                        #print("Bridge #",i2," attempt deleted from nodes ",startAddress," to ",endAddress, " in layer ",i)
                bDict[i].append(BRIDGE.generateRandomBridge(lSpace=lSpace,aSpace=aSpace,layer=i,startAddress=startAddress,endAddress=endAddress))
                bDictAddressPairs[i].append((startAddress,endAddress))
                #print("Bridge #",i2," generated from nodes ",startAddress," to ",endAddress, " in layer ",i)
        return (bDict,bDictAddressPairs)
    
    def generateAddressPairs(self,lSpace=None,aSpace=None,bDict=None):
        bDict=bDict or self.bDict
        lSpace=lSpace or self.lSpace
        aSpace=aSpace or self.aSpace
        
        bDictAddressPairs={}
        for i in range(lSpace[0],lSpace[1]):
            bDictAddressPairs[i]=list()
            for each in bDict[i]:
                bDictAddressPairs[i].append((each.startAddress, each.endAddress))
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
                if each.startAddress>=aSpace[0] and each.startAddress<=aSpace[1] and each.endAddress>=aSpace[0] and each.endAddress<=aSpace[1] and each.layer>=lSpace[0] and each.layer<lSpace[1]:
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
        for i in range(lSpace[0]+1,lSpace[1]+1):
            for each in bDict[i]:
                shelf[i-1].add(each.startAddress)
                shelf[i].add(each.endAddress)
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
    


    def connectionsRunner(self,inState,lSpace,bDict,lOut):        
        #Creating instance of nDict (to prevent overwriting from multiple runs)
        nDict=self.nDict
        #Running Bridge Computations
        for i in range(len(inState)):
            nDict[self.lIn][i]=inState[i]  #Adds the inputs from inState to nDict at lIn
        for i in range(lSpace[0]+1,lSpace[1]+1):
            
            #Activation function
            if i!=lSpace[0]+1:
                for i2 in nDict[i]:
                    nDict[i][i2]=algs.leakyReLU(nDict[i][i2])


            for each in bDict[i]:
                shelf=None
                if type(each)==BRIDGE.Bridge:
                    #print("Bridge should run here")
                    shelf=each.executeBridge(nDict[i-1][each.startAddress]) #Activates each bridge, layer by layer.
                    nDict[i][shelf[1]]+=shelf[0] #Adds resultant value to nDict location
                else:
                    #print("Submodel should run here")
                    inStateSub=()
                    for each2 in each.inG:
                        inStateSub.append(nDict[i-1][each2])
                    shelf=each.runModel(inState=inStateSub)[0]
                

                
            #print("Previous layer ",nDict[i-1])
            #print("Resultant layer ",nDict[i])
        outShelf=list()
        for each in self.outG:
            outShelf.append(nDict[lOut][each])# #Pulls all outG elements into outShelf list
        #print(self.nDict)
        self.outHandler.append((inState,outShelf))
        for i in nDict:
            for i2 in nDict[i]:
                nDict[i][i2]=0
        return outShelf
    


    def runModel(self,inState,lOut=None,outG=None):
        #Null Convergence/Declarations
        lOut=lOut or self.lOut
        outG=outG or self.outG
        bDict=self.bDict

        outShelf=self.connectionsRunner(inState,self.lSpace,bDict,lOut)

        return (inState,outShelf)
    

    
    def adjustElement(self,adjAmount=0.0001,idealE=None,adjLSpace=None,):

        #Define target node
        adjLSpace=adjLSpace or self.lSpace
        lSelected=self.adjustPointerLB[0] or random.randrange(adjLSpace[0]+1,adjLSpace[1]+1)  #ALWAYS PREFER POINTER TO AVOID WEIRD ERRORS
        bSelected=self.adjustPointerLB[1] or random.randrange(0,len(self.bDict[lSelected]))
        #print("Adjusting at LB: ", self.adjustPointerLB)


        oV=self.bDict[lSelected][bSelected].adjustElement(adjAmount=adjAmount,idealE=idealE)
        self.adjustPointerLB=(lSelected,bSelected)
        return oV


    def purgeLAE(self):
        self.bDict[self.adjustPointerLB[0]][self.adjustPointerLB[1]].purgeLAE()
        self.adjustPointerLB=(None,None)



    def sTmemPush(self,score=None,pullindex=0):
        self.sTmem.append((self.outHandler.pop(pullindex)),score)


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