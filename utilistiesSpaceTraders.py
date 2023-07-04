from enum import EnumMeta, Enum

token = ""
https = "https://api.spacetraders.io/v2"
myAgentURL = https + "/my/agent"
registerNewAgentURL = https + "/register"
contractURL = https + "/my/contracts"

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

#datas
dataRegister = {
    "faction": "",
    "symbol": ""
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
        for i in len(jsonInfo['deliver']):
            self.deliver.append(DeliverInfo(jsonInfo['deliver'][i]))

class Contract:
    def __init__(self, jsonInfo):
        self.id = jsonInfo['id']
        self.factionSymbol = jsonInfo['factionSymbol']
        self.type = jsonInfo['type']
        self.terms = ContractTerms(jsonInfo['terms'])
        self.startingFaction = jsonInfo['startingFaction']
        self.accepted = jsonInfo['accepted']
        self.fulfilled = jsonInfo['fulfilled']
        self.expiration = jsonInfo['expiration']
        self.deadlineToAccept = jsonInfo['deadlineToAccept']
