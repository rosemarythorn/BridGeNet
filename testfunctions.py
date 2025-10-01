import random
import MODEL
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

lSpace=10
aSpace=10
bCount=100
testcount=5
nettime=0
testmodel=MODEL.Model((0,lSpace),(0,aSpace),(0,1,2,3),(0,1,2,3,4,5,6,7,8,9),bCount=bCount)

for i in range(testcount):
        print(testmodel.runModel((26,7,19,4,63,7)))