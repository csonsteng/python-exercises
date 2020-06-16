import requests
from bs4 import BeautifulSoup
import json
from GamepediaScraper import SmiteGamepediaScraper
from smitebuilder import smiteBuild
from itemSystem import itemSystem
class determineCosts():
     def __init__(self):
         self.smite = smiteBuild()
         self.smite.choose_god("Cernunnos")
         self.smite.level_up()
         self.smite.level_up()
         tier1 = []
         tier2 = []
         tier3 = []
         self.rwt2 = {}
         self.rwt3 = {}
         self.all_traits = {}
         self.buffed_traits = {}
         self.system = itemSystem()
         for k,i in self.smite.items.items():
             self.getbuffs(i)
             self.system.add_item(i)
             '''
             for key, item in i.items():
                 if key == "Tier 1":
                     if item not in tier1: tier1.append(item)
                 elif key == "Tier 2":
                     if item not in tier2: tier2.append(item)
         for k,i in self.smite.items.items():
             for key, item in i.items():
                 if key == "Name" and item not in tier1 and item not in tier2:
                     tier3.append(item)
         self.tiers = [tier1,tier2,tier3]
         self.analyze_tier(1)
         self.analyze_tier(2)
         self.analyze_tier(3)
         self.verify_traits(self.all_traits)
         self.show_trait_vals()
         print(self.all_traits)
         '''
         self.system.calc()
         self.system.printsoln()
         #self.system.printsys()

     def verify_traits(self,traits={}):
         for k,v in traits.items():
             holdcount = len(v["Costs"])
             if len(v["Mods"]) != holdcount or len(v["Names"]) != holdcount:
                 print("error with",v["Name"])

     def show_trait_vals(self):
         for k,v in self.all_traits.items():
             estval = self.estimate(k,"1")
             print(k,":",estval," gold per point")

     def estimate(self,key,value):
         costs = self.all_traits[key]["Costs"]
         values = self.all_traits[key]["Mods"]
         retval = 0
         num = len(costs)
         totcost = float(0)
         totval = float(0)
         contributedcost = -1
         if num == len(values):
             for i in range(0,num):
                 totcost += float(costs[i])
                 try:
                     totval += float(values[i].strip("+%"))
                 except:
                     pass
             try:
                 avgcost = totcost/num
                 avgval = totval/num
                 cpv = avgcost/avgval
                 contributedcost = int(cpv*float(str(value).strip("+%")))
             except:
                 pass
         return contributedcost

     def buffcount(self,item):
         try:
             c = len(self.buffed_traits[item])
         except:
             c = 0
         return c

     def getbuffs(self,item):
         try:
              t = self.buffed_traits[item["Name"]]
         except:
              self.buffed_traits[item["Name"]] = {}
         for key, value in item.items():
             if key not in ["Name","URL","Gold","Tier 1","Tier 2"]:
                 #if key == "HP5": print(item,":",key,":",value)
                 if key == "Passive Effect": key = item["Name"] + "-pe"
                 try:
                     t = self.all_traits[key]
                 except:
                     self.all_traits[key] = {"Name" : key,"Costs" : [],"Mods" : [],"Names" : []}
                 self.buffed_traits[item["Name"]][key] = value

     def subtractFrom(self,low_item,high_item):
         uptier = self.smite.items[high_item]
         lowtier = self.smite.items[low_item]
         basecost = int(uptier["Gold"])-int(lowtier["Gold"])
         name = uptier["Name"]
         return_item = {"Name":name}
         for k,v in self.all_traits.items():
             cv = ""
             lv = ""
             upper_passive = False
             lower_passive = False
             try:
                 cv = uptier[k]
                 if k == "Passive Effect":upper_passive = True
                 lv = lowtier[k]
                 if k == "Passive Effect":lower_passive = True
                 sign = ""
                 pBool = False
                 if cv[0] in ["+","-"]: sign = cv[0]
                 if cv.find("%") > 0: pBool = True
                 rem = sign + str(int(cv.strip("-+%")) - int(lv.strip("-+%")))
                 if pBool == True: rem = rem + "%"
                 modcost = self.estimate(k,int(lv.strip("-+%")))
                 #print(name,k,v,modcost)
                 if modcost != -1:
                     basecost = basecost - modcost
                 #print(k,rem)
                 return_item[k] = rem
             except:
                 if cv != "" and lv == "":
                     return_item[k] = cv
             if upper_passive == True:
                 if lower_passive == True:
                     return_item[k] = "difference between " + uptier[k] + " and " + lowtier[k]
         #print(cost,"=",basecost,"-",modcost)
         return_item["Gold"] = basecost
         return return_item

     def upgrade_val(self,item):
         try:
             data = self.smite.items[item]
         except:
             try:
                 data = self.rwt2[item]
             except:
                 data = self.rwt3[item]
         t1 = t2 = ""
         ri = {}
         try:
             fullcost = data["Gold"]
             t1 = data["Tier 1"]
             t2 = data["Tier 2"]
         except:
             pass
         if t2 != "":
             ri = self.subtractFrom(t2,item)
             ri["Name"]  += "-reworkedt3"
             self.rwt3[ri["Name"]] = ri
         elif t1 != "":
             ri = self.subtractFrom(t1,item)
             ri["Name"]  += "-reworkedt2"
             self.rwt2[ri["Name"]] = ri
         else: ri = data
         #print(ri)
         return ri

     def reworked(self,t=0):
         tier = []
         t -= 1
         if t==1:
             if self.rwt2 == {}:
                 tier = self.tiers[t]
             else:
                 for k,i in self.rwt2.items():
                     tier.append(k)
         elif t==2:
                 if self.rwt3 == {}:
                     tier = self.tiers[t]
                 else:
                     for k,i in self.rwt3.items():
                         tier.append(k)
         elif t==0:
             tier = self.tiers[t]
         else:
             print("bad tier")
         return tier

     def analyze_tier(self,t = 0):
         temp_traits = {}
         for i in range(1,3):
             print("analyzing tier",t,"... Run:",i)
             tier = self.reworked(t)
             for iterate in tier:
                 item = self.upgrade_val(iterate)
                 if iterate == "Combat Boots" or item["Name"] == "Combat Boots-reworkedt2": print("check")
                 try:
                     psv = item["Passive Effect"]
                     print(item["Name"]," has a passive effect: ",psv)
                 except:
                     try:
                         activeeffect = item["Active Effect"]
                         print(item["Name"]," has an active effect: ",activeeffect)
                     except:
                         print("::",item)
                         item_name = item["Name"]
                         if i == 1:
                             try:
                                 b = self.buffed_traits[item_name]
                             except:
                                 self.buffed_traits[item_name] = {}
                             cost = int(item["Gold"])
                             self.getbuffs(item)
                             if self.buffcount(item_name) == 1:
                                 for k,v in self.buffed_traits[item_name].items():
                                     if cost > 0:
                                         self.all_traits[k]["Mods"].append(v)
                                         self.all_traits[k]["Costs"].append(cost)
                                         self.all_traits[k]["Names"].append(item_name)
                                     else:
                                         ght = 1#print("item_name:",item_name)
                         else:
                             if self.buffcount(item_name) == 2:

                                 for q in range(1,3):
                                     if q == 1: remcost = cost
                                     for k,v in self.buffed_traits[item_name].items():
                                         knownval = self.estimate(k,v)
                                         if knownval != -1 and q == 1 and remcost == cost:
                                             remcost = remcost-knownval
                                         elif knownval == -1 and q == 2:
                                             try:
                                                 t = temp_traits[k]
                                             except:
                                                 temp_traits[k] = {"Name" : k,"Costs" : [],"Mods" : [], "Names" : []}
                                             if remcost > 0:
                                                 if not item_name in set(temp_traits[k]["Names"]):
                                                     temp_traits[k]["Costs"].append(remcost)
                                                     temp_traits[k]["Mods"].append(v)
                                                     temp_traits[k]["Names"].append(item_name)
                                                 else:
                                                     print("what the shit")
                                             else:
                                                 print("FUCK HERE")

                             elif self.buffcount(item_name) > 2:
                                 estval = 0
                                 for buff, val in self.buffed_traits[item_name].items():
                                     try:
                                         t = self.buffed_traits[item_name]["Passive Effect"]
                                     except:
                                         estval = estval + self.estimate(buff,val)
                                         #print(buff,val)
                                 goldmult = float(estval)/float(item["Gold"])
                                 for buff, val in self.buffed_traits[item_name].items():
                                     newval = float(self.estimate(buff,val))/goldmult
                                     if newval > 0:
                                         try:
                                             t = temp_traits[buff]
                                         except:
                                             temp_traits[buff] = {"Name" : buff,"Costs" : [],"Mods" : [], "Names" : []}
                                         temp_traits[buff]["Costs"].append(newval)
                                         temp_traits[buff]["Mods"].append(val)
                                         temp_traits[buff]["Names"].append(item_name)
                                 #print(item_name,"est:",estval,"act:",item["Gold"])
         for k,v in temp_traits.items():
             cnt = len(v["Costs"])
             if cnt == len(v["Mods"]) and cnt == len(v["Names"]):
                  for c in range(0,cnt):
                     try:
                         if v["Mods"][c] != "" and int(v["Costs"][c]) > 0 and v["Names"][c] not in set(self.all_traits[k]["Names"]):
                             self.all_traits[k]["Mods"].append(v["Mods"][c])
                             self.all_traits[k]["Costs"].append(v["Costs"][c])
                             self.all_traits[k]["Names"].append(v["Names"][c])
                         else:
                             print(v["Names"][c],"costs negative gold for ",v["Mods"][c],v["Name"],":",v["Costs"][c])
                     except:
                         pass
