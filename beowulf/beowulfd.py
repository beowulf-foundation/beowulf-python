# coding=utf-8
import logging
from funcy.seqs import first
from beowulfbase.chains import known_chains
from beowulfbase.http_client import HttpClient
from .instance import get_config_node_list
from .utils import compat_compose_dictionary
logger = logging.getLogger(__name__)

class Beowulfd(HttpClient):
    """ Connect to the Beowulf network.

        Args:

            nodes (list): A list of Beowulf HTTP RPC nodes to connect to. If
            not provided, official beowulfchain nodes will be used.

        Returns:

            Beowulfd class instance. It can be used to execute commands
            against beowulf node.

        Example:

           If you would like to override the official Beowulfchain nodes
           (default), you can pass your own.  When currently used node goes
           offline, ``Beowulfd`` will automatically fail-over to the next
           available node.

           .. code-block:: python

               nodes = [
                   'https://beowulfd.yournode1.com',
                   'https://beowulfd.yournode2.com',
               ]

               s = Beowulfd(nodes)

       """

    def __init__(self, nodes=None, **kwargs):
        if not nodes:
            nodes = get_config_node_list() or ['https://bw.beowulfchain.com']

        super(Beowulfd, self).__init__(nodes, **kwargs)

    @property
    def chain_params(self):
        """ Identify the connected network. This call returns a
            dictionary with keys chain_id, prefix, and other chain
            specific settings
        """
        props = self.get_dynamic_global_properties()
        chain = props["current_supply"].split(" ")[1]

        assert chain in known_chains, "The chain you are connecting " + \
                                      "to is not supported"
        return known_chains.get(chain)

    @property
    def last_irreversible_block_num(self):
        """ Newest irreversible block number. """
        return self.get_dynamic_global_properties()[
            'last_irreversible_block_num']

    @property
    def head_block_number(self):
        """ Newest block number. """
        return self.get_dynamic_global_properties()['head_block_number']

    def get_account(self, account):
        """ Lookup account information such as user profile, public keys,
        balances, etc.

        Args:
            account (str): BEOWULF username that we are looking up.

        Returns:
            dict: Account information.

        """
        return first(self.call('get_accounts', [account]))

    def get_all_usernames(self, last_user=''):
        """ Fetch the full list of BEOWULF usernames. """
        usernames = self.lookup_accounts(last_user, 1000)
        batch = []
        while len(batch) != 1:
            batch = self.lookup_accounts(usernames[-1], 1000)
            usernames += batch[1:]

        return usernames

    def _get_blocks(self, blocks):
        """ Fetch multiple blocks from beowulfd at once.

        Warning: This method does not ensure that all blocks are returned,
        or that the results are ordered.  You will probably want to use
        `beowulfd.get_blocks()` instead.

        Args:
            blocks (list): A list, or a set of block numbers.

        Returns:
            A generator with results.

        """
        results = self.call_multi_with_futures(
            'get_block', blocks, max_workers=10)
        return (compat_compose_dictionary(x, block_num=int(x['block_id'][:8], base=16))
                for x in results if x)

    def get_blocks(self, block_nums):
        """ Fetch multiple blocks from beowulfd at once, given a range.

        Args:

            block_nums (list): A list of all block numbers we would like to
            tech.

        Returns:

            dict: An ensured and ordered list of all `get_block` results.

        """
        required = set(block_nums)
        available = set()
        missing = required - available
        blocks = {}

        while missing:
            for block in self._get_blocks(missing):
                blocks[block['block_num']] = block

            available = set(blocks.keys())
            missing = required - available

        return [blocks[x] for x in block_nums]

    def get_blocks_range(self, start, end):
        """ Fetch multiple blocks from beowulfd at once, given a range.

        Args:

            start (int): The number of the block to start with

            end (int): The number of the block at the end of the range. Not
            included in results.

        Returns:
            dict: An ensured and ordered list of all `get_block` results.

        """
        return self.get_blocks(list(range(start, end)))

    def get_block_header(self, block_num):
        """ Get block headers, given a block number.

        Args:
           block_num (int) number.

        Returns:
           dict headers in a JSON compatible format.

        Example:

            .. code-block:: python

               s.get_block_headers(8888888)

            ::

                {'extensions': [],
                 'previous': '0087a2372163ff5c5838b09589ce281d5a564f66',
                 'timestamp': '2017-01-29T02:47:33',

                 'transaction_merkle_root':
                 '4ddc419e531cccee6da660057d606d11aab9f3a5',
                 'supernode': 'chainsquad.com'}
        """
        return self.call('get_block_header', block_num, api='database_api')

    def get_block(self, block_num):
        """ Get the full block, transactions and all, given a block number.

        Args:
            block_num (int) number.

        Returns:
            dict in a JSON compatible format.

        """
        return self.call('get_block', block_num, api='database_api')

    def get_ops_in_block(self, block_num, virtual_only):
        """ get_ops_in_block """
        return self.call(
            'get_ops_in_block', block_num, virtual_only, api='database_api')

    def get_config(self):
        """ Get internal chain configuration. """
        return self.call('get_config', api='database_api')

    def get_dynamic_global_properties(self):
        """ get_dynamic_global_properties """
        return self.call('get_dynamic_global_properties', api='database_api')

    def get_chain_properties(self):
        """ Get supernode elected chain properties.

        ::

            {'account_creation_fee': '30.000 BWF',
             'maximum_block_size': 65536,
             'wd_interest_rate': 250}

        """
        return self.call('get_chain_properties', api='database_api')

    def get_supernode_schedule(self):
        """ get_supernode_schedule """
        return self.call('get_supernode_schedule', api='database_api')

    def get_hardfork_version(self):
        """ Get the current version of the chain.

        Note:
            This is not the same as latest minor version.

        """
        return self.call('get_hardfork_version', api='database_api')

    def get_next_scheduled_hardfork(self):
        """ get_next_scheduled_hardfork """
        return self.call('get_next_scheduled_hardfork', api='database_api')

    def get_accounts(self, account_names):
        """ Lookup account information such as user profile, public keys,
        balances, etc.

        This method is same as ``get_account``, but supports querying for
        multiple accounts at the time.

        """
        return self.call('get_accounts', account_names, api='database_api')

    def lookup_account_names(self, account_names):
        """ lookup_account_names """
        return self.call(
            'lookup_account_names', account_names, api='database_api')

    def lookup_accounts(self, after, limit):
        """Get a list of usernames from all registered accounts.

        Args:

            after (str, int): Username to start with. If '', 0 or -1, it
            will start at beginning.

            limit (int): How many results to return.

        Returns:
            list: List of usernames in requested chunk.

        """
        return self.call('lookup_accounts', after, limit, api='database_api')

    def get_account_count(self):
        """ How many accounts are currently registered on BEOWULF? """
        return self.call('get_account_count', api='database_api')

    def get_owner_history(self, account):
        """ get_owner_history """
        return self.call('get_owner_history', account, api='database_api')

    def get_transaction_hex(self, signed_transaction):
        """ get_transaction_hex """
        return self.call(
            'get_transaction_hex', signed_transaction, api='database_api')

    def get_transaction(self, transaction_id):
        """ get_transaction """
        return self.call('get_transaction', transaction_id, api='database_api')

    def get_required_signatures(self, signed_transaction,
                                available_keys):
        """ get_required_signatures """
        return self.call(
            'get_required_signatures',
            signed_transaction,
            available_keys,
            api='database_api')

    def get_potential_signatures(self, signed_transaction):
        """ get_potential_signatures """
        return self.call(
            'get_potential_signatures', signed_transaction, api='database_api')

    def verify_authority(self, signed_transaction):
        """ verify_authority """
        return self.call(
            'verify_authority', signed_transaction, api='database_api')

    def get_account_votes(self, account):
        """ All votes the given account ever made.

        Returned votes are in the following format:
        ::

           {'authorperm':
           'alwaysfelicia/time-line-of-best-time...',
           'percent': 100, 'rshares': 709227399, 'time':
           '2016-08-07T16:06:24', 'weight': '3241351576115042'},


        Args:
            account (str): BEOWULF username that we are looking up.

        Returns:
            list: List of votes.


        """
        return self.call('get_account_votes', account, api='database_api')

    def get_supernodes(self, supernode_ids):
        """ get_supernodes """
        return self.call('get_supernodes', supernode_ids, api='database_api')

    def get_supernode_by_account(self, account):
        """ get_supernode_by_account """
        return self.call('get_supernode_by_account', account, api='database_api')

    def get_supernodes_by_vote(self, from_account, limit):
        """ get_supernodes_by_vote """
        return self.call(
            'get_supernodes_by_vote', from_account, limit, api='database_api')

    def lookup_supernode_accounts(self, from_account, limit):
        """ lookup_supernode_accounts """
        return self.call(
            'lookup_supernode_accounts', from_account, limit, api='database_api')

    def get_supernode_count(self):
        """ get_supernode_count """
        return self.call('get_supernode_count', api='database_api')

    def get_active_supernodes(self):
        """ Get a list of currently active supernodes. """
        return self.call('get_active_supernodes', api='database_api')

    def get_version(self):
        """ Get beowulfd version of the node currently connected to. """
        return self.call('get_version', api='login_api')

    def broadcast_transaction(self, signed_transaction):
        """ broadcast_transaction """
        return self.call(
            'broadcast_transaction',
            signed_transaction,
            api='network_broadcast_api')

    def broadcast_transaction_synchronous(
            self, signed_transaction):
        """ broadcast_transaction_synchronous """
        return self.call(
            'broadcast_transaction_synchronous',
            signed_transaction,
            api='network_broadcast_api')

    def broadcast_block(self, block):
        """ broadcast_block """
        return self.call('broadcast_block', block, api='network_broadcast_api')

    def get_key_references(self, public_keys):
        """ get_key_references """
        if type(public_keys) == str:
            public_keys = [public_keys]
        return self.call(
            'get_key_references', public_keys, api='account_by_key_api')

    def find_smt_tokens_by_name(self, name):
        """ find_smt_tokens_by_name """
        return self.call('find_smt_tokens_by_name', [name], api='database_api')

    def list_smt_tokens(self):
        """ list_smt_tokens """
        return self.call('list_smt_tokens', api='database_api')

    def get_balance(self, account, token):
        """ get_balance """
        return self.call('get_balance', account, token, api='database_api')

    def get_supernode_voted_by_acc(self, account):
        """ get_supernode_voted_by_acc """
        return self.call('get_supernode_voted_by_acc', account, api='database_api')

    def get_pending_transaction_count(self):
        """ get_pending_transaction_count """
        return self.call('get_pending_transaction_count', api='database_api')

    def get_transaction_with_status(self, tx_hex):
        """ get_transaction_with_status """
        return self.call('get_transaction_with_status', tx_hex, api='database_api')
