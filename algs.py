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

def testScorer(inState,outState):
    w=outState[0]
    x=outState[1]
    y=outState[2]
    z=outState[3]
    return (1000/((w+x)*(2*(y-z))+(1000-x)))

defaultBounds=(-800,800)
defaultInitialBounds=(-8,8)
adjAmountW=0.01
adjAmountB=0.01
stepSize=0.01
adjRangeW=(-1,1)
adjRangeB=(-1,1)
    
algsDict={
    "Pass": Pass,
    "sigmoid": sigmoid,
    "leakyReLU": leakyReLU,
    "testScorer": testScorer
}