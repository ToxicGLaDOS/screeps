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



class Builder(Role):
    priority = {
        STRUCTURE_POWER_SPAWN: -2,
        STRUCTURE_SPAWN:       -1,
        STRUCTURE_CONTAINER:    0,
        STRUCTURE_EXTENSION:    1,
        STRUCTURE_RAMPART:      2,
        STRUCTURE_STORAGE:      3,
        STRUCTURE_TOWER:        4,
        STRUCTURE_ROAD:         5,
        STRUCTURE_WALL:         6,
    }
    def __init__(self):
        super().__init__()

    def initalize(self, creep: Creep):
        creep.memory.role = "builder"
        creep.memory.curAction = "charging"
        
    def findBuildSite(self, creep: Creep):
        constructionSites = creep.room.find(FIND_CONSTRUCTION_SITES)
        constructionSites = sorted(constructionSites, key=self.prioritize)
        if len(constructionSites) > 0:
            creep.memory.dest = constructionSites[0].id
        else:
            creep.memory.dest = None

    def prioritize(self, site:ConstructionSite):
        if site.structureType in Builder.priority:
            return Builder.priority[site.structureType]
        else:
            return float('inf')

    def run(self, creep: Creep):
        if not creep.memory.role or not creep.memory.curAction:
            if not self.initalize(creep):
                creep.say("init fail")
                return

        if creep.memory.curAction == "building":
            self.build(creep)
        elif creep.memory.curAction == "charging":
            self.charge(creep)
    
    def build(self, creep: Creep):
        target = Game.getObjectById(creep.memory.dest)

        # target could be None here because the site was finished building
        # or because there are no build sites left
        # or because we just spawned
        if target == None:
            self.findBuildSite(creep)
            target = Game.getObjectById(creep.memory.dest)
            # if still None then there's no sites left
            if target == None:
                creep.say("no site")
                return

        err = creep.build(target)
        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ff00', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_NOT_ENOUGH_RESOURCES:
                creep.memory.curAction = "charging"
            else:
                creep.say("b err: " + err) 


    def charge(self, creep: Creep):
        target = self.getClosestContainer(creep.pos)
        console.log(target)
        err = creep.withdraw(target, RESOURCE_ENERGY)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ff00', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            elif err == ERR_FULL:
                creep.memory.curAction = "building"
            elif err == ERR_NOT_ENOUGH_ENERGY:
                creep.say("con empty")
            else:
                creep.say("w err: " + err) 

    def getClosestContainer(self, pos:RoomPosition):
        return pos.findClosestByPath(FIND_STRUCTURES, {'filter': lambda struct: struct.structureType == STRUCTURE_CONTAINER and struct.store.getUsedCapacity() > 0})


