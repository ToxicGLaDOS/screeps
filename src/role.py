from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')



class Role(object):
    def __init__(self):
        pass
    
    def run(self, creep: Creep):
        """
        :param Creep creep: the creep to run
        :return: None
        :rtype: None
        """

        print("Role.run shouldn't be called directly. This method is supposed to be overridden. Creep id: " + creep.id)
    
    def initalize(self, creep: Creep):
        """
        :param Creep creep: the creep to initalize
        :return: True if initalization successful, else False
        :rtype: bool
        """
        print("Role.initalize shouldn't be called directly. This method is supposed to be overridden. Creep id: " + creep.id)
    
    def getBodyParts(self, spawner: StructureSpawn):
        """
        :param StructureSpawn spawner: The spawner that's going to spawn the creep
        :return: A list of body parts to use for spawning the creep
        :rtype: list
        """
        print("Role.getBodyParts shouldn't be called directly. This method is supposed to be overridden.")
    

    def getStructureFutureEnergy(self, structure: Structure):
        if structure.store == None:
            return None
        
        creepsTargetingContainer = [Game.creeps[creepName] for creepName in Object.keys(Game.creeps) if Game.creeps[creepName].memory.dest == structure.id]
        creepsWithdrawing = [creep for creep in creepsTargetingContainer if creep.memory.curAction == "charging"]
        creepsDepositing = [creep for creep in creepsTargetingContainer if creep.memory.curAction == "distributing" or creep.memory.curAction == "depositing"]
        totalWithdrawAmount = sum([creep.store.getFreeCapacity(RESOURCE_ENERGY) for creep in creepsWithdrawing])
        totalDepositAmount  = sum([creep.store.getUsedCapacity(RESOURCE_ENERGY) for creep in creepsDepositing])

        return structure.store.getUsedCapacity(RESOURCE_ENERGY)  + totalDepositAmount - totalWithdrawAmount

    def findClosestByPath(self, creep: Creep, targets: list, opt={}):
        pathObjs = {target:PathFinder.search(creep.pos, target, opt).cost for target in targets}
        minValue = min(Object.values(pathObjs))
        minDist = [target for target in targets if pathObjs[target] == minValue]
        return minDist[0]
    