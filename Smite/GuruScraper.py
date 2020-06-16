import requests
from bs4 import BeautifulSoup
import json
import GamepediaScraper
import urllib.request
from PIL import Image
import math, operator
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt

class player():
    god = ""
    playerName = ""
    kills = ""
    deaths = ""
    assists = ""
    build = ""

class match():
    god = ""
    myTeam = List[str]
    theirTeam = List[str]
    kills = ""
    assists = ""
    deaths = ""
    ID = ""
    duration = ""
    time = ""
    ELO = ""
    date = ""

    def request_soup(self,url = ""):
         r = requests.get(url)
         soup = BeautifulSoup(r.content, "html.parser")


         return soup

    def __init__(self, link, playerName):
        matchSoup = self.request_soup(link)
        header = matchSoup.find_all("section",{"class","profile-header"})[0]
        header_stats = header.find_all("div",{"class","header-stat"})
        for stat in header_stats:
            if "Time" in stat.text:
                self.date = stat.get("title")
            if "Duration" in stat.text:
                self.duration = stat.text.strip().partition(" ")[0]
        #print(matchSoup)
        tableRows = matchSoup.find_all("tr")
        if tableRows != []:
            for tr in tableRows:
                if playerName in tr.text:
                    tds = tr.find_all("td")
                    #lastTD = ""
                    i = 0
                    for td in tds:
                        if i == 3 and self.ELO == "":#gross fix, because it kept coming back and overriding elo vals
                            self.ELO = td.text.strip()
                        i+=1
                        '''if "%" in lastTD:
                            self.ELO = td.text.strip()
                            print(self.ELO)
                        lastTD = td.text'''


        #print(duration, ELO)




class sgMatches():

     def __init__(self, opened = True, platform = "xb"):
         self.platform = platform

         self.saveFile = "sgMatches.txt"
         self.base_url = "http://smite.guru/profile/" + self.platform + "/"
         self.records = {}
         self.items = {}
         if opened == True:
             clan_members = ["BeaverBeliever9", "RichHomieCon503", "upperscoreswag", "flarghunstow", "teggybear95", "lilduzivert"]
             self.open_records()
             for cm in clan_members: self.pull_player(cm)
             self.save()
             self.calc_records()

 #       self.print_records(callPlayer = "BeaverBeliever",myGod = "Ah Muzen Cab", against = "Loki")
     def pull_player(self, playerName, save = True):
         if playerName not in list(self.records.keys()): self.records[playerName] = {"Matches": {},
                                                                                     "ELO": {},
                                                                                     "Teams": {},
                                                                                     "Opponents": {}
                                                                                     }
         self.get_current_ELO(playerName)
         self.pull_matches(playerName)


     def match_lengths(self,playerName):
         shortest_duration = -1
         shortID = ""
         longest_duration = 0
         longID = ""
         for match, data in self.records[playerName][0].items():
             duration = int(data["Duration"].strip('mh'))
             if shortest_duration == -1 or duration < shortest_duration:
                 shortest_duration = duration
                 shortID = match
             if duration > longest_duration:
                 longest_duration = duration
                 longID = match
         print("Shortest match:",shortID,":",shortest_duration)
         print("Longest match:",longID,":",longest_duration)

     def print_records(self,callPlayer = "", callGT="",showTeams = True,nGames = 2,checkOpp = "",checkTeam = "",myGod = "", against = ""):
         for player, record in self.records.items():
             if callPlayer == "" or callPlayer == player:
                 gametypes = record[0]
                 teammates = record[1]
                 opponents = record[2]
                 total_games = gametypes["Global"]["Wins"] + gametypes["Global"]["Losses"]
                 print("{0:15}:{5:16}\t{1:5} Games Played\t{2:5} Wins\t{3:5} Losses\t{4:5} Win PCT".format(player,total_games,gametypes["Global"]["Wins"],gametypes["Global"]["Losses"],gametypes["Global"]["PCT"],""))
                 for gametype, data in gametypes.items():
                     if gametype != "Global" and callGT == "" or callGT == gametype:
                         total_games = data["Wins"] + data["Losses"]
                         print("{5:17}{0:15}:\t{1:5} Games Played\t{2:5} Wins\t{3:5} Losses\t{4:5} Win PCT".format(gametype,total_games,data["Wins"],data["Losses"],data["PCT"],""))
                         prtstr = ""
                         curwinstrk = 0
                         oldwinstrk = 0
                         curlosestrk = 0
                         oldlosestrk = 0
                         for m, result in data["Matches"].items():
                             if result == "win":
                                 curwinstrk += 1
                                 if curlosestrk > oldlosestrk: oldlosestrk = curlosestrk
                                 curlosestrk = 0
                             else:
                                 curlosestrk += 1
                                 if curwinstrk > oldwinstrk: oldwinstrk = curwinstrk
                                 curwinstrk = 0
                         if curlosestrk > oldlosestrk: oldlosestrk = curlosestrk
                         if curwinstrk > oldwinstrk: oldwinstrk = curwinstrk
                         #print("\tWin Streak:",oldwinstrk,"\tLoss Streak:",oldlosestrk)
                         for god, dat in data["Gods"].items():
                             prtstr = prtstr + "\t\t[" + god + ": " + str(dat["Wins"]) + " wins and " + str(dat["Losses"]) + " (" + dat["PCT"] + ")]\n"
                         if callGT != "": print(prtstr)
                 if showTeams:
                     i = 0
                     for team in [teammates,opponents]:
                         print("\n")
                         if checkOpp == "":
                             emptyOpp = True
                         else:
                             emptyOpp = False
                         if checkTeam == "":
                             emptyTeam = True
                         else:
                             emptyTeam = False
                         if i == 0:
                             vs = "Teammate"
                             i += 1
                         else: vs = "Opponent"
                         for teammate, data in team.items():
                             if emptyOpp and emptyTeam or emptyOpp and i == 1 or emptyTeam and i == 0 or teammate == checkOpp or teammate == checkTeam:
                                 total_games = data["Wins"] + data["Losses"]
                                 if total_games > nGames: print("\t{4:8}: {0:15}\t{1:5} Games Played\t{2:5} Wins\t{3:5} Losses".format(teammate,total_games,data["Wins"],data["Losses"],vs))
     def save(self):
         f = open(self.saveFile,'w')
         f.write(json.dumps([self.records, self.items]))
         print("file saved")

     def open_records(self):
         filename = self.saveFile
         try:
             f = open(filename, 'r')
             tempread = json.loads(f.read())
             self.records = tempread[0]
             self.items = tempread[1]
             f.close
         except:
             print("no file found")
             pass

     def request_soup(self,url = ""):
         r = requests.get(url)
         soup = BeautifulSoup(r.content, "html.parser")
         return soup

     def gen_url(self,player, tab, page):
         page_url = self.base_url + player + "/" + tab + "?page=" + str(page)
         return page_url

     def open_img(self,file):
         try:
             savefolder = "_thumbs\\"
             imgname = file.rpartition("/")[2]
             savename = savefolder + "temp"
         except:
             savename = file
         try:
             im = Image.open(savename)
         except:
             file = "http:" + file.lstrip("htps:")
             urllib.request.urlretrieve(file,savename)
             im = Image.open(savename)
         return im

     def compare_img(self,im1file, im2file):
         im1 = self.open_img(im1file).resize((75,75))
         im2 = self.open_img(im2file).resize((75,75))
         #err = np.sum(im1.astype("float") - im2.astype("float")) ** 2)
         #err /= float(im1.shape[0] * im1.shape[1])
         #s = ssim(im1,im2)
         if im1 == im2:
             return True
         else:
             return False

     def find_item(self,num, img):
         item_path = Path("_thumbs\\_items\\")
         for item in item_path.iterdir():
             if self.compare_img(img,item):
                 print("item number",num,"is",item)

     def pull_match(self, link, player):
        newMatch = match(link, player)
        return newMatch

     def get_current_ELO(self,player):
        tab = "casual"
        soup = self.request_soup(self.base_url + player + "/" + tab)
        queue_widgets = soup.find_all("div",{"class":"widget queue-widget"})
        for qw in queue_widgets:
            mType = qw.find_all("div",{"class":"widget-header"})[0].text.partition("Rank")[0].strip()
            ELO = qw.find_all("span", {"class":"lg-text"})
            if ELO != []:
                self.records[player]["ELO"][mType] = ELO[0].text.strip()

     def plot_ELO(self,player):
        dates = []
        elos = []
        for mID, matchData in self.records[player]["Matches"].items():
            dates.append(matchData["Date"])
            elos.append(matchData["ELO"])
        plt.plot(dates,elos)
        plt.xlabel("dates")
        plt.ylabel("elo")
        plt.show()




     def pull_matches(self,player):
         tab = "matches"
         page = 1
         pagepulling = True
         matchcount = 0
         alwaysdown = True
         lastID = 0
         while pagepulling:
             ttc = 0
             soup = self.request_soup(self.gen_url(player, tab, page))
             match_widgets = soup.find_all("div",{"class":"widget match-widget"})
             tool_tips = soup.find_all("id",{"class":'qtip'})
             if match_widgets == []:# or page == 15:
                 pagepulling = False
             for mw in match_widgets:
                 mID = mw.find_all("div",{"class":"right-header-flex"})[0].find_all("a")[0].get("href").rpartition("/")[2]
                 if float(mID) > float(lastID) and lastID != 0: alwaysdown = False
                 try:
                     #print("checking match {}".format(mID))
                     m = self.records[player]["Matches"][mID]
                     #print("{} found.".format(mID))
                     pagepulling = False
                     break
                 except:
                     print("pulling",mID,"for",player)
                     outcome = mw.find_all("div",{"class":"widget-header match-loss"})
                     if outcome != []:
                         headInfo = outcome[0].text
                         outcome = "loss"
                     else:
                         outcome = mw.find_all("div",{"class":"widget-header match-victory"})
                         if outcome != []:
                             headInfo = outcome[0].text
                             outcome = "win"
                     god = mw.find_all("div",{"class":"name"})[0].text
                     mType = headInfo.partition("-")[0].strip()
                     dELO = headInfo.partition("Elo")[0].partition("(")[2].strip()
                     kills = mw.find_all("span",{"class":"text-kills"})[0].text
                     deaths = mw.find_all("span",{"class":"text-deaths"})[0].text
                     assists = mw.find_all("span",{"class":"text-assists"})[0].text
                     view_link = "http://smite.guru/match/" + self.platform + "/" + mID
                     matchData = self.pull_match(view_link, player)
                     team = []
                     opps = []
                     gameplayers = mw.find_all("div",{"class":"col-sm-6","style":""})[0].find_all("div",{"style":"display: inline-block; width: calc(50% - 5px); padding-left: 5px; overflow: hidden"})
                     inumer=0
                     for gp in gameplayers:
                         tempteam = []
                         inumer += 1
                         teams = gp.find_all("div",{"class":"team"})
                         if teams != []:
                             for teammate in teams:
                                 if teammate.text.strip() != "":tempteam.append(teammate.text.strip())
                         for teammate in tempteam:
                             if player == teammate:
                                team = tempteam
                         if team != tempteam:
                             opps = tempteam
                     for t in team:
                         if t == player: team.remove(t)
                     '''matchsoup = self.request_soup(view_link)
                     header = matchsoup.find_all("section",{"class":"profile-header"})
                     mID = header[0].find_all("small")[0].text
                     mType = header[0].text.partition(mID)[0].strip()''
                     mID = mID.partition(":")[2].strip()'''
                     self.records[player]["Matches"][mID] = {"God" : god,
                                                     "Result" : outcome,
                                                     "Type" : mType,
                                                     "Kills" : kills,
                                                     "Deaths" : deaths,
                                                     "Assists" : assists,
                                                     "Team":team,
                                                     "Date":matchData.date,
                                                     "Duration":matchData.duration,
                                                     "dELO":dELO,
                                                     "ELO":matchData.ELO,
                                                     "Opponents":opps,
                                                     "Items":[]}
                     #print(self.records[player]["Matches"][mID])
                     item_cards = mw.find_all("div",{"class":"card-sm-img"})
                     items = []
                     for ic in item_cards:
                         #try:
                         #print("{}",ic)
                         item_no = ic.get("data-item").strip()
                         #print("item_no:",item_no)
                         #print(ic)
                         #qtip = "qtip-3"
                         '''item_tooltip = mw.find_all("div",{"id",qtip})[0]
                         item_name = item_tooltip.find_all("div",{"class","tooltip-name"})[0].text
                         print(item_name)'''
                         if int(item_no) != 0:
                             self.records[player]["Matches"][mID]["Items"].append(item_no)
                             #item_img = ic.find_all("img")[0].get("src")
                             if not item_no in self.items:
                                 self.items[item_no] = "unknown_name_" + item_no
                             #cfe = self.find_item(item_no,item_img)
                     #print(self.records[player][0][mID])
                     #print(self.items)
                 lastID = mID
             page = page + 1
 #           #pagepulling = False
         print("All matches up to date for",player)

     def calc_records(self):
         for player, record in self.records.items():
             matches = record["Matches"]
             gametypes = {}
             teams = {}
             opponents = {}
             gametypes["Global"] = {"Wins" : 0, "Losses" : 0, "PCT" : "","Matches" : {}, "Gods" : {}}
             for match, data in matches.items():
                 id = int(match)
                 #print(player,data["Team"])
                 try:
                     g = gametypes[data["Type"]]
                 except:
                     gametypes[data["Type"]] = {"Wins" : 0, "Losses" : 0, "PCT" : "","Matches" : {},  "Gods" : {}}
                 try:
                     g = gametypes[data["Type"]]["Gods"][data["God"]]
                 except:
                     gametypes[data["Type"]]["Gods"][data["God"]]= {"Wins" : 0, "Losses" : 0, "PCT" : "","Matches" : {}}
                 try:
                     g = gametypes["Global"]["Gods"][data["God"]]
                 except:
                     gametypes["Global"]["Gods"][data["God"]]= {"Wins" : 0, "Losses" : 0, "PCT" : "","Matches" : {}}
                 #print(gametypes)
                 for teammate in data["Team"]:
                     if not teammate in teams.keys():
                         teams[teammate] = {"Wins" : 0,"Losses" : 0,"PCT" : "","Matches" : {}}
                 for opponent in data["Opponents"]:
                     if not opponent in opponents.keys():
                         opponents[opponent] = {"Wins" : 0,"Losses" : 0,"PCT" : "","Matches" : {}}
                 if data["Result"] == "loss":
                     for gt in ["Global",data["Type"]]:
                         gametypes[gt]["Losses"] += 1
                         gametypes[gt]["Matches"][id] = "loss"
                         gametypes[gt]["Gods"][data["God"]]["Losses"] += 1
                         gametypes[gt]["Gods"][data["God"]]["Matches"][id] = "loss"
                     for teammate in data["Team"]:
                         teams[teammate]["Losses"] += 1
                         teams[teammate]["Matches"][id] = "loss"
                     for opponent in data["Opponents"]:
                         opponents[opponent]["Losses"] += 1
                         opponents[opponent]["Matches"][id] = "loss"
                 elif data["Result"] == "win":
                     for gt in ["Global",data["Type"]]:
                         #print(gt)
                         gametypes[gt]["Wins"] += 1
                         gametypes[gt]["Matches"][id] = "win"
                         gametypes[gt]["Gods"][data["God"]]["Wins"] += 1
                         gametypes[gt]["Gods"][data["God"]]["Matches"][id] = "win"
                     for teammate in data["Team"]:
                         teams[teammate]["Wins"] += 1
                         teams[teammate]["Matches"][id] = "win"
                     for opponent in data["Opponents"]:
                         opponents[opponent]["Wins"] += 1
                         opponents[opponent]["Matches"][id] = "win"
             for gt, data in gametypes.items():
                 wins = int(data["Wins"])
                 losses = int(data["Losses"])
                 matchcount = wins + losses
                 winpct = int(100*wins/matchcount)
                 data["PCT"] = str(winpct) + "%"
                 for god, dat in data["Gods"].items():
                     wins = int(dat["Wins"])
                     losses = int(dat["Losses"])
                     matchcount = wins + losses
                     winpct = int(100*wins/matchcount)
                     dat["PCT"] = str(winpct) + "%"
             #self.records[player] = [gametypes, teams, opponents]
