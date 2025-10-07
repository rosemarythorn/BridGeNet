import MODEL
import ENV
import algs
import random

class Intermediate:
    def __init__(self, mdlDict, envDict,algDict):
        self.mdlDict=mdlDict
        self.envDict=envDict
        self.algDict=algDict


    def backprop(self,inState,opModelIndex,scorerIndex=(False,"Pass"),adjAmount=0.01,stepsize=0.01,flip=True):
        #scorerIndex is a dual index where element 0 is a boolean dictating True if the scorer is a model and False if it is handcoded.
        #second element of scorerIndex is just the key in mdlDict or algDict it's found at.
        outState1=self.mdlDict[opModelIndex].runModel(inState)
        score1=0
        if scorerIndex[0]:
            score1=self.mdlDict[scorerIndex[1]].runModel(inState+outState1)
        else:
            score1=self.algDict[scorerIndex[1]].runAlg(inState+outState1)
        #Adjusts and runs model
        if flip==True:
            if random.randrange(0,1)==1:
                adjAmount=-adjAmount

        
        if oV+adjAmount>1:
            adjAmount=1-oV
        elif oV+adjAmount<-1:
            adjAmount=-1-oV

        oV=self.mdlDict[opModelIndex].adjustElement(adjAmount)
        
        
        outState2=self.mdlDict[opModelIndex].runModel(inState)
        #Finds post-adjustment score
        score2=0
        if scorerIndex[0]:
            score2=self.mdlDict[scorerIndex[1]].runModel(inState+outState2)
        else:
            score2=self.algDict[scorerIndex[1]].runAlg(inState+outState2)

        dS=score2-score1
        dE=adjAmount
        grad=dS/dE
        step=stepsize*grad
        if oV+step>1:
            step=1-oV
        elif oV+step<1:
            step=-1-oV
        else:
            step=step*min(abs(-1-(oV+step)),abs(1-(oV+step)))#first find oV and stepscaled, then calculate the absolute distance from either endpoint (Whichever is lower) iff value is between -1 and 1. If it isnt, normalize it to whichever of those values it's closest to.
        actualstep=step-adjAmount
        self.mdlDict[opModelIndex].adjustElement(actualstep)
        

        


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

    