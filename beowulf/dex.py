from .instance import shared_beowulfd_instance


class Dex(object):
    """ This class allows to access calls specific for the internal
        exchange of BWF.

        :param Beowulfd beowulfd_instance: Beowulfd() instance to use when
        accessing a RPC
    """
    assets = ["BWF", "W"]

    def __init__(self, beowulfd_instance=None):
        self.beowulfd = beowulfd_instance or shared_beowulfd_instance()

    def _get_asset(self, symbol):
        """ Return the properties of the assets tradeable on the
            network.

            :param str symbol: Symbol to get the data for (i.e. BWF, W,
            M)
        """
        if symbol == "BWF":
            return {"symbol": "BWF", "precision": 5}
        elif symbol == "W":
            return {"symbol": "W", "precision": 5}
        elif symbol == "M":
            return {"symbol": "M", "precision": 5}
        else:
            return None

    def _get_assets(self, quote):
        """ Given the `quote` asset, return base. If quote is W, then
            base is BWF and vice versa.
        """
        assets = self.assets.copy()
        assets.remove(quote)
        base = assets[0]
        return self._get_asset(quote), self._get_asset(base)
