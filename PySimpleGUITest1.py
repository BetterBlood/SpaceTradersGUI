import PySimpleGUI as sg
import requests
import json
import time
from utilistiesSpaceTraders import *

class SpaceTrader:
    agent = ""
    fleet = [] # TODO : modifier pour enlever le "1" et ptetre initialiser mais normalement pas nécessaire car sera initialisé au moment ou on get la fleet
    token = ""
    faction = Faction.COSMIC
    contracts = []
    currentLocation = ""
    
    auto_mode = False

    # timers :
    current_time = int(round(time.time() * 100))
    sleep_time = 50 # 50 = 0.5 sec
    current_sleep_timer = 0
    sleep_start_time = 0

    contractindex = 0
    contractDeliverMaterialIndex = 0
    usernames = []

    # simplify the login when you already login once with token
    try:
        with open('datas.json', 'r') as f:
            jsonData = json.load(f)
            defaultUsername = jsonData['data'][0]['username']
            print("default username updated : " + defaultUsername)
            for i in range(len(jsonData['data'])):
                usernames.append(jsonData['data'][i]['username'])
    except Exception:
        defaultUsername = ""
        print("default username not set.")

    # layouts
    layoutMainMenu = [  
        [
            sg.Text('Username  : ', size=(10,1)), 
            sg.InputText(defaultUsername, size=(18,1), enable_events=True, key='USERNAME'), 
            sg.Combo([e for e in usernames], size=(18,1), readonly=True, enable_events=True, key='USERNAME_LIST')
        ],
        [
            sg.Text('Faction      : ', size=(10,1)), 
            sg.InputText('COSMIC', size=(18,1), disabled=True, key='FACTION'), 
            sg.Combo([e.value for e in Faction], size=(18,1), readonly=True, enable_events=True, key='FACTION_LIST')
        ],
        [sg.Text('Token        : ', size=(10,1)), sg.InputText(enable_events=True, size=(40,1), key='TOKEN', password_char='*',)],
        [sg.Text('Info            : ', size=(10,1)), sg.Text("None", enable_events=True, key='INFO')],
        [sg.Button('Connect', enable_events=True, key='CONNECT'), sg.Button('Register', enable_events=True, key='REGISTER'), sg.Button('Cancel')]
    ]
    
    inGameInfos = [
        [sg.Text(defaultUsername, enable_events=True, size=(10,1), key='USERNAME'), sg.Text('Contract Status', size=(10,1), enable_events=True, key='CONTRACTSTATUS')],
        [sg.Text("0", enable_events=True, size=(10,1), key='GOLD')],
        [sg.Text('COSMIC', enable_events=True, size=(10,1), key='FACTION')]
        ]
    can=sg.Canvas(size=(700,500), background_color='black', key='CANVAS')
    middleInfos = [
        [
            sg.Button('Map', enable_events=True, key='MAP'), 
            sg.Button('Fleet', enable_events=True, key='MIDDLE_FLEET'), 
            sg.Button('Ship1', enable_events=True, key='MIDDLE_SHIP1')
        ],
        [can]
    ]
    layoutMainScene = [
        [sg.Column(inGameInfos, vertical_alignment='top'), sg.VSeparator(), sg.Column(middleInfos, vertical_alignment='center')]
    ]

    sg.theme('LightBrown13') 
    # Create the Window
    windowMainMenu = sg.Window('Welcome to SpaceTraders', layoutMainMenu)
    windowMainScene = sg.Window('SpaceTradersGUI with pySimpleGUI', layoutMainScene, size=(960, 540), finalize=True)
    windowMainScene.hide()
    
    def __init__(self):
        self.dataRegister = dataRegister

    def initLayoutMainScene(self):
        inGameInfos = [
            [sg.Text(self.agent.symbol, enable_events=True, size=(20, 1), key='USERNAME')],
            [sg.Text(self.agent.credits, enable_events=True, size=(20, 1), key='GOLD')],
            [sg.Text(self.agent.startingFaction, enable_events=True, size=(20, 1), key='FACTION')],
            [sg.Text('Contract Status', size=(20, 1), enable_events=True, key='CONTRACT_STATUS')],
            [sg.HSeparator()],
            [
                sg.Text("Timers :", enable_events=False, size=(10,1)), 
                sg.Text("MM:ss.mmm", enable_events=False, justification='right', size=(10, 1))
            ],
            [
                sg.Text("Sleep Time :", enable_events=False, size=(10, 1)), 
                sg.Text("0", enable_events=True, size=(10, 1), key='TIMER_SLEEP', justification='right')
            ],
            [
                sg.Text("Reload Time :", enable_events=False, size=(10, 1)), 
                sg.Text("0", enable_events=True, size=(10, 1), key='TIMER_RELOAD', justification='right')
            ],
            [
                sg.Text("Nav Time :", enable_events=False, size=(10, 1)), 
                sg.Text("0", enable_events=True, size=(10, 1), key='TIMER_NAVIGATION', justification='right')
            ]
        ]
        
        self.can=sg.Canvas(size=(700,500), background_color='black', key='CANVAS')

        middleButtons = []
        middleButtons.append(sg.Button('Map', enable_events=True, key='MAP'))
        middleButtons.append(sg.Button('Fleet', enable_events=True, key='MIDDLE_FLEET'))
        for i in range(len(self.fleet)): #TODO : get le nom du ship, mais seulement pour le nom du bouton !
            middleButtons.append(sg.Button('Ship' + str(i + 1), enable_events=True, key='MIDDLE_SHIP' + str(i + 1)))

        middleButtons.append(sg.Push())
        middleButtons.append(sg.Button('Auto', enable_events=True, key='AUTO'))
        middleInfos = [
            middleButtons,
            [self.can]
        ]
        
        layoutMainScene = [
            [sg.Column(inGameInfos, vertical_alignment='top'), sg.VSeparator(), sg.Column(middleInfos, vertical_alignment='center')]
        ]
        return sg.Window('SpaceTradersGUI with pySimpleGUI', layoutMainScene, size=(960, 540), finalize=True)

    def setShipsURL(self, realShipname):
        self.shipsURL = "/my/ships"
        self.shipName = "/" + realShipname
        self.myShipsURL = https + self.shipsURL + self.shipName
        self.extractURL = self.myShipsURL + "/extract"
        self.cargoURL = self.myShipsURL + "/cargo"
        self.dockURL = self.myShipsURL + "/dock"
        self.orbitURL = self.myShipsURL + "/orbit"
        self.sellURL = self.myShipsURL + "/sell"
        self.purchaseURL = self.myShipsURL + "/purchase" 
        self.refuelURL = self.myShipsURL + "/refuel"
        self.navigateURL = self.myShipsURL + "/navigate"

    def setHeadersWithToken(self, token):
        self.token = token
        self.headersAuth = {"Authorization": "Bearer " + self.token}
        self.headersJson = {
            "Authorization": self.headersAuth['Authorization'],
            "Accept": "application/json"
        }
        self.headersAuthJsonAccept = {
            "Authorization": self.headersAuth['Authorization'],
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.headersAuthAccept = {
            "Authorization": self.headersAuth['Authorization'],
            "Accept": "application/json"
        }

    def decreaseSleepTimer(self):
        self.current_sleep_timer = (self.current_time - self.sleep_start_time)
        return self.sleep_time - self.current_sleep_timer
    
    def setSleepTimer(self):
        self.current_sleep_timer = 0 # TEST
        self.sleep_start_time = self.current_time

    def acceptContract(self, contractIndex = 0):
        contractAccepteURL = self.getURLContractVerb(self.contracts[contractIndex].id)
        r = requests.post((contractAccepteURL), headers = self.headersAuthJsonAccept)
        self.setSleepTimer()
        if (r.status_code == 200):
            print("contract accepted !!!")
            self.contracts[contractIndex] = Contract(r.json()['data']['contract'])
        elif (r['error']['code'] == 4501): # normaly useless, cause contracts is updated so it shouldn't ask to accept if already done
            print("contract already accepted !") 
            self.contracts[contractIndex].accepted = True

    """
    verb can be : 'accept', 'deliver' or 'fulfill' ('accept' by default)
    """
    def getURLContractVerb(self, contractId, verb="accept"):
        return contractURL + "/" + contractId + "/" + verb

    """
    shipNumber can't be greater than len(fleet) - 1
    """
    def getURLWayPointsfromSystem(self, shipNumber = 0):
        return systemsURL + "/" + self.fleet[shipNumber].nav.systemSymbol + "/waypoints"

    def getSystemFromWayPoint(self, waypoint):
        return waypoint[0:7] # TODO : split from end by '-' could be better in case of the lenght of systems symbol change 

    def getURLShipyardFromWayPoint(self, waypoint):
        return systemsURL + "/" + self.getSystemFromWayPoint(waypoint) + "/waypoints/" + waypoint + "/shipyard"

    # Event Loop to process "events" and get the "values" of the inputs
    def displayMainWindow(self):
        userNamePrevLength = len(self.defaultUsername)
        userNameCurrLength = len(self.defaultUsername)

        while True:
            event, values = self.windowMainMenu.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                return False

            userNameCurrLength = len(values['USERNAME'])

            #print(event)
            if event == "USERNAME_LIST":
                self.windowMainMenu['USERNAME'].update(values['USERNAME_LIST'])

            if event == "FACTION_LIST":
                self.windowMainMenu['FACTION'].update(values['FACTION_LIST'])

            if event == "CONNECT":
                if (len(values['TOKEN']) != 0):
                    self.setHeadersWithToken(values['TOKEN'])
                    respons = requests.get((https), headers = self.headersJson)
                    time.sleep(0.5)
                    if (respons.status_code == 200):
                        print("connected !!!")
                        print(respons.json()['status'])
                        agentInfo = requests.get((myAgentURL), headers = self.headersJson)
                        time.sleep(0.5)
                        # TODO : si le token n'est pas connu enregistrer les infos
                        if (agentInfo.status_code == 200): # TODO : display les infos proprement
                            self.agent = Agent(agentInfo.json()['data'])
                            fleetInfo = requests.get((shipsURL), headers = self.headersAuthAccept)
                            if (fleetInfo.status_code == 200):
                                for i in range(len(fleetInfo.json()['data'])):
                                    self.fleet.append(Ship(fleetInfo.json()['data'][i]))
                                    print(str(i) + " " + self.fleet[i].symbol)
                                
                                self.windowMainMenu.hide()
                                return True
                            else :
                                self.windowMainMenu['INFO'].update("fleet informations needed, not reacheable")
                        else :
                            self.windowMainMenu['INFO'].update("agent informations failed to load from server")
                    else:
                        print(respons.json())
                elif len(values['USERNAME']) < 3 or len(values['USERNAME']) > 14:
                    self.windowMainMenu['INFO'].update("length of your username should be from 3 to 14, or token should be given")
                else: # elif len(values['FACTION']) == 0:
                    try:
                        with open("datas.json", 'r') as f:
                            found = False
                            data = json.load(f)
                            for i in data['data']:
                                if (values['USERNAME'] == i['username']):
                                    self.token = i['token']
                                    self.windowMainMenu['TOKEN'].update(self.token)
                                    self.windowMainMenu['INFO'].update("token filled, ready to connect")
                                    found = True
                                    break
                            if not found:
                                self.windowMainMenu['INFO'].update("Impossible to find associate token, try to register first")
                    except FileNotFoundError:
                        print("The files associate with this username 'datas.json' does not exist")
                        self.windowMainMenu['INFO'].update("Impossible to find associate token")
                    except Exception as e:
                        print ("??? data structure ??? : " + e.__str__)

            if event == "REGISTER":
                if len(values['USERNAME']) >= 3 and len(values['USERNAME']) <= 14:
                    if len(values['FACTION']) >= 1 and values['FACTION'] in Faction:
                        self.windowMainMenu['INFO'].update("")
                        self.dataRegister['faction'] = values['FACTION']
                        self.dataRegister['symbol'] = values['USERNAME']
                        agentInfo = requests.post((registerNewAgentURL), headers=headersRegisterNewAgent, json=self.dataRegister)
                        print(agentInfo.json())
                        time.sleep(0.5)
                        if (agentInfo.status_code == 201):
                            print(json.dumps(agentInfo.json(), indent=2))
                            self.token = agentInfo.json()['data']['token']
                            self.agent = Agent(agentInfo.json()['data']['agent'])

                            try:
                                with open("datas.json", 'r') as f:
                                    data = json.load(f)
                                    found = False
                                    for i in data['data']:
                                        if (values['USERNAME'] == i['username']):
                                            i['token'] = self.token
                                            with open('datas.json', 'w') as outfile:
                                                json.dump(data, outfile, indent = 4)
                                            self.windowMainMenu['TOKEN'].update(self.token)
                                            self.windowMainMenu['INFO'].update("token updated and filled, ready to connect")
                                            found = True
                                            break
                                    if not found:
                                        print("new User")
                                        uniqueDataJsonExample['username'] = self.agent.symbol
                                        uniqueDataJsonExample['token'] = self.token
                                        data['data'].append(uniqueDataJsonExample)
                                        with open('datas.json', 'w') as outfile:
                                            json.dump(data, outfile, indent = 4)
                                        self.windowMainMenu['TOKEN'].update(self.token)
                                        self.windowMainMenu['INFO'].update("token saved and filled, ready to connect")
                            except FileNotFoundError:
                                print("file not found")
                                with open('datas.json', 'w') as outfile:
                                    dataJsonExample['data'][0]['username'] = self.agent.symbol
                                    dataJsonExample['data'][0]['token'] = self.token
                                    #print(dataJsonExample['data'][0]['username'])
                                    #print(dataJsonExample['data'][0]['token'])
                                    json.dump(dataJsonExample, outfile, indent = 4)
                                    print("file created, token saved and filled, ready to connect")
                                    
                                self.windowMainMenu['TOKEN'].update(self.token)
                                self.windowMainMenu['INFO'].update("file created, token saved and filled, ready to connect")

                            except Exception as e:
                                print ("??? data structure ??? : " + e.__str__)

                            self.windowMainMenu['TOKEN'].update(self.token)
                            self.windowMainMenu['INFO'].update("token filled, ready to connect")
                    else :
                        self.windowMainMenu['INFO'].update("Faction unkown")
                else:
                    self.windowMainMenu['INFO'].update("length of your username should be from 3 to 14")

            if (userNameCurrLength != userNamePrevLength): 

                if ((len(values['USERNAME']) > 0) and (values['USERNAME'].isprintable())):

                    for i, c in enumerate(values['USERNAME']):

                        if c not in ('0123456789qwertzuiopasdfghjklyxcvbnmQWERTZUIOPLKJHGFDSAYXCVBNM-_'):
                            self.windowMainMenu['USERNAME'].update(values['USERNAME'][:i] + values['USERNAME'][i+1:])
                            self.windowMainMenu['INFO'].update("char not supported")

                        if len(values['USERNAME']) > 0 and values['USERNAME'][i] in ('qwertzuiopasdfghjklyxcvbnm'): #uppercase the letters
                            self.windowMainMenu['USERNAME'].update(values['USERNAME'].upper())
                            self.windowMainMenu['INFO'].update("char uppered")
                            userNameCurrLength = len(values['USERNAME'])

            userNamePrevLength = userNameCurrLength
        return False

    def displayMainScene(self):

        self.windowMainScene = self.initLayoutMainScene()
        tkc=self.can.TKCanvas
        button_color_default = ('white','darkRed')
        button_color_selected = ('white','darkBlue')
        
        self.windowMainScene.un_hide()
        start_time = int(round(time.time() * 100))

        self.current_time = 0
        
        self.setSleepTimer()

        have_mine_drone = False
        shipYardWayPoint = ""
        shipYardHaveMiningDrone = False

        while True:
            event, values = self.windowMainScene.read(timeout=10)
            if event == sg.WIN_CLOSED:
                break

            self.current_time = int(round(time.time() * 100)) - start_time

            if event == "AUTO":
                if (not self.auto_mode):
                    self.windowMainScene['AUTO'].update("Manual")
                    print("mode automatique activé !")
                    # TODO : utiliser test1.py pour aller miner, vendre la marchandise, livrer les ressources au contract Point et finaliser le contract si les conditions sont remplies
                else :
                    self.windowMainScene['AUTO'].update("Auto")
                    print("mode automatique désactivé !")
                self.auto_mode = not self.auto_mode

            if self.current_sleep_timer < self.sleep_time:
                display_sleep_timer = self.decreaseSleepTimer()
                self.windowMainScene['TIMER_SLEEP'].update('{:02d}:{:02d}:{:03d}'.format((display_sleep_timer // 100) // 60,
                                                                  (display_sleep_timer // 100) % 60,
                                                                  (display_sleep_timer % 100)*10))
                continue # skip inputs if sleep timer is active (to respect the max(2) requests per seconde)
            elif (self.current_sleep_timer != self.sleep_time):
                display_sleep_timer = 0
                self.windowMainScene['TIMER_SLEEP'].update('{:02d}:{:02d}:{:03d}'.format((display_sleep_timer // 100) // 60,
                                                                  (display_sleep_timer // 100) % 60,
                                                                  (display_sleep_timer % 100)*10))

            #print(event, values)

            if self.auto_mode :
                print("action auto !")
                if (len(self.contracts) == 0):
                    print("recherche des infos concernant les contrats...")
                    contractsInfo = requests.get((contractURL), headers = self.headersJson)
                    self.setSleepTimer()
                    if (contractsInfo.status_code == 200):
                        #print(json.dumps(contractsInfo.json(), indent=2))
                        for i in range(len(contractsInfo.json()['data'])):
                            self.contracts.append(Contract(contractsInfo.json()['data'][i]))
                    else :
                        self.auto_mode = False
                        print("auto-mode desactivated, contract impossible to find")
                elif (len(self.contracts) == 1):
                    contract = self.contracts[0]
                    print("1 contract disponible, accepted : " + str(contract.accepted))

                    if (not contract.accepted):
                        self.acceptContract(0)
                    else :
                        print("TODO : faire ce qu'il faut pour faire le contract !!!")

                        # TODO : trouver et acheter un drone de minage si pas déjà de drone de minage dans la flotte
                        for i in range(len(self.fleet)):
                            #print(self.fleet[i].registration.role)
                            if (self.fleet[i].registration.role == "EXCAVATOR"):
                                have_mine_drone = True
                                break
                        
                        if (not have_mine_drone):
                            # pour acheter un drone de minage :
                            print("no mining drone !")

                            if (shipYardHaveMiningDrone): # buy the mining drone
                                dataBuyShip['shipType'] = "SHIP_MINING_DRONE"
                                dataBuyShip['waypointSymbol'] = shipYardWayPoint
                                print("test")
                                purchasedShipInfo = requests.post(shipsURL, json=dataBuyShip, headers=self.headersAuthJsonAccept)
                                self.setSleepTimer()
                                if (purchasedShipInfo.status_code == 201):
                                    print(purchasedShipInfo.json()['data'])
                                    print(purchasedShipInfo.json()['data']['ship']['registration']['role'])
                                    self.fleet.append(Ship(purchasedShipInfo.json()['data']['ship']))
                                    print(self.fleet[len(self.fleet) - 1].registration.role)
                                    have_mine_drone = True
                            elif (shipYardWayPoint != ""): # si on a le way point d'un SHIPYARD on regarder si SHIP_MINING_DRONE dispo
                                #print(shipYardWayPoint)
                                shipYardInfo = requests.get(self.getURLShipyardFromWayPoint(shipYardWayPoint), headers = self.headersAuthAccept)
                                self.setSleepTimer()
                                if (shipYardInfo.status_code == 200):
                                    for i in range(len(shipYardInfo.json()['data']['shipTypes'])):
                                        #print(shipYardInfo.json()['data']['shipTypes'][i])
                                        if (shipYardInfo.json()['data']['shipTypes'][i]['type'] == 'SHIP_MINING_DRONE'):
                                            shipYardHaveMiningDrone = True
                                            break
                            else : # vérifier SHIPYARD
                                wayPointsInfo = requests.get((self.getURLWayPointsfromSystem()), headers = self.headersAuthAccept)
                                self.setSleepTimer()
                                if (wayPointsInfo.status_code == 200): # TODO : factorise for loops
                                    for k in range(len(wayPointsInfo.json()['data'])):
                                        #print("k" + str(k))
                                        for j in range(len(wayPointsInfo.json()['data'][k]['traits'])):
                                            #print("j" + str(j) + " traits : " + wayPointsInfo.json()['data'][k]['traits'][j]['symbol'])
                                            if (wayPointsInfo.json()['data'][k]['traits'][j]['symbol'] == "SHIPYARD"):
                                                #print("shipyard finded way point : " + wayPointsInfo.json()['data'][k]['symbol'])
                                                shipYardWayPoint = wayPointsInfo.json()['data'][k]['symbol']
                        else :
                            print("we already have a mining drone !!!")

                        
                        # TODO : se déplacer au waypoint pour miner avec le drone de minage
                        # TODO : miner jusqu'à cargo plein
                        # TODO : gérer déplacement au contract et revenir miner si contract pas fulfilled




                self.setSleepTimer()

            if event == "MAP":
                self.windowMainScene['MAP'].update(button_color = button_color_selected)
                self.windowMainScene['MIDDLE_FLEET'].update(button_color = button_color_default)
                for i in range(len(self.fleet)):
                    self.windowMainScene["MIDDLE_SHIP" + str(i + 1)].update(button_color = button_color_default)

                # TODO : afficher les info sur la map
                tkc.delete("all")
                tkc.create_rectangle(100, 100, 600, 400, outline='white')
                tkc.create_line(50, 50, 650, 450, fill='green', width=5)
                tkc.create_oval(200,150,600,350, fill='red')
                tkc.create_text(350, 250, text="Hello World", fill='white', font=('Arial Bold', 16))

            if event == "MIDDLE_FLEET":
                # TODO : afficher les infos sur la fleet
                self.windowMainScene['MIDDLE_FLEET'].update(button_color = button_color_selected)
                self.windowMainScene['MAP'].update(button_color = button_color_default)
                for i in range(len(self.fleet)):
                    self.windowMainScene["MIDDLE_SHIP" + str(i + 1)].update(button_color = button_color_default)
                tkc.delete("all")
                tkc.create_rectangle(100, 100, 600, 400, outline='white')
                tkc.create_line(50, 50, 650, 450, fill='red', width=5)
                tkc.create_oval(150,150,550,350, fill='blue')
                tkc.create_text(350, 250, text="Hello World", fill='white', font=('Arial Bold', 16))
            
            for i in range(len(self.fleet)):
                tmp_event_name = "MIDDLE_SHIP" + str(i + 1)
                if event == tmp_event_name:
                    # TODO : afficher les info sur le vaisseau i
                    self.windowMainScene['MAP'].update(button_color = button_color_default)
                    self.windowMainScene['MIDDLE_FLEET'].update(button_color = button_color_default)
                    for j in range(len(self.fleet)):
                        self.windowMainScene["MIDDLE_SHIP" + str(j + 1)].update(button_color = button_color_default)
                    
                    print("touch")
                    self.windowMainScene["MIDDLE_SHIP" + str(i + 1)].update(button_color = button_color_selected)

                    tkc.delete("all")
                    tkc.create_rectangle(100, 100, 600, 400, outline='white')
                    tkc.create_line(50, 50, 650, 450, fill='red', width=5)
                    tkc.create_oval(150,150,550,350, fill='blue')
                    tkc.create_text(350, 250, text="ship" + str(i + 1), fill='white', font=('Arial Bold', 16))

            # TODO : faire une fonction pour get les infos des ships (le nombre et les noms) et faire une fonction qui cré le layout en fonction des infos dispos

            # TODO : on fleet modification (or ship modification) :
                #windowTMP = self.initLayoutMainScene()
                #self.windowMainScene.close()
                #self.windowMainScene = windowTMP
                #tkc=self.can.TKCanvas


def main():
    spaceTrader = SpaceTrader()
    if (spaceTrader.displayMainWindow()):
        #TODO : continue the programme
        print("yey")
        spaceTrader.displayMainScene()
        spaceTrader.windowMainScene.close()
    else :
        # TODO : close the application
        print("nop")

    spaceTrader.windowMainMenu.close()
if __name__ == "__main__":
    main()