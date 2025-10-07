def Pass(inState):
    return inState

def sigmoid(x):
    if x>10:
        return 1
    elif x<-10:
        return -1
    else: 
        return round(((2*(1 / (1 + np.exp(-x))))-1),5)
    
algsDict={
    "Pass": Pass,
    "sigmoid": sigmoid,

}