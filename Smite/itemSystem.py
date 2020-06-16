#import sympy as sympy
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sbn
#from scipy import *

class itemSystem():
    
    def __init__(self,huh="huh"):
        self.a = np.ones((1,1))
        self.b = np.ones((1,1))
        self.varnames = ["init"]
        self.itemnames = ["init"]

    def add_item(self, item):
        try:
            t = item["Active Effect"]
            print("please no actives")
        except:
            #try:
            cost = item["Gold"]
            name = item["Name"]
            self.itemnames.append(name)
            nzVars = []
            nzMods = []
            for k,value in item.items():
                if k not in ["Name","URL","Gold","Tier 1","Tier 2"]:
                    if k == "Passive Effect":
                        newkey = item["Name"] + "-pe"
                        nzVars.append(newkey)
                        nzMods.append("1")
                        #print("I DONT WANT PASSIVES")
                    else:
                        nzVars.append(k)
                        nzMods.append(value.strip('+-%'))
            #except:
            #print(item," not a real item")
            varPos = []
            i=0
            for nzVar in nzVars:
                #print(i)
                i += 1
                if nzVar not in self.varnames:
                    self.varnames.append(nzVar)
                    #print(self.a,self.b,len(self.b),sep="\n")
                    newzero = np.zeros((len(self.b),1))
                    #print("shapes",self.a.shape,self.b.shape,newzero.shape)
                    self.a = np.hstack([self.a,newzero])
                varPos.append(self.varnames.index(nzVar))
            newRow = np.zeros(len(self.varnames))
            #print(varPos)
            for i in range(len(varPos)):
                newRow[varPos[i]] = nzMods[i].strip('+-%')
            self.a = np.vstack([self.a,newRow]) #add row to bottom of A matrix
            self.b = np.vstack([self.b,cost])
            #print(name,self.varnames,self.a,self.b,sep="\n")
	  
    def calc(self):
        #self.x = np.linalg.solve(self.a,self.b)
        try:
            self.x = np.linalg.lstsq(self.a,self.b)
            print("shape of x:",len(self.x))
            for i in range(len(self.x)):
                print(len(self.x[i]))
        except:
            print("Item system not solvable.\nA =",self.a,"\nB =",self.b.transpose())
            print("shapes: A",self.a.shape,"B:",self.b.shape,"X:", len(self.x))
            
    def printsoln(self):
        for i in range(len(self.varnames)):
            if i != 0:
                print(self.varnames[i],":",self.x[0][i])

    def printsys(self):
        for i in range(len(self.itemnames)):
            print(self.itemnames[i],":",end=" ")
            for j in range(len(self.varnames)):
                if self.a[i][j] != 0: print(self.a[i][j],self.varnames[j],end=" ")
            print("costs ",self.b[i])
                
