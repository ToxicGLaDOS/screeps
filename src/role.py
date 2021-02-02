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
