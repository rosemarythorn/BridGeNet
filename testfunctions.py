import random
import MODEL
import BRIDGE
import INTERMEDIATE
import numpy as np
import algs
import pickle
#0 may be invalid address


def generateexampleNDict():
        examplenDict={}
        for i1 in range(0,10):
            examplenDict[i1]={}
            for i2 in range(0,3):
                examplenDict[i1][i2]=random.random()
        return examplenDict
def printNDict(nDictinput):
     for key,value in nDictinput.items():
          print(f"{key}: {value}")

def generateTestMdlDict():
      mdlDict={
        1:MODEL.Model(lSpace,aSpace,(1,2,3,4),(1,2,3,4,5,6),bCount=bCount,wBounds=algs.defaultInitialBounds,bBounds=algs.defaultInitialBounds)
      }
      return mdlDict

lSpace=(0,2)
aSpace=(1,6)
bCount=100
testcount=10000
nettime=0
#testmodel=MODEL.Model(lSpace,aSpace,(0,1,2,3),(0,1,2,3,4,5),bCount=bCount)
#testinter=INTERMEDIATE.Intermediate(generateTestMdlDict(),{},algs.algsDict)

with open("deepOut.txt", "w") as f:
        f.write("")
with open("shallowOut.txt", "w") as f:
        f.write("")


for i in range(testcount):
        #testmodel.adjustElement(0.001)
        #testmodel.adjustElement(-0.001)
        #print(testmodel.adjustElement(-0.001))
        #print(testmodel.adjustElement(-0.001))
        #print(testmodel.adjustElement(-0.001))
        #print(testmodel.adjustElement(-0.001))
        #testmodel.purgeLAE()
        #tickdown=abs(np.sin(i/20)/5)
        #tickdown=2**((-((i+1)/5000)))
        #print(testmodel.pollElement())
        #print(tickdown)
        #offset=random.random()*tickdown
        #print(i)
        #print(testmodel.runModel((0,5,5,5,5,5,5,5)))
        #testoutput=testinter.backprop((0,1,10),1,(False,"testScorer"),adjAmountDef=0.1,adjRangeDef=(-2*tickdown,2*tickdown),batchCount=6,stepsize=tickdown,flip=True,iterationID=i,wBounds=algs.defaultBounds,bBounds=algs.defaultBounds,doEndpointScaling=False,ascent=True,scoreNormalize=True)
        #testoutput=testinter.sortOptim((0,1,10),1,(False,"testScorer"),adjAmountDef=0.1,adjRangeDef=((-2*tickdown)+offset,(2*tickdown)+offset),batchCount=3,flip=True,iterationID=i,wBounds=algs.defaultBounds,bBounds=algs.defaultBounds,doEndpointScaling=False,ascent=True,scoreNormalize=True)
        #print(testoutput)
        pass

testmodel1=MODEL.Model((0,1,2,3),(0,1,2,3,4,5),bCount=bCount)
algs.printToDeep(f"{vars(testmodel1)}\n")
testmodel2=MODEL.Model(5,((0,2),(1,3)),5,7,bCount=bCount)
algs.printToDeep(f"{vars(testmodel2)}\n")
algs.printToDeep(f"{testmodel2}\n")
testmodel3=MODEL.Model((((7,2),(4,5),(3,1)),((7,2),(4,5),(3,1))),(0,1,2,3,4,5),lSpace=[0,9],aSpace="Alpha",bCount=bCount)
algs.printToDeep(f"{vars(testmodel3)}\n")
testmodel4=MODEL.Model(None,77,(0,3,5),((6,9),(4,5),(3,2)),bCount=bCount)
algs.printToDeep(f"{vars(testmodel4)}\n")
testmodel5=MODEL.Model((0,1,2,3),(0,1,2,3,4,5),subModels=((1,testmodel3),(3,testmodel2)),bCount=bCount,lSpace=3, aSpace=7)
algs.printToDeep(f"{vars(testmodel5)}\n")
algs.printToDeep(f"{testmodel5.bDict}\n")
#print(99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999)
print(testmodel5.runModel((0,3,4,6,1)))