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


class Reserver(Role):
    def __init__(self, homeRoom, remoteRoom):
        self.homeRoom = homeRoom
        self.remoteRoom = remoteRoom

    def getBodyParts(self, spawner: StructureSpawn):
        base = [MOVE, CLAIM]
        cost = sum([BODYPART_COST[part] for part in base])
        additionalClaims = math.floor(spawner.room.energyCapacityAvailable / BODYPART_COST[CLAIM])
        for x in range(additionalClaims):
            base.append(CLAIM)

        return base

    def initalize(self, creep: Creep):
        creep.memory.role = "reserver"
        creep.memory.curAction = "reserving"
        self.chooseTarget(creep)

    def run(self, creep: Creep):
        if not creep.memory.role or not creep.memory.curAction:
            self.initalize(creep)
        
        if creep.memory.curAction == "reserving":
            self.reserve(creep)

    def chooseTarget(self, creep: Creep):
        remoteRoom = Game.rooms[self.remoteRoom]
        creep.memory.dest = remoteRoom.controller.id

    def reserve(self, creep: Creep):
        target = Game.getObjectById(creep.memory.dest)

        err = creep.reserveController(target)

        if err != OK:
            if err == ERR_NOT_IN_RANGE:
                creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ffff', 'lineStyle': 'dashed', 'strokeWidth': .15, 'opacity': .1}})
            else:
                creep.say("c err: " + err)