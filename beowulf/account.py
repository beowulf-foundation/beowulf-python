import time
from beowulfbase.exceptions import AccountDoesNotExistsException
from .amount import Amount
from .converter import Converter
from .instance import shared_beowulfd_instance
from .utils import parse_time, json_expand


class Account(dict):
    """ This class allows to easily access Account data

        :param str account_name: Name of the account
        :param Beowulfd beowulfd_instance: Beowulfd() instance to use when
            accessing a RPC

    """

    def __init__(self, account_name, beowulfd_instance=None):
        self.beowulfd = beowulfd_instance or shared_beowulfd_instance()
        self.name = account_name

        # caches
        self._converter = None

        self.refresh()

    def refresh(self):
        account = self.beowulfd.get_account(self.name)
        if not account:
            raise AccountDoesNotExistsException

        # load json_metadata
        account = json_expand(account, 'json_metadata')
        super(Account, self).__init__(account)

    def __getitem__(self, key):
        return super(Account, self).__getitem__(key)

    def items(self):
        return super(Account, self).items()

    @property
    def converter(self):
        if not self._converter:
            self._converter = Converter(self.beowulfd)
        return self._converter

    @property
    def sp(self):
        vests = Amount(self['vesting_shares']).amount
        return round(self.converter.vests_to_sp(vests), 3)

    @property
    def balances(self):
        return self.get_balances()

    def get_balances(self):
        available = {
            'BWF': Amount(self['balance']).amount,
            'W': Amount(self['wd_balance']).amount,
            'M': Amount(self['vesting_shares']).amount,
        }

        return {'available': available}
        
    def voting_power(self):
        return self['voting_power'] / 100

    # def virtual_op_count(self):
    #     try:
    #         last_item = self.beowulfd.get_account_history(self.name, -1, 0)[0][0]
    #     except IndexError:
    #         return 0
    #     else:
    #         return last_item

    def get_account_votes(self):
        return self.beowulfd.get_account_votes(self.name)

    def get_withdraw_routes(self):
        return self.beowulfd.get_withdraw_routes(self.name, 'all')

    @staticmethod
    def filter_by_date(items, start_time, end_time=None):
        start_time = parse_time(start_time).timestamp()
        if end_time:
            end_time = parse_time(end_time).timestamp()
        else:
            end_time = time.time()

        filtered_items = []
        for item in items:
            if 'time' in item:
                item_time = item['time']
            elif 'timestamp' in item:
                item_time = item['timestamp']
            timestamp = parse_time(item_time).timestamp()
            if end_time > timestamp > start_time:
                filtered_items.append(item)

        return filtered_items

    # def get_account_history(self,
    #                         index,
    #                         limit,
    #                         start=None,
    #                         stop=None,
    #                         order=-1,
    #                         filter_by=None,
    #                         raw_output=False):
    #     """ A generator over beowulfd.get_account_history.
    #
    #     It offers serialization, filtering and fine grained iteration control.
    #
    #     Args:
    #         index (int): start index for get_account_history
    #         limit (int): How many items are we interested in.
    #         start (int): (Optional) skip items until this index
    #         stop (int): (Optional) stop iteration early at this index
    #         order: (1, -1): 1 for chronological, -1 for reverse order
    #         filter_by (str, list): filter out all but these operations
    #         raw_output (bool): (Defaults to False). If True, return history in
    #             beowulfd format (unchanged).
    #     """
    #     history = self.beowulfd.get_account_history(self.name, index, limit)
    #     for item in history[::order]:
    #         index, event = item
    #
    #         # start and stop utilities for chronological generator
    #         if start and index < start:
    #             continue
    #
    #         if stop and index > stop:
    #             return
    #
    #         op_type, op = event['op']
    #         block_props = dissoc(event, 'op')
    #
    #         def construct_op(account_name):
    #             # verbatim output from beowulfd
    #             if raw_output:
    #                 return item
    #
    #             # index can change during reindexing in
    #             # future hard-forks. Thus we cannot take it for granted.
    #             immutable = op.copy()
    #             immutable.update(block_props)
    #             immutable.update({
    #                 'account': account_name,
    #                 'type': op_type,
    #             })
    #             _id = Blockchain.hash_op(immutable)
    #             immutable.update({
    #                 '_id': _id,
    #                 'index': index,
    #             })
    #             return immutable
    #
    #         if filter_by is None:
    #             yield construct_op(self.name)
    #         else:
    #             if type(filter_by) is list:
    #                 if op_type in filter_by:
    #                     yield construct_op(self.name)
    #
    #             if type(filter_by) is str:
    #                 if op_type == filter_by:
    #                     yield construct_op(self.name)
    #
    # def history(self,
    #             filter_by=None,
    #             start=0,
    #             batch_size=1000,
    #             raw_output=False):
    #     """ Stream account history in chronological order.
    #     """
    #     max_index = self.virtual_op_count()
    #     if not max_index:
    #         return
    #
    #     start_index = start + batch_size
    #     i = start_index
    #     while i < max_index + batch_size:
    #         for account_history in self.get_account_history(
    #                 index=i,
    #                 limit=batch_size,
    #                 start=i - batch_size,
    #                 stop=max_index,
    #                 order=1,
    #                 filter_by=filter_by,
    #                 raw_output=raw_output,
    #         ):
    #             yield account_history
    #         i += (batch_size + 1)
    #
    # def history_reverse(self,
    #                     filter_by=None,
    #                     batch_size=1000,
    #                     raw_output=False):
    #     """ Stream account history in reverse chronological order.
    #     """
    #     start_index = self.virtual_op_count()
    #     if not start_index:
    #         return
    #
    #     i = start_index
    #     while i > 0:
    #         if i - batch_size < 0:
    #             batch_size = i
    #         for account_history in self.get_account_history(
    #                 index=i,
    #                 limit=batch_size,
    #                 order=-1,
    #                 filter_by=filter_by,
    #                 raw_output=raw_output,
    #         ):
    #             yield account_history
    #         i -= (batch_size + 1)
