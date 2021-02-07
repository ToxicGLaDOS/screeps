
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

from harvester import Harvester
from builder import Builder
from distributor import Distributor
from upgrader import Upgrader
from remoteHarvester import RemoteHarvester
from reserver import Reserver

import math

class Spawner(object):
    roles = {
        'harvester': Harvester(),
        'builder':   Builder(),
        'distributor': Distributor(),
        'upgrader': Upgrader(),
        'remoteHarvester': RemoteHarvester('E41N41', 'E42N41'),
        'reserver': Reserver('E41N41', 'E42N41')
    }

    targetCreeps = {
        'harvester': 2,
        'distributor': 2,
        'builder':   2,
        'reserver': 1,
        'remoteHarvester': 5,
        'upgrader': 3
    }
    def __init__(self):
        pass

    def run(self, spawn: StructureSpawn):
        if spawn.spawning:
            return
        
        creepRoles = [creep.memory.role for creep in Object.values(Game.creeps)]
        roleAssignments = dict(_.countBy(creepRoles))
        for role in Object.keys(Spawner.roles):
            if not role in roleAssignments:
                roleAssignments[role] = 0

        print(JSON.stringify(roleAssignments))
        remoteRoom = Game.getObjectById(Game.rooms['E42N41'])
        desiredUpgraders = math.floor([struct for struct in spawn.room.find(FIND_STRUCTURES) if struct.structureType == STRUCTURE_STORAGE][0].store.getUsedCapacity() / 10000)
        desiredBuilders = math.ceil(sum([site.progressTotal - site.progress for site in spawn.room.find(FIND_CONSTRUCTION_SITES)]) / 3000)

        # Spawn harvesters if we don't have enough
        if roleAssignments['harvester'] < Spawner.targetCreeps['harvester']:
            self.spawn(spawn, 'harvester')
        # Spawn additional harvester if any are close to dying
        elif roleAssignments['harvester'] == Spawner.targetCreeps['harvester'] and any([creep.ticksToLive < 500 for creep in Object.values(Game.creeps) if creep.memory.role == 'harvester']):
            self.spawn(spawn, 'harvester')
        # Spawn distributor if we don't have enough
        elif roleAssignments['distributor'] < Spawner.targetCreeps['distributor']:
            self.spawn(spawn, 'distributor')
        # Spawn additional distributor if any are close to dying
        elif roleAssignments['distributor'] == Spawner.targetCreeps['distributor'] and any([creep.ticksToLive < 500 for creep in Object.values(Game.creeps) if creep.memory.role == 'distributor']):
            self.spawn(spawn, 'distributor')
        # Spawn builders up to some fraction of the remaining progress on all construction sites (allProgressRemaining / 2000)
        elif roleAssignments['builder'] < desiredBuilders:
            self.spawn(spawn, 'builder')
        # Spawn reserver if we don't have one and don't have vision on the remoteRoom (remoteRoom == None) or if the reservation will end in < 1000 ticks
        elif roleAssignments['reserver'] == 0 and (remoteRoom == None or remoteRoom.controller.reservation.ticksToEnd < 1000):
            self.spawn(spawn, 'reserver')
        # Spawn remote harvesters if we don't have enough
        elif roleAssignments['remoteHarvester'] < Spawner.targetCreeps['remoteHarvester']:
            self.spawn(spawn, 'remoteHarvester')
        # Spawn upgrader if the storage / 10000 > numUpgraders
        elif roleAssignments['upgrader'] < desiredUpgraders:
            self.spawn(spawn, 'upgrader')
        else:
            print("No desired creeps to spawn")

    def spawn(self, spawn: StructureSpawn, roleName: str):
        bodyParts = Spawner.roles[roleName].getBodyParts(spawn)
        cost = sum([BODYPART_COST[part] for part in bodyParts])
        if cost <= spawn.room.energyAvailable:
            spawn.spawnCreep(bodyParts, roleName + "_" + Game.time, {'memory': {'role':roleName}})
        else:
            print("Want to spawn: " + roleName)
