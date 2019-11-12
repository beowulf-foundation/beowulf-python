import logging
import random
from beowulfbase import operations
from beowulfbase.account import PrivateKey, PublicKey
from beowulfbase.exceptions import AccountExistsException, MissingKeyError, AccountDoesNotExistsException, \
    InvalidParamCreateAccount
from beowulfbase.operations import asset_tokens
from beowulfbase.storage import configStorage
from wallet_file.wallet_file import WalletFile
from .account import Account
from .amount import Amount
from .instance import shared_beowulfd_instance
from .transactionbuilder import TransactionBuilder
from .wallet import Wallet

log = logging.getLogger(__name__)

BEOWULF_100_PERCENT = 10000
BEOWULF_1_PERCENT = (BEOWULF_100_PERCENT / 100)
BEOWULF_NAI_SHIFT = 5
SMT_ASSET_NUM_CONTROL_MASK = 0x10
SMT_ASSET_NUM_CONTROL_REVERT_MASK = 0xF
BEOWULF_NAI_DATA_DIGITS = 100
MIN_ACCOUNT_NAME_LENGTH = 2
MAX_ACCOUNT_NAME_LENGTH = 16
MIN_ACCOUNT_CREATION_FEE = Amount("0.1 W")
MIN_TOKEN_CREATION_FEE = Amount("1000 W")
MIN_TRANSFER_FEE = Amount("0.01 W")


class Commit(object):
    """ Commit things to the Beowulf network.

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
          ``owner`` keys for any account. This mode is only used for
          *foreign* signatures!
    """

    def __init__(self, beowulfd_instance=None, no_broadcast=False, no_wallet_file=True, **kwargs):
        self.beowulfd = beowulfd_instance or shared_beowulfd_instance()
        self.no_broadcast = no_broadcast
        self.no_wallet_file = no_wallet_file
        self.unsigned = kwargs.get("unsigned", False)
        self.expiration = int(kwargs.get("expiration", 60))
        self.wallet = None
        self.wallet_file = None
        if self.no_wallet_file:
            self.wallet = Wallet(self.beowulfd, **kwargs)
        else:
            self.wallet_file = WalletFile(**kwargs)

    def finalizeOp(self, ops, account, permission, extensions=None):
        """ This method obtains the required private keys if present in
            the wallet, finalizes the transaction, signs it and
            broadacasts it

            :param operation ops: The operation (or list of operations) to
                broadcast

            :param operation account: The account that authorizes the
                operation
            :param string permission: The required permission for
                signing (owner)
            :param extensions: The extensions add to operation
            ... note::

                If ``ops`` is a list of operation, they all need to be
                signable by the same key! Thus, you cannot combine ops
                that require active permission with ops that require
                posting permission. Neither can you use different
                accounts for different operations!
        """
        tx = TransactionBuilder(
            None,
            beowulfd_instance=self.beowulfd,
            wallet_instance=self.wallet,
            wallet_file_instance=self.wallet_file,
            no_broadcast=self.no_broadcast,
            no_wallet_file=self.no_wallet_file,
            expiration=self.expiration,
            extensions=extensions)
        tx.appendOps(ops)

        if self.unsigned:
            tx.addSigningInformation(account, permission)
            return tx
        else:
            tx.appendSigner(account, permission)
            tx.sign()

        return tx.broadcast()

    def sign(self, unsigned_trx, wifs=[]):
        """ Sign a provided transaction with the provided key(s)

            :param dict unsigned_trx: The transaction to be signed and returned
            :param string wifs: One or many wif keys to use for signing
                a transaction. If not present, the keys will be loaded
                from the wallet as defined in "missing_signatures" key
                of the transactions.
        """
        tx = TransactionBuilder(
            unsigned_trx,
            beowulfd_instance=self.beowulfd,
            wallet_instance=self.wallet,
            no_broadcast=self.no_broadcast,
            expiration=self.expiration)

        tx.appendMissingSignatures(wifs)
        tx.sign()
        return tx.json()

    def broadcast(self, signed_trx):
        """ Broadcast a transaction to the Beowulf network

            :param tx signed_trx: Signed transaction to broadcast
        """
        tx = TransactionBuilder(
            signed_trx,
            beowulfd_instance=self.beowulfd,
            wallet_instance=self.wallet,
            no_broadcast=self.no_broadcast,
            expiration=self.expiration)
        return tx.broadcast()

    def create_account(
        self,
        account_name,
        json_meta=None,
        owner_keys=[],
        owner_accounts=[],
        owner_weight_threshold=1,
        creator=None,
    ):
        if not creator:
            creator = configStorage.get("default_account")
        if not creator:
            raise ValueError(
                "Not creator account given. Define it with " +
                "creator=x, or set the default_account using beowulfpy")

        required_fee_beowulf = MIN_ACCOUNT_CREATION_FEE.amount

        s = {
            'creator': creator,
            'fee': '%s W' % required_fee_beowulf,
            'json_metadata': json_meta or {},
            'new_account_name': account_name,
            'owner': {
                'account_auths': owner_accounts,
                'key_auths': owner_keys,
                'weight_threshold': (owner_weight_threshold or 1)
            },
            'prefix': self.beowulfd.chain_params["prefix"]
        }
        op = operations.AccountCreate(**s)
        return self.finalizeOp(op, creator, "owner")

    def create_account_simple(
            self,
            account_name,
            json_meta=None,
            password_seed=None,
            owner_key=None,
            store_keys=True,
            store_owner_key=True,
            creator=None,
            password_wallet=None
    ):
        """ Create new account in Beowulf

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
            :param str password_seed: Alternatively to providing keys, one
                                 can provide a password from which the
                                 keys will be derived
            :param password_wallet: Password of wallet file
            :param bool store_keys: Store new keys in the wallet (default:
            ``True``)

            :param bool store_owner_key: Store owner key in the wallet
            (default: ``False``)

            :param str creator: which account should pay the registration fee
                                (defaults to ``default_account``)

            :raises AccountExistsException: if the account already exists on the blockchain
        """
        return self.create_account_advance(account_name=account_name,
                                    json_meta=json_meta,
                                    password_seed=password_seed,
                                    owner_key=owner_key,
                                    store_keys=store_keys,
                                    store_owner_key=store_owner_key,
                                    owner_weight_threshold=1,
                                    creator=creator,
                                    password_wallet=password_wallet)

    def create_account_advance(
            self,
            account_name,
            json_meta=None,
            password_seed=None,
            owner_key=None,
            additional_owner_keys=[],
            additional_owner_accounts=[],
            owner_weight_threshold=1,
            store_keys=True,
            store_owner_key=True,
            creator=None,
            password_wallet=None
    ):
        """ Create new account with advance mode in Beowulf

                    :param str account_name: (**required**) new account name
                    :param str json_meta: Optional meta data for the account
                    :param str owner_key: Main owner key
                    :param str password_seed: Alternatively to providing keys, one
                                         can provide a password from which the
                                         keys will be derived
                    :param password_wallet: Password of wallet file
                    :param list additional_owner_keys:  Additional owner public keys

                    :param list additional_owner_accounts: Additional owner account
                    names
                    :param owner_weight_threshold: Owner weight threshold owner
                    key/account
                    :param bool store_keys: Store new keys in the wallet (default:
                    ``True``)

                    :param bool store_owner_key: Store owner key in the wallet
                    (default: ``False``)

                    :param str creator: which account should pay the registration fee
                                        (defaults to ``default_account``)

                :raises AccountExistsException: if the account already exists on the
                blockchain

                """

        assert MIN_ACCOUNT_NAME_LENGTH < len(
            account_name) <= MAX_ACCOUNT_NAME_LENGTH, "Account name must be 3-16 chars long"

        if not creator:
            creator = configStorage.get("default_account")
        if not creator:
            raise ValueError(
                "Not creator account given. Define it with " +
                "creator=x, or set the default_account using beowulfpy")
        if password_seed and owner_key:
            raise ValueError("You cannot use 'password' AND provide keys!")
        if not password_wallet:
            raise ValueError("You must provide 'password_wallet'!")
        # check if account already exists
        try:
            Account(account_name, beowulfd_instance=self.beowulfd)
        except:  # noqa FIXME
            pass
        else:
            raise AccountExistsException("account has been created")

        " Generate new keys from password"
        from beowulfbase.account import PasswordKey, PublicKey
        if password_seed:
            owner_key = PasswordKey(account_name, password_seed, role="owner")
            owner_pubkey = owner_key.get_public_key()
            owner_privkey = owner_key.get_private_key()
            # store private keys
            if store_keys:
                if store_owner_key:
                    if self.wallet is not None:
                        self.wallet.addPrivateKey(owner_privkey)
                    try:
                        new_wallet_file = WalletFile(password=password_wallet,
                                                     wallet_file=account_name + ".json", account=account_name)
                        new_wallet_file.add_private_key(owner_privkey)
                        new_wallet_file.encrypt_to_cipher_data()
                        new_wallet_file.save_file()
                        logging.info("New wallet file:" + new_wallet_file.wallet_filename)
                        new_wallet_file.purge()
                    except:
                        raise ValueError(
                            "Create new wallet file incomplete!")

        elif owner_key:
            owner_pubkey = PublicKey(format(PrivateKey(owner_key).pubkey,
                                            self.beowulfd.chain_params["prefix"]))
        else:
            raise ValueError(
                "Call incomplete! Provide either a password or public keys!")

        owner = format(owner_pubkey, self.beowulfd.chain_params["prefix"])

        owner_key_authority = [[owner, 1]]
        owner_accounts_authority = []

        total_owner_weight = 1
        # additional authorities
        for k in additional_owner_keys:
            owner_key_authority.append([k, 1])
            total_owner_weight += 1

        for k in additional_owner_accounts:
            owner_accounts_authority.append([k, 1])
            total_owner_weight += 1

        if not owner_weight_threshold:
            owner_weight_threshold = 1

        if total_owner_weight < owner_weight_threshold:
            raise InvalidParamCreateAccount("total weight of owner permission must greater than owner_weight_threshold")

        return self.create_account(account_name=account_name,
                                   json_meta=json_meta,
                                   owner_keys=owner_key_authority,
                                   owner_accounts=owner_accounts_authority,
                                   owner_weight_threshold=owner_weight_threshold,
                                   creator=creator)

    def account_update(
            self,
            account_name,
            json_meta=None,
            password=None,
            owner_key=None,
            store_keys=True,
            store_owner_key=False,
    ):
        """ Create new account in Beowulf

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
            :param str password: Alternatively to providing keys, one
                                 can provide a password from which the
                                 keys will be derived
            :param list additional_owner_keys:  Additional owner public keys

            :param list additional_owner_accounts: Additional owner account
            names

            :param bool store_keys: Store new keys in the wallet (default:
            ``True``)

            :param bool store_owner_key: Store owner key in the wallet
            (default: ``False``)

        :raises AccountExistsException: if the account already exists on the
        blockchain

        """
        assert len(
            account_name) <= 16, "Account name must be at most 16 chars long"

        # check if account already exists
        try:
            Account(account_name, beowulfd_instance=self.beowulfd)
        except:  # noqa FIXME
            raise AccountDoesNotExistsException("Can not update unavailable account")

        " Generate new keys from password"
        from beowulfbase.account import PasswordKey, PublicKey
        if password:
            owner_key = PasswordKey(account_name, password, role="owner")
            owner_pubkey = owner_key.get_public_key()
            owner_privkey = owner_key.get_private_key()
            # store private keys
            if store_keys:
                if store_owner_key:
                    self.wallet.addPrivateKey(owner_privkey)

        elif owner_key:
            owner_pubkey = PublicKey(
                owner_key, prefix=self.beowulfd.chain_params["prefix"])
        else:
            raise ValueError(
                "Call incomplete! Provide either a password or public keys!")

        owner = format(owner_pubkey, self.beowulfd.chain_params["prefix"])

        owner_key_authority = [[owner, 1]]
        owner_accounts_authority = []

        # accounts authen
        for k in owner_accounts_authority:
            owner_accounts_authority.append([k, 1])

        required_fee_beowulf = MIN_ACCOUNT_CREATION_FEE.amount

        s = {
            'account': account_name,
            'fee': '%s W' % required_fee_beowulf,
            'json_metadata': json_meta or {},
            'owner': {
                'account_auths': owner_accounts_authority,
                'key_auths': owner_key_authority,
                'weight_threshold': 1
            },
            'prefix': self.beowulfd.chain_params["prefix"]
        }
        op = operations.AccountUpdate(**s)

        return self.finalizeOp(op, account_name, "owner")

    def transfer(self, to, amount, asset, fee=None, asset_fee=None, memo="", account=None, extensions=None):
        """ Transfer W or BWF to another account.

            :param str to: Recipient

            :param float amount: Amount to transfer

            :param str asset: Asset to transfer (``W`` or ``BWF``)

            :param float fee: Fee to transfer

            :param str asset_fee: Asset fee to transfer (``W``)

            :param str memo: (optional) Memo, may begin with `#` for encrypted
            messaging

            :param str account: (optional) the source account for the transfer
            if not ``default_account``

            :param str extensions: extend data

        """
        if not account:
            account = configStorage.get("default_account")
        if not account:
            raise ValueError("You need to provide an account")

        assert asset in ['BWF', 'W']

        if not fee and not asset_fee:
            fee = MIN_TRANSFER_FEE.amount
            asset_fee = MIN_TRANSFER_FEE.symbol
        else:
            assert asset_fee is 'W'

        if memo and memo[0] == "#":
            from beowulfbase import memo as Memo
            from_account = Account(account, beowulfd_instance=self.beowulfd)
            pub_from = next(iter(from_account["owner"]["key_auths"][0]))
            to_account = Account(to, beowulfd_instance=self.beowulfd)
            pub_to = next(iter(to_account["owner"]["key_auths"][0]))

            if self.no_wallet_file:
                memo_wif = self.wallet.getOwnerKeyForAccount(account)
            else:
                memo_wif = self.wallet_file.get_privkey_from_pubkey_in_wallet_file(pub_from)
            if not memo_wif:
                raise MissingKeyError("Memo key for %s missing!" % account)
            nonce = random.getrandbits(64)
            memo = Memo.encode_memo(
                PrivateKey(memo_wif),
                PublicKey(
                    pub_to,
                    prefix=self.beowulfd.chain_params["prefix"]),
                nonce,
                memo)

        op = operations.Transfer(
            **{
                "from":
                    account,
                "to":
                    to,
                "amount":
                    '{:.{prec}f} {asset}'.format(
                        float(amount), prec=5, asset=asset),
                "fee":
                    '{:.{prec}f} {asset}'.format(
                        float(fee), prec=5, asset=asset_fee),
                "memo":
                    memo
            })
        return self.finalizeOp(op, account, "owner", extensions)

    def create_token(self, creator, control_account, max_supply, decimals, token_name):
        """ Create new token.

            :param str creator: initminer account

            :param str control_account: the account control token

            :param uint64 max_supply: Amount to setup token

            :param uint16 decimals: the decimals place

            :param str token_name: token name
        """
        if not creator:
            creator = configStorage.get("default_account")
        if not creator:
            raise ValueError("You need to provide an account")

        required_fee_beowulf = MIN_TOKEN_CREATION_FEE.amount

        op = operations.SmtCreate(
            **{
                'control_account':
                    control_account,
                'smt_creation_fee':
                    '%s W' % required_fee_beowulf,
                'precision':
                    decimals,
                'creator':
                    creator,
                'symbol': {
                    'decimals': decimals,
                    'name': token_name},
                'max_supply':
                    max_supply,
                'extensions':
                    [],
            })

        new_token = {
            'decimals': decimals,
            'name': token_name}

        return self.finalizeOp(op, creator, "owner"), new_token

    def transfer_token(self, to, amount, asset_name, fee=None, asset_fee=None, memo="", account=None):
        """ Transfer W or BWF to another account.

            :param str to: Recipient

            :param amount: Amount to transfer

            :param asset_name: Name of token to transfer

            :param fee: Fee to transfer

            :param str asset_fee: Asset fee to transfer (``W``)

            :param str memo: (optional) Memo, may begin with `#` for encrypted
            messaging

            :param str account: (optional) the source account for the transfer
            if not ``default_account``
        """
        if not account:
            account = configStorage.get("default_account")
        if not account:
            raise ValueError("You need to provide an account")

        if not fee and not asset_fee:
            fee = MIN_TRANSFER_FEE.amount
            asset_fee = MIN_TRANSFER_FEE.symbol
        else:
            assert asset_fee is 'W'

        if memo and memo[0] == "#":
            from beowulfbase import memo as Memo
            from_account = Account(account, beowulfd_instance=self.beowulfd)
            pub_from = next(iter(from_account["owner"]["key_auths"][0]))
            to_account = Account(to, beowulfd_instance=self.beowulfd)
            pub_to = next(iter(to_account["owner"]["key_auths"][0]))

            if self.no_wallet_file:
                memo_wif = self.wallet.getOwnerKeyForAccount(account)
            else:
                memo_wif = self.wallet_file.get_privkey_from_pubkey_in_wallet_file(pub_from)
            if not memo_wif:
                raise MissingKeyError("Memo key for %s missing!" % account)
            nonce = random.getrandbits(64)
            memo = Memo.encode_memo(
                PrivateKey(memo_wif),
                PublicKey(
                    pub_to,
                    prefix=self.beowulfd.chain_params["prefix"]),
                nonce,
                memo)

        # Get asset token from name
        list_asset_token = self.beowulfd.find_smt_tokens_by_name(asset_name)
        if len(list_asset_token) == 0:
            raise ValueError(
                "Asset token doesn't exist!")

        # Get asset token from name
        asset_token = list_asset_token[0]['liquid_symbol']
        asset_tokens[asset_token['name']] = asset_token['decimals']

        op = operations.Transfer(
            **{
                "from":
                    account,
                "to":
                    to,
                "amount":
                    '{:.{prec}f} {asset}'.format(
                        float(amount), prec=asset_token['decimals'], asset=asset_token['name']),
                "fee":
                    '{:.{prec}f} {asset}'.format(
                        float(fee), prec=5, asset=asset_fee),
                "memo":
                    memo
            })

        try:
            return self.finalizeOp(op, account, "owner")
        except Exception as e:
            raise e
        finally:
            del asset_tokens[asset_token['name']]

    def withdraw_vesting(self, amount, fee=None, account=None):
        """ Withdraw M from the vesting account.

            :param float amount: number of M to withdraw over a period of
            104 weeks

            :param float fee: fee to transfer

            :param str account: (optional) the source account for the transfer
            if not ``default_account``
        """
        if not account:
            account = configStorage.get("default_account")
        if not account:
            raise ValueError("You need to provide an account")

        if not fee:
            fee = MIN_TRANSFER_FEE.amount

        op = operations.WithdrawVesting(
            **{
                "account":
                    account,
                "vesting_shares":
                    '{:.{prec}f} {asset}'.format(
                        float(amount), prec=6, asset="M"),
                "fee":
                    '{:.{prec}f} {asset}'.format(
                        float(fee), prec=5, asset='W'),
            })

        return self.finalizeOp(op, account, "owner")

    def transfer_to_vesting(self, amount, to, fee=None, account=None):
        """ Vest BWF

        :param float amount: number of BWF to vest

        :param float fee: fee to transfer

        :param str to: (optional) the source account for the transfer if not
        ``default_account``

        :param str account: (optional) the source account for the transfer
        if not ``default_account``
        """
        if not account:
            account = configStorage.get("default_account")
        if not account:
            raise ValueError("You need to provide an account")

        if not to:
            to = account  # powerup on the same account

        if not fee:
            fee = MIN_ACCOUNT_CREATION_FEE.amount

        op = operations.TransferToVesting(
            **{
                "from":
                    account,
                "to":
                    to,
                "amount":
                    '{:.{prec}f} {asset}'.format(
                        float(amount), prec=5, asset='BWF'),
                "fee":
                    '{:.{prec}f} {asset}'.format(
                        float(fee), prec=5, asset='W')
            })

        return self.finalizeOp(op, account, "owner")

    def supernode_update(self, signing_key, fee=None, account=None):
        """ Update properties supernode

            :param pubkey signing_key: Signing key
            :param float fee: fee to update supernode
            :param str account: (optional) supernode account name

        """
        if not account:
            account = configStorage.get("default_account")
        if not account:
            raise ValueError("You need to provide an account")

        try:
            PublicKey(signing_key)
        except Exception as e:
            raise e

        if not fee:
            fee = MIN_ACCOUNT_CREATION_FEE.amount

        op = operations.SupernodeUpdate(
            **{
                "owner": account,
                "block_signing_key": signing_key,
                "fee":
                    '{:.{prec}f} {asset}'.format(
                        float(fee), prec=5, asset='W'),
                "prefix": self.beowulfd.chain_params["prefix"]
            })
        return self.finalizeOp(op, account, "owner")

    @staticmethod
    def _test_weights_treshold(authority):
        weights = 0
        for a in authority["account_auths"]:
            weights += a[1]
        for a in authority["key_auths"]:
            weights += a[1]
        if authority["weight_threshold"] > weights:
            raise ValueError("Threshold too restrictive!")

    def approve_supernode(self, supernode, account=None, vesting_shares=None, fee=None, approve=True):
        """ Vote **for** a supernode. This method adds a supernode to your
            set of approved supernodes. To remove supernodes see
            ``disapprove_supernode``.

            :param str supernode: supernode to approve
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
            :param float fee: fee to vote supernode

        """
        if not account:
            account = configStorage.get("default_account")
        if not account:
            raise ValueError("You need to provide an account")

        if not fee:
            fee = MIN_ACCOUNT_CREATION_FEE.amount

        op = operations.AccountSupernodeVote(**{
            "account": account,
            "supernode": supernode,
            "approve": approve,
            "votes": vesting_shares,
            "fee":
                '{:.{prec}f} {asset}'.format(
                    float(fee), prec=5, asset='W'),
        })
        return self.finalizeOp(op, account, "owner")

    def disapprove_supernode(self, supernode, account=None, vesting_shares=None, fee=None):
        """ Remove vote for a supernode. This method removes
            a supernode from your set of approved supernodes. To add
            supernodes see ``approve_supernode``.

            :param str supernode: supernode to approve
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
            :param float fee: fee to unvote supernode

        """
        return self.approve_supernode(
            supernode=supernode, account=account, vesting_shares=vesting_shares, approve=False, fee=fee)
