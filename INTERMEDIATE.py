import MODEL
import ENV
import algs
import random
import pickle
import copy

class Intermediate:
    def __init__(self, mdlDict, envDict,algDict=algs.algsDict):
        self.mdlDict=mdlDict
        self.envDict=envDict
        self.algDict=algDict



    def makeAdjAmountsList(batchCount,adjAmount,adjRange,flip=True):
        adjAmountList=list()
        if batchCount==1:
            algs.printToDeep(f"Batch Count 1: Performing single step test\n")
            adjAmountList.append(adjAmount)
            if flip:
                if bool(random.randint(0, 1)):
                    algs.printToDeep(f"Flipped\n")
                    adjAmountList[0]=-adjAmountList[0]
        else:
            algs.printToDeep(f"Batch Count: {batchCount}\n")
            batchStep=(adjRange[1]-adjRange[0])/batchCount
            algs.printToDeep(f"Batch Step: {batchStep}\n")
            for i in range(batchCount+1):
                adjAmountList.append(adjRange[0]+(i*batchStep))
        return adjAmountList


    def backprop(self,inState,opModelIndex,scorerIndex=(False,"Pass"),smuggle=None,adjAmountW=algs.adjAmountW,adjRangeW=algs.adjRangeW,adjAmountB=algs.adjAmountB,adjRangeB=algs.adjRangeB,adjRangeDef=None,boundsDef=None,adjAmountDef=None,stepsize=0.01,flip=True,iterationID=None,wBounds=algs.defaultBounds,bBounds=algs.defaultBounds,doEndpointScaling=False,batchCount=1,ascent=False,scoreNormalize=False):
        #scorerIndex is a dual index where element 0 is a boolean dictating True if the scorer is a model and False if it is handcoded.
        #second element of scorerIndex is just the key in mdlDict or algDict it's found at.
        for i in range(10):
            algs.printToDeep(f"Starting Backprop Step: Iteration ID {iterationID}\n")
        algs.printToDeep(f"\n")
        algs.printToDeep(f"Initial Poll: {self.mdlDict[opModelIndex].pollElement()}\n")

        zeroOutState=self.mdlDict[opModelIndex].runModel(inState)[1]
        algs.printToDeep(f"zeroOutState: {zeroOutState}\n")
        zeroScore=0
        if scorerIndex[0]:
            zeroScore=self.mdlDict[scorerIndex[1]].runModel(inState+zeroOutState+smuggle)
            algs.printToDeep(f"Model {scorerIndex[1]} as Scorer Used\n")
        else:
            zeroScore=self.algDict[scorerIndex[1]](inState,zeroOutState,smuggle)
            algs.printToDeep(f"Alg Scorer {scorerIndex[1]} used\n")

        algs.printToDeep(f"zeroScore: {zeroScore}\n")

        #ADD SCORING ENV SUPPORT LATER 

            #print("Running Alg ",scorerIndex[1])
        #Adjusts and runs model

        pollShelf=self.mdlDict[opModelIndex].pollElement()
        algs.printToDeep(f"pollShelf: {pollShelf}\n")
        oV=copy.deepcopy(pollShelf[0])

        #Issue from here
        
        adjE=copy.deepcopy(pollShelf[1])
        algs.printToDeep(f"Post adjE declare Poll: {self.mdlDict[opModelIndex].pollElement()}\n")

        algs.printToDeep(f"oV: {oV}\n")
        algs.printToDeep(f"adjE: {adjE}\n")
        modScore=0
        modScoresList=list()
        modGradList=list()

        #Assigns weight or bias specific values
        if adjE==1:
            algs.printToDeep(f"Operating on Weight\n")
            adjRange=adjRangeDef or adjRangeW
            adjAmount=adjAmountDef or adjAmountW
            bounds=boundsDef or bBounds
            #print(f"Bounds: {bounds}\n")
        elif adjE==2:
            algs.printToDeep(f"Operating on Bias\n")
            adjRange=adjRangeDef or adjRangeB
            adjAmount=adjAmountDef or adjAmountB
            bounds=boundsDef or bBounds
        algs.printToDeep(f"Post weightorbias declare Poll: {self.mdlDict[opModelIndex].pollElement()}\n")
        
        algs.printToDeep(f"adjAmount: {adjAmount}, adjRange: {adjRange}, bounds: {bounds}\n")
        algs.printToDeep(f"\n")
        #to here
        algs.printToDeep(f"Pre AdjListMake Poll: {self.mdlDict[opModelIndex].pollElement()}\n")
        adjAmountList=Intermediate.makeAdjAmountsList(batchCount,adjAmount,adjRange)
        

        algs.printToDeep(f"List of Adjustments to test: {adjAmountList}\n")
        algs.printToDeep(f"Pre Loop Poll: {self.mdlDict[opModelIndex].pollElement()}\n")
        algs.printToDeep(f"\n")
    
        for each in adjAmountList:
            algs.printToDeep(f"Running Individual Test with adjAmount: {each}\n")
            adjAmount=each
            #Scale to bounds
            if oV+adjAmount>bounds[1]:
                adjAmount=bounds[1]-oV
                algs.printToDeep(f"target value {oV}+{adjAmount}={oV+adjAmount} exceeded upper bound {bounds[1]}\n")
                algs.printToDeep(f"adjusted adjAmount to {adjAmount}\n")
            elif oV+adjAmount<bounds[0]:
                adjAmount=bounds[0]-oV
                algs.printToDeep(f"target value {oV}+{adjAmount}={oV+adjAmount} exceeded lower bound {bounds[0]}\n")
                algs.printToDeep(f"adjusted adjAmount to {adjAmount}\n")
        
            #Perform Adjustment
            algs.printToDeep(f"Pre Adjustment Poll: {self.mdlDict[opModelIndex].pollElement()}\n")
            self.mdlDict[opModelIndex].adjustElement(adjAmount)
            #print(adjAmount," Adjust amount\n")
            algs.printToDeep(f"Adjusted Model by {adjAmount}\n")
            algs.printToDeep(f"Post Adjustment Poll: {self.mdlDict[opModelIndex].pollElement()}\n")
            
            outStateMod=self.mdlDict[opModelIndex].runModel(inState)[1]
            algs.printToDeep(f"Model Run, outState {outStateMod}\n")

            self.mdlDict[opModelIndex].setElement(oV)
            algs.printToDeep(f"Model Returned to original parameters\n")
            algs.printToDeep(f"Post Adjustment Poll: {self.mdlDict[opModelIndex].pollElement()}\n")
            #rectifies

            #Finds post-adjustment score
            if scorerIndex[0]:
                modScore=self.mdlDict[scorerIndex[1]].runModel(inState+outStateMod)
                algs.printToDeep(f"Model {scorerIndex[1]} as Scorer Used\n")
            else:
                modScore=self.algDict[scorerIndex[1]](inState,outStateMod,smuggle)
                algs.printToDeep(f"Alg Scorer {scorerIndex[1]} used\n")
            
            algs.printToDeep(f"resulting score: {modScore}\n")
            

            #print("ModScoreAverage"," ",score2)
            #print("zeroScore: ",zeroScore)
            #print("Score2: ",score2)
            dS=0
            #print(oV," oV\n")
            if ascent:
                dS=modScore-zeroScore
                algs.printToDeep(f"dS: {dS}, Ascent Used\n")
            else:
                dS=zeroScore-modScore
                algs.printToDeep(f"dS: {dS}, Descent Used\n")
            dS1=dS
            if scoreNormalize:
                dS=dS/abs(zeroScore)
                algs.printToDeep(f"dS normalized to {dS}\n")
            

            
            dS2=dS        
            '''
            if ((adjE==1 and adjRangeW[0]>0) or (adjE==2 and adjRangeB[0]>0)) and dS<0:
                dS=dS*reverseScale
            #revise this
            '''
            #print(dS," dS\n")
            dE=adjAmount
            algs.printToDeep(f"dE: {dE}\n")
            #print(dE," dE\n")
            grad=0
            if dE!=0 and dS!=0:
                grad=dS/dE
                algs.printToDeep(f"nonZero, nonInfinite gradient {grad} detected\n")
                modGradList.append(grad)
                modScoresList.append(modScore)
                algs.printToDeep(f"Avg Valid Gradient: {sum(modGradList)/len(modGradList)}\n")
                algs.printToDeep(f"Gradient List: {modGradList}\n")
                #finalAdjAmountList.append(adjAmount)
                
                #revise for formatting
            algs.printToDeep(f"\n")
            
            

        algs.printToDeep(f"\n")
        algs.printToDeep(f"\n")
        algs.printToDeep(f"Final Gradient List: {modGradList}\n")
        algs.printToDeep(f"\n")
        algs.printToDeep(f"\n")

        #print("Gradient: ",grad)
        if len(modGradList)>0:
            step=stepsize*sum(modGradList)/len(modGradList)
            algs.printToDeep(f"Step from stepsize {stepsize}: {step}\n")
            step1=step    #for testing
            #print("Step ",step)

            if oV+step>bounds[1]:
                step=bounds[1]-oV
                algs.printToDeep(f"target value {oV}+{step}={oV+step} exceeded upper bound {bounds[1]}\n")
                algs.printToDeep(f"adjusted adjAmount to {step}\n")
                #print("Above Bound\n")
            elif oV+step<bounds[0]:
                step=bounds[0]-oV
                algs.printToDeep(f"target value {oV}+{step}={oV+step} exceeded lower bound {bounds[0]}\n")
                algs.printToDeep(f"adjusted adjAmount to {step}\n")
                #print("Below Bound\n")
            else:
                #print("Between bounds\n")
                algs.printToDeep(f"target value within bounds\n")
                if doEndpointScaling:
                    algs.printToDeep(f"Endpoint scaling active\n")
                    step=step*min(abs(bounds[0]-(oV+step)),abs(bounds[1]-(oV+step)))#first find oV and stepscaled, then calculate the absolute distance from either Bound (Whichever is lower) iff value is between -1 and 1. If it isnt, normalize it to whichever of those values it's closest to.
                    #IMPORTANT: if using endpoint scaling, adjust to consider above-1 values of bound. otherwise, multiplies by a large value, distorting things
                    algs.printToDeep(f"Endpoint Scaling active, step after endpoint scaling: {step}\n")
            #print("Step", step)

            step2=step    #for testing
            
            self.mdlDict[opModelIndex].adjustElement(step)
            

            algs.printToDeep(f"Final Poll: {self.mdlDict[opModelIndex].pollElement()}\n")


            finalState=self.mdlDict[opModelIndex].runModel(inState)[1]
            algs.printToDeep(f"Final OutState: {finalState}\n")
            if scorerIndex[0]:
                finalScore=self.mdlDict[scorerIndex[1]].runModel(inState+finalState)
                #zeroScore=self.mdlDict[scorerIndex[1]].runModel(inState+zeroOutState+smuggle)
                algs.printToDeep(f"Model {scorerIndex[1]} as Scorer Used\n")
            else:
                finalScore=self.algDict[scorerIndex[1]](inState,finalState,smuggle)
                algs.printToDeep(f"Alg Scorer {scorerIndex[1]} used\n")

            algs.printToDeep(f"zeroScore: {zeroScore}\n")
            algs.printToDeep(f"outputScore: {finalScore}\n")

            backpropSuccess=True
            if finalScore<zeroScore:
                algs.printToDeep(f"Final Test Failed: Undoing\n")
                self.mdlDict[opModelIndex].setElement(oV)
                algs.printToDeep(f"Final Poll: {self.mdlDict[opModelIndex].pollElement()}\n")
                backpropSuccess=False
                #print("Final adjustment test failed, undoing step\n")

            newV=self.mdlDict[opModelIndex].pollElement()[0]
            algs.printToDeep(f"New Final Element State: {newV}\n")


            backpropSummary=f"{iterationID}, success:{backpropSuccess} adjE: {adjE}, zeroScore:{zeroScore}, average score:{sum(modScoresList)/len(modScoresList)} oV:{oV} average grad:{sum(modGradList)/len(modGradList)}, step1:{step1} step2:{step2} actualStep:{step} newV:{newV}\n"
            #print(backpropSummary)
            with open("shallowOut.txt", "a") as f:
                f.write(backpropSummary)
        
        #DEBUGGING
            #print(newV, " New V\n")
        #DEBUGGING

        else:
            #print("All attempted changes had no effect on score!\n")
            algs.printToDeep(f"All attempted changes had no effect on score!\n")
            '''
            backpropSummary=f"{iterationID}, backprop test failed across all tested scores: no effect on gradient whatsoever.\n"
            print(backpropSummary)
            with open("shallowOut.txt", "a\n") as f:
                f.write(backpropSummary)
            #currentlist.append((iterationID, zeroScore,zeroScore, Score2,score2, oV,oV, dS,dS, dE,dE, grad,grad, step1,step1, step2,step2, actualStep,actualstep, newV",newV))
            '''
            pass        
        finalState=self.mdlDict[opModelIndex].runModel(inState)[1]
        if scorerIndex[0]:
            finalScore=self.mdlDict[scorerIndex[1]].runModel(inState+finalState)
            zeroScore=self.mdlDict[scorerIndex[1]].runModel(inState+zeroOutState+smuggle)
            algs.printToDeep(f"Model {scorerIndex[1]} as Scorer Used\n")
        else:
            finalScore=self.algDict[scorerIndex[1]](inState,finalState,smuggle)
            algs.printToDeep(f"Alg Scorer {scorerIndex[1]} used\n")

        algs.printToDeep(f"Resultant Final Test Score: {finalScore}\n")

        self.mdlDict[opModelIndex].purgeLAE()
        algs.printToDeep(f"Purged LAE\n")
        return zeroOutState
        

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




    def frogProp():

        '''
        pseudo

        For each in provided list of adjAmounts (0 included):
            adjust element by each
            run model
            un-adjust model
            get score
            add paired Score and adjAmount to list
        sort list by score
        pick highest score element from list
        adjust by adjElement paired with score
        '''

    def playGame(self,Player, InterimScorer, EndScorer, Env):
        gameOver=False
        while gameOver==False:
            EnvReady=False
            while EnvReady==False:
                #Training protocol here
                print("nothin goin on here yet\n")
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

    