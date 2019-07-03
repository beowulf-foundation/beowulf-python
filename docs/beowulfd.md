# beowulf

# beowulf.beowulfd

## Beowulfd
```python
Beowulfd(self, nodes=None, **kwargs)
```
Connect to the Beowulf network.

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


### chain_params
Identify the connected network. This call returns a
dictionary with keys chain_id, prefix, and other chain
specific settings

### head_block_number
Newest block number.
### last_irreversible_block_num
Newest irreversible block number.
### get_account
```python
Beowulfd.get_account(self, account)
```
Lookup account information such as user profile, public keys,
balances, etc.

Args:
    account (str): BEOWULF username that we are looking up.

Returns:
    dict: Account information.


### get_all_usernames
```python
Beowulfd.get_all_usernames(self, last_user='')
```
Fetch the full list of BEOWULF usernames.
### get_blocks
```python
Beowulfd.get_blocks(self, block_nums)
```
Fetch multiple blocks from beowulfd at once, given a range.

Args:

    block_nums (list): A list of all block numbers we would like to
    tech.

Returns:

    dict: An ensured and ordered list of all `get_block` results.


### get_blocks_range
```python
Beowulfd.get_blocks_range(self, start, end)
```
Fetch multiple blocks from beowulfd at once, given a range.

Args:

    start (int): The number of the block to start with

    end (int): The number of the block at the end of the range. Not
    included in results.

Returns:
    dict: An ensured and ordered list of all `get_block` results.


### get_block_header
```python
Beowulfd.get_block_header(self, block_num)
```
Get block headers, given a block number.

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

### get_block
```python
Beowulfd.get_block(self, block_num)
```
Get the full block, transactions and all, given a block number.

Args:
    block_num (int) number.

Returns:
    dict in a JSON compatible format.


### get_ops_in_block
```python
Beowulfd.get_ops_in_block(self, block_num, virtual_only)
```
get_ops_in_block
### get_config
```python
Beowulfd.get_config(self)
```
Get internal chain configuration.
### get_dynamic_global_properties
```python
Beowulfd.get_dynamic_global_properties(self)
```
get_dynamic_global_properties
### get_chain_properties
```python
Beowulfd.get_chain_properties(self)
```
Get supernode elected chain properties.

::

    {'account_creation_fee': '30.000 BWF',
     'maximum_block_size': 65536,
     'wd_interest_rate': 250}


### get_supernode_schedule
```python
Beowulfd.get_supernode_schedule(self)
```
get_supernode_schedule
### get_hardfork_version
```python
Beowulfd.get_hardfork_version(self)
```
Get the current version of the chain.

Note:
    This is not the same as latest minor version.


### get_next_scheduled_hardfork
```python
Beowulfd.get_next_scheduled_hardfork(self)
```
get_next_scheduled_hardfork
### get_accounts
```python
Beowulfd.get_accounts(self, account_names)
```
Lookup account information such as user profile, public keys,
balances, etc.

This method is same as ``get_account``, but supports querying for
multiple accounts at the time.


### lookup_account_names
```python
Beowulfd.lookup_account_names(self, account_names)
```
lookup_account_names
### lookup_accounts
```python
Beowulfd.lookup_accounts(self, after, limit)
```
Get a list of usernames from all registered accounts.

Args:

    after (str, int): Username to start with. If '', 0 or -1, it
    will start at beginning.

    limit (int): How many results to return.

Returns:
    list: List of usernames in requested chunk.


### get_account_count
```python
Beowulfd.get_account_count(self)
```
How many accounts are currently registered on BEOWULF?
### get_owner_history
```python
Beowulfd.get_owner_history(self, account)
```
get_owner_history
### get_transaction_hex
```python
Beowulfd.get_transaction_hex(self, signed_transaction)
```
get_transaction_hex
### get_transaction
```python
Beowulfd.get_transaction(self, transaction_id)
```
get_transaction
### get_required_signatures
```python
Beowulfd.get_required_signatures(self, signed_transaction, available_keys)
```
get_required_signatures
### get_potential_signatures
```python
Beowulfd.get_potential_signatures(self, signed_transaction)
```
get_potential_signatures
### verify_authority
```python
Beowulfd.verify_authority(self, signed_transaction)
```
verify_authority
### get_account_votes
```python
Beowulfd.get_account_votes(self, account)
```
All votes the given account ever made.

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



### get_supernodes
```python
Beowulfd.get_supernodes(self, supernode_ids)
```
get_supernodes
### get_supernode_by_account
```python
Beowulfd.get_supernode_by_account(self, account)
```
get_supernode_by_account
### get_supernodes_by_vote
```python
Beowulfd.get_supernodes_by_vote(self, from_account, limit)
```
get_supernodes_by_vote
### lookup_supernode_accounts
```python
Beowulfd.lookup_supernode_accounts(self, from_account, limit)
```
lookup_supernode_accounts
### get_supernode_count
```python
Beowulfd.get_supernode_count(self)
```
get_supernode_count
### get_active_supernodes
```python
Beowulfd.get_active_supernodes(self)
```
Get a list of currently active supernodes.
### get_version
```python
Beowulfd.get_version(self)
```
Get beowulfd version of the node currently connected to.
### broadcast_transaction
```python
Beowulfd.broadcast_transaction(self, signed_transaction)
```
broadcast_transaction
### broadcast_transaction_synchronous
```python
Beowulfd.broadcast_transaction_synchronous(self, signed_transaction)
```
broadcast_transaction_synchronous
### broadcast_block
```python
Beowulfd.broadcast_block(self, block)
```
broadcast_block
### get_key_references
```python
Beowulfd.get_key_references(self, public_keys)
```
get_key_references
