from defs import *
from role import Role

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Distributor(Role):
    collectionPriority = {
        STRUCTURE_CONTAINER: 0,
        STRUCTURE_STORAGE: 1
    }
    depositPriority = {
        STRUCTURE_EXTENSION: 0,
        STRUCTURE_SPAWN: 1,
        STRUCTURE_TOWER: 2,
        STRUCTURE_STORAGE: 3,
        STRUCTURE_CONTAINER: 4
    }
    def __init__(self):
        super().__init__()

    def initalize(self, creep: Creep):
        creep.memory.role = "distributor"
        creep.memory.curAction = "charging"

    def run(self, creep: Creep):
        if not creep.memory.role or not creep.memory.curAction:
            self.initalize(creep)
        
        if creep.memory.curAction == "charging" and creep.store.getFreeCapacity() == 0:
            creep.memory.curAction = "distributing"
        elif creep.memory.curAction == "distributing" and creep.store.getUsedCapacity() == 0:
            creep.memory.curAction = "charging"
 
        if creep.memory.curAction == "charging":
            self.charge(creep)
        elif creep.memory.curAction == "distributing":
            self.distribute(creep)
    

    def charge(self, creep: Creep):
        closest = self.getClosestContainer(creep)
        err = creep.withdraw(closest, RESOURCE_ENERGY)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(closest, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ff00', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_NOT_ENOUGH_ENERGY:
                creep.say("con empty")
            else:
                creep.say("w err: " + err)

    def distribute(self, creep: Creep):
        deposit = self.getBestDeposit(creep)
        if not deposit:
            return

        err = creep.transfer(deposit, RESOURCE_ENERGY)

        if err != OK:
            # We have to combine these errors because ERR_NOT_IN_RANGE has higher 'precedence'
            # basically if a container is full and you're out of range you'll get back a ERR_NOT_IN_RANGE
            # TODO: Make this logic possible to hit. Because self.getBestDeposit() always either returns something
            # with a not full inventory or None we'll never use this, but i'd like to make it so the creeps
            # close in on one of the containers to save time
            if err == ERR_NOT_IN_RANGE or err == ERR_FULL:
                if deposit.store.getFreeCapacity() == 0:
                    bufferDist = 3 # The distance creeps should stay until they can perform their action
                    
                    # If we're already too close, back off
                    if creep.pos.getRangeTo(deposit) < bufferDist:
                        creep.say("Fleeing: " + creep.pos.getRangeTo(deposit))
                        depositPos = {'pos': deposit.pos, 'range': bufferDist}
                        path = PathFinder.search(creep.pos, depositPos, {'flee': True})
                        creep.moveByPath(path.path)
                    # If we're out of range than get as close as bufferDist allows
                    else:
                        creep.moveTo(deposit, {'range': bufferDist, 'visualizePathStyle': {'fill': 'transparent','stroke': '#ff0000', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
                else:
                    creep.moveTo(deposit, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ff0000', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            else:
                creep.say("t err: " + err)
        
    def getClosestContainer(self, creep: Creep):
        structures = [struct for struct in creep.room.find(FIND_STRUCTURES) if  
                    Object.keys(Distributor.collectionPriority).includes(struct.structureType) and struct.store.getUsedCapacity() >= creep.store.getFreeCapacity()]
        

        if len(structures) == 0:
            return None
        # Get the highest priority structure type
        # Would use min() but the javascript translation doesn't seem to use the key argument
        highestPriorityType = sorted(structures, key=self.prioritizeCollection)[0].structureType
        # Filter out low priority structures
        structures = [struct for struct in structures if struct.structureType == highestPriorityType]
        harvesterContainers = [struct for struct in structures if len(struct.pos.findInRange(FIND_SOURCES, 4)) > 0]

        # If there are containers near harvesters that are good we prioritize those
        # even if they're further away. This prevents creeps from repeatedly depositing and withdrawing
        # in the same container when they could be hauling from harvester containers
        if len(harvesterContainers) > 0:
            return creep.pos.findClosestByPath(harvesterContainers)
        else:
            return creep.pos.findClosestByPath(structures)
    
    def prioritizeCollection(self, structure: Structure):
        if Object.keys(Distributor.collectionPriority).includes(structure.structureType):
            return Distributor.collectionPriority[structure.structureType]
        else:
            return float('inf')


    def getBestDeposit(self, creep: Creep):
        deposits = [struct for struct in creep.room.find(FIND_STRUCTURES) if 
                    Object.keys(Distributor.depositPriority).includes(struct.structureType) and struct.store.getFreeCapacity(RESOURCE_ENERGY) > 0]
        print("A: "+ deposits)
        deposits = [struct for struct in deposits if struct.structureType != STRUCTURE_CONTAINER or len(struct.pos.findInRange(FIND_SOURCES, 4)) == 0]
        print("B: " + deposits)
        if len(deposits) == 0:
            return None

        # Get the highest priority structure type
        # Would use min() but the javascript translation doesn't seem to use the key argument
        highestPriorityType = sorted(deposits, key=self.prioritizeDeposit)[0].structureType
        # Filter out low priority structures
        deposits = [struct for struct in deposits if struct.structureType == highestPriorityType]
        print("C: " + deposits)
        return creep.pos.findClosestByPath(deposits)


        return deposits[0]
    
    def prioritizeDeposit(self, structure: Structure):
        if Object.keys(Distributor.depositPriority).includes(structure.structureType):
            return Distributor.depositPriority[structure.structureType]
        else:
            return float('inf')


