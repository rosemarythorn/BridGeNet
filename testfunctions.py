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
        1:MODEL.Model(lSpace,aSpace,(1,2,3,4),(1,2,3,4,5,6),bCount=bCount)
      }
      return mdlDict

lSpace=(0,2)
aSpace=(1,6)
bCount=100
testcount=10000
nettime=0
testmodel=MODEL.Model(lSpace,aSpace,(0,1,2,3),(0,1,2,3,4,5),bCount=bCount)
testinter=INTERMEDIATE.Intermediate(generateTestMdlDict(),{},algs.algsDict)

for i in range(testcount):
        #testmodel.adjustElement(0.001)
        #testmodel.adjustElement(-0.001)
        #print(testmodel.adjustElement(-0.001))
        #print(testmodel.adjustElement(-0.001))
        #print(testmodel.adjustElement(-0.001))
        #print(testmodel.adjustElement(-0.001))
        #testmodel.purgeLAE()
        testoutput=testinter.backprop((0,1,10),1,(False,"testScorer"),adjAmountW=0.1,adjAmountB=0.1,stepsize=0.1,flip=True,iterationID=i,wBounds=algs.defaultBounds,bBounds=algs.defaultBounds,doEndpointScaling=False)
        #print(testoutput)
