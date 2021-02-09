from defs import *
from role import Role
import random

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class RemoteHarvester(Role):
    def __init__(self, homeRoom, remoteRoom):
        self.homeRoom = homeRoom
        self.remoteRoom = remoteRoom

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
        creep.memory.role = "remoteHarvester"
        creep.memory.curAction = "harvesting"
        self.chooseTarget(creep)

    def run(self, creep: Creep):
        if not creep.memory.role or not creep.memory.curAction or not creep.memory.dest:
            self.initalize(creep)
        
        if creep.memory.curAction == "harvesting" and creep.store.getFreeCapacity() == 0:
            creep.memory.curAction = "depositing"
            self.chooseTarget(creep)
        elif creep.memory.curAction == "depositing" and creep.store.getUsedCapacity() == 0:
            creep.memory.curAction = "harvesting"
            self.chooseTarget(creep)
 
        if creep.memory.curAction == "harvesting":
            self.harvest(creep)
        elif creep.memory.curAction == "depositing":
            self.deposit(creep)
    
    def chooseTarget(self, creep: Creep):
        if creep.memory.curAction == "harvesting":
            target = self.getBestSource(creep)
            creep.memory.dest = target.id if target != None else None
        elif creep.memory.curAction == "depositing":
            target = self.getClosestContainer(creep)
            creep.memory.dest = target.id if target != None else None
    

    def harvest(self, creep: Creep):
        target = Game.getObjectById(creep.memory.dest)
        # Target could be None here because we don't have vision on the room
        if not target:
            self.chooseTarget(creep)
            target = Game.getObjectById(creep.memory.dest)
            roomExitDir = Game.map.findExit(creep.room, self.remoteRoom)
            roomExit = creep.pos.findClosestByRange(roomExitDir)
            creep.moveTo(roomExit)
            creep.say("No target")
            return

        err = creep.harvest(target)

        if err != OK:
            if err == ERR_NOT_IN_RANGE or err == ERR_NOT_ENOUGH_RESOURCES:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ffffff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            else:
                creep.say("h err: " + err)
        else:
            if creep.memory.totalHarvested == None:
                creep.memory.totalHarvested = 0
            creep.memory.totalHarvested += min(HARVEST_POWER*len(part for part in creep.body if part == WORK), creep.store.getFreeCapacity())

    def deposit(self, creep: Creep):
        target = Game.getObjectById(creep.memory.dest)
        if not target:
            creep.say("No target")
            return

        err = creep.transfer(target, RESOURCE_ENERGY)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ffffff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            else:
                creep.say("t err: " + err)
        
    def getClosestContainer(self, creep: Creep):
        homeRoom = Game.rooms[self.homeRoom]
        structures = [struct for struct in homeRoom.find(FIND_STRUCTURES) if
                    struct.structureType in [STRUCTURE_STORAGE] and self.getStructureFutureEnergy(struct) + creep.store.getUsedCapacity() <= struct.store.getCapacity()]
        return structures[0] if structures != None else None
        #nonHarvesterContainers = [struct for struct in structures if len(struct.pos.findInRange(FIND_SOURCES, 4)) > 0]
        #if len(structures) == 0:
        #    return None

        #if len(nonHarvesterContainers) > 0:
        #    return creep.pos.findClosestByPath(nonHarvesterContainers)
        #else:
        #    return None
    
    def getBestSource(self, creep: Creep):
        remoteRoom = Game.rooms[self.remoteRoom]
        if remoteRoom == None:
            return None
        creepDests = [creep.memory.dest for creep in Object.values(Game.creeps)]
        sources = remoteRoom.find(FIND_SOURCES)
        target = sources[random.randint(0, len(sources)-1)]
        if not sources:
            return None

        # Use a list comp in a dict comp here because list.count() isn't a method in javascript :(
        useCounts = {source.id:len([dest for dest in creepDests if dest == source.id]) for source in sources}
        minValue = min(Object.values(useCounts))
        minUsed = [Game.getObjectById(sourceID) for sourceID in Object.keys(useCounts) if useCounts[sourceID] == minValue]
        target = self.findClosestByPath(creep, minUsed)
        return target