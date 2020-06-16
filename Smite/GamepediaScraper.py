import requests
from bs4 import BeautifulSoup  
import json
from PIL import Image
from pathlib import Path
import shutil

class SmiteGamepediaScraper():
    
    def request_soup(self, url = ""):
         try:
             r = requests.get(url)
             soup = BeautifulSoup(r.content, "html.parser")
             return soup
         except:
             pass

    def pull_infobox(self, url = ""):
         try:
             soup = self.request_soup(url)
             infobox = soup.find_all("table", {"class" : "infobox"})
             trs = infobox[0].find_all("tr")
             return trs
         except:
             return []

    def pull_wikitable(self, url = ""):
         try:
             soup = self.request_soup(url)
             wikitable = soup.find_all("table", {"class" : "wikitable"})
             trs = wikitable[0].find_all("tr")
             return trs
         except:
             return []

    def get_gods(self):
         print("loading gods...")
         gods_url = self.base_url + "/Gods"
         god_soup = self.request_soup(gods_url)
         gods = god_soup.find_all("a", {"class" : "image"})
         all_gods = {}
         tryone = 1
         for god in gods:
             parent = god.parent
             name = parent.contents[1].find_all("a")[0].get("title")
             url = self.base_url + parent.contents[1].find_all("a")[0].get("href")
             god_dict = {}
             god_dict["Name"] = name
             god_dict["URL"] = url
             abil_dict = {}
             count = 1
             if tryone == 1:
                 try:
                     checktables = self.request_soup(url).find_all("table")
                 except:
                     checktables = []
                 for c in checktables:
                     findbody = c.find_all("td")
                     for fb in findbody:
                         #print(fb)
                         foundAbilities = fb.find_all("table",{"class":"wikitable"})
                         for fA in foundAbilities:
                             ability = {}
                             slotname = ""
                             abilname = ""
                             try:
                                 slot = fA.find_all("th")[0]
                                 abilname = slot.find_all("span")[0].text
                                 slotname = slot.text.partition("-")[0]
                                 flavorText = ""
                                 mod = ""
                             except:
                                 pass
                             if abilname != "":
                                 ability["Slot"] = slotname
                                 ability["Name"] = abilname
                                 trs = fA.find_all("tr")
                                 for tr in trs:
                                     tds = tr.find_all("td")
                                     for td in tds:
                                         try:
                                             mod = td.text.strip()
                                             if flavorText == "" and mod != "":
                                                 flavorText = mod
                                                 ability["Flavor"] = flavorText
                                             else:
                                                 try:
                                                     if mod.find(":") > 0 and mod.find("Ability Video") <= 0:
                                                         kvs = mod.partition(":")
                                                         key = kvs[0]
                                                         value = kvs[2]
                                                         ability[str(key)] = str(value)
                                                 except:
                                                     pass
                                         except:
                                             pass
                                 abil_dict[slotname] = ability
                 god_dict["Abilities"] = abil_dict
                 for tr in self.pull_infobox(url):
                     try:
                         key = tr.find_all("th")[0].text.rstrip(":")
                         value = tr.find_all("td")[0].text
                         if value.find("(") != -1:
                             parted = value.partition(" ")
                             value = [parted[0],parted[2].strip("()")] 
                         god_dict[key] = value
                     except:
                         pass

             all_gods[name] = god_dict
             #print(name)
             tryone = 1
         print("gods loaded")
         self.mGods = all_gods
         return all_gods

    def gods(self):
         self.get_gods()
         
    def save_image(self,image,savefolder, name):
         fileurl = "http:" + image.lstrip("htps:")
         print("trying",fileurl)
         png = requests.get(fileurl, stream=True)
         print("image data downloaded... saving to png")
         pngfile = savefolder + name + ".jpg"
         with open(Path(pngfile), "wb") as out_file:
               shutil.copyfileobj(png.raw, out_file)
         print("png saved to disk. opening with pillow")
         im = Image.open(pngfile)
         savepath = str(Path(str(savefolder) + str(name) + ".jpg"))
         im.resize((75,75))
         print("savepath is",savepath)
         im.convert("RGB")
         im.save(Path(savepath),format="JPEG")

    def save_item_image(self,image,name):
         savefolder = "_thumbs/_items/"
         #self.save_image(image,savefolder, name)
         
    def save_god_image(self,image,name):
         savefolder = "_thumbs/_gods/"
         #self.save_image(image,savefolder, name)

    def get_items(self):
         print("loading items...")
         items_url = self.base_url + "/Items"
         soup = self.request_soup(items_url)
         items = soup.find_all("td", {"class" : "tooltip-hover"})
         all_items = {}
         for item in items:
             onesave = False
             name = item.contents[1].find_all("a")[1].text
             url = self.base_url + item.contents[1].find_all("a")[1].get("href")
             try:
                 gold = item.contents[1].find_all("span")[0].text
             except:
                 gold = "0"
             effects = item.contents[3].find_all("dd")
             item_dict = {}
             item_dict["Name"] = name
             item_dict["URL"] = url
             item_dict["Gold"] = gold 
             try:
                 secondary = item.contents[3].find_all("dt")[0].text
             except:
                 secondary = "N/A"
             effectcount = 0
             for effect in effects:
                 effectcount = effectcount + 1	 
             currenteffect = 0
             for effect in effects:
                 currenteffect = currenteffect + 1
                 if currenteffect == effectcount and secondary != "N/A":
                    item_dict[secondary] = effect.text
                 else:
                    effect_parts = effect.text.partition(" ")
                    item_dict[effect_parts[2]] = str(effect_parts[0])
             for tr in self.pull_infobox(url):
                 #try:
                 if onesave == False:
                     #self.save_item_image(item.contents[1].find_all("img")[0].get("src"),name)
                     onesave = True
                 #except:
                     #pass
                 th = tr.find_all("th")
                 td = tr.find_all("td")
                 try:
                     if "Tier" in th[0].text:
                         tier = td[0].text
                         try:
                             tiernum = int(tier.rpartition(" ")[2])
                         except:
                             tiernum = 0
                 except:
                     pass
             tier_one = ""
             tier_two = ""
             for tr in self.pull_wikitable(url):
                 try:
                     item_name = tr.find_all("td")[0].find_all("a")[0].get("title")
                     if tiernum > 1 and tier_one == "":
                         tier_one = item_name
                         item_dict['Tier 1'] = tier_one
                     elif tiernum > 2 and tier_two == "":
                         tier_two = item_name
                         item_dict['Tier 2'] = tier_two
                 except:
                     pass
             #pull item picture!
             all_items[name] = item_dict  
         print("items loaded")
         return all_items

    def analyzeStat(self, gods={},stat=""):
         nv = {"Name" : "", "Value" : 0}
         mm = {"Max" : nv, "Min" : nv}
         stats = {"Level 1" : mm, "Level 20" : mm}
         store_stats = {}
         level_stats = {}

         if gods != {} and stat != "":
             for god, values in gods.items():
                 try:
                     s = values[stat]
                     base = s[0]
                     addl = s[1]
                     level_stats["Level 1"] = int(base)
                     level_stats["Level 20"] = int(base) + 20*int(addl)
                     store_stats[god] = level_stats
                 except:
                     pass
             if store_stats != {}:
                 for g, vs in store_stats.items():
                     l1 = vs["Level 1"]
                     l20 = vs["Level 20"]
                     print(g,l1,l20)
                     if l1 > stats["Level 1"]["Max"]["Value"]: 
                         stats["Level 1"]["Max"] = {"Name" : g, "Value" : l1}
                     if l1 < stats["Level 1"]["Min"]["Value"]: 
                         stats["Level 1"]["Min"] = {"Name" : g, "Value" : l1}
                     if l20 > stats["Level 20"]["Max"]["Value"]: 
                         stats["Level 20"]["Max"] = {"Name" : g, "Value" : l20}
                     if l20 < stats["Level 20"]["Min"]["Value"]: 
                         stats["Level 20"]["Min"] = {"Name" : g, "Value" : l20}  
             print(stats)

    def pullSmite(self):

         items = self.get_items()
         gods = self.get_gods()
         print("There are",len(gods), "gods.") 
         print("There are",len(items), "items.")
         gamepedia = [items,gods]
         return gamepedia

    def pull_gamepedia(self, bool=False):
         filename = self.saveFile
         try:
             f = open(filename, 'r')
             gamepedia = json.loads(f.read())
         except:
             bool = True
         if(bool):
             f = open(filename,'w')
             gamepedia = self.pullSmite()
             f.write(json.dumps(gamepedia))
         f.close
         return gamepedia
         
    def open_gamepedia(self, bool=False):
         gamepedia = self.pull_gamepedia(bool)
         gcount = 0
         items = gamepedia[0]
         gods = gamepedia[1]
         self.mItems = items
         self.mGods = gods
         
    def save(self):
         gp = [self.mItems,self.mGods]
         f = open(self.saveFile,'w')
         f.write(json.dumps(gp))
         
    def __init__(self, bool=False):
         self.mItems = {}
         self.mGods = {}
         self.base_url = "http://smite.gamepedia.com"
         self.saveFile = "gamepedia_save.txt"
         self.open_gamepedia(bool)
