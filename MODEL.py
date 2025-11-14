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
    def __init__(self, inG, outG,lSpace=configs.defaultLSpace, aSpace=configs.defaultASpaceLayer, maxKernelCount=1,kernelOuts=True, lIn=None,lOut=None,subModels=(),bRAW=None,bCount=None,mdlDict=None,wBounds=configs.defaultBounds,bBounds=configs.defaultBounds):
        #Submodels input example format:((layer, submodel),(layer,submodel),etc)
        self.subModels=subModels
        self.bRAW=bRAW
        self.mdlDict=mdlDict
        self.bCount=bCount   #for generating a new model from scratch when one is not provided
        self.outHandler=list()
        self.wBounds=wBounds
        self.bBounds=bBounds
        self.kernelOuts=kernelOuts
        self.maxKernelCount=maxKernelCount
        self.adjPointerLB=[None,None]



        self.lSpace=self.formLSpace(lSpace)

        self.bCountList=self.formBCountList(self.lSpace,bCount)

        self.aSpaceList=self.formASpaceList(aSpace,self.lSpace)
        
        self.inGList=self.formInGList(inG)
        
        self.outGList=self.formOutGList(outG)

        self.lInList=self.formLInList(lIn,self.inGList,self.lSpace)

        self.lOutList=self.formLOutList(lOut,self.outGList,self.lSpace)

        
        
        if self.bRAW==None:
            shelf=self.generateBridges(lSpace=self.lSpace,aSpaceList=self.aSpaceList)
            self.bDict=shelf[0]
            self.bDictUnsorted=self.bDict
            self.bDictAddressPairs=shelf[1]
            self.bDictAddressPairsFull=shelf[2]
        else:
            self.bDictUnsorted=self.decomp()
            self.bDict=self.vCheck()
            self.bDictAddressPairs=self.generateAddressPairs()
        #algs.printToDeep(self.bDictUnsorted)
        #algs.printToDeep("bDict Unsorted Generated")
        #algs.printToDeep(self.bDict)
        #algs.printToDeep("bDict zoned to only include addresses within aSpace and lSpace")
        self.aDict=self.coallateAddresses()
        #algs.printToDeep(self.aDict)
        #algs.printToDeep("Addresses coallated")
        self.nDict=self.makeNDict()
        #algs.printToDeep(self.nDict)
        #algs.printToDeep("Nodes Dict generated")
        
        

    def formLSpace(self,lSpace):
        lSpaceOp=None
        #single endpoint provided
        if type(lSpace)==int:
            lSpaceOp=(0,lSpace)
        #Both endpoints provided
        elif len(lSpace)==2:
            lSpaceOp=(lSpace[0],lSpace[1])     #lSpace[0] should never have elements to run on it.lSpace[1] is final layer, and thus should be included in calculations before export
        #Invalid
        else:
            algs.printToDeep("lSpace entry is invalid: reverting to default")
            lSpaceOp=configs.defaultLSpace
        return lSpaceOp
    
    def formBCountList(self,lSpace,bCount):
        bCountList=[0]
        if type(bCount)==int:
            for L in range(lSpace[0]+1,lSpace[1]+1):
                bCountList.append(bCount)
        elif type(bCount)==None:
            for L in range(lSpace[0]+1,lSpace[1]+1):
                bCountList.append(configs.defaultBCount)
        elif len(bCount)==(1+lSpace[1]-lSpace[0]):
            for each in bCount:
                bCountList.append(each)
        return(bCountList)
            

    def formASpaceList(self,aSpace,lSpace=None):
        lSpace=lSpace or self.lSpace
        aSpaceList=[]
        #Single Endpoint provided
        if type(aSpace)==int:
            for L in range(self.lSpace[0],self.lSpace[1]+1):
                aSpaceList.append((0,aSpace))
        #Both endpoints provided
        elif type(aSpace[0])==int:
            for L in range(self.lSpace[0],self.lSpace[1]+1):
                aSpaceList.append(tuple(aSpace))
        #List of endpoints with size equal to number of layers
        elif len(aSpace)==1+lSpace[1]-lSpace[0]:
            for each in aSpace:
                aSpaceList.append(each)
        #Invalid Entry
        else:
            algs.printToDeep("Invalid aSpace data format: defaulting to configs")
            for L in range(self.lSpace[0],self.lSpace[1]+1):
                aSpaceList.append(configs.defaultASpaceLayer)
        aSpaceList=tuple(aSpaceList)
        return aSpaceList
    
    def formInGList(self,inG):
        inGList=[]
        #No inputs whatsoever
        if inG==None:
            pass
        #single inG, single input
        elif type(inG)==int:
            inGList=(((inG,inG),),)
        #List of input targets which are also considered sources    
        elif type(inG[0])==int:
            inGList=[[],]
            for i in range(len(inG)):
                inGList[0].append((inG[i],inG[i]),)
            inGList[0]=tuple(inGList[0])
        #list of pairs of sources and targets
        elif type(inG[0][0])==int:
            inGList=[[],]
            for i in range(len(inG)):
                inGList[0].append(tuple(inG[i]),)
            inGList[0]=tuple(inGList[0])
        #list of inGs, each made of pairs of sources and targets
        else:
            for each in inG:
                inGList.append(tuple(each))
        inGList=tuple(inGList)
        return inGList

    def formOutGList(self,outG):
        outGList=[]
        #No inputs whatsoever
        if outG==None:
            pass
        #single outG, single input
        elif type(outG)==int:
            outGList=(((outG,outG),),)
        #List of input targets which are also considered sources    
        elif type(outG[0])==int:
            outGList=[[]]
            for i in range(len(outG)):
                outGList[0].append((outG[i],outG[i]))
            outGList[0]=tuple(outGList[0])
        #list of pairs of sources and targets
        elif type(outG[0][0])==int:
            outGList=[[],]
            for i in range(len(outG)):
                outGList[0].append(tuple(outG[i]))
            outGList[0]=tuple(outGList[0])
        #list of outGs, each made of pairs of sources and targets
        else:
            for each in outG:
                outGList.append(tuple(each))
        outGList=tuple(outGList)
        return outGList

    def formLInList(self,lIn,inGList,lSpace):
        inGList=inGList or self.inGList
        lSpace=lSpace or self.lSpace
        lInList=[]
        #Single output layer
        if type(lIn)==int:
            for i in range(len(inGList)):
                lInList.append(lIn)
        #Multiple output layers, with count equal to size of inGList
        elif lIn!=None:
            if len(lIn)==len(inGList):
                lInList=tuple(lIn)
        #Invalid or no specified answer provided
        else:       
            for i in range(len(inGList)):
                lInList.append(lSpace[0])
        lInList=tuple(lInList)
        return lInList

    def formLOutList(self,lOut,outGList=None,lSpace=None):
        lSpace=lSpace or self.lSpace
        outGList=outGList or self.outGList
        
        lOutList=[]
        #Single output layer
        if type(lOut)==int:
            for i in range(len(outGList)):
                lOutList.append(lOut)
        #Multiple output layers, with count equal to size of outGList
        elif lOut!=None:
            if len(lOut)==len(outGList):
                lOutList=tuple(lOut)
        #Invalid or no specified answer provided
        else:       
            for i in range(len(outGList)):
                lOutList.append(lSpace[0])
        lOutList=tuple(lOutList)
        return lOutList
    
    


    def decomp(self,bRAW=None,lSpace=None,aSpace=None):
        bRAW=bRAW or self.bRAW
        lSpace=lSpace or self.lSpace
        aSpaceList=aSpaceList or self.aSpaceList
        

        #Add later once i figure out the storage method for compiled bridges
        bDictUnsorted={}

        for L in range(lSpace[0]+1,lSpace[1]+1):
            bDictUnsorted[L]=list()
            for i2 in range(0,self.bCount):
                bDictUnsorted[L].append(BRIDGE.generateRandomBridge(lSpace=lSpace,aSpace=aSpaceList[L],layer=L))
        
        
    def generateBridges(self,lSpace=None,aSpaceList=None,wBounds=None,bBounds=None,subModels=None,bCountList=None):
        if subModels==None:
            subModels=self.subModels
        bDictAddressPairs={}
        wBounds=wBounds or self.wBounds
        bBounds=bBounds or self.bBounds
        if bCountList==None:
            bCountList=self.bCountList
        else:
            bCountList=self.formBCountList(self.lSpace,bCountList) 
        bDict={}
        lSpace=lSpace or self.lSpace
        aSpaceList=aSpaceList or self.aSpaceList

        #Initializes empty lists for all Valid operative Addresses
        for L in range(lSpace[0]+1,lSpace[1]+1):  #goes from 1 layer above lSpace[0] to final element lSpace[1]+1
            bDict[L]=[]
            bDictAddressPairs[L]=[]
        
        shelf=Model.addSubmodels(bDict,subModels,bDictAddressPairs,aSpaceList)
        bDict=shelf[0]
        bDictAddressPairs=shelf[1]
        bDictAddressPairsFull=shelf[2]
        

        
            
        for L in range(lSpace[0]+1,lSpace[1]+1): #does not generate bridges originating on the first layer, since yknow. that would cause problems.
            bCountMax=(1+self.aSpaceList[L][1]-self.aSpaceList[L][0])**2
            algs.printToDeep(f"\nGenerating Bridges for layer {L}")
            algs.printToDeep(f"\nbcount prior to adjustment: {bCountList[L]}, bDictAddressPairs {bDictAddressPairs}")
            algs.printToDeep(f"\nbDictAddressPairs Slice {bDictAddressPairs[L]}")
            if bCountList[L]>bCountMax-len(bDictAddressPairs[L]):
                bCountList[L]=bCountMax-len(bDictAddressPairs[L])
                algs.printToDeep("More bridges requested than number of valid address pair combinations within scope: bridge count lowered to prevent repeats")
            algs.printToDeep(f"\nnumber of bridges to be generated: {bCountList[L]}, bCountMax before adjustment {bCountMax}")
            for i2 in range(0,bCountList[L]):
                startAddress=0
                endAddress=0
                keepgoing=True
                while keepgoing:
                    startAddress=random.randint(aSpaceList[L-1][0],aSpaceList[L-1][1])
                    endAddress=random.randint(aSpaceList[L][0],aSpaceList[L][1])
                    if (startAddress,endAddress) not in bDictAddressPairs[L]:
                        keepgoing=False
                    #else:
                        #algs.printToDeep("Bridge #",i2," attempt deleted from nodes ",startAddress," to ",endAddress, " in layer ",L)
                bDict[L].append(BRIDGE.generateRandomBridge(lSpace=lSpace,aSpaceList=aSpaceList,layer=L,startAddress=startAddress,endAddress=endAddress,wBounds=wBounds,bBounds=bBounds))
                bDictAddressPairs[L].append((startAddress,endAddress))
                bDictAddressPairsFull[L].append((startAddress,endAddress))
                #algs.printToDeep("Bridge #",i2," generated from nodes ",startAddress," to ",endAddress, " in layer ",L)
        return (bDict,bDictAddressPairs,bDictAddressPairsFull)
    
    
    def addSubmodels(bDict,subModels,bDictAddressPairs,aSpaceList):
        bDictAddressPairsFull=copy.deepcopy(bDictAddressPairs)
        for each in subModels:
            bDict[each[0]].append(each)
            algs.printToDeep(f"\nbDict added {each} at {each[0]}, now {bDict}\n")
            modelAddressesInPre=[]
            modelAddressesOutPre=[]
            modelAddressesInPost=[]
            modelAddressesOutPost=[]
            for each2 in each[1].inGList:
                #each2 is an individual inG
                for each3 in each2:
                    #each3 is an individual pair of source-target
                    modelAddressesInPre.append(each3[0])
            kernelSizeIn=1+max(modelAddressesInPre)-min(modelAddressesInPre)
            for i in range(each[1].maxKernelCount):
                for each2 in modelAddressesInPre:
                    modelAddressesInPost.append(each2+(i*kernelSizeIn))
            
            for each2 in each[1].outGList:
                #each2 is an individual outG
                for each3 in each2:
                    #each3 is an individual pair of source-target
                    modelAddressesOutPre.append(each3[1])
            kernelSizeOut=1+max(modelAddressesOutPre)-min(modelAddressesOutPre)
            for i in range(each[1].maxKernelCount):
                for each2 in modelAddressesOutPre:
                    modelAddressesOutPost.append(each2+(i*kernelSizeOut))


            for each2 in modelAddressesInPost:
                for each3 in modelAddressesOutPost:
                    bDictAddressPairsFull[each[0]].append([each2,each3])
                    if (each2>=aSpaceList[each[0]-1][0] and each2<=aSpaceList[each[0]-1][1]) and (each2>=aSpaceList[each[0]][0] and each2<=aSpaceList[each[0]][1]):
                        bDictAddressPairs[each[0]].append([each2,each3])
        return (bDict,bDictAddressPairs,bDictAddressPairsFull)

    
    def generateAddressPairs(self,lSpace=None,aSpaceList=None,bDict=None):
        bDict=bDict or self.bDict
        lSpace=lSpace or self.lSpace
        aSpaceList=aSpaceList or self.aSpaceList
        
        bDictAddressPairs={}
        for L in range(lSpace[0],lSpace[1]+1):
            bDictAddressPairs[L]=list()
            for each in bDict[L]:
                bDictAddressPairs[L].append((each.startAddress, each.endAddress))
        return bDictAddressPairs


    
    def vCheck(self, bDictUnsorted=None, aSpace=None, lSpace=None):
        bDictUnsorted=bDictUnsorted or self.bDictUnsorted
        lSpace=lSpace or self.lSpace
        aSpace=aSpace or self.aSpace
        shelf={}
        for L in range(lSpace[0],lSpace[1]+1):
            shelf[L]=list()
        for L in range(lSpace[0],lSpace[1]+1):
            for each in bDictUnsorted[L]:
                #allows for premature terminations of check if any condition is found to be false to save on performance
                if each.startAddress>=aSpace[0] and each.startAddress<=aSpace[1] and each.endAddress>=aSpace[0] and each.endAddress<=aSpace[1] and each.layer>=lSpace[0] and each.layer<lSpace[1]:
                    shelf[L].append(each)
        return shelf



    def coallateAddresses(self,bDict=None,lSpace=None,inGList=None,outGList=None,lInList=None, lOutList=None):
        bDict=bDict or self.bDict
        lSpace=lSpace or self.lSpace
        inGList=inGList or self.inGList
        outGList=outGList or self.outGList
        lInList=lInList or self.lInList
        lOutList=lOutList or self.lOutList
        
        shelf={}
        for L in range(lSpace[0],lSpace[1]+1):
            shelf[L]=set()
            #algs.printToDeep(shelf)
        for L in range(lSpace[0]+1,lSpace[1]+1):
            for each in bDict[L]:
                if type(each)==BRIDGE.Bridge:
                    shelf[L-1].add(each.startAddress)
                    shelf[L].add(each.endAddress)
                else:
                    #Aggregate sources and targets from submodel
                    #All inGs
                    for inG in each[1].inGList:
                        #Individual inG
                        for inGEl in inG:
                            #individiaul source-target pair
                            shelf[L-1].add(inGEl[0])
                    #All outGs
                    for outG in each[1].outGList:
                        #Individual outG
                        for outGEl in outG:
                            #individiaul source-target pair
                            shelf[L].add(outGEl[1])

                    
        for i in range(len(outGList)):
            outG=outGList[i]
            for each in outG:
                shelf[lOutList[i]].add(each[0])
        for i in range(len(inGList)):
            inG=inGList[i]
            for each in inG:
                shelf[lInList[i]].add(each[1])
        return shelf
    
    def makeNDict(self,aDict=None,lSpace=None):
        aDict=aDict or self.aDict
        lSpace=lSpace or self.lSpace
        
        nodeshopper={}
        for L in range(lSpace[0],lSpace[1]+1):
            nodeshopper[L]={}
        for L in range(lSpace[0],lSpace[1]+1):
            for each in aDict[L]:
                nodeshopper[L][each]=0
        return nodeshopper
    


    def connectionsRunner(self,inState,lSpace,bDict,lOutList):        
        #Creating instance of nDict (to prevent overwriting from multiple runs)
        opNDict=copy.deepcopy(self.nDict)
        #Running Bridge Computations
        for i in range(len(self.inG)):
            if len(inState)>i:    #for example, if i=3, and length of 3, it means index 3 doesnt exist in inState, since it would only go up to 2. 
                opNDict[self.lIn][self.inG[i]]=inState[i]  #Adds the inputs from inState to nDict at lIn
        for L in range(lSpace[0]+1,lSpace[1]+1):
            
            #Activation function
            if L!=lSpace[0]+1:
                for i2 in opNDict[L]:
                    opNDict[L][i2]=algs.leakyReLU(opNDict[L][i2])   #Tinker with activ func
                    

            for each in bDict[L]:
                shelf=None
                if type(each)==BRIDGE.Bridge:
                    #algs.printToDeep("Bridge should run here")
                    '''
                    shelf=each.executeBridge(opNDict[L-1][each.startAddress]) #Activates each bridge, layer by layer.
                    opNDict[L][shelf[1]]+=shelf[0] #Adds resultant value to nDict location
                    #Variant using experimental optimized individual value calculation
                    '''
                    each.executeBridgeDependent(opNDict)
                '''
                else:
                    #algs.printToDeep("Submodel should run here")
                    inStateSub=()
                    for each2 in each.inG:
                        inStateSub.append(opNDict[L-1][each2])
                    shelf=each.runModel(inState=inStateSub)[0]
                '''

                
            #algs.printToDeep("Previous layer ",opNDict[L-1])
            #algs.printToDeep("Resultant layer ",opNDict[L])
        outShelf=list()
        for each in self.outG:
            outShelf.append(opNDict[lOut][each])# #Pulls all outG elements into outShelf list
            #algs.printToDeep(outShelf)
        #algs.printToDeep(outShelf)
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
        #algs.printToDeep("Adjusting at LB: ", self.adjPointerLB)

        shelf=self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjustElement(adjAmount=adjAmountProvided,idealE=idealE)
        oV=shelf[0]
        adjE=shelf[1]
        '''
        algs.printToDeep("Adjusted element at ",self.adjPointerLB)
        if type(self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]])==BRIDGE.Bridge:
            algs.printToDeep("Bridge in scope below adjusted, adjusted element ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerE)
        else:
            algs.printToDeep("Model adjusted in scope below, Pointer ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerLB)
        '''
        return (oV,adjE)
    


    def setElement(self,adjAmount=0,idealE=None,adjLSpace=None):

        #Define target node
        #algs.printToDeep(type(self.adjPointerLB))
        self.setTarget(adjLSpace=adjLSpace)
        #algs.printToDeep("Adjusting at LB: ", self.adjPointerLB)

        shelf=self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].setElement(adjAmount=adjAmount,idealE=idealE)
        oV=shelf[0]
        adjE=shelf[1]
        '''
        algs.printToDeep("Adjusted element at ",self.adjPointerLB)
        if type(self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]])==BRIDGE.Bridge:
            algs.printToDeep("Bridge in scope below adjusted, adjusted element ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerE)
        else:
            algs.printToDeep("Model adjusted in scope below, Pointer ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerLB)
        '''
        return (oV,adjE)
    
    def pollElement(self,idealE=None,adjLSpace=None):
        #Define target node
        self.setTarget(adjLSpace=adjLSpace)

        shelf=self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].pollElement(idealE=idealE)
        oV=shelf[0]
        adjE=shelf[1]
        '''
        algs.printToDeep("Adjusted element at ",self.adjPointerLB)
        if type(self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]])==BRIDGE.Bridge:
            algs.printToDeep("Bridge in scope below adjusted, adjusted element ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerE)
        else:
            algs.printToDeep("Model adjusted in scope below, Pointer ",self.bDict[self.adjPointerLB[0]][self.adjPointerLB[1]].adjPointerLB)
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
    algs.printToDeep(f"Elapsed time for Short Bridge Execution: {elapsed_time} seconds")
    algs.printToDeep(f"Elapsed time for full nDict transfer: {elapsed_time2} seconds")
    algs.printToDeep("Difference: ",elapsed_time-elapsed_time2)
    nettime+=(elapsed_time-elapsed_time2)

#i fucking guess we go with full nDict transfer then. unless we 

algs.printToDeep("Total time difference (Positive indicates short failure, negative indicates full failure): ",nettime)
algs.printToDeep("Average time difference between iterations: ",nettime/testcount)###
'''