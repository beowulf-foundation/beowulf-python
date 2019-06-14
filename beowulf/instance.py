import sys

_shared_beowulfd_instance = None


def get_config_node_list():
    from beowulfbase.storage import configStorage
    nodes = configStorage.get('nodes', None)
    if nodes:
        return nodes.split(',')


def shared_beowulfd_instance():
    """ This method will initialize _shared_beowulfd_instance and return it.
    The purpose of this method is to have offer single default Beowulf
    instance that can be reused by multiple classes.  """

    global _shared_beowulfd_instance
    if not _shared_beowulfd_instance:
        if sys.version >= '3.0':
            from beowulf.beowulfd import Beowulfd
            _shared_beowulfd_instance = Beowulfd(
                nodes=get_config_node_list())
        else:
            from beowulf.beowulfd import Beowulfd
            _shared_beowulfd_instance = Beowulfd(
                nodes=get_config_node_list())
    return _shared_beowulfd_instance


def set_shared_beowulfd_instance(beowulfd_instance):
    """ This method allows us to override default beowulf instance for all
    users of _shared_beowulfd_instance.  """

    global _shared_beowulfd_instance
    _shared_beowulfd_instance = beowulfd_instance
