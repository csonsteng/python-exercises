

def shoo_gen(number_of_decks):
    #generates a shoo given the number of number_of_decks
    #a shoo is the entire deck pile which is typically multiple decks
    suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
    vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
    global shoo
    shoo = []
    for i in range(number_of_decks):
        for suit in suits:
            for val in vals:
                card = str(val) + ' of ' + suit
                short_val = gen_short(val)
                shoo.append([card, short_val])
    return shoo

def gen_short(val):

    if str(val) == '10':
        return '0'
    else:
        return str(val)

def draw_card():
    #randomly draw a card from the shoo
    #remove it from shoo and return it.
    random.seed
    i = random.randint(0,len(shoo)-1)

    card = shoo.pop(i)

    return card

def hand_val(hand):
    #finds the hand count for the starting hand only
    #requires exactly 2 cards
    cvs =[card_val(hand[0]), card_val(hand[1])]

    hv_pre = 0

    if any([cvs[0]== 1,cvs[1]== 1]):
        #if any of the cards were an Ace.
        hv_pre = int(cvs[0]) + int(cvs[1])

        if hv_pre == 11:
            hv = str(21) #BLACKJACK
        else:
            hv = str(hv_pre) + '/' + str(10 + hv_pre) #show the soft value
    else:
        #no aces = straight addition
        hv = str(int(cvs[0]) + int(cvs[1]))

    return hv

def card_val(card):

    if card in ['J','Q','K','0']:
        val = 10
    elif card == 'A':
        val = 1
    else:
        val = int(card)

    return int(val)

import random


def gen_hand():
    #draw 2 cards for the starting hand

    c1 = draw_card()
    c2 = draw_card()

    count = hand_val([c1[1], c2[1]])

    #returns just the long names of cards and the hand count
    hand = [c1[0],c2[0], count]
    return hand

import time

def gen_table(coffers):

    n = len(coffers)-1

    if n >= 0: # we need players

        players = ['Dealer']
        hands = [gen_hand()]
        insured = ['n/a']
        splat = ['n/a'] #holds a boolean yes/no for splitting
        bets = ['n/a']
        cash = ['0']

        #print('Dealer has an %s showing!' % hands[0][1])

        for i in range(n):
            players.append('Player ' + str(i+1))
            hands.append(gen_hand())
            insured.append('0')
            splat.append('0')
            bets.append('0')


            cash.append(coffers[i+1])

        return [players, hands, insured, splat, bets, cash]

    else:
        return -1

def add_card(card, hand):

    hand.insert(len(hand)-1, card[0])

    cv = card_val(card[1])
    if '/' in str(hand[len(hand) - 1]): #if the hand was already soft
        #ops contains the upper and lower hand values due to aces
        ops = str(hand[len(hand) - 1]).split('/')
        if int(ops[1]) + cv > 21:
            nv = int(ops[0]) + cv
        elif int(ops[1]) + cv == 21:
            nv = 21
        else:
            nv = str(int(ops[0]) + cv) + '/' + str(int(ops[1]) + cv)
        hand[len(hand)-1] = nv
    else:
        if all([cv == 1, hand[len(hand)-1] == '10']):
            #blackjack!
            hand[len(hand)-1] = 21
        elif all([cv == 1, int(hand[len(hand)-1]) < 10]):
            #ace that makes a soft hand
            hand[len(hand)-1] = str(int(hand[len(hand)-1]) + cv) + '/' + str(int(hand[len(hand)-1]) + 11)
        else:
            #all other hands
            hand[len(hand)-1] = int(hand[len(hand)-1]) + cv

    return hand

def deal_card(player,hand):

    card = draw_card()

    print('A {} is dealt to {}'.format(card[0], player))

    nh = add_card(card,hand)

    return nh

def split_cards(player, hand):

    hands = [[hand[0],card_val(hand[0].split()[0])],[hand[1],card_val(hand[1].split()[0])]]

    for i in range(len(hands)):
        hands[i] = deal_card(player, hands[i])
        print('hands[i]',hands[i])

        hands[i][2] = hand_val(hands[i])
        sys.stdout.flush
        time.sleep(1)


    table = [player, hands]

    return table

def yn_check(yn):
    if yn in 'Nn':
        return False
    elif yn not in 'Yy':
        while yn not in 'YyNn':
            yn = input('Please enter valid input.')
    else:
        return True

def play_again():
    time.sleep(1)

    return yn_check(input('Continue Playing? '))


def action(hand, firstpass):
    #contextually assemble potential lists of actions for the player.
    actions = []

    if int(str(hand[-1]).split('/')[0]) < 21:
        actions = ['[h]it','[s]tay']

        if firstpass == True:
            actions.append('[d]ouble')

        if card_val(hand[0].split()[0]) == card_val(hand[1].split()[0]):
            actions.append('spli[t]')


        act = input('\nWhat would you like to do?{}'.format(actions))
    else:
        act = 's'
    return act


def bust_chk(val):

    return int(str(val).split('/')[0]) > 21

def dealer_hitcheck(dh):

    if '/' in str(dh):
        if int(str(dh).split('/')[0]) < 8:
            return True
        else:
            return False
    else:
        if int(dh) < 17:
            return True
        else:
            return False


def check_win(player, hand, dh, splt, bet):
#player, player hand, dealer hand
#this is ran for each player to see if they won or lost
    dvs = str(dh[len(dh)-1]).split('/')
    pvs = str(hand[len(hand)-1]).split('/')

    #dealer hand value and player hand value
    dv = dvs[len(dvs)-1]
    pv = pvs[len(pvs)-1]

    #check if player and/or dealer has busted
    db = bust_chk(dv)
    pb = bust_chk(pv)
    time.sleep(1.5)
    print('{} has {}'.format(player,hand))
    sys.stdout.flush()
    time.sleep(1.5)
    if not pb:  #if the player busts, it doesn't matter what they had

        #player has to have 21 and didn't split
        if all([len(hand)==3,hand[2] == '21', splt == '0']):
            print(player,'wins with blackjack!')
            moneymod = bet*5//4
        else:
            if db: #if the dealer busted and the player didn't the player wins
                print('Dealer busted, {} wins!'.format(player))
                moneymod = bet
            elif int(pv) > int(dv): #player has more value than dealer
                print('{} wins with {} against {}!'.format(player,pv, dv))
                moneymod = bet
            elif int(pv) == int(dv): #it's a tie!!
                print('{} pushes on {}'.format(player,pv))
                moneymod = 0
            else: #all other cases (player < dealer) is loss
                print('{} loses with {} against {}!'.format(player,pv, dv))
                moneymod = -bet

    else:
        print(player,'is busted')
        moneymod = -bet
    print('\n')
    sys.stdout.flush()

    return moneymod #new money amount

import sys

def taketurns(table):
    #this is where players choose their actions
    num_hands = len(table[0])s
    i = 1
    spt = False

    #for j in range(1, len(table[0])):
    while i < num_hands:


        time.sleep(1)
        print('\n',table[0][i], ':: You have the following hand:', table[1][i], end='')
        sys.stdout.flush()
        for j in range(3):
            time.sleep(0.5)
            print('.',end='')
            sys.stdout.flush()
        print('   Dealer has %s showing.' % table[1][0][1])
        sys.stdout.flush()
        if all([table[1][i][2] == '21', table[3][i] == '0']):
            #blackjack! doesn't count it you paid for insurance...
            print('\nBLACKJACK!!\n')
            sys.stdout.flush()
        else:
            dobd = 1 #this is for doubling. You can only take one card if you double
            firstpass = True

            while all([table[1][i][-1] != '21',dobd == 1]):
                time.sleep(.75)


                bp = 1

                while bp != 0:

                    act = action(table[1][i],firstpass)

                    if all([act in 'Dd', firstpass == True]):
                        #double down
                        table[4][i] *= 2
                        dobd = 0
                        act = 'h'
                    firstpass = False

                    if act in 'Tt':
                        print('Splitting is broken. You are staying')
                        '''
                        #split
                        minitab = split_cards(table[0][i],table[1][i])

                        table[1][i] = minitab[1][1]
                        table[0].insert(i, minitab[0])
                        table[1].insert(i, minitab[1][0])
                        table[3][i] = '1'
                        table[3].insert(i, '1')
                        table[4].insert(i, table[4][i])
                        num_hands += 1
                        firstpass = True
                        print('\n',table[0][i], ':: You have the following hand:', table[1][i], end='')
                        sys.stdout.flush()
                        break

'''
                    if act in 'Hh':
                        #hit
                        table[1][i] = deal_card(table[0][i],table[1][i])
                        sys.stdout.flush()
                        time.sleep(1)
                        print(table[1][i])
                        sys.stdout.flush()
                    elif act in 'Ss':
                        dobd = 0
                        break
                    else:
                        bp = 2
                    bp -= 1
                if bust_chk(table[1][i][len(table[1][i])-1]):
                    time.sleep(1)
                    print(table[0][i], 'busted!')
                    sys.stdout.flush()
                    break


        i += 1
    return table


def placebets(table):

    #asks each nondealer player for a bet amount
    for i in range(1, len(table[0])):

        while True:
            try:
                bet = int(input('{}, you have {} at the table. How much would you like to bet?  '.format(table[0][i], table[5][i])))
                if all([bet > 0, bet <= int(table[5][i])]):
                    table[4][i] = bet
                    break
                elif bet == 0:
                    print('\nI guess we can let you play for free.\n')
                    sys.stdout.flush
                    time.sleep(2)
                    table[4][i] = 0
                    break
                else:
                    print('\nYou don\'t have that much money!\n')
                    sys.stdout.flush
                    time.sleep(1)
            except ValueError:
                print('That doesn\'t count as money around here.\n')
                sys.stdout.flush
                time.sleep(1)

    return table


def cashquery(n):
    #for n players this performs a query to see how much each player is starting with
    coffers = ['0'] #this is the dealers money. They are the only one that can go negative
    for i in (range(n)):

        while True:
            try:
                money = int(input('How much money does Player {} have? '.format(str(i+1))))
                if money > 0:
                    coffers.append(money)
                    break
                else:
                    print('You need at least 1 money to play blackjack.\n')
                    sys.stdout.flush
                    time.sleep(1)
            except ValueError:
                print("Please enter a valid number.\n")
                sys.stdout.flush
                time.sleep(1)
    return coffers

def main():



    shoo_gen(2)

    n = int(input('How many players? '))

    coffers = cashquery(n)

    while 1:

        table = gen_table(coffers)

        table = placebets(table)

        #it would have been way smarter to use a table object rather than array
        #buuuuuut....
        #table[1][0][1] is the first card in the dealers hand
        #which is only the full string, hence the split
        #there is a lot of potential for cleanup
        if str(table[1][0][1]).split()[0] == 'A':
            #if the dealer has an Ace then ask for insurance
            for i in range(1,n + 1):
                print('\n\n   Dealer has %s showing.' % table[1][0][1])
                sys.stdout.flush()
                time.sleep(1)

                print('\n',table[0][i], ':: You have the following hand:', table[1][i], end='')
                sys.stdout.flush()
                time.sleep(1)

                if yn_check(input('\n{} would you like insurance?'.format(table[0][i]))) == True:
                    table[2][i] = 1

        if table[1][0][2] == '21':
            #dealer has blackjack!
            #this doesn't actually do anything to money
            #just displays results
            print('Dealer has %s in the hole.' % table[1][0][0])
            print('Dealer has blackjack.\n')
            for i in range(1,n + 1):
                if table[2][i] == 1:
                    print(table[0][i], ' is insured!')
                else:
                    print(table[0][i], ' loses')
            if not play_again():
                break


        table = taketurns(table)


        print('\n\nDealer has: %s\n' % table[1][0])
                #print('Hand value is {}!'.format(table[1][0][len(table[1][0])-1]))

        sys.stdout.flush()
        while dealer_hitcheck(table[1][0][len(table[1][0])-1]):
            #loop through dealer logic to automate dealer hands
            #hit on a soft 17 or lower
            time.sleep(1.5)

            sys.stdout.flush()
            time.sleep(1)
            table[1][0] = deal_card(table[0][0],table[1][0])
            sys.stdout.flush()
            time.sleep(1)
            print('\n',table[1][0],'\n')
            sys.stdout.flush()
            #print('Hand value is {}!'.format(table[1][0][len(table[1][0])-1]))
        db = bust_chk(table[1][0][len(table[1][0])-1]) #dealer hand val
        if db:
            print('Dealer busted!\n')
            sys.stdout.flush()
            time.sleep(1)
        for i in range(1,len(table[0])):
            #loop through all player hands to check if there is a # WARNING:
            #and update $$$$
            table[5][i] += check_win(table[0][i],table[1][i],table[1][0], table[3][i], table[4][i]) #player name, player hand, dealer hand, was-split?, bet

        coffers = table[5]


        if not play_again():
            break

def gen_deals():
    shoo_gen(0)

    genruns = 10000000

    for j in range(genruns):

        cardnum = random.randint(1,52)

        shoo[cardnum-1][1] += 1

    for k in range(52):
        print('{}: {}'.format(shoo[k][0],shoo[k][1]/genruns))

main()
