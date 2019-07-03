#beowulf-python

beowulf-python is library python client for Beowulf blockchain.  

## Full Documentation
- Please have a look at the [Wiki](https://github.com/beowulf-foundation/beowulf-python/wiki) for full documentation, examples, operational details and other information.  
- The api documentation can be found in the official beowulf developers portal: https://beowulfchain.com/developer-guide/walletsdk  

## Main Functions Supported
1. CHAIN  
- get_block
- get_transaction
2. TRANSACTION  
- broadcast_transaction
- create transaction transfer
- create account

#### Requirements
* `beowulf-python` requires Python 3.5 or higher.  
* Library dependencies
```sh
appdirs
certifi
ecdsa>=0.13
funcy
future
langdetect
prettytable
pycrypto>=1.9.1
pylibscrypt>=1.6.1
scrypt>=0.8.0
toolz
ujson
urllib3
voluptuous
w3lib
```


#### Installation

```sh
git clone https://github.com/beowulf-foundation/beowulf-python
cd beowulf-python
python3 setup.py install        # python setup.py install for 2.7
or
make install
```  


#### Configuration
Create a new client instance of Beowulfd  
  
```python
from beowulf.beowulfd import Beowulfd
from beowulf.commit import Commit

# Client setup
s = Beowulfd()
pri_key = "5Jxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
creator = "creatorwallet"
c = Commit(beowulfd_instance=s, no_wallet_file=True)
c.wallet.unlock("your_password")

if not c.wallet.getOwnerKeyForAccount(creator):
    c.wallet.addPrivateKey(pri_key)    
```

#### Example Usage

##### Get account
```python
acc = c.wallet.getAccounts()
print(acc)
# get public key
pub_key = c.wallet.getPublicKeys()
print(pub_key)
```

##### Creating a wallet
```python
# Variances
new_account_name = "newwallet"
creator = "creatorwallet"
new_password_seed = "password_seed"
new_password_wallet = "password_wallet"

# Create account
if not c.beowulfd.get_account(new_account_name):
  c.create_account_simple(account_name=new_account_name, creator=creator, password_seed=new_password_seed, password_wallet=new_password_wallet)
```

##### Signing and pushing a transaction

```python
# Transfer native coin
asset_bwf = "BWF"
asset_w = "W"
asset_tot = "TOT"
asset_fee = "W"
amount = "1.00000"
fee = "0.01000"

# Transfer BWF from creator to new_account_name
c.transfer(account=creator, amount=amount, asset=asset_bwf, fee=fee, asset_fee=asset_fee, memo="", to=new_account_name)
# Transfer W from creator to new_account_name
c.transfer(account=creator, amount=amount, asset=asset_w, fee=fee, asset_fee=asset_fee, memo="", to=new_account_name)
# Transfer Token TOT from creator to new_account_name
c.transfer_token(to=new_account_name, amount=amount, asset_name=asset_tot, fee=fee, asset_fee=asset_fee, memo="", account=creator)
```

##### Getting a block
```python
# Get block from block number
block_num = 1869
block = c.beowulfd.get_block(block_num)
print(block)
```

## Bugs and Feedback
For bugs or feature requests please create a [GitHub Issue](https://github.com/beowulf-foundation/beowulf-python/issues).  

## Example
The [sample module](https://github.com/beowulf-foundation/beowulf-python/tree/master/sample) of the beowulf-python project provides showcases for the most common acitivies and operations users want to perform.  
Beside that you can find a lot of snippets and examples in the different [Wiki sections](https://github.com/beowulf-foundation/beowulf-python/wiki).  
