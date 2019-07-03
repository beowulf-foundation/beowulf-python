# beowulf

# beowulf.commit

## Commit
```python
Commit(self, beowulfd_instance=None, no_broadcast=False, no_wallet_file=True, **kwargs)
```
Commit things to the Beowulf network.

This class contains helper methods to construct, sign and broadcast
common transactions, such as posting, voting, sending funds, etc.

:param Beowulfd beowulfd: Beowulfd node to connect to*
:param bool offline: Do **not** broadcast transactions! *(optional)*
:param bool debug: Enable Debugging *(optional)*

:param list,dict,string keys: Predefine the wif keys to shortcut the
wallet database

Three wallet operation modes are possible:

* **Wallet Database**: Here, the beowulflibs load the keys from the
  locally stored wallet SQLite database (see ``storage.py``).
  To use this mode, simply call ``Beowulf()`` without the
  ``keys`` parameter
* **Providing Keys**: Here, you can provide the keys for
  your accounts manually. All you need to do is add the wif
  keys for the accounts you want to use as a simple array
  using the ``keys`` parameter to ``Beowulf()``.
* **Force keys**: This more is for advanced users and
  requires that you know what you are doing. Here, the
  ``keys`` parameter is a dictionary that overwrite the
  ``active``, ``owner``, ``posting`` or ``memo`` keys for
  any account. This mode is only used for *foreign*
  signatures!

### finalizeOp
```python
Commit.finalizeOp(self, ops, account, permission)
```
This method obtains the required private keys if present in
the wallet, finalizes the transaction, signs it and
broadacasts it

:param operation ops: The operation (or list of operations) to
    broadcast

:param operation account: The account that authorizes the
    operation
:param string permission: The required permission for
    signing (active, owner, posting)

... note::

    If ``ops`` is a list of operation, they all need to be
    signable by the same key! Thus, you cannot combine ops
    that require active permission with ops that require
    posting permission. Neither can you use different
    accounts for different operations!

### sign
```python
Commit.sign(self, unsigned_trx, wifs=[])
```
Sign a provided transaction with the provided key(s)

:param dict unsigned_trx: The transaction to be signed and returned
:param string wifs: One or many wif keys to use for signing
    a transaction. If not present, the keys will be loaded
    from the wallet as defined in "missing_signatures" key
    of the transactions.

### broadcast
```python
Commit.broadcast(self, signed_trx)
```
Broadcast a transaction to the Beowulf network

:param tx signed_trx: Signed transaction to broadcast

### create_account_simple
```python
Commit.create_account_simple(self, account_name, json_meta=None, password_seed=None, owner_key=None, store_keys=True, store_owner_key=True, creator=None, password_wallet=None)
```
Create new account in Beowulf

The brainkey/password can be used to recover all generated keys
(see `beowulfbase.account` for more details.

By default, this call will use ``default_account`` to
register a new name ``account_name`` with all keys being
derived from a new brain key that will be returned. The
corresponding keys will automatically be installed in the
wallet.

.. note:: Account creations cost a fee that is defined by
   the network. If you create an account, you will
   need to pay for that fee!

   **You can partially pay that fee by delegating M.**

   To pay the fee in full in BWF, leave
   ``delegation_fee_beowulf`` set to ``0 BWF`` (Default).

   To pay the fee partially in BWF, partially with delegated
   M, set ``delegation_fee_beowulf`` to a value greater than ``1
   BWF``. `Required M will be calculated automatically.`

   To pay the fee with maximum amount of delegation, set
   ``delegation_fee_beowulf`` to ``1 W``. `Required M will be
   calculated automatically.`

.. warning:: Don't call this method unless you know what
              you are doing! Be sure to understand what this
              method does and where to find the private keys
              for your account.

.. note:: Please note that this imports private keys (if password is
present) into the wallet by default. However, it **does not import
the owner key** unless `store_owner_key` is set to True (default
False). Do NOT expect to be able to recover it from the wallet if
you lose your password!

:param str account_name: (**required**) new account name
:param str json_meta: Optional meta data for the account
:param str owner_key: Main owner key
:param str active_key: Main active key
:param str posting_key: Main posting key
:param str memo_key: Main memo_key
:param str password: Alternatively to providing keys, one
                     can provide a password from which the
                     keys will be derived
:param list additional_owner_keys:  Additional owner public keys

:param list additional_active_keys: Additional active public keys

:param list additional_posting_keys: Additional posting public keys

:param list additional_owner_accounts: Additional owner account
names

:param list additional_active_accounts: Additional active account
names

:param list additional_posting_accounts: Additional posting account
names

:param bool store_keys: Store new keys in the wallet (default:
``True``)

:param bool store_owner_key: Store owner key in the wallet
(default: ``False``)

:param str delegation_fee_beowulf: (Optional) If set, `creator` pay a
fee of this amount, and delegate the rest with M (calculated
automatically). Minimum: 1 BWF. If left to 0 (Default), full fee
is paid without M delegation.

:param str creator: which account should pay the registration fee
                    (defaults to ``default_account``)

:raises AccountExistsException: if the account already exists on the blockchain

### account_update
```python
Commit.account_update(self, account_name, json_meta=None, password=None, owner_key=None, store_keys=True, store_owner_key=False)
```
Create new account in Beowulf

The brainkey/password can be used to recover all generated keys
(see `beowulfbase.account` for more details.

By default, this call will use ``default_account`` to
register a new name ``account_name`` with all keys being
derived from a new brain key that will be returned. The
corresponding keys will automatically be installed in the
wallet.

.. note:: Account creations cost a fee that is defined by
   the network. If you create an account, you will
   need to pay for that fee!

   **You can partially pay that fee by delegating M.**

   To pay the fee in full in BEOWULF, leave
   ``delegation_fee_beowulf`` set to ``0 BWF`` (Default).

   To pay the fee partially in BWF, partially with delegated
   M, set ``delegation_fee_beowulf`` to a value greater than ``1
   BWF``. `Required M will be calculated automatically.`

   To pay the fee with maximum amount of delegation, set
   ``delegation_fee_beowulf`` to ``1 BWF``. `Required M will be
   calculated automatically.`

.. warning:: Don't call this method unless you know what
              you are doing! Be sure to understand what this
              method does and where to find the private keys
              for your account.

.. note:: Please note that this imports private keys (if password is
present) into the wallet by default. However, it **does not import
the owner key** unless `store_owner_key` is set to True (default
False). Do NOT expect to be able to recover it from the wallet if
you lose your password!

:param str account_name: (**required**) new account name
:param str json_meta: Optional meta data for the account
:param str owner_key: Main owner key
:param str active_key: Main active key
:param str posting_key: Main posting key
:param str memo_key: Main memo_key
:param str password: Alternatively to providing keys, one
                     can provide a password from which the
                     keys will be derived
:param list additional_owner_keys:  Additional owner public keys

:param list additional_active_keys: Additional active public keys

:param list additional_posting_keys: Additional posting public keys

:param list additional_owner_accounts: Additional owner account
names

:param list additional_active_accounts: Additional active account
names

:param list additional_posting_accounts: Additional posting account
names

:param bool store_keys: Store new keys in the wallet (default:
``True``)

:param bool store_owner_key: Store owner key in the wallet
(default: ``False``)

:param str delegation_fee_beowulf: (Optional) If set, `creator` pay a
fee of this amount, and delegate the rest with M (calculated
automatically). Minimum: 1 BWF. If left to 0 (Default), full fee
is paid without M delegation.

:param str creator: which account should pay the registration fee
                    (defaults to ``default_account``)

:raises AccountExistsException: if the account already exists on the blockchain

### transfer
```python
Commit.transfer(self, to, amount, asset, fee, asset_fee, memo='', account=None)
```
Transfer W or BWF to another account.

:param str to: Recipient

:param float amount: Amount to transfer

:param str asset: Asset to transfer (``W`` or ``BWF``)

:param float fee: Fee to transfer

:param str asset_fee: Asset fee to transfer (``W``)

:param str memo: (optional) Memo, may begin with `#` for encrypted
messaging

:param str account: (optional) the source account for the transfer
if not ``default_account``

### create_token
```python
Commit.create_token(self, creator, control_account, max_supply, decimals, token_name)
```
Create new token.

:param str creator: initminer account

:param str control_account: the account control token

:param uint64 max_supply: Amount to setup token

:param uint16 decimals: the decimals place

:param str token_name: token name

### transfer_token
```python
Commit.transfer_token(self, to, amount, asset_name, fee, asset_fee, memo='', account=None)
```
Transfer W or BWF to another account.

:param str to: Recipient

:param amount: Amount to transfer

:param asset_name: Name of token to transfer

:param fee: Fee to transfer

:param str asset_fee: Asset fee to transfer (``W``)

:param str memo: (optional) Memo, may begin with `#` for encrypted
messaging

:param str account: (optional) the source account for the transfer
if not ``default_account``

### withdraw_vesting
```python
Commit.withdraw_vesting(self, amount, fee=None, account=None)
```
Withdraw M from the vesting account.

:param float amount: number of M to withdraw over a period of
104 weeks

:param float fee: fee to transfer

:param str account: (optional) the source account for the transfer
if not ``default_account``

### transfer_to_vesting
```python
Commit.transfer_to_vesting(self, amount, to, fee=None, account=None)
```
Vest BWF

:param float amount: number of BWF to vest

:param float fee: fee to transfer

:param str to: (optional) the source account for the transfer if not
``default_account``

:param str account: (optional) the source account for the transfer
if not ``default_account``

### supernode_update
```python
Commit.supernode_update(self, signing_key, fee=None, account=None)
```
Update supernode

:param pubkey signing_key: Signing key
:param dict props: Properties
:param float fee: fee to update supernode
:param str account: (optional) supernode account name

 Properties:::

    {
        "account_creation_fee": x,
        "maximum_block_size": x,
    }


### approve_supernode
```python
Commit.approve_supernode(self, supernode, account=None, vesting_shares=None, fee=None, approve=True)
```
Vote **for** a supernode. This method adds a supernode to your
set of approved supernodes. To remove supernodes see
``disapprove_supernode``.

:param str supernode: supernode to approve
:param str account: (optional) the account to allow access
    to (defaults to ``default_account``)
:param float fee: fee to vote supernode


### disapprove_supernode
```python
Commit.disapprove_supernode(self, supernode, account=None, vesting_shares=None, fee=None)
```
Remove vote for a supernode. This method removes
a supernode from your set of approved supernodes. To add
supernodes see ``approve_supernode``.

:param str supernode: supernode to approve
:param str account: (optional) the account to allow access
    to (defaults to ``default_account``)
:param float fee: fee to unvote supernode


