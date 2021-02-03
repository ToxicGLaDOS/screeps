from harvester import Harvester
from builder import Builder
from distributor import Distributor
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
        'distributor': Distributor()
    }

    targetCreeps = {

        'distributor': 4,
        'harvester': 8,
        'builder':   3
    }

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
        if not spawn.spawning:
            if spawn.room.energyAvailable >= 250:
                for roleName in Object.keys(targetCreeps):
                    numTargetCreeps = len([creepName for creepName in Object.keys(Game.creeps) if Game.creeps[creepName].memory.role == roleName])
                    if numTargetCreeps < targetCreeps[roleName]:
                        spawn.spawnCreep([WORK, CARRY, MOVE, MOVE], roleName + "_" + Game.time, {'memory': {'role':roleName}})
                        break # Break because multiple calls to spawn seems to spawn the last one

module.exports.loop = main
