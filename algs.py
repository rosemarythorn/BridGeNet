def Pass(inState):
    return inState

def sigmoid(x):
    if x>10:
        return 1
    elif x<-10:
        return -1
    else: 
        return round(((2*(1 / (1 + np.exp(-x))))-1),5)

def leakyReLU(x):
    return max(x,x/10)

def testScorer(inState,outState,smuggle):
    w=outState[0]
    x=outState[1]
    y=outState[2]
    z=outState[3]
    denom=(w+x)*(2*(y-z))+(1000-x)
    if denom!=0:
        return (1000/denom)
    else:
        return 99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999

    
algsDict={
    "Pass": Pass,
    "sigmoid": sigmoid,
    "leakyReLU": leakyReLU,
    "testScorer": testScorer
}

def printToDeep(inStr):
     with open("deepOut.txt", "a") as f:
                f.write(inStr)
                
def printToShallow(inStr):
      with open("shallowOut.txt", "a") as f:
                f.write(inStr)