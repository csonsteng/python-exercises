from budget import dashboard, typeOfAccount, typeOfEntry, period, analysisType

db = dashboard()


#db.addAccount("Barclays", 22295.11, typeOfAccount.savings, 0.022, period.monthly)
#db.addAccount("Unitus", 4015.32+8.95, typeOfAccount.savings, 0.003, period.monthly)

#db.addAccount("HSA", 6209.49, typeOfAccount.retirement, 0.05, period.daily)
#db.addAccount("401k", 22959.61, typeOfAccount.retirement, 0.07, period.daily)
#db.addAccount("Roth", 28504.94, typeOfAccount.retirement, 0.07, period.daily)       #Roth IRA
#db.addAccount("Vanguard", 24462, typeOfAccount.savings, 0.07, period.daily)         #Brokerage
#db.addAccount("SIMPLE", 575.59, typeOfAccount.retirement, 0.07, period.daily)       #SIMPLE IRA (work)

#db.addAccount("Capital One", -21.67, typeOfAccount.debt, -0.25, period.monthly)
#db.addAccount("Chase", -674.66, typeOfAccount.debt, -0.25, period.monthly)      #AFTER 1 MONTH ACCRUE INTEREST

#db.addAccount("Cash", 365, typeOfAccount.savings, 0, period.monthly)
#db.addAccount("Poker", 130, typeOfAccount.savings, 0, period.monthly)

#db.addAccount("Barclays", 22295.11, typeOfAccount.savings, 0.022, period.monthly)
#db.addAccount("Unitus", 4015.32+8.95, typeOfAccount.savings, 0.003, period.monthly)
#Net Worth 108829.68

#NEED TO START STORING DATA

#Add all accounts ("name", value,retirement, savings, or debt, interest rate, compound period)
db.addAccount("Barclays", 24373.67, typeOfAccount.savings, 0.022, period.monthly)
db.addAccount("Unitus", 1122.31+4+8.95, typeOfAccount.savings, 0.003, period.monthly)

db.addAccount("HSA", 6665.61, typeOfAccount.retirement, 0.05, period.daily)
db.addAccount("401k", 23727.36, typeOfAccount.retirement, 0.07, period.daily)
db.addAccount("Roth", 30340.79, typeOfAccount.retirement, 0.07, period.daily)       #Roth IRA
db.addAccount("Vanguard", 24462, typeOfAccount.savings, 0.07, period.daily)         #Brokerage
db.addAccount("SIMPLE", 1294.85, typeOfAccount.retirement, 0.07, period.daily)       #SIMPLE IRA (work)

db.addAccount("Capital One", -26.67, typeOfAccount.debt, -0.25, period.monthly)
db.addAccount("Chase", 0.00, typeOfAccount.debt, -0.25, period.monthly)      #AFTER 1 MONTH ACCRUE INTEREST

db.addAccount("Cash", 200, typeOfAccount.savings, 0, period.monthly)
db.addAccount("Poker", 100, typeOfAccount.savings, 0, period.monthly)

db.setPrimaryAccount("Unitus")
db.setEmergencyMonths(6)
db.setWithdrawalRate(0.04)
db.setCashFund(20000)
db.setCashAccount("Barclays")
db.setBrokerageAccount("Vanguard")

db.addEntry("Paycheck", 1681.64, typeOfEntry.debit, "Unitus", period.biweekly)
db.addEntry("Rent", 950, typeOfEntry.credit, "Unitus", period.monthly)
db.addEntry("Utilities", 203.34, typeOfEntry.credit, "Chase", period.monthly)
db.addEntry("Food", 25, typeOfEntry.credit, "Chase", period.daily)
db.addEntry("Gas", 50, typeOfEntry.credit, "Chase", period.semimonthly)
db.addEntry("Entertainment", 275, typeOfEntry.credit, "Chase", period.monthly)

db.addEntry("Renters Insurance", 185, typeOfEntry.credit, "Chase", period.biannually)
db.addEntry("Car Insurance", 589, typeOfEntry.credit, "Chase", period.biannually)

db.addEntry("SIMPLE IRA Contribution", (1181.8+184.62)/2, typeOfEntry.debit, "SIMPLE", period.biweekly)
db.addEntry("HSA Contribution", (230.76+38.46)/2, typeOfEntry.debit, "HSA", period.biweekly)

db.addTransaction("Roth IRA Contribution", "Unitus", "Roth", 500, period.monthly)
db.addTransaction("Barclays Contribution", "Unitus", "Barclays", 521.35, period.monthly)


#db.howLongUntilRetirement()
db.printAccounts()
print(db.monthlyCashFlow())
monthlyExpenses = db.periodExpenses(period.monthly)
netWorth = db.currentNetWorth()
ef = db.emergencyFund()
sustain = monthlyExpenses/ef
print(monthlyExpenses)
print((24373.67+1135.26)/monthlyExpenses)
#db.plotNetWorth()
