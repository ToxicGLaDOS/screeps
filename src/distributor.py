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
        STRUCTURE_SPAWN: 0,
        STRUCTURE_TOWER: 2, # only for more than half empty towers
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

        err = creep.pickup(target)
        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ff00', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_INVALID_TARGET:
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
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#0000ff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            else:
                creep.say("t err: " + err)
        # If there is no error we choose a new target
        # Either we gave it all our energy so we're empty
        # or we still have energy and it's full
        # in either case we want to choose a new target
        # This is important because towers that are constantly shooting will never
        # have their energy be full to hit the condition to switch targets
        # that most other containers do at the top of this function
        else:
            self.chooseTarget(creep)
        
    def getClosestContainer(self, creep: Creep):
        droppedResources = [resource for resource in creep.room.find(FIND_DROPPED_RESOURCES) if resource.resourceType == RESOURCE_ENERGY]
        if len(droppedResources) > 0:
            return creep.pos.findClosestByPath(droppedResources)
        else:
            structures = [struct for room in Object.values(Game.rooms) for struct in room.find(FIND_STRUCTURES) if
                        struct.structureType in Distributor.collectionPriority and
                        (self.getStructureFutureEnergy(struct) >= creep.store.getFreeCapacity() or self.getStructureFutureEnergy(struct) >= struct.store.getCapacity())]
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
                return self.findClosestByPath(creep, harvesterContainers)
            else:
                return self.findClosestByPath(creep, structures)

        def prioritizeCollection(self, structure: Structure):
            if structure.structureType in Distributor.collectionPriority:
                return Distributor.collectionPriority[structure.structureType]
            else:
                return float('inf')


    def getBestDeposit(self, creep: Creep):
        deposits = [struct for room in Object.values(Game.rooms) for struct in room.find(FIND_STRUCTURES) if
                    struct.structureType in Distributor.depositPriority and self.getStructureFutureEnergy(struct) < struct.store.getCapacity(RESOURCE_ENERGY)]
        deposits = [struct for struct in deposits if struct.structureType != STRUCTURE_CONTAINER or len(struct.pos.findInRange(FIND_SOURCES, 4)) == 0]
        if len(deposits) == 0:
            return None
        # Get the highest priority structure type
        # Would use min() but the javascript translation doesn't seem to use the key argument
        highestPriorityType = sorted(deposits, key=self.prioritizeDeposit)[0].structureType
        # Account for some priorities being equal
        highestPriorityTypes = [structType for structType in Object.keys(Distributor.depositPriority) if Distributor.depositPriority[structType] == Distributor.depositPriority[highestPriorityType]]
        # Filter out low priority structures
        # TODO: Make sure other creeps aren't going to fill it up like we do when checking for container to withdraw from
        deposits = [struct for struct in deposits if struct.structureType in highestPriorityTypes]
        return self.findClosestByPath(creep, deposits)


        return deposits[0]
    
    def prioritizeDeposit(self, structure: Structure):
        if structure.structureType == STRUCTURE_TOWER:
            if structure.store.getUsedCapacity(RESOURCE_ENERGY) < structure.store.getCapacity(RESOURCE_ENERGY) / 2:
                return Distributor.depositPriority[structure.structureType]
            else:
                return Distributor.depositPriority[STRUCTURE_STORAGE] + 1
        if structure.structureType in Distributor.depositPriority:
            return Distributor.depositPriority[structure.structureType]
        else:
            return float('inf')


