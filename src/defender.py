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


class Defender(Role):
    def __init__(self):
        pass

    def getBodyParts(self, spawner):
        return [MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, TOUGH, TOUGH, TOUGH]

    def initalize(self, creep):
        creep.memory.role = "defender"
        creep.memory.curAction = "patrolling"

    def run(self, creep):
        if not creep.memory.role or not creep.memory.curAction:
            self.initalize(creep)
        
        hostiles = [hostile for room in Object.values(Game.rooms) for hostile in room.find(FIND_HOSTILE_CREEPS)]

        if len(hostiles) > 0:
            creep.memory.curAction = "attacking"
        else:
            creep.memory.curAction = "patrolling"
        

        if creep.memory.curAction == "attacking":
            target = self.findClosestByPath(creep, hostiles)
            creep.memory.dest = target.id
            err = creep.attack(target)

            if err != OK:
                if err == ERR_NOT_IN_RANGE:
                    creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#ff0000', 'lineStyle': None, 'strokeWidth': .15, 'opacity': 1}})
                else:
                    creep.say('a err: ' + err)
        elif creep.memory.curAction == "patrolling":
            target = [flag for room in Object.values(Game.rooms) for flag in room.find(FIND_FLAGS) if flag.name == "DefenderPosition"][0]
            creep.moveTo(target, {'visualizePathStyle': {'fill': 'transparent','stroke': '#00ff00', 'lineStyle': None, 'strokeWidth': .15, 'opacity': 1}})
        
        

