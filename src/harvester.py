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

class Harvester(Role):
    def __init__(self):
        super().__init__()
    
    def getBodyParts(self, spawner: StructureSpawn):
        base = [MOVE, CARRY, WORK]
        cost = sum([BODYPART_COST[part] for part in base])
        extraWorks = math.floor(spawner.room.energyCapacityAvailable - cost / BODYPART_COST[WORK])
        # One creep is enough to mine out a source with enough work parts
        extraWorks = min(extraWorks, 9)
        for x in range(extraWorks):
            base.append(WORK)
        return base

    def initalize(self, creep: Creep):
        creep.memory.role = "harvester"
        creep.memory.curAction = "harvesting"
        creepDests = self.getOtherCreepDests()
        sources = creep.room.find(FIND_SOURCES)
        if not sources:
            return False

        # Use a list comp in a dict comp here because list.count() isn't a method in javascript :(
        useCounts = {source.id:len([dest for dest in creepDests if dest == source.id]) for source in sources}
        minValue = min(Object.values(useCounts))
        minUsed = [Game.getObjectById(sourceID) for sourceID in Object.keys(useCounts) if useCounts[sourceID] == minValue]
        creeps = [creep for creep in Object.values(Game.creeps)]
        soonestDeaths = sorted(minUsed, key=lambda source: min([creep.ticksToLive for creep in creeps if creep.memory.dest == source.id]))
        # We ignore creeps because we don't want creeps to be the reason a location doesn't get picked (they'll move soon enough hopefully)
        target = soonestDeaths[0]
        creep.memory.dest = target.id if target != None else None
        return True

    def run(self, creep: Creep):
        if not creep.memory.dest or not creep.memory.role or not creep.memory.curAction:
            # Break early if failed to initalize
            if not self.initalize(creep):
                creep.say("init fail")
                return

        if creep.memory.curAction == "harvesting" and creep.store.getFreeCapacity() == 0:
            creep.memory.curAction = "depositing"
        elif creep.memory.curAction == "depositing" and creep.store.getUsedCapacity() == 0:
            creep.memory.curAction = "harvesting"

        
        if creep.memory.curAction == "harvesting":
            self.harvest(creep)
        elif creep.memory.curAction == "depositing":
            self.deposit(creep)

    def harvest(self, creep: Creep):
        droppedResources = creep.pos.findInRange(FIND_DROPPED_RESOURCES, 0)
        if len(droppedResources) > 0:
            err = creep.pickup(droppedResources[0])

            if err != OK:
                creep.say("p err: " + err)

        else:
            source = Game.getObjectById(creep.memory.dest)
            err = creep.harvest(source)

            if err != OK:
                if err == ERR_NOT_IN_RANGE:
                    creep.moveTo(source, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ffffff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
                elif err == ERR_NOT_ENOUGH_RESOURCES:
                    creep.moveTo(source, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ffffff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
                else:
                    creep.say("h err: " + err)


    def deposit(self, creep: Creep):
        container = self.getClosestContainer(creep.pos)

        # Fallback to putting into spawn
        if not container:
            container = Object.values(Game.spawns)[0]
        err = creep.transfer(container, RESOURCE_ENERGY)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(container, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ffffff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_FULL:
                creep.memory.curAction = "harvesting"
            elif err == ERR_NOT_ENOUGH_RESOURCES:
                pass
            else:
                creep.say("t err: " + err)
            
    def getOtherCreepDests(self):
        """
        Gets a list of object ids with which all creeps intend to interact with (creep.memory.dest specifically)
        :rtype: list
        :return: list of destination object IDs for all creeps
        """
        return [creep.memory.dest for creep in Object.values(Game.creeps) if creep.memory.role == "harvester"]
    
    def getClosestContainer(self, pos:RoomPosition):
        return pos.findClosestByPath(FIND_STRUCTURES, {'filter': {'structureType': STRUCTURE_CONTAINER}})
