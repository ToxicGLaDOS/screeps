from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
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
    

    def getContainerFutureEnergy(self, container: StructureContainer):
        creepsTargetingContainer = [Game.creeps[creepName] for creepName in Object.keys(Game.creeps) if Game.creeps[creepName].memory.dest == container.id]
        creepsWithdrawing = [creep for creep in creepsTargetingContainer if creep.memory.curAction == "charging"]
        creepsDepositing = [creep for creep in creepsTargetingContainer if creep.memory.curAction == "distributing" or creep.memory.curAction == "depositing"]
        totalWithdrawAmount = sum([creep.store.getFreeCapacity(RESOURCE_ENERGY) for creep in creepsWithdrawing])
        totalDepositAmount  = sum([creep.store.getFreeCapacity(RESOURCE_ENERGY) for creep in creepsDepositing])

        return container.store.getUsedCapacity(RESOURCE_ENERGY)  + totalDepositAmount - totalWithdrawAmount