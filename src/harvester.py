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

class Harvester(Role):
    def __init__(self):
        super().__init__()

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
        minUsed = [source for source in Object.keys(useCounts) if useCounts[source] == minValue]
        creep.memory.dest = minUsed[0] #TODO: Instead of picking the first one pick the closest one
        return True

    def run(self, creep: Creep):
        if not creep.memory.dest or not creep.memory.role or not creep.memory.curAction:
            # Break early if failed to initalize
            if not self.initalize(creep):
                creep.say("init fail")
                return
        if creep.memory.curAction == "harvesting":
            self.harvest(creep)
        elif creep.memory.curAction == "depositing":
            self.deposit(creep)

    def harvest(self, creep: Creep):
        source = Game.getObjectById(creep.memory.dest)
        err = creep.harvest(source)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(source, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ff0000', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_NOT_ENOUGH_RESOURCES:
                pass
            else:
                creep.say("h err: " + err)

        if creep.store.getFreeCapacity() == 0:
            creep.memory.curAction = "depositing"
            self.deposit(creep)


    def deposit(self, creep: Creep):
        container = self.getClosestContainer(creep.pos)
        err = creep.transfer(container, RESOURCE_ENERGY)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(container, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ff0000', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_FULL:
                pass
            elif err == ERR_NOT_ENOUGH_RESOURCES:
                pass
            else:
                creep.say("t err: " + err)
            
        if creep.store.getUsedCapacity() == 0:
            creep.memory.curAction = "harvesting"
            self.harvest(creep)

    def getOtherCreepDests(self):
        """
        Gets a list of object ids with which all creeps intend to interact with (creep.memory.dest specifically)
        :rtype: list
        :return: list of destination object IDs for all creeps
        """
        return [creep.memory.dest for creep in Object.values(Game.creeps) if creep.memory.role == "harvester"]
    
    def getClosestContainer(self, pos:RoomPosition):
        return pos.findClosestByPath(FIND_STRUCTURES, {filter: lambda struct: struct.structureType == STRUCTURE_CONTAINER})
