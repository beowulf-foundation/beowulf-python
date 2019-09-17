import base64
import hashlib
import json
import os
from binascii import hexlify, unhexlify
import Crypto
from Crypto import Random
from Crypto.Cipher import AES
from appdirs import user_data_dir
from beowulfbase.account import PrivateKey
from beowulf.utils import compat_bytes

appname = "BWF"
appauthor = "Kdev Team"
wallet_dir = user_data_dir(appname, appauthor)

SALT_SIZE = 16

# number of iterations in the key generation
NUMBER_OF_ITERATIONS = 20

# the size multiple required for AES
AES_MULTIPLE = 16


class WalletFile(object):
    """ The keys are encrypted with a KeyEncryptionKey that is stored in
        the configurationStore. It has a checksum to verify correctness
        of the user_passphrase
    """
    wallet_filename = ""
    user_passphrase = ""
    username = ""
    plain_keys = {}
    cipher_data = {}
    is_opened = False

    #: This key identifies the encrypted KeyEncryptionKey
    # stored in the configuration
    default_wallet = "wallet.json"
    default_account = "default account"
    default_password = "default password"

    def __init__(self, **kwargs):
        """ The encrypted private keys in `keys` are encrypted with a
            random encrypted KeyEncryptionKey that is stored in the
            configuration.

            The user_passphrase is used to encrypt this KeyEncryptionKey. To
            decrypt the keys stored in the keys database, one must use
            BIP38, decrypt the KeyEncryptionKey from the configuration
            store with the user_passphrase, and use the decrypted
            KeyEncryptionKey to decrypt the BIP38 encrypted private keys
            from the keys storage!

            :param str user_passphrase: Password to use for en-/de-cryption
        """

        self.user_passphrase = kwargs.get("password")
        if self.user_passphrase is None:
            self.user_passphrase = self.default_password

        self.username = kwargs.get("account")
        if self.username is None:
            self.username = self.default_account

        self.wallet_filename = os.path.join(wallet_dir, kwargs.get("wallet_file", self.default_wallet))

        self.plain_keys = {
            "keys": []}

    def derive_key(self, passphrase: str, salt: bytes = None) -> [str, bytes]:
        if salt is None:
            salt = Crypto.Random.get_random_bytes(SALT_SIZE)
        return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf8"), salt, 1000), salt

    def derive_cipher_data(self, cipher_keys, salt, checksum_rawkeys, cipher_type="aes-256-cbc"):
        self.cipher_data['cipher_keys'] = hexlify(cipher_keys).decode('utf8')
        self.cipher_data['salt'] = base64.b64encode(salt).decode('utf-8')
        self.cipher_data['checksum_rawkeys'] = checksum_rawkeys
        self.cipher_data['cipher_type'] = cipher_type
        self.cipher_data['account'] = self.username

    @staticmethod
    def derive_checksum(s):
        checksum = hashlib.sha512(compat_bytes(s, "ascii")).hexdigest()
        return checksum

    @staticmethod
    def _pad_text(text, multiple):
        extra_bytes = len(text) % multiple
        padding_size = multiple - extra_bytes
        padding = chr(padding_size) * padding_size
        padded_text = text + padding
        return padded_text

    @staticmethod
    def _unpad_text(padded_text):
        padding_size = ord(padded_text[-1])
        text = padded_text[:-padding_size]
        return text

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def encrypt_to_cipher_data(self):
        if any(self.plain_keys):
            key, salt = self.derive_key(self.user_passphrase)
            iv = key[:AES.block_size]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_plaintext = self._pad_text(json.dumps(self.plain_keys), AES_MULTIPLE)
            checksum_rawkeys = self.derive_checksum(json.dumps(self.plain_keys))

            try:
                if not self.plain_keys:
                    raise Exception("Key not decrypted")
                cipher_keys = cipher.encrypt(str.encode(padded_plaintext))
            except Exception as e:
                raise e
            self.derive_cipher_data(cipher_keys, salt, checksum_rawkeys)
        else:
            raise Exception("Missing Data Cipher")

    def decrypt_from_cipher_data(self):
        if self.is_opened:
            if not self.cipher_data:
                raise Exception("Can not load file wallet")
            cipher_text = unhexlify(self.cipher_data['cipher_keys'])
            key, _ = self.derive_key(self.user_passphrase, base64.b64decode(self.cipher_data['salt']))
            iv = key[:AES.block_size]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            try:
                padded_plaintext = cipher.decrypt(cipher_text)
            except Exception as e:
                raise e

            try:
                plain_Keys = self._unpad_text(padded_plaintext.decode("utf-8"))
                check = self.derive_checksum(plain_Keys)
                if self.cipher_data['checksum_rawkeys'] != check:
                    raise Exception("Wrong password")
            except Exception as e:
                raise e("Can not Unpad")

            self.plain_keys = json.loads(plain_Keys)
        else:
            raise Exception("Missing File Wallet")

    def get_privkey_from_pubkey_in_wallet_file(self, pub):
        if self.is_opened:
            for keypairs in self.plain_keys['keys']:
                if keypairs[0] == pub:
                    return keypairs[1]
            return None
        else:
            raise Exception("Missing File Wallet")

    def add_private_key(self, wif):
        """ Add a private key to the wallet database
        """
        if isinstance(wif, PrivateKey) or isinstance(wif, PrivateKey):
            wif = str(wif)
        try:
            pub = format(PrivateKey(wif).pubkey, "BEO")
        except:
            raise Exception(
                "Invalid Private Key Format. Please use WIF!")
        keypair = [pub, wif]
        self.plain_keys['keys'].append(keypair)

    def change_passphrase(self, newpassphrase):
        """ Change the passphrase
        """
        if self.is_opened:
            self.user_passphrase = newpassphrase
            self.encrypt_to_cipher_data()
        else:
            raise Exception("Missing File Wallet")

    def save_file(self):
        """ Store the encrypted Key in file .json
        """
        if any(self.cipher_data):
            cipherData = json.dumps(self.cipher_data)
            try:
                if not os.path.exists(self.wallet_filename):
                    with open(self.wallet_filename, 'w'): pass

                f = open(self.wallet_filename, "w")
                f.write(cipherData)
                f.close()
            except Exception as e:
                raise e
        else:
            raise Exception("Keys haven't been encrypted yet")

    def open_file(self):
        if self.is_opened:
            self.purge()

        if not os.path.exists(self.wallet_filename):
            with open(self.wallet_filename, 'w'): pass

        with open(self.wallet_filename) as json_data:
            cipherData = json.load(json_data)
            try:
                self.cipher_data = cipherData
                self.is_opened = True
            except Exception as e:
                raise e("File doesn't have right format")

    def set_up_wallet(self):
        self.open_file()
        self.decrypt_from_cipher_data()

    def purge(self):
        """ Remove the KeyEncryptionKey from the configuration store
        """
        self.wallet_filename = ""
        self.user_passphrase = ""
        self.username = ""
        self.plain_keys = {}
        self.cipher_data = {}
        self.is_opened = False
