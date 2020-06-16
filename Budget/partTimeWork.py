from enum import Enum
from budget import period

class deductionType(Enum):
    none = 0 #no deductions apply
    all = 1 #deductions across all taxes (such as HSA)
    red = 2 #reductions only applied to fed and state (such as IRA)

class deduction():
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type

class payCheck():       #ONLY WORKS FOR BIWEEKLY CHECKS





    def __init__(self, rate, hours, stateAll, fedAll):
        self.rate = rate
        self.hours = hours
        self.gross = rate*hours
        self.net = 0
        self.stateAll = stateAll
        self.fedAll = fedAll
        self.deducts = []

    def addDeduction(self,name, value, type):    #ALL DEDUCTIONS ARE CURRENTLY PER BIWEEKLY PAYCHECK
        d = deduction(name,value, type)
        self.deducts.append(d)

    def calcTax(self, rate, dType):
            taxable = self.gross
            for d in self.deducts:
                if d.type == dType: taxable -= d.value
            return taxable*rate

    def socialSecurityTax(self):
        SSRate = .062
        return self.calcTax(SSRate, deductionType.all)

    def medicareTax(self):
        if self.gross*2080 > 200000:
            medicareRate = .0235
        else:
            medicareRate = .0145
        return self.calcTax(medicareRate, deductionType.all)

    def transitTax(self):
        transitRate = .001
        return self.calcTax(transitRate, deductionType.all)

    def WBFTax(self):
        WBFRate = .012  #cents/hour
        return WBFRate*self.hours

    def ORTax(self):
        #from withholding tax formulas 2019
        #only applies currently to single with under 3 allowances
        #assumes standard deductions
        #formulas are all based on annual WAGES
        #assume wages = gross*26
        taxable = self.gross
        for d in self.deducts: taxable -= d.value
        wages = taxable*26
        fedTax = self.fedTax()*26
        stdDeduction = 2270

    #Fed Tax phase out - There is probably a slicker way to do this
        if wages < 125000:
            phaseOut = 6800
        elif wages < 130000:
            phaseOut = 5450
        elif wages < 135000:
            phaseOut = 4100
        elif wages < 140000:
            phaseOut = 2700
        elif wages < 145000:
            phaseOut = 1350
        else: phaseOut = 0

        if fedTax > phaseOut: fedTax = phaseOut
        base = wages - fedTax - stdDeduction

#probably also a slicker way to calculate final withholdings (general formula?)
        if wages <= 50000:
            if base < 3550:
                WH = 206 + 0.05*base - 206*self.stateAll
            elif base < 8900:
                WH = 383.5 + 0.07*(base-3550) - 206*self.stateAll
            else:
                WH = 758 + 0.09*(base-8900) - 206*self.stateAll
        else:
            if base < 125000:
                WH = 552 + 0.09*(base-8900) - 206*self.stateAll
            else: WH = 11001 + 0.099*(base-125000) - 206*self.stateAll

        return WH/26

    def fedTax(self):
        class method (Enum):
            percentage = 1

        taxable = self.gross
        for d in self.deducts: taxable -= d.value
        m = method.percentage
        #p = period.biweekly
        #hardcoded for biweekly
        if m == method.percentage:
            #allowances = {"Daily": 16.20, "Weekly": 80.80, "Biweekly": 161.5, semimonthly: 175, monthly: 350, quarterly: 1050]
            #if p = period.weekly:
            allowance = 161.50

            thresholds = [0, 146, 519, 1664, 3385, 6328, 7996, 19773]
            percentages = [.1, .12, .22, .24, .32, .35, .37]
            additions = [0, 37.3, 174.7, 553.32, 1259.64, 1793.40, 5915.35]

            for i in range(0, len(thresholds)-1):
                if taxable > thresholds[i] and taxable <= thresholds[i+1]:
                    p = percentages[i]


        return allowance*self.fedAll

    def netPay(self):
        allTaxes = [self.socialSecurityTax, self.medicareTax, self.transitTax, self.WBFTax, self.ORTax, self.fedTax]

        print("gross :",self.gross)
        sum = 0
        for t in allTaxes:
            sum += t()
            print(t,":", t())

        for d in self.deducts:
            sum += d.value
            print(d.name,":", d.value)

        self.net = self.gross - sum
        print("net :",self.net)




pc = payCheck(38.46,80 , 1, 1)
pc.addDeduction("HSA", 115.38, deductionType.all)
pc.addDeduction("Simple IRA", 590.90, deductionType.red)

pc.netPay()
