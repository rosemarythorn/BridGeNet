import random
import BRIDGE
import numpy as np
import time
import multiprocessing
import algs
import configs
import copy

#Note: add submodel support into initialize functions
#bDict elements should be able to be initialized as the same thing, right?
#We should probably code ztuff such that models stored in bDict are indexes to mDict


class Model:
    def __init__(self, inG, outG,lSpace=configs.defaultLSpace, aSpace=configs.defaultASpaceLayer, maxKernelCount=1,kernelOuts=True, lIn=None,lOut=None,bRAW=None,bCount=None,mdlDict=None,wBounds=configs.defaultBounds,bBounds=configs.defaultBounds):
        self.bRAW=bRAW
        self.mdlDict=mdlDict
        self.bCount=bCount   #for generating a new model from scratch when one is not provided
        self.outHandler=list()
        self.wBounds=wBounds
        self.bBounds=bBounds
        self.kernelOuts=kernelOuts
        self.maxKernelCount=maxKernelCount
        self.adjPointerLB=[None,None]


        self.lSpace=None
        #single endpoint provided
        if type(lSpace)==int:
            self.lSpace=(0,lSpace)
        #Both endpoints provided
        elif len(lSpace)==2:
            self.lSpace=(lSpace[0],lSpace[1])     #lSpace[0] should never have elements to run on it.lSpace[1] is final layer, and thus should be included in calculations before export
        #Invalid
        else:
            print("lSpace entry is invalid: reverting to default")

        self.aSpaceList=[]
        #Single Endpoint provided
        if type(aSpace)==int:
            for i in range(self.lSpace[0],self.lSpace[1]+1):
                self.aSpaceList.append((0,aSpace))
        #Both endpoints provided
        elif type(aSpace[0])==int:
            for i in range(self.lSpace[0],self.lSpace[1]+1):
                self.aSpaceList.append(tuple(aSpace))
        #List of endpoints with size equal to number of layers
        elif len(aSpace)==1+lSpace[1]-lSpace[0]:
            for each in aSpace:
                self.aSpaceList.append(each)
        #Invalid Entry
        else:
            print("Invalid aSpace data format: defaulting to configs")
            for i in range(self.lSpace[0],self.lSpace[1]+1):
                self.aSpaceList.append(configs.defaultASpaceLayer)
            
        self.aSpaceList=tuple(self.aSpaceList)
        

        self.inGList=[]

        #No inputs whatsoever
        if inG==None:
            pass
        #single inG, single input
        elif type(inG)==int:
            self.inGList=[((inG,inG))]
        #List of input targets which are also considered sources    
        elif type(inG[0])==int:
            self.inGList=[[]]
            for i in range(len(inG)):
                self.inGList[0].append((inG[i],inG[i]))
        #list of pairs of sources and targets
        elif type(inG[0][0])==int:
            self.inGList=[[]]
            for i in range(len(inG)):
                self.inGList[0].append(tuple(inG[i]))
        #list of inGs, each made of pairs of sources and targets
        else:
            for each in inG:
                self.inGList.append(tuple(each))
        self.inGList=tuple(self.inGList)
        

        self.outGList=[]
        #No inputs whatsoever
        if outG==None:
            pass
        #single outG, single input
        elif type(outG)==int:
            self.outGList=[((outG,outG))]
        #List of input targets which are also considered sources    
        elif type(outG[0])==int:
            self.outGList=[[]]
            for i in range(len(outG)):
                self.outGList[0].append((outG[i],outG[i]))
        #list of pairs of sources and targets
        elif type(outG[0][0])==int:
            self.outGList=[[]]
            for i in range(len(outG)):
                self.outGList[0].append(tuple(outG[i]))
        #list of outGs, each made of pairs of sources and targets
        else:
            for each in outG:
                self.outGList.append(tuple(each))
        self.outGList=tuple(self.outGList)



        self.lInList=[]
        #Single output layer
        if type(lIn)==int:
            for i in range(len(self.inGList)):
                self.lInList.append(lIn)
        #Multiple output layers, with count equal to size of inGList
        elif type(lIn)!=None and len(lIn)==len(self.inGList):
            self.lInList=tuple(lIn)
        #Invalid or no specified answer provided
        else:       
            for i in range(len(self.inGList)):
                self.lInList.append(self.lSpace[0])
        self.lInList=tuple(self.lInlist)


        self.lOutList=[]
        if type(lOut)==int:
            for i in range(len(self.outGList)):
                self.lOutList.append(lOut)
        elif type(lOut)!=None:
            self.lOutList=lOut
        else:
            for i in range(len(self.outGList)):
                self.lOutList.append(self.lSpace[1])
        self.lOutList=tuple(self.lOutList)
        
        '''
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
    '''
        


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
        
        
    def generateBridges(self,lSpace=None,aSpace=None,wBounds=None,bBounds=None):
        bDictAddressPairs={}
        wBounds=wBounds or self.wBounds
        bBounds=bBounds or self.bBounds
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
                bDict[i].append(BRIDGE.generateRandomBridge(lSpace=lSpace,aSpace=aSpace,layer=i,startAddress=startAddress,endAddress=endAddress,wBounds=wBounds,bBounds=bBounds))
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
        opNDict=copy.deepcopy(self.nDict)
        #Running Bridge Computations
        for i in range(len(self.inG)):
            if len(inState)>i:    #for example, if i=3, and length of 3, it means index 3 doesnt exist in inState, since it would only go up to 2. 
                opNDict[self.lIn][self.inG[i]]=inState[i]  #Adds the inputs from inState to nDict at lIn
        for i in range(lSpace[0]+1,lSpace[1]+1):
            
            #Activation function
            if i!=lSpace[0]+1:
                for i2 in opNDict[i]:
                    opNDict[i][i2]=algs.leakyReLU(opNDict[i][i2])   #Tinker with activ func
                    

            for each in bDict[i]:
                shelf=None
                if type(each)==BRIDGE.Bridge:
                    #print("Bridge should run here")
                    '''
                    shelf=each.executeBridge(opNDict[i-1][each.startAddress]) #Activates each bridge, layer by layer.
                    opNDict[i][shelf[1]]+=shelf[0] #Adds resultant value to nDict location
                    #Variant using experimental optimized individual value calculation
                    '''
                    each.executeBridgeDependent(opNDict)
                '''
                else:
                    #print("Submodel should run here")
                    inStateSub=()
                    for each2 in each.inG:
                        inStateSub.append(opNDict[i-1][each2])
                    shelf=each.runModel(inState=inStateSub)[0]
                '''

                
            #print("Previous layer ",opNDict[i-1])
            #print("Resultant layer ",opNDict[i])
        outShelf=list()
        for each in self.outG:
            outShelf.append(opNDict[lOut][each])# #Pulls all outG elements into outShelf list
            #print(outShelf)
        #print(outShelf)
        self.outHandler.append((inState,outShelf))
        return outShelf
    


    def runModel(self,inState,lOut=None,outG=None):
        #Null Convergence/Declarations
        lOut=lOut or self.lOut
        outG=outG or self.outG
        bDict=self.bDict

        outShelf=self.connectionsRunner(inState,self.lSpace,bDict,lOut)

        return (inState,outShelf)
    

    def setTarget(self,adjLSpace):
        #algs.printToDeep(f"adjPointerLB: {self.adjPointerLB}\n")
        adjLSpace=adjLSpace or self.lSpace

        if self.adjPointerLB[0]==None:
            self.adjPointerLB[0]=random.randrange(adjLSpace[0]+1,adjLSpace[1]+1)  #ALWAYS PREFER POINTER TO AVOID WEIRD ERRORS
        
        
        #algs.printToDeep(f"adjPointerLB: {self.adjPointerLB}\n")
        
        if self.adjPointerLB[1]==None:
            self.adjPointerLB[1]=random.randrange(0,len(self.bDict[self.adjPointerLB[0]]))
        
        #algs.printToDeep(f"adjPointerLB: {self.adjPointerLB}\n")

    
    def adjustElement(self,adjAmountProvided=0.0001,idealE=None,adjLSpace=None):

        #Define target node
        self.setTarget(adjLSpace=adjLSpace)
        #print("Adjusting at LB: ", self.adjPointerLB)

        shelf=self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjustElement(adjAmount=adjAmountProvided,idealE=idealE)
        oV=shelf[0]
        adjE=shelf[1]
        '''
        print("Adjusted element at ",self.adjPointerLB)
        if type(self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]])==BRIDGE.Bridge:
            print("Bridge in scope below adjusted, adjusted element ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerE)
        else:
            print("Model adjusted in scope below, Pointer ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerLB)
        '''
        return (oV,adjE)
    


    def setElement(self,adjAmount=0,idealE=None,adjLSpace=None):

        #Define target node
        #print(type(self.adjPointerLB))
        self.setTarget(adjLSpace=adjLSpace)
        #print("Adjusting at LB: ", self.adjPointerLB)

        shelf=self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].setElement(adjAmount=adjAmount,idealE=idealE)
        oV=shelf[0]
        adjE=shelf[1]
        '''
        print("Adjusted element at ",self.adjPointerLB)
        if type(self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]])==BRIDGE.Bridge:
            print("Bridge in scope below adjusted, adjusted element ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerE)
        else:
            print("Model adjusted in scope below, Pointer ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerLB)
        '''
        return (oV,adjE)
    
    def pollElement(self,idealE=None,adjLSpace=None):
        #Define target node
        self.setTarget(adjLSpace=adjLSpace)

        shelf=self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].pollElement(idealE=idealE)
        oV=shelf[0]
        adjE=shelf[1]
        '''
        print("Adjusted element at ",self.adjPointerLB)
        if type(self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]])==BRIDGE.Bridge:
            print("Bridge in scope below adjusted, adjusted element ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerE)
        else:
            print("Model adjusted in scope below, Pointer ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerLB)
        '''
        return (oV,adjE)

        

    def purgeLAE(self):
        if self.adjPointerLB!=[None,None]:
            self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].purgeLAE()
            self.adjPointerLB=[None,None]



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