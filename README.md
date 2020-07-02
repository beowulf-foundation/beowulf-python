# Official Python BEOWULF Library

`beowulf-python` is the official Beowulf library for Python. It comes with a
BIP38 encrypted wallet and a practical CLI utility called `beowulfpy`.

This library currently works on Python 2.7, 3.5 and 3.6. Python 3.3 and 3.4 support forthcoming.

## Main Functions Supported
1. CHAIN  
- get_block
- get_transaction
2. TRANSACTION  
- broadcast_transaction
- create transaction transfer
- create account

## Requirements
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

### OSX

On Mac OSX, you may need to do the following first:

```bash
brew install openssl
export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"
```

### Ubuntu
On Ubuntu, Beowulf-python requires libssl-dev
```bash
sudo apt-get install libssl-dev
```

## Installation

From pip:  
```bash
pip install beowulf-python
```

From Source:  

```
git clone https://github.com/beowulf-foundation/beowulf-python.git
cd beowulf-python

python3 setup.py install        # python setup.py install for 2.7
or
make install
```
## Configuration

* Create a new client instance of Beowulfd and add your account to wallet  
* Replace nodes with your endpoints which participate to MAINNET or TESTNET chain  
*Note:* Client library will detect MAINNET or TESTNET properties through your provided endpoint.

##### Client setup
```
from beowulf.beowulfd import Beowulfd
from beowulf.commit import Commit

s = Beowulfd(nodes = ['https://testnet-bw.beowulfchain.com/rpc'])
```
##### Replace with your Private key and account name already have or get 
##### from services
```pri_key = "5Jxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
account = "creatorwallet"

c = Commit(beowulfd_instance=s, no_wallet_file=True)
```
##### Provide a passphrase for the new wallet for the first time.
##### Unlock wallet before create transactions with passphrase.
```c.wallet.unlock("your_password")

if not c.wallet.getOwnerKeyForAccount(account):
    c.wallet.addPrivateKey(pri_key)   
```

## Example Usage

##### Get block
```python
# Get block from block number
block_num = 1869
block = c.beowulfd.get_block(block_num)
print(block)
```

##### Get transaction
```python
# Get transaction from transaction_id
transaction_id = '45618f73e9dbbe87a9ae6bfc316de8457c502b7c'
trx = c.beowulfd.get_transaction(transaction_id)
print(trx)
```
##### Transfer native coin
###### Transfer BWF
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
```

###### Transfer W
```python
# Transfer native coin
asset_bwf = "BWF"
asset_w = "W"
asset_tot = "TOT"
asset_fee = "W"
amount = "1.00000"
fee = "0.01000"

# Transfer W from creator to new_account_name
c.transfer(account=creator, amount=amount, asset=asset_w, fee=fee, asset_fee=asset_fee, memo="", to=new_account_name)
```

##### Create wallet
```python
# Variances
creator = "creatorwallet"
new_account_name = "newwallet"
new_password_seed = "password_seed"
new_password_wallet = "password_wallet"

# Create account
if not c.beowulfd.get_account(new_account_name):
  c.create_account_simple(account_name=new_account_name, creator=creator, password_seed=new_password_seed, password_wallet=new_password_wallet)
```
