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



class Upgrader(Role):
    collectionPriority = {
        STRUCTURE_CONTAINER: 0,
        STRUCTURE_STORAGE: 1
    }
    def __init__(self):
        pass

    def getBodyParts(self, spawner: StructureSpawn):
        base = [MOVE, CARRY, WORK]
        cost = sum([BODYPART_COST[part] for part in base])
        nextPart = MOVE
        # Cycle through adding MOVE -> CARRY -> WORK until too expensive
        while cost <= spawner.room.energyCapacityAvailable:
            if nextPart == MOVE:
                base.append(MOVE)
                cost += BODYPART_COST[MOVE]
                nextPart = CARRY
            elif nextPart == CARRY:
                base.append(CARRY)
                cost += BODYPART_COST[CARRY]
                nextPart = WORK
            elif nextPart == WORK:
                base.append(WORK)
                cost += BODYPART_COST[WORK]
                nextPart = MOVE
        base.pop(len(base)-1)
        return base


    def initalize(self, creep: Creep):
        creep.memory.role = "upgrader"
        creep.memory.curAction = "charging"

    def run(self, creep: Creep):
        if not creep.memory.role or not creep.memory.curAction:
            self.initalize(creep)
        
        if creep.memory.curAction == "charging" and creep.store.getFreeCapacity() == 0:
            creep.memory.curAction = "upgrading"
            self.chooseTarget(creep)
        elif creep.memory.curAction == "upgrading" and creep.store.getUsedCapacity() == 0:
            creep.memory.curAction = "charging"
            self.chooseTarget(creep)
 
        if creep.memory.curAction == "charging":
            self.charge(creep)
        elif creep.memory.curAction == "upgrading":
            self.upgrade(creep)
    
    def chooseTarget(self, creep: Creep):
        if creep.memory.curAction == "charging":
            target = self.getClosestContainer(creep)
            creep.memory.dest = target.id if target != None else None
        elif creep.memory.curAction == "upgrading":
            roomControllers = [struct for struct in creep.room.find(FIND_STRUCTURES) if struct.structureType == STRUCTURE_CONTROLLER]
            target = roomControllers[0] if len(roomControllers) > 0 else None
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

    def upgrade(self, creep: Creep):
        target = Game.getObjectById(creep.memory.dest)
        if not target:
            creep.say("No target")
            return

        err = creep.upgradeController(target)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ff00ff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            else:
                creep.say("u err: " + err)
        
    def getClosestContainer(self, creep: Creep):
        structures = [struct for struct in creep.room.find(FIND_STRUCTURES) if  
                    struct.structureType in Upgrader.collectionPriority and self.getContainerFutureEnergy(struct) >= creep.store.getFreeCapacity()]
        

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
        if structure.structureType in Upgrader.collectionPriority:
            return Upgrader.collectionPriority[structure.structureType]
        else:
            return float('inf')
