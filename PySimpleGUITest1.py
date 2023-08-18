import PySimpleGUI as sg
import time
import os
import random
from collections import deque
from utilistiesSpaceTraders import *

class SpaceTrader:
    orders = deque()
    agent = ""
    fleet = []
    token = ""
    faction = Faction.COSMIC
    contracts = []
    currentLocation = ""
    shipYardWayPoint = ""
    shipYardHaveMiningDrone = False
    have_mine_drone = False
    currentSystem = ""
    
    auto_mode = False

    # timers :
    secToTimer = 100
    current_time = int(round(time.time() * secToTimer))
    sleep_time = 50 # 50 = 0.5 sec
    nav_time = 1
    laser_time = 1

    current_sleep_timer = 0
    current_nav_timer = 0
    current_laser_timer = 0

    sleep_start_time = 0
    nav_start_time = 0
    laser_start_time = 0


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
    canSize = (700,700)
    can=sg.Canvas(size=canSize, background_color='black', key='CANVAS')
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
    tkc = can.TKCanvas

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
        
        self.can=sg.Canvas(size=(700,700), background_color='black', key='CANVAS')

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

        self.tkc = self.can.TKCanvas

        return sg.Window('SpaceTradersGUI with pySimpleGUI', layoutMainScene, size=(960, 750), finalize=True)

    def setShipsURL(self, realShipname):
        self.currentShipSymbol = realShipname
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
        self.getNavShipURL = self.myShipsURL + "/nav"
        self.cooldownURL = self.myShipsURL + "/cooldown"

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
    
    def setSleepTimer(self):
        self.current_sleep_timer = 0 # TEST
        self.sleep_start_time = self.current_time

    def decreaseSleepTimer(self):
        self.current_sleep_timer = (self.current_time - self.sleep_start_time)
        return self.sleep_time - self.current_sleep_timer
    
    def setNavTimer(self, navTime):
        self.nav_time = navTime
        self.current_nav_timer = 0 # TEST
        self.nav_start_time = self.current_time
    
    def decreaseNavTimer(self):
        self.current_nav_timer = (self.current_time - self.nav_start_time)
        return self.nav_time - self.current_nav_timer
    
    def setLaserTimer(self, laserTime = 7000):
        #print("laserTime", laserTime)
        self.laser_time = laserTime
        self.current_laser_timer = 0 # TEST
        self.laser_start_time = self.current_time
    
    def decreaseLaserTimer(self):
        self.current_laser_timer = (self.current_time - self.laser_start_time)
        return self.laser_time - self.current_laser_timer

    def acceptContract(self, contractIndex = 0):
        self.orders.append(Order(True, RequestType('ACCEPT_CONTRACT'), self.getURLContractVerb(self.contracts[contractIndex].id), headers=self.headersAuthJsonAccept))

    """
    verb can be : 'accept', 'deliver' or 'fulfill' ('accept' by default)
    """
    def getURLContractVerb(self, contractId, verb="accept"):
        return contractURL + "/" + contractId + "/" + verb

    def getShipSystem(self, shipNumber = 0):
        return self.fleet[shipNumber].nav.systemSymbol

    """
    shipNumber can't be greater than len(fleet) - 1
    """
    def getURLWayPointsfromShipSystem(self, shipNumber = 0):
        return systemsURL + "/" + self.getShipSystem(shipNumber) + "/waypoints"

    def getURLSystems(self, systemSymbol):
        return systemsURL + "/" + systemSymbol

    def getSystemFromWayPoint(self, waypoint):
        return waypoint.rsplit('-',1)[0]

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
                        print(json.dumps(respons.json(), indent=2))
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
                                if os.path.getsize("datas.json") == 0:
                                    print("datas.json vide !")
                                    raise JsonEmptyError("os.path.getsize(\"datas.json\") == 0")
                                    
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
                            except (JsonEmptyError, FileNotFoundError) as e:
                                print(e)
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
                                raise Exception

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

    def drawSun(self, sunType):
        # display sun :
        self.tkc.create_oval(self.canSize[0]/2 - 15, self.canSize[1]/2 - 15,
                        self.canSize[0]/2 + 15 , self.canSize[1]/2 + 15, fill='orange')
        self.tkc.create_text(self.canSize[0]/2, self.canSize[1]/2, 
                        text=sunType, fill='white', font=('Arial Bold', 8))
    
    def displayPlanets(self, wayPoints):
        tmpX = 0
        tmpY = 0
        count = 0

        for i in range(len(wayPoints)):
            sameCoord = False
            systemItem = wayPoints[i]
            fact = 4

            itemRadius = 20 # TODO : def en fonction du corps celeste
            systemCenterX = self.canSize[0]/2 + int(systemItem['x']) * fact
            systemCenterY = self.canSize[1]/2 + int(systemItem['y']) * fact

            xS = systemCenterX - itemRadius/2
            yS = systemCenterY - itemRadius/2
            xE = systemCenterX + itemRadius/2
            yE = systemCenterY + itemRadius/2

            if tmpX == xS and tmpY == yS:
                sameCoord = True
                count += 1
            else :
                count = 0

            print(i, systemItem)
            print(xS,yS,xE,yE)

            if (systemItem['type'] == 'PLANET'):
                self.tkc.create_oval(xS, yS, xE, yE, fill='green')
                self.tkc.create_text(self.canSize[0]/2 + int(systemItem['x']) * fact, 
                                self.canSize[1]/2 + int(systemItem['y']) * fact, 
                                text=str(i), fill='white', font=('Arial Bold', 12))
                
            elif systemItem['type'] == 'GAS_GIANT' :
                self.tkc.create_oval(xS, yS, xE, yE, fill='#b5651d')
                self.tkc.create_text(self.canSize[0]/2 + int(systemItem['x']) * fact, 
                                self.canSize[1]/2 + int(systemItem['y']) * fact, 
                                text=str(i), fill='black', font=('Arial Bold', 12))
                
            elif systemItem['type'] == 'NEBULA' :
                self.tkc.create_oval(xS, yS, xE, yE, fill='yellow')
                self.tkc.create_text(self.canSize[0]/2 + int(systemItem['x']) * fact, 
                                self.canSize[1]/2 + int(systemItem['y']) * fact, 
                                text=str(i), fill='black', font=('Arial Bold', 12))
                
            elif systemItem['type'] == 'GRAVITY_WELL' :
                self.tkc.create_line(xS, yS, xE, yE, fill='red')
                self.tkc.create_line(xS, yE, xE, yS, fill='red')
                self.tkc.create_text(self.canSize[0]/2 + int(systemItem['x']) * fact, 
                                self.canSize[1]/2 + int(systemItem['y']) * fact, 
                                text=str(i), fill='black', font=('Arial Bold', 12))
            
            elif sameCoord :
                if (systemItem['type'] == 'MOON'):
                    gap = 5
                    distanceToPlanet = count*gap
                    moonDiagonal = 4
                    # trajectory :
                    self.tkc.create_oval(xS-distanceToPlanet, yS-distanceToPlanet, xE+distanceToPlanet, yE+distanceToPlanet, outline='white')
                    # moon :
                    self.tkc.create_oval(self.canSize[0]/2 + int(systemItem['x']) * fact + itemRadius/2 + distanceToPlanet - moonDiagonal/2, 
                                    self.canSize[1]/2 + int(systemItem['y']) * fact - moonDiagonal/2, 
                                    self.canSize[0]/2 + int(systemItem['x']) * fact + itemRadius/2 + distanceToPlanet + moonDiagonal/2, 
                                    self.canSize[1]/2 + int(systemItem['y']) * fact + moonDiagonal/2, fill='grey')
                    
                elif systemItem['type'] == 'ORBITAL_STATION':
                    gap = 5
                    distanceToPlanet = count*gap
                    moonDiagonal = 4
                    # trajectory :
                    self.tkc.create_oval(xS-distanceToPlanet, yS-distanceToPlanet, xE+distanceToPlanet, yE+distanceToPlanet, outline='white')
                    # orbital station :
                    self.tkc.create_rectangle(self.canSize[0]/2 + int(systemItem['x']) * fact + itemRadius/2 + distanceToPlanet - moonDiagonal/2, 
                                    self.canSize[1]/2 + int(systemItem['y']) * fact - moonDiagonal/2, 
                                    self.canSize[0]/2 + int(systemItem['x']) * fact + itemRadius/2 + distanceToPlanet + moonDiagonal/2, 
                                    self.canSize[1]/2 + int(systemItem['y']) * fact + moonDiagonal/2, fill='grey')

            elif systemItem['type'] == 'ASTEROID_FIELD' :
                self.tkc.create_oval(xS, yS, xE, yE, fill='grey')
                self.tkc.create_text(self.canSize[0]/2 + int(systemItem['x']) * fact, 
                                self.canSize[1]/2 + int(systemItem['y']) * fact, 
                                text=str(i), fill='white', font=('Arial Bold', 12))
                
            elif systemItem['type'] == 'DEBRIS_FIELD':
                self.tkc.create_rectangle(xS, yS, xE, yE, fill='grey')
                self.tkc.create_text(self.canSize[0]/2 + int(systemItem['x']) * fact, 
                                self.canSize[1]/2 + int(systemItem['y']) * fact, 
                                text=str(i), fill='white', font=('Arial Bold', 12))
                
            elif systemItem['type'] == 'JUMP_GATE':
                self.tkc.create_oval(xS, yS, xE, yE, fill='lightblue')
                jumpGateWidth = 3
                self.tkc.create_oval(xS+jumpGateWidth, yS+jumpGateWidth, xE-jumpGateWidth, yE-jumpGateWidth, fill='black')
                self.tkc.create_text(self.canSize[0]/2 + int(systemItem['x']) * fact, 
                                self.canSize[1]/2 + int(systemItem['y']) * fact, 
                                text=str(i), fill='white', font=('Arial Bold', 12))


            tmpX = xS
            tmpY = yS

    def drawSystem(self, systemInfo):
        systemDatas = systemInfo.json()['data']
        self.tkc = self.can.TKCanvas
        self.tkc.delete("all")

        self.drawSun(systemDatas['type']) # display sun
        self.displayPlanets(systemDatas['waypoints']) # display planets

    def reloadMainScene(self):
        windowTMP = self.initLayoutMainScene()
        self.windowMainScene.close()
        self.windowMainScene = windowTMP

    def updateDataNavigateShip(self, waypoint):
        self.dataNavigateShip = {
            "waypointSymbol": waypoint
        }

    def updateAgentAndDisplay(self, agentInfos):
        self.agent = Agent(agentInfos)
        self.windowMainScene['GOLD'].update(self.agent.credits)

    def deliverCargoToContract(self, currentShip, contract):
        dataDeliverCargo['shipSymbol'] = currentShip.symbol
        dataDeliverCargo['tradeSymbol'] = currentShip.cargo.inventory[0].symbol
        dataDeliverCargo['units'] = currentShip.cargo.inventory[0].units

        self.orders.append(Order(True, RequestType("DELIVER_CARGO_TO_CONTRACT"), 
                                shipSymbol=currentShip.symbol, 
                                url=contract.deliverURL, 
                                headers=self.headersAuthJsonAccept,
                                json=dataDeliverCargo))

    def doRequest(self, orderTmp):
        if orderTmp.requestType.value != "WAIT":
            print("Doing the following request :", orderTmp.requestType.value)

        infos = orderTmp.doRequest()
        #print(json.dumps(infos.json(),indent=2))

        match orderTmp.requestType.value:
            case "GET_STATUS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "REGISTER_NEW_AGENT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_AGENT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "LIST_AGENTS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_PUBLIC_AGENT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "LIST_CONTRACTS":
                if (infos.status_code == 200):
                    #print(json.dumps(infos.json(), indent=2))
                    for i in range(len(infos.json()['data'])):
                        self.contracts.append(Contract(infos.json()['data'][i]))
                else :
                    self.auto_mode = False
                    print("auto-mode desactivated, contract impossible to find")
                    print(json.dumps(infos.json(), indent=2))
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_CONTRACT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "ACCEPT_CONTRACT":
                if (infos.status_code == 200):
                    print("contract accepted !!!")
                    for i in range(len(self.contracts)):
                        if self.contracts[i].id == infos.json()['data']['contract']['id']:
                            self.contracts[i] = Contract(infos.json()['data']['contract'])
                    self.updateAgentAndDisplay(infos.json()['data']['agent'])
                    
                elif (infos.status_code == 404):
                    print("notfound ???")
                elif (infos.json()['error']['code'] == 4501): # normaly useless, cause contracts is updated so it shouldn't ask to accept if already done
                    print("contract already accepted !")
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "DELIVER_CARGO_TO_CONTRACT":
                if (infos.status_code == 200):
                    # TODO : faire une méthode pour get le contrat en rapport, (son id par exemple qui est utilisé dans l'url)
                    self.contracts[0] = infos.json()['data']['contract']
                    # TODO : utiliser le shipSymbol dans les datas de la requete pour trouver le bon ship
                    self.fleet[self.miningDroneIndex].cargo = Cargo(infos.json()['data']['cargo'])
                    print("delivery to contract made, need ", 
                          self.contracts[0].terms.deliver[0].unitsRequired,
                          "of",
                          self.contracts[0].terms.deliver[0].tradeSymbol,
                          "to fulfilled contract.")
                else :
                    print(json.dumps(infos.json(), indent=2))
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "FULFILL_CONTRACT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "LIST_FACTIONS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_FACTION":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "LIST_SHIPS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "PURCHASE_SHIP":
                if (infos.status_code == 201):
                    print(infos.json()['data'])
                    print(infos.json()['data']['ship']['registration']['role'])
                    self.fleet.append(Ship(infos.json()['data']['ship']))
                    self.updateAgentAndDisplay(infos.json()['data']['agent'])
                    #print(self.fleet[len(self.fleet) - 1].registration.role)
                    self.have_mine_drone = True
                    self.reloadMainScene()
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_SHIP":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_SHIP_CARGO":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "ORBIT_SHIP":
                if (infos.status_code == 200):
                    self.fleet[self.miningDroneIndex].nav = Nav(infos.json()['data']['nav'])
                    print(self.fleet[self.miningDroneIndex].symbol, self.fleet[self.miningDroneIndex].nav.status)
                else :
                    if infos.json()['error']['code'] == 4214 :
                        self.setNavTimer(infos.json()['error']['data']['secondsToArrival']*self.secToTimer)
                        print("nav timer updated :", infos.json()['error']['data']['secondsToArrival'], "s. to arrial\n","\torders cleared")
                        self.orders.clear()
                    else :
                        print (json.dumps(infos.json(), indent=2))

                #print("action not defined for this case:", orderTmp.requestType.value)

            case "SHIP_REFINE":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "CREATE_CHART":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_SHIP_COOLDOWN":
                unknown = -1
                if infos.status_code == 204: # no cooldown
                    #TODO : set all ship cooldown to 0
                    print("no cooldown, TODO : set all ship cd to 0")
                elif infos.status_code == 200:
                    #print(json.dumps(infos.json(), indent=2))
                    print("cd remaining seconds :", infos.json()['data']['remainingSeconds'])

                    if int(infos.json()['data']['totalSeconds']) == 70:
                        print("TODO update ship extraction cd")
                        self.setLaserTimer(infos.json()['data']['remainingSeconds'] * self.secToTimer)

                    elif int(infos.json()['data']['totalSeconds']) == unknown:
                        print("TODO update ship unknown cd")

                    else:
                        print("TODO update ship navigation cd")
                        self.setNavTimer(int(infos.json()['data']['remainingSeconds']) * self.secToTimer)

                    #print(json.dumps(infos.json(), indent=2))
                else :
                    print(json.dumps(infos.json(), indent=2))

                #print("action not defined for this case:", orderTmp.requestType.value)

            case "DOCK_SHIP":
                if (infos.status_code == 200):
                    self.fleet[self.miningDroneIndex].nav = Nav(infos.json()['data']['nav'])
                    print(self.fleet[self.miningDroneIndex].symbol, self.fleet[self.miningDroneIndex].nav.status)
                else :
                    if infos.json()['error']['code'] == 4214 :
                        self.setNavTimer(infos.json()['error']['data']['secondsToArrival']*self.secToTimer)
                        print("nav timer updated :", infos.json()['error']['data']['secondsToArrival'], "s. to arrial\n","\torders cleared")
                        self.orders.clear()
                    else :
                        print (json.dumps(infos.json(), indent=2))
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "CREATE_SURVEY":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "EXTRACT_RESOURCES":
                if (infos.status_code == 201):
                    # TODO : CD in ships
                    self.fleet[self.miningDroneIndex].updateCDExtract(infos.json()['data']['cooldown']['remainingSeconds'])
                    self.setLaserTimer(infos.json()['data']['cooldown']['remainingSeconds'] * self.secToTimer)

                    self.fleet[self.miningDroneIndex].cargo = Cargo(infos.json()['data']['cargo'])
                    extartionInfo = infos.json()['data']['extraction']['yield']
                    print(self.fleet[self.miningDroneIndex].symbol, "extract", extartionInfo['units'], extartionInfo['symbol'])

                elif (infos.status_code == 400):
                    print (json.dumps(infos.json(), indent=2))

                elif infos.json()['error']['code'] == 4000:
                    self.fleet[self.miningDroneIndex].updateCDExtract(infos.json()['error']['data']['cooldown']['remainingSeconds'])
                    self.setLaserTimer(infos.json()['error']['data']['cooldown']['remainingSeconds'] * self.secToTimer)
                    print(self.fleet[self.miningDroneIndex].symbol, "wait to extract")

                else :
                    print (json.dumps(infos.json(), indent=2))

                #print("action not defined for this case:", orderTmp.requestType.value)

            case "JETTISON_CARGO":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "JUMP_SHIP":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "NAVIGATE_SHIP":
                if infos.status_code == 200:
                    currentShip = self.fleet[self.miningDroneIndex]
                    # TODO : modifier l'index, ptetre faire une fonction qui get le symbol du ship (depuis l'url) 
                    # puis boucler sur fleet pour trouver lequel modifier
                    currentShip.fuel = Fuel(infos.json()['data']['fuel'])
                    currentShip.nav = Nav(infos.json()['data']['nav'])
                    self.setNavTimer(currentShip.getDiffFromRouteTime()*self.secToTimer)
                else :
                    print(json.dumps(infos.json()))

                #print("action not defined for this case:", orderTmp.requestType.value)

            case "PATCH_SHIP_NAV":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_SHIP_NAV":
                if infos.status_code == 200:
                    currentShip = self.fleet[self.miningDroneIndex]
                    # TODO : modifier l'index, ptetre faire une fonction qui get le symbol du ship (depuis l'url) 
                    # puis boucler sur fleet pour trouver lequel modifier
                    currentShip.nav = Nav(infos.json()['data'])
                    if self.current_nav_timer >= self.nav_time:
                        diff = currentShip.nav.route.getDiffFromRouteTimeArrival()
                        print("diff :", diff)
                        if diff > 0:
                            self.setNavTimer(diff * self.secToTimer)
                        else :
                            self.setNavTimer(2)
                else :
                    print(json.dumps(infos.json()))

                #print("action not defined for this case:", orderTmp.requestType.value)

            case "WARP_SHIP":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "SELL_CARGO":
                if infos.status_code == 201:
                    self.updateAgentAndDisplay(infos.json()['data']['agent'])
                    self.fleet[self.miningDroneIndex].cargo = Cargo(infos.json()['data']['cargo'])
                    print(json.dumps(infos.json()['data']['transaction'], indent=2))
                else :
                    print(json.dumps(infos.json(), indent=2))
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "SCAN_SYSTEMS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "SCAN_WAYPOINTS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "SCAN_SHIPS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "REFUEL_SHIP":
                if (infos.status_code == 200):
                    self.fleet[self.miningDroneIndex].fuel = Fuel(infos.json()['data']['fuel'])
                    self.updateAgentAndDisplay(infos.json()['data']['agent'])
                    print(json.dumps(infos.json()['data']['transaction'], indent=2))
                else :
                    print (json.dumps(infos.json(), indent=2))
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "PURCHASE_CARGO":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "TRANSFER_CARGO":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "NEGOTIATE_CONTRACT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_MOUNTS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "INSTALL_MOUNT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "REMOVE_MOUNT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "LIST_SYSTEMS":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_SYSTEM":
                if (infos.status_code == 200):
                    self.currentSystem = System(infos.json()['data'])
                    self.drawSystem(infos)
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "LIST_WAYPOINTS_IN_SYSTEM":
                if (infos.status_code == 200): # TODO : factorise for loops
                    for k in range(len(infos.json()['data'])):
                        #print("k" + str(k))
                        for j in range(len(infos.json()['data'][k]['traits'])):
                            #print("j" + str(j) + " traits : " + wayPointsInfo.json()['data'][k]['traits'][j]['symbol'])
                            if (infos.json()['data'][k]['traits'][j]['symbol'] == "SHIPYARD"):
                                #print("shipyard finded way point : " + wayPointsInfo.json()['data'][k]['symbol'])
                                self.shipYardWayPoint = infos.json()['data'][k]['symbol']
                                return True # stop the 2 for loop at the first shipYardFound
                    return False # no shipYard 
                    # TODO : ptetre directement ajouter ici dans la liste d'ordre ce qu'il faut faire pour chopper le shipyard le plus proche
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_WAYPOINT":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_MARKET":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_SHIPYARD":
                print(orderTmp.url)
                if (infos.status_code == 200):
                    for i in range(len(infos.json()['data']['shipTypes'])):
                        #print(shipYardInfo.json()['data']['shipTypes'][i])
                        if (infos.json()['data']['shipTypes'][i]['type'] == 'SHIP_MINING_DRONE'):
                            self.shipYardHaveMiningDrone = True
                            break
                #print("action not defined for this case:", orderTmp.requestType.value)

            case "GET_JUMP_GATE":
                print("action not defined for this case:", orderTmp.requestType.value)

            case "WAIT":
                tmp = 0

            case _:
                print("action not defined for this case: " + orderTmp.requestType.value)

    def displayMainScene(self):

        self.windowMainScene = self.initLayoutMainScene()
        button_color_default = ('white','darkRed')
        button_color_selected = ('white','darkBlue')
        
        self.windowMainScene.un_hide()
        start_time = int(round(time.time() * self.secToTimer))
        self.tkc = self.can.TKCanvas

        self.current_time = 0
        
        self.setSleepTimer()
        self.setLaserTimer(1)
        self.setNavTimer(1)

        systemInfo = ""
        for i in range(len(self.fleet)): #verify if we possess a mining drone
            if (self.fleet[i].registration.role == "EXCAVATOR"):
                self.have_mine_drone = True
                self.miningDroneIndex = i
                break

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

            #region TIMERS
            # request timer
            if self.current_sleep_timer < self.sleep_time:
                display_sleep_timer = self.decreaseSleepTimer()
                self.windowMainScene['TIMER_SLEEP'].update('{:02d}:{:02d}:{:03d}'.format((display_sleep_timer // 100) // 60,
                                                                  (display_sleep_timer // 100) % 60,
                                                                  (display_sleep_timer % 100)*10))
            elif (self.current_sleep_timer != self.sleep_time):
                display_sleep_timer = 0
                self.windowMainScene['TIMER_SLEEP'].update('{:02d}:{:02d}:{:03d}'.format((display_sleep_timer // 100) // 60,
                                                                  (display_sleep_timer // 100) % 60,
                                                                  (display_sleep_timer % 100)*10))
            
            # nav timer
            if self.current_nav_timer < self.nav_time:
                display_nav_timer = self.decreaseNavTimer()
                self.windowMainScene['TIMER_NAVIGATION'].update('{:02d}:{:02d}:{:03d}'.format((display_nav_timer // 100) // 60,
                                                                  (display_nav_timer // 100) % 60,
                                                                  (display_nav_timer % 100)*10))
            elif (self.current_nav_timer != self.nav_time):
                display_nav_timer = 0
                self.windowMainScene['TIMER_NAVIGATION'].update('{:02d}:{:02d}:{:03d}'.format((display_nav_timer // 100) // 60,
                                                                  (display_nav_timer // 100) % 60,
                                                                  (display_nav_timer % 100)*10))

            # laser timer
            if self.current_laser_timer < self.laser_time:
                display_laser_timer = self.decreaseLaserTimer()
                self.windowMainScene['TIMER_RELOAD'].update('{:02d}:{:02d}:{:03d}'.format((display_laser_timer // 100) // 60,
                                                                  (display_laser_timer // 100) % 60,
                                                                  (display_laser_timer % 100)*10))
            elif (self.current_nav_timer != self.nav_time):
                display_laser_timer = 0
                self.windowMainScene['TIMER_RELOAD'].update('{:02d}:{:02d}:{:03d}'.format((display_laser_timer // 100) // 60,
                                                                  (display_laser_timer // 100) % 60,
                                                                  (display_laser_timer % 100)*10))
            #endregion

            # REQUESTS EXECUTION :
            if len(self.orders) != 0:
                if self.current_sleep_timer >= self.sleep_time:
                    orderTmp = self.orders.popleft()
                    #orderTmp = self.orders[random.randint(0, len(self.orders) - 1)]
                    #print(len(self.orders))
                    #print("request Type : ", orderTmp.requestType.value)

                    self.doRequest(orderTmp)
                    self.setSleepTimer()

                    # TMP :
                    #for i in range(len(self.orders)):
                        #orderTmp = self.orders[i]
                        #print(i, "request Type :", orderTmp.requestType.value)
                        #print(orderTmp)
            
            #print(event, values)

            if self.auto_mode :
                #print("action auto !")
                if (len(self.contracts) == 0):
                    print("recherche des infos concernant les contrats...")
                    if len(self.orders) == 0:
                        self.orders.append(Order(False, RequestType('LIST_CONTRACTS'), url=contractURL, headers=self.headersJson))
                elif (len(self.contracts) >= 1):
                    contract = self.contracts[0]

                    if (not contract.accepted):
                        if len(self.orders) == 0:
                            print("1 contract available, accepted : " + str(contract.accepted))
                            self.acceptContract(0)
                    elif not self.have_mine_drone :
                        print("no mining drone !")

                        if (self.shipYardHaveMiningDrone): # buy the mining drone
                            if len(self.orders) == 0:
                                dataBuyShip['shipType'] = "SHIP_MINING_DRONE"
                                dataBuyShip['waypointSymbol'] = self.shipYardWayPoint
                                self.orders.append(Order(True, RequestType('PURCHASE_SHIP'), url=shipsURL, headers=self.headersAuthJsonAccept, json=dataBuyShip))  
                        elif (self.shipYardWayPoint != ""): # si on a le way point d'un SHIPYARD on regarder si SHIP_MINING_DRONE dispo
                            #print(shipYardWayPoint)
                            if len(self.orders) == 0:
                                self.orders.append(Order(False, RequestType('GET_SHIPYARD'), 
                                                        url=self.getURLShipyardFromWayPoint(self.shipYardWayPoint), 
                                                        headers=self.headersAuthAccept))
                        else : # vérifier si SHIPYARD dans le system
                            if len(self.orders) == 0:  
                                self.orders.append(Order(False, RequestType('LIST_WAYPOINTS_IN_SYSTEM'), url=self.getURLWayPointsfromShipSystem(), headers=self.headersAuthAccept))
                    else :
                        #left auto mode :
                        """ self.windowMainScene['AUTO'].update("Auto")
                        print("mode automatique désactivé !")
                        self.auto_mode = not self.auto_mode
                        
                        print("we already have a mining drone !!!") """

                        if (self.currentSystem != ""):
                            for waypoint in self.currentSystem.wayPoints:
                                if waypoint.type == "ASTEROID_FIELD":
                                    self.asteroidFieldWaypoint = waypoint.symbol
                                    self.updateDataNavigateShip(waypoint.symbol)
                        
                        if len(self.fleet) != 0 and len(self.orders) == 0:
                            currentShip = self.fleet[self.miningDroneIndex]
                            self.setShipsURL(currentShip.symbol)
                            # we are not in asteroid field so we need to navigate to # TODO  replace with == contract waypoint
                            if currentShip.nav.waypointSymbol != self.asteroidFieldWaypoint:
                                print("ship status :", currentShip.nav.status, "- timers :", self.current_nav_timer, self.nav_time)
                                if self.current_nav_timer < self.nav_time : # navigation processing
                                    print("navigation processing")
                                    self.orders.append(Order(True, RequestType("WAIT")))
                                    
                                elif currentShip.cargo.capacity - currentShip.cargo.units <= 0 and currentShip.nav.waypointSymbol == contract.getWayPointForDeliverThis(currentShip.cargo.inventory[0].symbol): 
                                    # dock
                                    self.orders.append(Order(True, RequestType("DOCK_SHIP"), 
                                                            shipSymbol=currentShip.symbol, 
                                                            url=currentShip.dockURL, 
                                                            headers=self.headersAuthJsonAccept))
                                    
                                    # Deliver Cargo to Contract
                                    self.deliverCargoToContract(currentShip, contract)
                                    
                                    # refuel if necessary
                                    if currentShip.fuel.current * 2 <= currentShip.fuel.capacity:
                                        self.orders.append(Order(True, RequestType("REFUEL_SHIP"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=currentShip.refuelURL, 
                                                                headers=self.headersAuthJsonAccept))
                                    
                                    # orbit 
                                    self.orders.append(Order(True, RequestType("ORBIT_SHIP"), 
                                                            shipSymbol=currentShip.symbol,
                                                            url=currentShip.orbitURL, 
                                                            headers=self.headersAuthJsonAccept))
                                    
                                    # nav to asteroid if contract not fulfilled 
                                    self.updateDataNavigateShip(self.asteroidFieldWaypoint)
                                    self.orders.append(Order(True, RequestType("NAVIGATE_SHIP"), 
                                                            shipSymbol=currentShip.symbol,
                                                            url=currentShip.navigateURL,
                                                            headers=self.headersAuthJsonAccept, 
                                                            json=self.dataNavigateShip))
                                    
                                    # set the timer for the navigation
                                    self.orders.append(Order(False, RequestType("GET_SHIP_NAV"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=currentShip.getNavShipURL, 
                                                                headers=self.headersAuthAccept))

                                elif (self.current_nav_timer >= self.nav_time): #TODO : modifier ! cela n'a aucun sens
                                    # if we are docked
                                    if (currentShip.nav.status == "DOCKED"):
                                        # orbit Ship
                                        self.orders.append(Order(True, RequestType("ORBIT_SHIP"), 
                                                                shipSymbol=currentShip.symbol,
                                                                url=self.orbitURL, 
                                                                headers=self.headersAuthJsonAccept))
                                        # navigate to asteroid field
                                        self.orders.append(Order(True, RequestType("NAVIGATE_SHIP"), 
                                                                shipSymbol=currentShip.symbol,
                                                                url=self.navigateURL,
                                                                headers=self.headersAuthJsonAccept, 
                                                                json=self.dataNavigateShip))
                                        # get the information to set timers
                                        self.orders.append(Order(False, RequestType("GET_SHIP_NAV"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=currentShip.getNavShipURL, 
                                                                headers=self.headersAuthAccept))
                                    elif (currentShip.nav.status == "IN_TRANSIT"):
                                        self.orders.append(Order(False, RequestType("GET_SHIP_NAV"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=currentShip.getNavShipURL, 
                                                                headers=self.headersAuthAccept))
                                    elif currentShip.nav.status == "IN_ORBIT":
                                        self.orders.append(Order(True, RequestType("NAVIGATE_SHIP"), 
                                                                shipSymbol=currentShip.symbol,
                                                                url=self.navigateURL,
                                                                headers=self.headersAuthJsonAccept, 
                                                                json=self.dataNavigateShip))
                                        
                                        self.orders.append(Order(False, RequestType("GET_SHIP_NAV"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=currentShip.getNavShipURL, 
                                                                headers=self.headersAuthAccept))

                                else :
                                    print("bug ?")
                                    self.orders.append(Order(True, RequestType("WAIT")))

                            elif currentShip.nav.waypointSymbol == self.asteroidFieldWaypoint:
                                if self.nav_time == 1 :# no info
                                    print("getting nav info", currentShip.nav.waypointSymbol, ", timers :", self.current_nav_timer, self.nav_time)
                                    self.orders.append(Order(False, RequestType("GET_SHIP_NAV"), 
                                                                    shipSymbol=currentShip.symbol, 
                                                                    url=currentShip.getNavShipURL, 
                                                                    headers=self.headersAuthAccept))
                                elif self.current_nav_timer < self.nav_time : # navigation processing
                                    print("navigate to", currentShip.nav.waypointSymbol, "- timers :", self.current_nav_timer, self.nav_time)
                                    self.orders.append(Order(True, RequestType('WAIT')))

                                elif currentShip.fuel.current * 2 <= currentShip.fuel.capacity: # refuel
                                    print("dock, refuel, orbit")
                                    # dock
                                    self.orders.append(Order(True, RequestType("DOCK_SHIP"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=self.dockURL, 
                                                                headers=self.headersAuthJsonAccept))
                                    # refuel
                                    self.orders.append(Order(True, RequestType("REFUEL_SHIP"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=self.refuelURL, 
                                                                headers=self.headersAuthJsonAccept))
                                    # orbit
                                    self.orders.append(Order(True, RequestType("ORBIT_SHIP"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=self.orbitURL, 
                                                                headers=self.headersAuthJsonAccept))
                                    
                                elif currentShip.cargo.capacity - currentShip.cargo.units > 0: # cargo not full
                                    if self.current_laser_timer >= self.laser_time:
                                        if currentShip.nav.status != "IN_ORBIT":
                                            self.orders.append(Order(True, RequestType("ORBIT_SHIP"), 
                                                                    shipSymbol=currentShip.symbol, 
                                                                    url=self.orbitURL, 
                                                                    headers=self.headersAuthJsonAccept))
                                        self.orders.append(Order(True, RequestType("EXTRACT_RESOURCES"), 
                                                                    shipSymbol=currentShip.symbol, 
                                                                    url=currentShip.getURLWithVerb("extract"), 
                                                                    headers=self.headersAuthJsonAccept))
                                        #self.orders.append(Order(False, RequestType("GET_SHIP_COOLDOWN"), shipSymbol=currentShip.symbol, url=self.cooldownURL, headers=self.headersAuthAccept))
                                    else:
                                        # nothing to do for the moment (wait timer to come to his end) but if multiple mining drone, will see
                                        print("add a wait time for 0.5 s.")
                                        self.orders.append(Order(True, RequestType('WAIT')))
                                
                                else : # cargo plein
                                    fullOfContractOre, sellDatas = currentShip.getSellDatas(researchedOre=contract.getContractDeliverSymbols())

                                    if fullOfContractOre: # TODO : si contient que contrat, navigate to contract, Get Ship Nav
                                        print("going to contract location ?")
                                        contractWaypoint = contract.getWayPointForDeliverThis(contract.getContractDeliverSymbols()[0])
                                        if contractWaypoint != None:
                                            self.updateDataNavigateShip(contractWaypoint)
                                            print(self.dataNavigateShip)
                                            self.orders.append(Order(True, RequestType("NAVIGATE_SHIP"), 
                                                                    shipSymbol=currentShip.symbol,
                                                                    url=self.navigateURL,
                                                                    headers=self.headersAuthJsonAccept, 
                                                                    json=self.dataNavigateShip))
                                            
                                            self.orders.append(Order(False, RequestType("GET_SHIP_NAV"), 
                                                                    shipSymbol=currentShip.symbol, 
                                                                    url=currentShip.getNavShipURL, 
                                                                    headers=self.headersAuthAccept))
                                        else :
                                            print("contract waypoint didn't find. TODO : désactiver le mode auto")
                                        
                                    else : # TODO : si cargo plein mais contient autre matériaux que contrat : dock, vendre tout sauf contract, orbit, mine,GET_SHIP_COOLDOWN
                                        self.orders.append(Order(True, RequestType("DOCK_SHIP"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=self.dockURL, 
                                                                headers=self.headersAuthJsonAccept))
                                        
                                        for data in sellDatas:
                                            self.orders.append(Order(True, RequestType("SELL_CARGO"), 
                                                                        shipSymbol=currentShip.symbol, 
                                                                        url=currentShip.sellURL, 
                                                                        headers=self.headersAuthJsonAccept,
                                                                        json=data))
                                            
                                        self.orders.append(Order(True, RequestType("ORBIT_SHIP"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=self.orbitURL, 
                                                                headers=self.headersAuthJsonAccept))
                                        
                                        self.orders.append(Order(True, RequestType("EXTRACT_RESOURCES"), 
                                                                shipSymbol=currentShip.symbol, 
                                                                url=currentShip.getURLWithVerb("extract"), 
                                                                headers=self.headersAuthJsonAccept))
                                                                                 
                # continue

            if event == "MAP":
                # update button display
                self.windowMainScene['MAP'].update(button_color = button_color_selected)
                self.windowMainScene['MIDDLE_FLEET'].update(button_color = button_color_default)
                for i in range(len(self.fleet)):
                    self.windowMainScene["MIDDLE_SHIP" + str(i + 1)].update(button_color = button_color_default)
                    
                if len(self.contracts) != 0:
                    if (systemInfo == ""):
                        self.orders.append(Order(False, RequestType('GET_SYSTEM'), url=self.getURLSystems(self.getSystemFromWayPoint(self.contracts[0].terms.deliver[0].destinationSymbol)), headers=self.headersAuthAccept))
                else :
                    self.orders.append(Order(False, RequestType('GET_SYSTEM'), url=self.getURLSystems(self.getSystemFromWayPoint(self.agent.headquarters)), headers=self.headersAuthAccept))
            
            if event == "MIDDLE_FLEET":
                # TODO : afficher les infos sur la fleet
                self.windowMainScene['MIDDLE_FLEET'].update(button_color = button_color_selected)
                self.windowMainScene['MAP'].update(button_color = button_color_default)
                for i in range(len(self.fleet)):
                    self.windowMainScene["MIDDLE_SHIP" + str(i + 1)].update(button_color = button_color_default)
                self.tkc.delete("all")
                self.tkc.create_rectangle(100, 100, 600, 400, outline='white')
                self.tkc.create_line(50, 50, 650, 450, fill='red', width=5)
                self.tkc.create_oval(150,150,550,350, fill='blue')
                self.tkc.create_text(350, 250, text="Hello World", fill='white', font=('Arial Bold', 16))
            
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

                    self.tkc.delete("all")
                    self.tkc.create_rectangle(100, 100, 600, 400, outline='white')
                    self.tkc.create_line(50, 50, 650, 450, fill='red', width=5)
                    self.tkc.create_oval(150,150,550,350, fill='blue')
                    self.tkc.create_text(350, 250, text=self.fleet[i].symbol, fill='white', font=('Arial Bold', 16))

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