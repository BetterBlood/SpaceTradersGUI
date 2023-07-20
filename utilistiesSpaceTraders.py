from enum import EnumMeta, Enum

token = ""
https = "https://api.spacetraders.io/v2"
myAgentURL = https + "/my/agent"
registerNewAgentURL = https + "/register"
contractURL = https + "/my/contracts"
shipsURL = https + "/my/ships"
systemsURL = https + "/systems"

#headers
headersRegisterNewAgent = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
headersAuth = {"Authorization": "Bearer " + token}
headersJson = {
    "Authorization": headersAuth['Authorization'],
    "Content-Type": "application/json"
}
headersAuthAccept = {
    "Authorization": headersAuth['Authorization'],
    "Accept": "application/json"
}
headersAuthJsonAccept = {
    "Authorization": headersAuth['Authorization'],
    "Content-Type": "application/json",
    "Accept": "application/json"
}

#datas
dataRegister = {
    "faction": "",
    "symbol": ""
}

dataBuyShip = {
    "shipType": "",
    "waypointSymbol": ""
}

dataJsonExample = {
    "data": [
        {
            "username": "userTest",
            "token": "tokenTest"
        }
    ]
}
uniqueDataJsonExample = {
    "username": "userTest",
    "token": "tokenTest"
}


class MetaEnum(EnumMeta):

    def __contains__(self, other):
        try:
            self(other)
        except ValueError:
            return False
        else:
            return True

class Faction(str, Enum, metaclass=MetaEnum):
    COSMIC = 'COSMIC'
    VOID = 'VOID'
    GALACTIC = 'GALACTIC'
    QUANTUM = 'QUANTUM'
    DOMINION = 'DOMINION'
    ASTRO = 'ASTRO'
    CORSAIRS = 'CORSAIRS'
    OBSIDIAN = 'OBSIDIAN'
    AEGIS = 'AEGIS'
    UNITED = 'UNITED'
    SOLITARY = 'SOLITARY'
    COBALT = 'COBALT'
    OMEGA = 'OMEGA'
    ECHO = 'ECHO'
    LORDS = 'LORDS'
    CULT = 'CULT'
    ANCIENTS = 'ANCIENTS'
    SHADOW = 'SHADOW'
    ETHEREAL = 'ETHEREAL'

"""
Contract necessities
"""

class Agent:
    def __init__(self, jsonInfo):
        self.accountId = jsonInfo['accountId']
        self.symbol = jsonInfo['symbol']
        self.headquarters = jsonInfo['headquarters']
        self.credits = jsonInfo['credits']
        self.startingFaction = jsonInfo['startingFaction']

class DeliverInfo:
    def __init__(self, jsonInfo):
        self.tradeSymbol = jsonInfo['tradeSymbol']
        self.destinationSymbol = jsonInfo['destinationSymbol']
        self.unitsRequired = jsonInfo['unitsRequired']
        self.unitsFulfilled = jsonInfo['unitsFulfilled']

class ContractTerms:
    def __init__(self, jsonInfo):
        self.deadline = jsonInfo['deadline']
        self.payment = (jsonInfo['payment']['onAccepted'], jsonInfo['payment']['onFulfilled'])
        self.deliver = []
        for i in range(len(jsonInfo['deliver'])):
            self.deliver.append(DeliverInfo(jsonInfo['deliver'][i]))

class Contract:
    def __init__(self, jsonInfo):
        self.id = jsonInfo['id']
        self.factionSymbol = jsonInfo['factionSymbol']
        self.type = jsonInfo['type']
        self.terms = ContractTerms(jsonInfo['terms'])
        #self.startingFaction = jsonInfo['startingFaction']
        self.accepted = jsonInfo['accepted']
        self.fulfilled = jsonInfo['fulfilled']
        self.expiration = jsonInfo['expiration']
        self.deadlineToAccept = jsonInfo['deadlineToAccept']

"""
Fleet necessities :
"""

class Coord:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.type = jsonInfo['type']
        self.systemSymbol = jsonInfo['systemSymbol']
        self.x = jsonInfo['x']
        self.y = jsonInfo['y']

class Requirement:
    def __init__(self, jsonInfo):
        if 'power' in jsonInfo:
            self.power = jsonInfo['power']
        else :
            self.power = 0

        if 'crew' in jsonInfo:
            self.crew = jsonInfo['crew']
        else :
            self.crew = 0

        if 'slots' in jsonInfo:
            self.slots = jsonInfo['slots']
        else :
            self.slots = 0

class Route:
    def __init__(self, jsonInfo):
        self.departure = Coord(jsonInfo['departure'])
        self.destination = Coord(jsonInfo['destination'])
        self.arrival = jsonInfo['arrival']
        self.departureTime = jsonInfo['departureTime']

class Nav:
    def __init__(self, jsonInfo):
        self.systemSymbol = jsonInfo['systemSymbol']
        self.waypointSymbol = jsonInfo['waypointSymbol']
        self.route = Route(jsonInfo['route'])
        self.status = jsonInfo['status']
        self.flightMode = jsonInfo['flightMode']

class Crew:
    def __init__(self, jsonInfo):
        self.current = jsonInfo['current']
        self.capacity = jsonInfo['capacity']
        self.required = jsonInfo['required']
        self.rotation = jsonInfo['rotation']
        self.morale = jsonInfo['morale']
        self.wages = jsonInfo['wages']

class FuelConsumed:
    def __init__(self, jsonInfo):
        self.amount = jsonInfo['amount']
        self.timestamp = jsonInfo['timestamp']

class Fuel:
    def __init__(self, jsonInfo):
        self.current = jsonInfo['current']
        self.capacity = jsonInfo['capacity']

        if 'consumed' in jsonInfo:
            self.consumed = FuelConsumed(jsonInfo['consumed'])
        else :
            self.consumed = None

class Frame:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.name = jsonInfo['name']
        self.description = jsonInfo['description']
        self.moduleSlots = jsonInfo['moduleSlots']
        self.mountingPoints = jsonInfo['mountingPoints']
        self.fuelCapacity = jsonInfo['fuelCapacity']

        if 'condition' in jsonInfo:
            self.condition = jsonInfo['condition']
        else :
            self.condition = 100 # Condition is a range of 0 to 100 where 0 is completely worn out and 100 is brand new.

        self.requirements = Requirement(jsonInfo['requirements'])

class Reactor:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.name = jsonInfo['name']
        self.description = jsonInfo['description']

        if 'condition' in jsonInfo:
            self.condition = jsonInfo['condition']
        else :
            self.condition = 100 # Condition is a range of 0 to 100 where 0 is completely worn out and 100 is brand new.

        self.powerOutput = jsonInfo['powerOutput']
        self.requirements = Requirement(jsonInfo['requirements'])

class Engine:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.name = jsonInfo['name']
        self.description = jsonInfo['description']

        if 'condition' in jsonInfo:
            self.condition = jsonInfo['condition']
        else :
            self.condition = 100 # Condition is a range of 0 to 100 where 0 is completely worn out and 100 is brand new.
        
        self.speed = jsonInfo['speed']
        self.requirements = Requirement(jsonInfo['requirements'])

class Module:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.name = jsonInfo['name']
        self.description = jsonInfo['description']

        if 'capacity' in jsonInfo:
            self.capacity = jsonInfo['capacity']
        else :
            self.capacity = 0

        if 'range' in jsonInfo:
            self.range = jsonInfo['range']
        else :
            self.range = 0
        
        self.requirements = Requirement(jsonInfo['requirements'])

class Mount:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.name = jsonInfo['name']
        
        if 'description' in jsonInfo:
            self.description = jsonInfo['description']
        else :
            self.description = "No description"

        if 'strength' in jsonInfo:
            self.strength = jsonInfo['strength']
        else :
            self.strength = 0

        if 'deposits' in jsonInfo:
            for i in range(len(jsonInfo['deposits'])):
                self.deposits.append(jsonInfo['deposits'][i])
        else :
            self.deposits = [] # Mounts that have this value denote what goods can be produced from using the mount.

        self.requirements = Requirement(jsonInfo['requirements'])

class Registration:
    def __init__(self, jsonInfo):
        self.name = jsonInfo['name']
        self.factionSymbol = jsonInfo['factionSymbol']
        self.role = jsonInfo['role']

class Item:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.name = jsonInfo['name']
        self.description = jsonInfo['description']
        self.units = jsonInfo['units']

class Cargo:
    def __init__(self, jsonInfo):
        self.capacity = jsonInfo['capacity']
        self.units = jsonInfo['units']
        self.inventory = []
        for i in range(len(jsonInfo['inventory'])):
            self.inventory.append(Item(jsonInfo['inventory'][i]))

class Ship:
    def __init__(self, jsonInfo):
        self.symbol = jsonInfo['symbol']
        self.nav = Nav(jsonInfo['nav'])
        self.crew = Crew(jsonInfo['crew'])
        self.fuel = Fuel(jsonInfo['fuel'])
        self.frame = Frame(jsonInfo['frame'])
        self.reactor = Reactor(jsonInfo['reactor'])
        self.engine = Engine(jsonInfo['engine'])

        self.modules = []
        for i in range(len(jsonInfo['modules'])):
            self.modules.append(Module(jsonInfo['modules'][i]))

        self.mounts = []
        for i in range(len(jsonInfo['mounts'])):
            self.mounts.append(Module(jsonInfo['mounts'][i]))

        self.registration = Registration(jsonInfo['registration'])
        self.cargo = Cargo(jsonInfo['cargo'])
        

"""
Systems necessities :
"""


