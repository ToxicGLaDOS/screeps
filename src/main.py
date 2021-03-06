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
__pragma__('noalias', 'values')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

from spawner import Spawner

def main():
    """
    Main game logic loop.
    """

    containerTextStyle = {
        'color': '#ffffff',
        'font': '10px',
        'stroke': '#000000',
        'strokeWidth': .15
    }
    spawnerRole = Spawner()
    # Clean up memory
    for creepName in Object.keys(Memory.creeps):
        if not Game.creeps[creepName]:
            if Memory.creeps[creepName].role == "remoteHarvester":
                print("Cleaning up remoteHarvester. It mined: " + Memory.creeps[creepName].totalHarvested)
            del Memory.creeps[creepName]
            #print("Clearing non-existent creep memory: " + creepName)

    if Game.cpu.bucket == 10000:
        Game.cpu.generatePixel()
    # Run each creep
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        if creep.memory.role in Spawner.roles:
            Spawner.roles[creep.memory.role].run(creep)
        else:
            creep.say("No role")

    # Run tower code
    homeRoom = Object.values(Game.spawns)[0].room
    towers = [struct for room in Object.values(Game.rooms) for struct in room.find(FIND_STRUCTURES) if struct.structureType == STRUCTURE_TOWER]
    hostiles = homeRoom.find(FIND_HOSTILE_CREEPS)
    for tower in towers:
        structures = sorted([struct for struct in tower.room.find(FIND_STRUCTURES) if struct.hits < struct.hitsMax], key=lambda struct: struct.hits)
        if len(hostiles) > 0:
            tower.attack(tower.pos.findClosestByPath(hostiles))
            continue

        for structure in structures:
            if structure.hits < structure.hitsMax and structure.hits < 100000:
                tower.repair(structure)
                break

    # Run visuals
    for room in Object.values(Game.rooms):
        for container in [struct for struct in room.find(FIND_STRUCTURES) if struct.structureType == STRUCTURE_CONTAINER or struct.structureType == STRUCTURE_STORAGE]:
            room.visual.text(Spawner.roles['harvester'].getStructureFutureEnergy(container), container.pos, containerTextStyle)

    # Run each spawn
    for name in Object.keys(Game.spawns)[0:1]:
        spawn = Game.spawns[name]
        spawnerRole.run(spawn)


module.exports.loop = main
