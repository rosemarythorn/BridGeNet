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
    
algsDict={
    "Pass": Pass,
    "sigmoid": sigmoid,
    "leakyReLU": leakyReLU
}