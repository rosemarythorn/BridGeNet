import MODEL
import ENV
import algs
import random

class Intermediate:
    def __init__(self, mdlDict, envDict,algDict=algs.algsDict):
        self.mdlDict=mdlDict
        self.envDict=envDict
        self.algDict=algDict


    def backprop(self,inState,opModelIndex,scorerIndex=(False,"Pass"),adjAmountP=0.01,stepsize=0.01,flip=True):
        #scorerIndex is a dual index where element 0 is a boolean dictating True if the scorer is a model and False if it is handcoded.
        #second element of scorerIndex is just the key in mdlDict or algDict it's found at.
        adjAmount=adjAmountP or 0.01
        #print(adjAmount," Adjust amount")
        outState1=self.mdlDict[opModelIndex].runModel(inState)[1]
        score1=0
        if scorerIndex[0]:
            score1=self.mdlDict[scorerIndex[1]].runModel(inState+outState1)
        else:
            score1=self.algDict[scorerIndex[1]](inState,outState1)
            #print("Running Alg ",scorerIndex[1])
        #Adjusts and runs model
        if flip:
            if bool(random.randint(0, 1)):
                adjAmount=0-adjAmount
        #print(adjAmount," Adjust amount")
        

        oV=self.mdlDict[opModelIndex].adjustElement(0)
        if oV+adjAmount>1:
            adjAmount=1-oV
        elif oV+adjAmount<-1:
            adjAmount=-1-oV
        oV=self.mdlDict[opModelIndex].adjustElement(adjAmount)
        #print(adjAmount," Adjust amount")
        
        
        outState2=self.mdlDict[opModelIndex].runModel(inState)[1]
        #Finds post-adjustment score
        score2=0
        if scorerIndex[0]:
            score2=self.mdlDict[scorerIndex[1]].runModel(inState+outState2)
        else:
            score2=self.algDict[scorerIndex[1]](inState,outState2)
        #print(score1," ",score2)
        print("Score1: ",score1)
        #print(score2)

        dS=score2-score1        #loss
        print("SQR Difference in Score: ",dS)
        dE=adjAmount
        if dE!=0:
            grad=dS/dE
            print("Gradient: ",grad)
            step=stepsize*grad
            
            if oV+step>8:
                step=8-oV
            elif oV+step<0.125:
                step=0.125-oV
            else:
                step=step*min(abs(-1-(oV+step)),abs(1-(oV+step)))#first find oV and stepscaled, then calculate the absolute distance from either endpoint (Whichever is lower) iff value is between -1 and 1. If it isnt, normalize it to whichever of those values it's closest to.
            
            actualstep=step-adjAmount
            self.mdlDict[opModelIndex].adjustElement(actualstep)
        else:
            print("Couldn't change value any more without exceeding bounds!")
        self.mdlDict[opModelIndex].purgeLAE()
        print()

        return outState1
        

        


        '''pseudo: 
        Call opModel.runModel(inState)  result is outState
        Call scorer with inState and outState from runModel, resultant is baseLoss.
        call opModel.adjustElement (adjAmount, no given element)
        Call opModel runModel on same inState from earlier, results in new outState
        call IntermediateScorer with outState, resultant is adjLoss
        calculate dL=adjLoss-baseLoss
        dC=adjAmount
        Calculate slope of dL/dC
        Multiply by stepSize
        divide by average of dL/dC?
        once we’ve performed the above steps, we have value causedChange
        Subtract adjAmount from causedChange (since we didn’t change back)
        call opModel.adjustElement with result of subtraction as new adjAmount
        add causedChange to mdlDict[memoryEnvSqrd for player] at key outState
        run opModel.purgeLAE() to clear pointers
        return original outState from first runModel
        '''

    def playGame(self,Player, InterimScorer, EndScorer, Env):
        gameOver=False
        while gameOver==False:
            EnvReady=False
            while EnvReady==False:
                #Training protocol here
                print("nothin goin on here yet")
                EnvReady=Env.ready
            playerOutcome=Player.runModel(Env.state)

            if Env.vType==0:
                self.makeAttemptsList()
        
    def playTurn(self,Player,Env):
        playerOutcome=Player.runModel(Env.state)
        if Env.vType==0:
            attempts=self.makeAttemptsListCombine(playerOutcome,Env)
            i=-1
            valid==False
            while valid==False:
                i+=1
                valid=Env.checkValidity(attempts[i])
            



    def makeAttemptsListCombine(self,playerOutcome,Env):
        numberOfAttempts=len(playerOutcome[1])/Env.cSize
        index=0
        attempts=list()
        for i in range(numberOfAttempts):
            attempts[i]=list()
            for i2 in range(Env.cSize):
                attempts[i][i2].append(playerOutcome[1][index])
                index+=1
        return attempts

    