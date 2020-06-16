from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import copy

class typeOfAccount(Enum):
    savings = 1     #all accesible accounts
    retirement = 2  #accounts not accessible until retirement
    debt = 3
    asset = 4   #cars, house and such

class typeOfEntry(Enum):
    credit = 1
    debit = 2

class period(Enum):
    daily = 1
    weekly = 7
    biweekly = 14
    semimonthly = 15
    monthly = 30
    bimonthly = 61
    quarterly = 91
    semiannually = 183
    annually = 365
    biannually = 731

class analysisType(Enum):
    none = 0
    netWorth = 1
    liquidateableEquity = 2
    retirement = 3
    coast = 4

class account():        #Covers all financial assests and liabilities
    def __init__(self, accountName, accountValue, accountType, interestRate = "blank", compoundPeriod = "blank"):
        self.accountName = accountName
        self.accountValue = accountValue
        self.accountType = accountType          #savings, retirement, debt, or asset

        self.days = [0]
        self.values = [self.accountValue]

        if interestRate == "blank":
            if accountType == typeOfAccount.savings:
                interestRate = 2
            elif accountType == typeOfAccount.retirement:
                interestRate = 7
            elif accountType == typeOfAccount.debt:
                interestRate = 25

        self.interestRate = interestRate        #APR

        if compoundPeriod == "blank":
            if accountType == typeOfAccount.savings:
                compoundPeriod = period.monthly
            else:
                compoundPeriod = period.daily

        self.compoundPeriod = compoundPeriod

    def transact(self, day, value):
        self.accountValue += value
        if day == self.days[-1]:
            self.values[-1] = self.accountValue
        elif day > self.days[-1]:
            for i in range(self.days[-1]+1, day):
                self.days.append(i)
                self.values.append(self.accountValue - value)
            self.days.append(day)
            self.values.append(self.accountValue)

    def completeData(self, day):
        if day > self.days[-1]:
            for i in range(self.days[-1]+1, day):
                self.days.append(i)
                self.values.append(self.accountValue)

class entry():
    def __init__(self, entryName, entryValue, entryType, targetAccount, entryPeriod):
        self.entryName = entryName
        self.entryValue = entryValue
        self.entryType = entryType
        self.targetAccount = targetAccount
        self.entryPeriod = entryPeriod

class transaction():
    def __init__(self, transactionName, fromAccount, toAccount, transactionValue, transactionPeriod):
        self.transactionName = transactionName
        self.fromAccount = fromAccount
        self.toAccount = toAccount
        self.transactionValue = transactionValue
        self.transactionPeriod = transactionPeriod
        #add debt payment MAX

class budgetTemplate():

    def __init__(self):
        self.entries = {}

    def addEntry(self, entryName, entryValue, entryType, targetAccount, entryPeriod):
        e = entry(entryName, entryValue, entryType, targetAccount, entryPeriod)
        self.entries[entryName] = e

class dashboard():

    def __init__(self):
        self.accounts = {}
        self.transactions = []
        self.budget = budgetTemplate()
        self.primaryAccount = ""
        self.emergencyMonths = 0
        self.withdrawalRate = 0
        self.cashFund = 0
        self.cashAccount = ""
        self.brokerageAccount = ""
        self.analysis = analysisType.none
        self.goal = 0
        self.plotData = []
        self.plotRange = []

    def setBrokerageAccount(self, accountName):
        self.brokerageAccount = accountName
    def setCashAccount(self, accountName):
        self.cashAccount = accountName
    def setWithdrawalRate(self, rate):
        self.withdrawalRate = rate
    def setCashFund(self, cfValue):
        self.cashFund = cfValue
    def setAnalysis(self, analysis, goal):
        self.analysis = analysis
        self.goal = goal
    def setPrimaryAccount(self, primaryAccount):
        self.primaryAccount = primaryAccount
    def setEmergencyMonths(self, monthsOfEmergency):
        self.emergencyMonths = monthsOfEmergency
    def addEntry(self, entryName, entryValue, entryType, targetAccount, entryPeriod):
        self.budget.addEntry(entryName, entryValue, entryType, targetAccount, entryPeriod)
    def addTransaction(self, transactionName, fromAccount, toAccount, transactionValue, transactionPeriod):
        self.transactions.append(transaction(transactionName,fromAccount, toAccount, transactionValue, transactionPeriod))
    def monthlyCashFlow(self):
        cf = 0
        sign = 0
        for e, v in self.budget.entries.items():
            if v.entryType == typeOfEntry.debit:
                sign = 1
            else:
                sign = -1

            if v.targetAccount == "Unitus" or v.targetAccount == "Chase":
                cf += sign*v.entryValue*period.monthly.value/v.entryPeriod.value
        return cf
    def periodExpenses(self, expensePeriod):        #period.daily, monthly, etc...
        exp = 0
        for e, v in self.budget.entries.items():
            if v.entryType == typeOfEntry.credit:
                exp += v.entryValue*expensePeriod.value/v.entryPeriod.value
        return exp
    def annualExpenses(self):
        return self.periodExpenses(period.annually)
    def annualWithdrawal(self):
        totalValue = self.savingsValue() + self.retireValue()
        wd = totalValue * self.withdrawalRate
        return wd
    def retired(self):
        return self.annualExpenses() <= self.annualWithdrawal()
    def liquidGoal(self):
        return self.liquidateableEquity() >= self.goal
    def nwGoal(self):
        return self.currentNetWorth() >= self.goal
    def howLongUntilRetirement(self):
        self.analysis = analysisType.retirement
        self.runAnalysis()
    def howLongUntilLiquid(self, checkValue):
        self.analysis = analysisType.liquidateableEquity
        self.goal = checkValue
        self.runAnalysis()
    def howLongUntilNW(self, checkValue):
        self.analysis = analysisType.netWorth
        self.goal = checkValue
        self.runAnalysis()
    def processMonth(self):
        processBudgetEntries(period.monthly, 0)
        self.payDebts()
        self.processTransactions(period.monthly)
        self.accrueInterest()

        dif = self.accounts[self.cashAccount].accountValue - self.cashFund
        if dif > 0:
            self.accounts[self.cashAccount].accountValue -= dif
            self.accounts[self.brokerageAccount].accountValue += dif



        if self.accounts[self.primaryAccount].accountValue < 0:
            print("DANGER")

    def processBudgetEntries(self, entryPeriod, day):
        sign = 0
        for e, v in self.budget.entries.items():
            if v.entryPeriod == entryPeriod:
                if v.entryType == typeOfEntry.debit:
                    sign = 1
                    #print("adding ", v.entryValue, " to " , v.targetAccount, "\n")
                else:
                    sign = -1
                    #print("subtracting ", v.entryValue, " from " , v.targetAccount, "\n")
                self.accounts[v.targetAccount].transact(day, sign*v.entryValue)
    def accrueInterest(self, compoundPeriod, day):
        for a, v in self.accounts.items():
            if v.compoundPeriod == compoundPeriod:
                rate = v.interestRate*compoundPeriod.value/365
                interest = rate*v.accountValue
                v.transact(day, interest)
    def payDebts(self, day):     #ADD IN PAYMENT SCHEMES!!! NOT ALL DEBTS CAN BE CLOSED AT MONTH'S END
        debt = 0
        for a, v in self.accounts.items():
            if v.accountType == typeOfAccount.debt:
                #print("Paid off ", v.accountName, " of ", v.accountValue)
                self.accounts[self.primaryAccount].transact(day,v.accountValue)
                #print("Unitus has: ", self.accounts[self.primaryAccount].accountValue, "\n")
                v.transact(day,-v.accountValue)
    def processTransactions(self, transactionPeriod, day):
        for t in self.transactions:
            if t.transactionPeriod == transactionPeriod:
                self.accounts[t.toAccount].transact(day,t.transactionValue)
                self.accounts[t.fromAccount].transact(day,-t.transactionValue)
            #print("Moving ", t.transactionValue, " from ", t.fromAccount, " to ", t.toAccount, "\n")
    def addAccount(self, accountName, accountValue, accountType, interestRate, compoundPeriod):
        mAccount = account(accountName, accountValue, accountType, interestRate, compoundPeriod)
        self.accounts[accountName] = mAccount
    def printAccounts(self):
        for a, v in self.accounts.items():
            print(a, " : ", v.accountValue)
        print("\nSavings: ", self.savingsValue())
        print("Retirement: ", self.retireValue())
        print("Debt: ", self.debtValue())
        print("Net Worth", self.netWorth(), "\n")
    def currentNetWorth(self):
        return self.netWorth(self.accounts)
    def netWorth(self, accounts = []):
        if accounts == []:
            accounts = self.accounts
        nw = 0
        nw += self.savingsValue(accounts)
        nw += self.retireValue(accounts)
        nw += self.debtValue(accounts)
        return nw
    def currentSavingsValue(self):
        return self.savingsValue(self.accounts)
    def savingsValue(self, accounts = []):
        if accounts == []:
            accounts = self.accounts
        savings = 0
        for a, v in accounts.items():
            if v.accountType == typeOfAccount.savings:
                savings += v.accountValue
        return savings

        def currentRetireValue(self):
            return self.retireValue(self.accounts)
    def retireValue(self, accounts = []):
        if accounts == []:
            accounts = self.accounts
        retirement = 0
        for a, v in accounts.items():
            if v.accountType == typeOfAccount.retirement:
                retirement += v.accountValue
        return retirement
    def currentDebtValue(self):
        return self.debtValue(self.accounts)
    def debtValue(self, accounts = []):
        if accounts == []:
            accounts = self.accounts
        debt = 0
        for a, v in accounts.items():
            if v.accountType == typeOfAccount.debt:
                debt += v.accountValue
        return debt
    def emergencyFund(self):
        ef = self.emergencyMonths * self.monthlyCashFlow()
        return ef
    def liquidateableEquity(self):
        le = self.savingsValue() - self.emergencyFund()
        return le
    def runAnalysis(self):
        dayChecks = []
        for p in period:
            dayChecks.append(0)

        while True:
            #self.plotData.append(copy.deepcopy(self.accounts))
            self.plotRange.append(dayChecks[0])

            for j in range(0, len(dayChecks)):
                dayChecks[j] += 1

            self.processPeriod(period.daily, dayChecks[0])

            i = 0
            for p in period:
                if p.value != 1:
                    if dayChecks[i] == p.value:
                        self.processPeriod(p, dayChecks[0])
                        dayChecks[i] = 0
                i += 1
            print("it is day",dayChecks[0], "and net worth is at $", self.currentNetWorth())
            if self.checkCriteria(dayChecks[0]):
                break;
    def checkCriteria(self,days):
        if self.analysis == analysisType.netWorth and self.nwGoal():
            print("Net Worth goal of",self.goal, "reached in",days, "days.")
            return True
        elif self.analysis == analysisType.liquidateableEquity and self.liquidGoal():
            print("Liquidatable Equity goal of",self.goal, "reached in",days, "days.")
            return True
        elif self.analysis == analysisType.retirement and self.retired():
            print("Retired with", self.netWorth(), "in value and", self.annualExpenses(), "in expenses after", days, "days.")
            return True
        else:
            return False
    def processPeriod(self, pPeriod, day):
        self.processBudgetEntries(pPeriod, day)
        self.processTransactions(pPeriod, day)
        self.accrueInterest(pPeriod, day)
        if pPeriod == period.monthly:
            self.payDebts(day)
            dif = self.accounts[self.cashAccount].accountValue - self.cashFund
            if dif > 0:
                self.accounts[self.cashAccount].accountValue -= dif
                self.accounts[self.brokerageAccount].accountValue += dif
    def plotNetWorth(self):
        nw = []
        j = 0
        for d in self.plotRange:
            nw.append(0)
            for k,a in self.accounts.items():
                a.completeData(self.plotRange[-1])
                for i in range(0,len(a.days)):
                    if a.days[i] == d:
                        nw[j] += a.values[i]
            j += 1
        #print(len(self.plotRange), len(nw))
        plt.plot(self.plotRange, nw, label="Net Worth")
        plt.xlabel("days")
        plt.ylabel("net worth")
        plt.legend()
        plt.show()
