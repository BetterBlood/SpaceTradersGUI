import PySimpleGUI as sg
import requests
import json
import time
from utilistiesSpaceTraders import *

class SpaceTrader:
    agent = ""
    fleet = ["1"] # TODO : modifier pour enlever le "1" et ptetre initialiser mais normalement pas nécessaire car sera initialiser au moment ou on get la fleet
    token = ""
    faction = Faction.COSMIC

    contractindex = 0
    contractDeliverMaterialIndex = 0

    try:
        with open('users.txt', 'r') as f:
            usersRaw = f.read()
            if (len(usersRaw) > 0):
                defaultUsername = usersRaw.splitlines()[0]
                #print(usersRaw.splitlines()[0])
    except FileNotFoundError:
        defaultUsername = ""

    # layouts
    layoutMainMenu = [  
        [sg.Text('Username  : ', size=(10,1)), sg.InputText(defaultUsername, size=(40,1), enable_events=True, key='USERNAME')],
        [sg.Text('Faction      : ', size=(10,1)), sg.InputText('COSMIC', size=(18,1), disabled=True, key='FACTION'), 
         sg.Combo([e.value for e in Faction], size=(18,1), readonly=True, enable_events=True, key='FACTION_LIST')],
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
            [sg.Text(self.agent.symbol, enable_events=True, size=(20,1), key='USERNAME')],
            [sg.Text(self.agent.credits, enable_events=True, size=(20,1), key='GOLD')],
            [sg.Text(self.agent.startingFaction, enable_events=True, size=(20,1), key='FACTION')],
            [sg.Text('Contract Status', size=(20,1), enable_events=True, key='CONTRACT_STATUS')]
        ]
        
        self.can=sg.Canvas(size=(700,500), background_color='black', key='CANVAS')

        middleButtons = []
        middleButtons.append(sg.Button('Map', enable_events=True, key='MAP'))
        middleButtons.append(sg.Button('Fleet', enable_events=True, key='MIDDLE_FLEET'))
        for i in range(len(self.fleet)): #TODO : get le nom du ship, mais seulement pour le nom du bouton !
            middleButtons.append(sg.Button('Ship' + str(i + 1), enable_events=True, key='MIDDLE_SHIP' + str(i + 1)))

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

    # Event Loop to process "events" and get the "values" of the inputs
    def displayMainWindow(self):
        userNamePrevLength = len(self.defaultUsername)
        userNameCurrLength = len(self.defaultUsername)
        #factionPrevLength = 0
        #factionCurrLength = 0

        while True:
            event, values = self.windowMainMenu.read()

            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                return False

            userNameCurrLength = len(values['USERNAME'])
            #factionCurrLength = len(values['FACTION'])

            #print(event)

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
                        if (agentInfo.status_code == 200): # TODO : display les infos proprement
                            self.agent = Agent(agentInfo.json()['data'])
                            print("agent name : " + agentInfo.json()['data']['symbol'])
                            print("agent gold : " + str(agentInfo.json()['data']['credits']))
                            print("agent faction : " + agentInfo.json()['data']['startingFaction'])
                            self.windowMainMenu.hide()
                            return True
                    else:
                        print(respons.json())
                elif len(values['USERNAME']) < 3 or len(values['USERNAME']) > 14:
                    self.windowMainMenu['INFO'].update("length of your username should be from 3 to 14, or token should be given")
                else: # elif len(values['FACTION']) == 0:
                    try:
                        with open(values['USERNAME'] + '-token.txt', 'r') as f:
                            self.token = f.read()
                            self.windowMainMenu['TOKEN'].update(self.token)
                            self.windowMainMenu['INFO'].update("token filled, ready to connect")
                    except FileNotFoundError:
                        print("The files associate with this username " + values['USERNAME'] + "does not exist")
                        self.windowMainMenu['INFO'].update("Impossible to find associate token")

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
                            json.dumps(agentInfo.json(), indent=2) # n'a pas marché
                            self.token = agentInfo.json()['data']['token']
                            self.agent = Agent(agentInfo.json()['data']['agent'])

                            with open(values['USERNAME'] + '-token.txt', 'w') as f:
                                f.write(self.token)
                            with open('users.txt', 'a+') as f:
                                f.write("\n" + values['USERNAME'])

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

            """
            if (factionCurrLength != factionPrevLength):

                if ((len(values['FACTION']) > 0) and (values['FACTION'].isprintable())):

                    for i, c in enumerate(values['FACTION']):

                        if c not in ('qwertzuiopasdfghjklyxcvbnmQWERTZUIOPLKJHGFDSAYXCVBNM'):
                            self.windowMainMenu['FACTION'].update(values['FACTION'][:i] + values['FACTION'][i+1:])
                            self.windowMainMenu['INFO'].update("char not supported")

                        if len(values['FACTION']) > 0 and values['FACTION'][i] in ('qwertzuiopasdfghjklyxcvbnm'): #uppercase the letters
                            self.windowMainMenu['FACTION'].update(values['FACTION'].upper())
                            self.windowMainMenu['INFO'].update("char uppered")
                            factionCurrLength = len(values['FACTION'])

            factionPrevLength = factionCurrLength # """

            userNamePrevLength = userNameCurrLength
        return False

    def displayMainScene(self):

        self.windowMainScene = self.initLayoutMainScene()
        tkc=self.can.TKCanvas
        button_color_default = ('white','darkRed')
        button_color_selected = ('white','darkBlue')
        
        self.windowMainScene.un_hide()

        while True:
            event, values = self.windowMainScene.read()
            if event == sg.WIN_CLOSED:
                break
                
            #print(event, values)

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
                    for i in range(len(self.fleet)):
                        self.windowMainScene["MIDDLE_SHIP" + str(i + 1)].update(button_color = button_color_default)
                        print("touch")
                    self.windowMainScene["MIDDLE_SHIP" + str(i + 1)].update(button_color = button_color_selected)

            # TODO : faire une fonction pour get les infos des ships (le nombre et les noms) et faire une fonction qui cré le layout en fonction des infos dispos
            if event == "MIDDLE_SHIP1":
                tkc.delete("all")
                tkc.create_rectangle(100, 100, 600, 400, outline='white')
                tkc.create_line(50, 50, 650, 450, fill='red', width=5)
                tkc.create_oval(150,150,550,350, fill='blue')
                tkc.create_text(350, 250, text="ship ?", fill='white', font=('Arial Bold', 16))

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