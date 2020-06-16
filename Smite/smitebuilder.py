from SmiteGamepediaScraper import SmiteGamepediaScraper

class smiteBuild:

     def __init__(self, bool = False):
         gamepedia = SmiteGamepediaScraper(bool)
         self.gods = gamepedia.mGods
         self.items = gamepedia.mItems
         self.build = {
             "God" : "",
             "Items" : self.init_items(),
             "Stats" : self.init_stats()
             }
             
     def init_stats(self):
         stats = {
             "Level" : 0,
             "Speed" : 0,
             "Damage" : 0,
             "HP5" : 0,
             "MP5" : 0,
             "Health" : 0,
             "Mana" : 0,
             "Range" : 0,
             "Physical" : 0,
             "Magical" : 0,
             "Progression" : "",
             "Attack Speed" : 0
             }
         return stats
             
     def init_items(self):
         items = {}
         for i in range(1,7):
             slotname = "Slot " + str(i)
             items[slotname] = ""
         for i in range(1,2):
             slotname = "Active " + str(i)
             items[slotname] = ""
         return items
             
     def choose_god(self, god):
         self.build["God"] = self.gods[god]["Name"]
         
     def level_up(self):
         self.build["Stats"]["Level"] += 1
         self.update_stats()
         
     def find_god(self):
         return self.gods[self.build["God"]]

     def get_level(self):
         return int(self.build["Stats"]["Level"])
         
     def update_stats(self):
         print("updating stats")
         level = int(self.build["Stats"]["Level"])
         if self.build["God"] != "":
             god = self.find_god()
             for stat, statvalue in self.build["Stats"].items():
                 try:
                     s = god[stat]
                     base = float(s[0])
                     addl = float(s[1])
                     self.build["Stats"][stat] = base + addl*(level-1)
                 except:
                     print(stat,"failed")
                     pass
         
         
         