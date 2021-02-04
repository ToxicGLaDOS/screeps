from defs import *
from role import Role
import math

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
    
    def getBodyParts(self, spawner: StructureSpawn):
        numCarrys = math.floor(spawner.room.energyCapacityAvailable / (BODYPART_COST[MOVE]/ 2 +  BODYPART_COST[CARRY]))
        numMoves = math.ceil(numCarrys / 2) # Using ceil means we'll get moves before carrys
        body = []
        for x in range(numCarrys):
            body.append(CARRY)
        for x in range(numMoves):
            body.append(MOVE)
        
        # Sanity check
        cost = sum([BODYPART_COST[part] for part in body])
        if cost > spawner.room.energyCapacityAvailable:
            print("Can't spawn distributor. Math is wrong :(")
        
        return body

    def initalize(self, creep: Creep):
        creep.memory.role = "distributor"
        creep.memory.curAction = "charging"
        self.chooseTarget(creep)

    def run(self, creep: Creep):
        if not creep.memory.role or not creep.memory.curAction:
            self.initalize(creep)
        
        if creep.memory.curAction == "charging" and creep.store.getFreeCapacity() == 0:
            creep.memory.curAction = "distributing"
            self.chooseTarget(creep)
        elif creep.memory.curAction == "distributing" and creep.store.getUsedCapacity() == 0:
            creep.memory.curAction = "charging"
            self.chooseTarget(creep)
 
        if creep.memory.curAction == "charging":
            self.charge(creep)
        elif creep.memory.curAction == "distributing":
            self.distribute(creep)
    
    def chooseTarget(self, creep: Creep):
        if creep.memory.curAction == "charging":
            target = self.getClosestContainer(creep)
            creep.memory.dest = target.id if target != None else None
        elif creep.memory.curAction == "distributing":
            target = self.getBestDeposit(creep)
            creep.memory.dest = target.id if target != None else None

    def charge(self, creep: Creep):
        target = Game.getObjectById(creep.memory.dest)
        # Target could be None here because it was destroyed
        if not target:
            self.chooseTarget(creep)
            target = Game.getObjectById(creep.memory.dest)
            # This can happen if the creep is surrounded and can't path to anything
            # or if there really are no valid targets
            if not target:
                creep.say("No target")
                return

        err = creep.withdraw(target, RESOURCE_ENERGY)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ff00', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_NOT_ENOUGH_ENERGY:
                creep.say("con empty")
            else:
                creep.say("w err: " + err)

    def distribute(self, creep: Creep):
        target = Game.getObjectById(creep.memory.dest)
        # Target could be None here because it was destroyed
        if not target or target.store.getFreeCapacity(RESOURCE_ENERGY) == 0:
            self.chooseTarget(creep)
            target = Game.getObjectById(creep.memory.dest)
            # This can happen if the creep is surrounded and can't path to anything
            # or if there really are no valid targets
            if not target:
                creep.say("No target")
                return

        err = creep.transfer(target, RESOURCE_ENERGY)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ff00', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            else:
                creep.say("t err: " + err)
        
    def getClosestContainer(self, creep: Creep):
        structures = [struct for struct in creep.room.find(FIND_STRUCTURES) if  
                    Object.keys(Distributor.collectionPriority).includes(struct.structureType) and self.getContainerFutureEnergy(struct) >= creep.store.getFreeCapacity()]
        

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
        deposits = [struct for struct in deposits if struct.structureType != STRUCTURE_CONTAINER or len(struct.pos.findInRange(FIND_SOURCES, 4)) == 0]
        if len(deposits) == 0:
            return None

        # Get the highest priority structure type
        # Would use min() but the javascript translation doesn't seem to use the key argument
        highestPriorityType = sorted(deposits, key=self.prioritizeDeposit)[0].structureType
        # Filter out low priority structures
        deposits = [struct for struct in deposits if struct.structureType == highestPriorityType]
        return creep.pos.findClosestByPath(deposits)


        return deposits[0]
    
    def prioritizeDeposit(self, structure: Structure):
        if Object.keys(Distributor.depositPriority).includes(structure.structureType):
            return Distributor.depositPriority[structure.structureType]
        else:
            return float('inf')


