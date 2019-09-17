import logging
from beowulfbase import operations
from beowulfbase.account import PrivateKey
from beowulfbase.exceptions import (InsufficientAuthorityError, MissingKeyError,
                                    InvalidKeyFormat)
from beowulfbase.operations import Operation
from beowulfbase.transactions import SignedTransaction, fmt_time_from_now, \
    get_block_params, fmt_time_from_now_to_epoch
from .account import Account
from .instance import shared_beowulfd_instance

log = logging.getLogger(__name__)


class TransactionBuilder(dict):
    """ This class simplifies the creation of transactions by adding
        operations and signers.
    """

    def __init__(self,
                 tx=None,
                 beowulfd_instance=None,
                 wallet_instance=None,
                 wallet_file_instance=None,
                 no_broadcast=False,
                 no_wallet_file=True,
                 expiration=60):
        self.beowulfd = beowulfd_instance or shared_beowulfd_instance()
        self.no_broadcast = no_broadcast
        self.no_wallet_file = no_wallet_file
        self.expiration = expiration
        self.wallet = wallet_instance
        self.wallet_file = wallet_file_instance
        self.op = []
        self.wifs = []
        if tx and not isinstance(tx, dict):
            raise ValueError("Invalid Transaction (self.tx) Format")
        super(TransactionBuilder, self).__init__(tx or {})

    def appendOps(self, ops):
        if isinstance(ops, list):
            for op in ops:
                self.op.append(op)
        else:
            self.op.append(ops)
        self.constructTx()

    def appendSigner(self, account, permission):
        assert permission in ["owner"], "Invalid permission"
        account = Account(account, beowulfd_instance=self.beowulfd)

        required_treshold = account[permission]["weight_threshold"]

        def fetchkeys(account, level=0):
            if level > 2:
                return []
            r = []
            for authority in account[permission]["key_auths"]:
                if not self.no_wallet_file:
                    wif = self.wallet_file.get_privkey_from_pubkey_in_wallet_file(authority[0])
                else:
                    wif = self.wallet.getPrivateKeyForPublicKey(authority[0])
                if wif:
                    r.append([wif, authority[1]])

            if sum([x[1] for x in r]) < required_treshold:
                # go one level deeper
                for authority in account[permission]["account_auths"]:
                    auth_account = Account(
                        authority[0], beowulfd_instance=self.beowulfd)
                    r.extend(fetchkeys(auth_account, level + 1))

            return r

        keys = fetchkeys(account)
        self.wifs.extend([x[0] for x in keys])

    def appendWif(self, wif):
        if wif:
            try:
                PrivateKey(wif)
                self.wifs.append(wif)
            except:  # noqa FIXME
                raise InvalidKeyFormat

    def constructTx(self):
        if isinstance(self.op, list):
            ops = [Operation(o) for o in self.op]
        else:
            ops = [Operation(self.op)]
        expiration = fmt_time_from_now(self.expiration)
        ref_block_num, ref_block_prefix = get_block_params(self.beowulfd)
        created_time = fmt_time_from_now_to_epoch()
        tx = SignedTransaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops,
            created_time=created_time)
        super(TransactionBuilder, self).__init__(tx.json())

    def sign(self):
        """ Sign a provided transaction witht he provided key(s)

            :param dict tx: The transaction to be signed and returned
            :param string wifs: One or many wif keys to use for signing
                a transaction. If not present, the keys will be loaded
                from the wallet as defined in "missing_signatures" key
                of the transactions.
        """

        # We need to set the default prefix, otherwise pubkeys are
        # presented wrongly!
        if self.beowulfd:
            operations.default_prefix = self.beowulfd.chain_params["prefix"]
        elif "blockchain" in self:
            operations.default_prefix = self["blockchain"]["prefix"]

        try:
            # not signed yet
            signedtx = SignedTransaction(**self.json())
        except Exception as e:  # noqa FIXME
            raise e

        if not any(self.wifs):
            raise MissingKeyError

        signedtx.sign(self.wifs, chain=self.beowulfd.chain_params)

        self["signatures"].extend(signedtx.json().get("signatures"))

    def broadcast(self):
        """ Broadcast a transaction to the Beowulf network

            :param tx tx: Signed transaction to broadcast
        """
        if self.no_broadcast:
            log.warning("Not broadcasting anything!")
            return self

        try:
            if not self.beowulfd.verify_authority(self.json()):
                raise InsufficientAuthorityError
        except Exception as e:
            # There is an issue with some appbase builds which makes
            # `verify_authority` unusable. TODO: remove this case #212
            if 'Bad Cast:Invalid cast from string_type to Array' in str(e):
                log.error("Ignoring verify_authority failure. See #212.")
            else:
                raise e

        try:
            response = self.beowulfd.broadcast_transaction_synchronous(self.json())
            return response

        except Exception as e:
            raise e

        return self

    def addSigningInformation(self, account, permission):
        """ This is a private method that adds side information to a
            unsigned/partial transaction in order to simplify later
            signing (e.g. for multisig or coldstorage)
        """
        accountObj = Account(account, beowulfd_instance=self.beowulfd)
        authority = accountObj[permission]
        # We add a required_authorities to be able to identify
        # how to sign later. This is an array, because we
        # may later want to allow multiple operations per tx
        self.update({"required_authorities": {account: authority}})
        for account_auth in authority["account_auths"]:
            account_auth_account = Account(
                account_auth[0], beowulfd_instance=self.beowulfd)
            self["required_authorities"].update({
                account_auth[0]:
                    account_auth_account.get(permission)
            })

        # Try to resolve required signatures for offline signing
        self["missing_signatures"] = [x[0] for x in authority["key_auths"]]
        # Add one recursion of keys from account_auths:
        for account_auth in authority["account_auths"]:
            account_auth_account = Account(
                account_auth[0], beowulfd_instance=self.beowulfd)
            self["missing_signatures"].extend(
                [x[0] for x in account_auth_account[permission]["key_auths"]])
        self["blockchain"] = self.beowulfd.chain_params

    def json(self):
        return dict(self)

    def appendMissingSignatures(self, wifs):
        missing_signatures = self.get("missing_signatures", [])
        for pub in missing_signatures:
            wif = self.wallet.getPrivateKeyForPublicKey(pub)
            if wif:
                self.appendWif(wif)
