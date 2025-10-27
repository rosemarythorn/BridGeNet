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
testinter=INTERMEDIATE.Intermediate(generateTestMdlDict(),{},algs.algsDict)

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
        tickdown=abs(np.sin(i/20)/5)
        #tickdown=10**((-(i+1)/1000)+1)
        #print(tickdown)
        print(i)
        testoutput=testinter.backprop((0,1,10),1,(False,"testScorer"),adjAmountDef=0.1,adjRangeDef=(-2*tickdown,2*tickdown),batchCount=6,stepsize=tickdown,flip=True,iterationID=i,wBounds=algs.defaultBounds,bBounds=algs.defaultBounds,doEndpointScaling=False,ascent=True,scoreNormalize=True)
        #print(testoutput)
