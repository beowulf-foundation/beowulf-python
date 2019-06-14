from .instance import shared_beowulfd_instance
from beowulfbase.exceptions import SupernodeDoesNotExistsException


class Supernode(dict):
    """ Read data about a supernode in the chain

        :param str supernode: Name of the supernode
        :param Beowulfd beowulfd_instance: Beowulfd() instance to use when
        accessing a RPC
    """

    def __init__(self, supernode, beowulfd_instance=None):
        self.beowulfd = beowulfd_instance or shared_beowulfd_instance()
        self.supernode_name = supernode
        self.supernode = None
        self.refresh()

    def refresh(self):
        supernode = self.beowulfd.get_supernode_by_account(self.supernode_name)
        if not supernode:
            raise SupernodeDoesNotExistsException
        super(Supernode, self).__init__(supernode)

    def __getitem__(self, key):
        return super(Supernode, self).__getitem__(key)

    def items(self):
        return super(Supernode, self).items()
