import random
import MODEL
import BRIDGE
import INTERMEDIATE
import numpy as np


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

lSpace=(0,10)
aSpace=(0,10)
bCount=10
testcount=100
nettime=0
testmodel=MODEL.Model(lSpace,aSpace,(0,1,2,3),(0,1,2,3,4,5),bCount=bCount)

for i in range(testcount):
        testmodel.adjustElement(0.001)
        testmodel.adjustElement(-0.001)
        testmodel.purgeLAE()
        print(testmodel.runModel((26,7,19,4,63,7)))