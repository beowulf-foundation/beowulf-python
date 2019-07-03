# Wallet API

# beowulf.wallet

## Wallet
```python
Wallet(self, beowulfd_instance=None, **kwargs)
```
The wallet is meant to maintain access to private keys for
your accounts. It either uses manually provided private keys
or uses a SQLite database managed by storage.py.

:param Beowulf rpc: RPC connection to a Beowulf node

:param array,dict,string keys: Predefine the wif keys to shortcut
the wallet database

Three wallet operation modes are possible:

* **Wallet Database**: Here, beowulflibs loads the keys from the
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
  ``owner`` keys for any account. This mode is only used for *foreign*
  signatures!

### keyMap
dict() -> new empty dictionary
dict(mapping) -> new dictionary initialized from a mapping object's
    (key, value) pairs
dict(iterable) -> new dictionary initialized as if via:
    d = {}
    for k, v in iterable:
        d[k] = v
dict(**kwargs) -> new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)
### keys
dict() -> new empty dictionary
dict(mapping) -> new dictionary initialized from a mapping object's
    (key, value) pairs
dict(iterable) -> new dictionary initialized as if via:
    d = {}
    for k, v in iterable:
        d[k] = v
dict(**kwargs) -> new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)
### setKeys
```python
Wallet.setKeys(self, loadkeys)
```
This method is strictly only for in memory keys that are
passed to Wallet/Beowulf with the ``keys`` argument

### unlock
```python
Wallet.unlock(self, user_passphrase=None)
```
Unlock the wallet database

### lock
```python
Wallet.lock(self)
```
Lock the wallet database

### locked
```python
Wallet.locked(self)
```
Is the wallet database locked?

### changeUserPassphrase
```python
Wallet.changeUserPassphrase(self)
```
Change the user entered password for the wallet database

### created
```python
Wallet.created(self)
```
Do we have a wallet database already?

### newWallet
```python
Wallet.newWallet(self)
```
Create a new wallet database

### encrypt_wif
```python
Wallet.encrypt_wif(self, wif)
```
Encrypt a wif key

### decrypt_wif
```python
Wallet.decrypt_wif(self, encwif)
```
decrypt a wif key

### getUserPassphrase
```python
Wallet.getUserPassphrase(self, confirm=False, text='Passphrase: ')
```
Obtain a passphrase from the user

### addPrivateKey
```python
Wallet.addPrivateKey(self, wif)
```
Add a private key to the wallet database

### getPrivateKeyForPublicKey
```python
Wallet.getPrivateKeyForPublicKey(self, pub)
```
Obtain the private key for a given public key

:param str pub: Public Key

### removePrivateKeyFromPublicKey
```python
Wallet.removePrivateKeyFromPublicKey(self, pub)
```
Remove a key from the wallet database

### removeAccount
```python
Wallet.removeAccount(self, account)
```
Remove all keys associated with a given account

### getOwnerKeyForAccount
```python
Wallet.getOwnerKeyForAccount(self, name)
```
Obtain owner Private Key for an account from the wallet database

### getAccountFromPrivateKey
```python
Wallet.getAccountFromPrivateKey(self, wif)
```
Obtain account name from private key

### getAccountFromPublicKey
```python
Wallet.getAccountFromPublicKey(self, pub)
```
Obtain account name from public key

### getAccount
```python
Wallet.getAccount(self, pub, beowulfd_instance=None)
```
Get the account data for a public key

### getKeyType
```python
Wallet.getKeyType(self, name, pub)
```
Get key type

### getAccounts
```python
Wallet.getAccounts(self)
```
Return all accounts installed in the wallet database

### getAccountsWithPermissions
```python
Wallet.getAccountsWithPermissions(self)
```
Return a dictionary for all installed accounts with their
corresponding installed permissions

### getPublicKeys
```python
Wallet.getPublicKeys(self)
```
Return all installed public keys

