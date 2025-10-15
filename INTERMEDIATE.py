import MODEL
import ENV
import algs
import random
import pickle

class Intermediate:
    def __init__(self, mdlDict, envDict,algDict=algs.algsDict):
        self.mdlDict=mdlDict
        self.envDict=envDict
        self.algDict=algDict


    def backprop(self,inState,opModelIndex,scorerIndex=(False,"Pass"),adjAmountW=algs.adjAmountW,adjRangeW=algs.adjRangeW,adjAmountB=algs.adjAmountB,adjRangeB=algs.adjRangeB,stepsize=0.01,flip=True,iterationID=None,wBounds=algs.defaultBounds,bBounds=algs.defaultBounds,doEndpointScaling=False,reverseScale=0.0,batchCount=1):
        #scorerIndex is a dual index where element 0 is a boolean dictating True if the scorer is a model and False if it is handcoded.
        #second element of scorerIndex is just the key in mdlDict or algDict it's found at.

        outState1=self.mdlDict[opModelIndex].runModel(inState)[1]
        zeroScore=0
        if scorerIndex[0]:
            zeroScore=self.mdlDict[scorerIndex[1]].runModel(inState+outState1)
        else:
            zeroScore=self.algDict[scorerIndex[1]](inState,outState1)

        #ADD SCORING ENV SUPPORT LATER 

            #print("Running Alg ",scorerIndex[1])
        #Adjusts and runs model

        pollShelf=self.mdlDict[opModelIndex].pollElement()
        oV=pollShelf[0]
        adjE=pollShelf[1]

        modScore=0
        modScoresList=list()
        modGradList=list()
        
        adjAmountList=list()

        #Assigns weight or bias specific values
        if adjE==1:
            #print("Operating on Weight")
            adjRange=adjRangeW
            adjAmount=adjAmountW
            bounds=bBounds
            #print(f"Bounds: {bounds}")
        elif adjE==2:
            #print("Operating on Bias")
            adjRange=adjRangeB
            adjAmount=adjAmountB
            bounds=bBounds
            #print(f"Bounds: {bounds}")
        

        if batchCount==1:
            #print(f"Batch Count: 1")
            adjAmountList.append(adjAmount)
            if flip:
                if bool(random.randint(0, 1)):
                    #print("Flipped")
                    adjAmountList[0]=-adjAmountList[0]
        else:
            #print(f"Batch Count: {batchCount}")
            batchStep=(adjRange[1]-adjRange[0])/batchCount
            #print(f"Batchstep: {batchStep}")
            for i in range(batchCount):
                adjAmountList.append(adjRange[0]+(i*batchStep))

        #print(f"adjAmountList: {adjAmountList}")


        for each in adjAmountList:
            adjAmount=each
            #Scale to bounds
            if oV+adjAmount>bounds[1]:
                adjAmount=bounds[1]-oV
            elif oV+adjAmount<bounds[0]:
                adjAmount=bounds[0]-oV
        
            #Perform Adjustment
            self.mdlDict[opModelIndex].adjustElement(adjAmount)
            #print(adjAmount," Adjust amount")
            
            
            outStateMod=self.mdlDict[opModelIndex].runModel(inState)[1]

            self.mdlDict[opModelIndex].adjustElement(-adjAmount)
            #rectifies

            #Finds post-adjustment score
            if scorerIndex[0]:
                modScore=self.mdlDict[scorerIndex[1]].runModel(inState+outStateMod)
            else:
                modScore=self.algDict[scorerIndex[1]](inState,outStateMod)
            
            modScoresList.append(modScore)

            #print("ModScoreAverage"," ",score2)
            #print("zeroScore: ",zeroScore)
            #print("Score2: ",score2)

            #print(oV," oV")

            dS=(modScore-zeroScore)
            dSU=dS/abs(zeroScore)        #loss
            '''
            if ((adjE==1 and adjRangeW[0]>0) or (adjE==2 and adjRangeB[0]>0)) and dSU<0:
                dSU=dSU*reverseScale
            '''
            #print(dS," dS")
            dE=adjAmount
            #print(dE," dE")
            grad=0
            if dE!=0 and dSU!=0:
                grad=dSU/dE
                modGradList.append(grad)
                #finalAdjAmountList.append(adjAmount)
            
            



        #print("Gradient: ",grad)
        if len(modGradList)>0:
            step=stepsize*sum(modGradList)/len(modGradList)
            step1=step    #for testing
            #print("Step ",step)
            if oV+step>bounds[1]:
                step=bounds[1]-oV
                #print("Above Bound")
            elif oV+step<bounds[0]:
                step=bounds[0]-oV
                #print("Below Bound")
            else:
                #print("Between bounds")
                if doEndpointScaling:
                    step=step*min(abs(bounds[0]-(oV+step)),abs(bounds[1]-(oV+step)))#first find oV and stepscaled, then calculate the absolute distance from either Bound (Whichever is lower) iff value is between -1 and 1. If it isnt, normalize it to whichever of those values it's closest to.
            #print("Step", step)
            step2=step    #for testing
            actualstep=step
            #print("Actual Step ",actualstep)
            self.mdlDict[opModelIndex].adjustElement(actualstep)


            finalState=self.mdlDict[opModelIndex].runModel(inState)[1]
            if scorerIndex[0]:
                finalScore=self.mdlDict[scorerIndex[1]].runModel(inState+finalState)
            else:
                finalScore=self.algDict[scorerIndex[1]](inState,finalState)

            backpropSuccess=True
            if finalScore<zeroScore:
                self.mdlDict[opModelIndex].adjustElement(-actualstep)
                backpropSuccess=False
                #print("Final adjustment test failed, undoing step")

            newV=self.mdlDict[opModelIndex].pollElement()[0]
            backpropSummary=f"{iterationID}, success:{backpropSuccess} adjE: {adjE}, zeroScore:{zeroScore}, average score:{sum(modScoresList)/len(modScoresList)} oV:{oV} average grad:{sum(modGradList)/len(modGradList)}, step1:{step1} step2:{step2} actualStep:{actualstep} newV:{newV}\n"
            #print(backpropSummary)
            with open("testdata.txt", "a") as f:
                f.write(backpropSummary)
        
        #DEBUGGING
            #print(newV, " New V")
        #DEBUGGING

        else:
            #print("Couldn't change value any more without exceeding bounds!")
            '''
            backpropSummary=f"{iterationID}, backprop test failed across all tested scores.\n"
            print(backpropSummary)
            with open("testdata.txt", "a") as f:
                f.write(backpropSummary)
            #currentlist.append((iterationID, zeroScore,zeroScore, Score2,score2, oV,oV, dS,dS, dE,dE, grad,grad, step1,step1, step2,step2, actualStep,actualstep, newV",newV))
            '''
            pass        

        self.mdlDict[opModelIndex].purgeLAE()
        return outState1
        

        '''
        with open('data.pkl', 'wb') as file:
            pickle.dump(data, file)

        # Unpickling from a file
        with open('data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)'''


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

    