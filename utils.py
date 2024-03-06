import abc
import numpy as np
# this class characterizes an automaton
class FSA:
    def __init__ (self, numStates = 0, startStates=None, finalStates=None, alphabetTransitions=None) :
        self.numStates = numStates
        self.startStates = startStates
        self.finalStates = finalStates
        self.alphabetTransitions = alphabetTransitions

class NFA(FSA):
    def simulate(self, ipStr):
        S = set(self.startStates)
        newS = set()
        for i in range(len(ipStr)):
            symbol = ipStr[i]
            tm = self.alphabetTransitions[symbol]
            for state in S:
                trs = tm[state]
                for tr in range(len(trs)):
                    if trs[tr] == 1:
                        newS.add(tr)
            S = set(newS)
            newS = set()
        if len(self.finalStates) > 0 and not S.isdisjoint(self.finalStates):
            print("String Accepted")
            return True
        else:
            print("String Rejected")
            return False

    def getNFA(self):
        return self

class ETree:
    root = None
    nfa = None
    class ETNode:
        def __init__(self, val=" ", left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def compute(self, operands, operators):
            operator = operators.pop()
            if operator == "*":
                left = operands.pop()
                operands.append(self.ETNode(val=operator, left=left))
            elif operator == "+":
                right, left = operands.pop(), operands.pop()
                operands.append(self.ETNode(val=operator, left=left, right=right))
            elif operator == ".":
                right, left = operands.pop(), operands.pop()
                operands.append(self.ETNode(val=operator, left=left, right=right))

    def parseRegex(self, regex):
        operands, operators = [], []
        for i in range(len(regex)):
            if regex[i].isalpha():
                operands.append(self.ETNode(val=regex[i]))
            elif regex[i] == '(':
                operators.append(regex[i])
            elif regex[i] == ')':
                while operators[-1] != '(':
                    self.compute(operands, operators)
                operators.pop()
            else :
                operators.append(regex[i])
        while operators:
            self.compute(operands, operators)

        if len(operators) == 0:
            self.root = operands[-1]
        else :
            print("Parsing Regex failed.")

    def getTree(self):
        return self.root

    ###################################################################
    # IMPLEMENTATION STARTS AFTER THE COMMENT
    # Implement the following functions

    # In the below functions to be implemented delete the pass statement
    # and implement the functions. You may define more functions according
    # to your need.
    ###################################################################
    def resolveTransitionStates(self,treeL,treeR):
        treeLDict=treeL.alphabetTransitions
        treeRDict=treeR.alphabetTransitions
        newDict={'a':[],'b':[],'c':[],'e':[]}
        for sym in newDict:
            for rowi in range(len(treeLDict[sym])+len(treeRDict[sym])):
                if(rowi<len(treeLDict[sym])):
                    newRow=treeLDict[sym][rowi]+[0 for _ in range(len(treeRDict[sym]))]
                    newDict[sym].append(newRow)
                else:
                    newRow=[0 for _ in range(len(treeLDict[sym]))]+(treeRDict[sym][rowi-len(treeLDict[sym ])])
                    newDict[sym].append(newRow)
        
        newStartStates=set()
        newFinalStates=set()
        newNumStates=treeL.numStates+treeR.numStates
        newStartStates=newStartStates.union(treeL.startStates)
        newFinalStates=newFinalStates.union(treeL.finalStates)

        for state in treeR.startStates:
            newStartStates.add(state+treeL.numStates)
        
        for state in treeR.finalStates:
            newFinalStates.add(state+treeL.numStates)
              
        retFSA=FSA(newNumStates,newStartStates,newFinalStates,newDict)
        return retFSA

    # .
    def operatorDot(self, treeL,treeR):
        # print("Transitions:",self.nfa.alphabetTransitions,"\n")
        # print("Final: ", self.nfa.finalStates,"\n")
        # print("Start: ", self.nfa.startStates,"\n")

        treeLStart,treeLFinal=treeL.startStates,treeL.finalStates
        treeRStart,treeRFinal=treeR.startStates,treeR.finalStates
        
        tempFSA=self.resolveTransitionStates(treeL,treeR)
        # print("treeLStart:",treeLStart)
        # print("treeLFinal:",treeLFinal)
        # print("treeRStart:",treeRStart)
        # print("treeRFinal:",treeRFinal)
        
        markedStates=[]

        for LFinState in treeLFinal:
            for sym in tempFSA.alphabetTransitions:
                for rowi,row in enumerate(tempFSA.alphabetTransitions[sym]):
                    if(row[LFinState]==1):
                        markedStates.append((sym,rowi))
        
        
        for preFinalStates in markedStates:
            for rightStartStates in treeRStart:
                tempFSA.alphabetTransitions[preFinalStates[0]][preFinalStates[1]][rightStartStates+treeL.numStates]=1
        tempFSA.startStates=treeLStart
        
        newFinalStates=set()
        for states in treeRFinal:
            newFinalStates.add(states+treeL.numStates)
        
        tempFSA.finalStates=set()
        tempFSA.startStates=set()
        
        #If the left fsa accepts e, then the final state of left-fsa must also be a accpting state of the final fsa
        for states in treeLFinal:
            if states in treeLStart:
                newFinalStates.add(states)
                for syms in tempFSA.alphabetTransitions:
                    for coli in range(len(tempFSA.alphabetTransitions[syms][states])):

                        if(tempFSA.alphabetTransitions[syms][states][coli]==1) and ((coli-treeL.numStates) in treeRStart):
                            tempFSA.startStates.add(coli)

        
        #If the left fsa accepts e, then we must add the start states of right-fsa to the start states.
        


        tempFSA.finalStates=tempFSA.finalStates.union(newFinalStates)
        tempFSA.startStates=tempFSA.startStates.union(treeLStart)

        return tempFSA

    # +
    def operatorPlus(self,treeR,treeL):
        tempFSA=self.resolveTransitionStates(treeL,treeR)
        return tempFSA




    # *
    def operatorStar(self,treeLeft):
        # for sym in treeLeft.alphabetTransitions:
        #     for row in treeLeft.alphabetTransitions[sym]:
        #         row.append(0)
        #     treeLeft.alphabetTransitions[sym].append([0 for i in range(treeLeft.numStates+1)])
        preFinal=[]
        # postStart=[]

        # for state in treeLeft.startStates:
        #     for sym in treeLeft.alphabetTransitions:
        #         for coli in range(len(treeLeft.alphabetTransitions[sym])):
        #             if(treeLeft.alphabetTransitions[sym][state][coli]==1):
        #                 postStart.append((sym,coli))
        
        for state in treeLeft.finalStates:
            for sym in treeLeft.alphabetTransitions:
                for rowi,row in enumerate(treeLeft.alphabetTransitions[sym]):
                    if(row[state]==1):
                        preFinal.append((sym,rowi))

        
        # newStart=treeLeft.numStates
        # for target in postStart:
        #     treeLeft.alphabetTransitions[target[0]][newStart][target[1]]=1

        for stStates in treeLeft.startStates:
            for target in preFinal:
                treeLeft.alphabetTransitions[target[0]][target[1]][stStates]=1

        treeLeft.finalStates=treeLeft.startStates.copy()       
        
        # treeLeft.startStates=set()
        # treeLeft.finalStates=set()
        # treeLeft.startStates.add(treeLeft.numStates)
        # treeLeft.finalStates.add(treeLeft.numStates)
        # treeLeft.numStates+=1     
        return treeLeft

            
    # a, b, c and e for epsilon
    def alphabet(self, symbol):
        if(symbol!='e'):
            newStartState=set()
            newFinalState=set()
            newNumStates=0
            newStartState.add(newNumStates)
            newFinalState.add(newNumStates+1)
            newTransitions={'a':[[0,0],[0,0]],'b':[[0,0],[0,0]],'c':[[0,0],[0,0]],'e':[[0,0],[0,0]]}
            newTransitions[symbol][newNumStates][newNumStates+1]=1
            newNumStates+=2
            newFSA=FSA(newNumStates,newStartState,newFinalState,newTransitions)
            return newFSA
        else:
            newStartState=set()
            newFinalState=set()
            newNumStates=0
            newStartState.add(newNumStates)
            newFinalState.add(newNumStates)
            newTransitions={'a':[[0]],'b':[[0]],'c':[[0]],'e':[[0]]}
            newNumStates+=1
            newFSA=FSA(newNumStates,newStartState,newFinalState,newTransitions)
            return newFSA

        
    # Traverse the regular expression tree(ETree)
    # calling functions on each node and hence
    # building the automaton for the regular
    # expression at the root.
################################################
##CODE AND COMMENTS FROM HERE ON ARE THE AUTHORS
################################################
    #Anytime we work on a binary tree, the first thing that comes to mind is recursion. So thats what we will do.
         

    def buildNFA(self, root):

        # write code to populate the above datastructures for a regex tree
        
        if root.val.isalpha():
          retval=self.alphabet(root.val)
          print("val:",root.val)   
        else:
            symb=root.val
            print("symb:",symb)
            treeLeft=None
            treeRight=None
            if symb=='*':
                treeLeft=self.buildNFA(root.left)
                retval=self.operatorStar(treeLeft)
            else:
                treeLeft=self.buildNFA(root.left)
                treeRight=self.buildNFA(root.right)
                if symb=='+':
                    retval=self.operatorPlus(treeLeft,treeRight)
                else:
                    retval=self.operatorDot(treeLeft,treeRight)
        self.nfa=NFA(retval.numStates,retval.startStates,retval.finalStates,retval.alphabetTransitions)
        return self.nfa           
        # print NFA

    ######################################################################