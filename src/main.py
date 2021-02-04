from harvester import Harvester
from builder import Builder
from distributor import Distributor
from upgrader import Upgrader
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *

# These are currently required for Transcrypt in order to use the following names in JavaScript.
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def main():
    """
    Main game logic loop.
    """

    roles = {
        'harvester': Harvester(),
        'builder':   Builder(),
        'distributor': Distributor(),
        'upgrader': Upgrader()
    }

    targetCreeps = {

        'harvester': 5,
        'distributor': 3,
        'upgrader': 5,
        'builder':   3
    }

    containerTextStyle = {
        'color': '#ffffff',
        'font': '10px',
        'stroke': '#000000',
        'strokeWidth': .15
    }
    #print("CPU Usage: " + Game.cpu.getUsed())
    # Run each creep
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        if creep.memory.role:
            roles[creep.memory.role].run(creep)
        else:
            creep.say("No role")

    # Run each spawn
    for name in Object.keys(Game.spawns):

        spawn = Game.spawns[name]
        for container in [struct for struct in spawn.room.find(FIND_STRUCTURES) if struct.structureType == STRUCTURE_CONTAINER]:
            spawn.room.visual.text(roles['harvester'].getContainerFutureEnergy(container), container.pos, containerTextStyle)
        if not spawn.spawning:
            for roleName in Object.keys(targetCreeps):
                numTargetCreeps = len([creepName for creepName in Object.keys(Game.creeps) if Game.creeps[creepName].memory.role == roleName])
                if numTargetCreeps < targetCreeps[roleName]:
                    bodyParts = roles[roleName].getBodyParts(spawn)
                    cost = sum([BODYPART_COST[part] for part in bodyParts])
                    if cost <= spawn.room.energyAvailable:
                        spawn.spawnCreep(bodyParts, roleName + "_" + Game.time, {'memory': {'role':roleName}})
                        break # Break because multiple calls to spawn seems to spawn the last one

module.exports.loop = main
