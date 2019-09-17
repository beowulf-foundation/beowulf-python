import argparse
import json
import logging
import os
import pprint
import re
import sys
import click._compat
import pkg_resources
from prettytable import PrettyTable
import beowulf as bwf
from beowulfbase.account import PrivateKey
from beowulfbase.storage import configStorage
from .account import Account
from .amount import Amount
from .block import Block
from .blockchain import Blockchain
from .instance import shared_beowulfd_instance
from .supernode import Supernode

availableConfigurationKeys = [
    "default_account",
    "default_vote_weight",
    "nodes",
]


def legacyentry():
    """
    Piston like cli application.
    This will be re-written as a @click app in the future.
    """
    global args

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Command line tool to interact with the Beowulf network")
    """
        Default settings for all tools
    """
    parser.add_argument(
        '--node',
        type=str,
        default=configStorage["node"],
        help='URL for public Beowulf API (default: "https://bw.beowulfchain.com")'
    )

    parser.add_argument(
        '--no-broadcast',
        '-d',
        action='store_true',
        help='Do not broadcast anything')
    parser.add_argument(
        '--no-wallet',
        '-p',
        action='store_true',
        help='Do not load the wallet')
    parser.add_argument(
        '--unsigned',
        '-x',
        action='store_true',
        help='Do not try to sign the transaction')
    parser.add_argument(
        '--expires',
        '-e',
        default=60,
        help='Expiration time in seconds (defaults to 60)')
    parser.add_argument(
        '--verbose', '-v', type=int, default=3, help='Verbosity')
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {version}'.format(
            version=pkg_resources.require("beowulf")[0].version))

    subparsers = parser.add_subparsers(help='sub-command help')
    """
        Command "set"
    """
    setconfig = subparsers.add_parser('set', help='Set configuration')
    setconfig.add_argument(
        'key',
        type=str,
        choices=availableConfigurationKeys,
        help='Configuration key')
    setconfig.add_argument('value', type=str, help='Configuration value')
    setconfig.set_defaults(command="set")
    """
        Command "config"
    """
    configconfig = subparsers.add_parser(
        'config', help='Show local configuration')
    configconfig.set_defaults(command="config")
    """
        Command "info"
    """
    parser_info = subparsers.add_parser(
        'info', help='Show basic BWF blockchain info')
    parser_info.set_defaults(command="info")
    parser_info.add_argument(
        'objects',
        nargs='*',
        type=str,
        help='General information about the blockchain, a block, an account'
             ' name, a post, a public key, ...')
    """
        Command "changewalletpassphrase"
    """
    changepasswordconfig = subparsers.add_parser(
        'changewalletpassphrase', help='Change wallet password')
    changepasswordconfig.set_defaults(command="changewalletpassphrase")
    """
        Command "addkey"
    """
    addkey = subparsers.add_parser(
        'addkey', help='Add a new key to the wallet')
    addkey.add_argument(
        '--unsafe-import-key',
        nargs='*',
        type=str,
        help='private key to import into the wallet (unsafe, unless you ' +
             'delete your shell history)')
    addkey.set_defaults(command="addkey")

    parsewif = subparsers.add_parser(
        'parsewif', help='Parse a WIF private key without importing')
    parsewif.add_argument(
        '--unsafe-import-key',
        nargs='*',
        type=str,
        help='WIF key to parse (unsafe, delete your bash history)')
    parsewif.set_defaults(command='parsewif')
    """
        Command "delkey"
    """
    delkey = subparsers.add_parser(
        'delkey', help='Delete keys from the wallet')
    delkey.add_argument(
        'pub',
        nargs='*',
        type=str,
        help='the public key to delete from the wallet')
    delkey.set_defaults(command="delkey")
    """
        Command "getkey"
    """
    getkey = subparsers.add_parser(
        'getkey', help='Dump the privatekey of a pubkey from the wallet')
    getkey.add_argument(
        'pub',
        type=str,
        help='the public key for which to show the private key')
    getkey.set_defaults(command="getkey")
    """
        Command "listkeys"
    """
    listkeys = subparsers.add_parser(
        'listkeys', help='List available keys in your wallet')
    listkeys.set_defaults(command="listkeys")
    """
        Command "listaccounts"
    """
    listaccounts = subparsers.add_parser(
        'listaccounts', help='List available accounts in your wallet')
    listaccounts.set_defaults(command="listaccounts")
    """

        Command "transfer"
    """
    parser_transfer = subparsers.add_parser('transfer', help='Transfer BWF')
    parser_transfer.set_defaults(command="transfer")
    parser_transfer.add_argument('to', type=str, help='Recipient')
    parser_transfer.add_argument(
        'amount', type=float, help='Amount to transfer')
    parser_transfer.add_argument(
        'asset',
        type=str,
        choices=["BWF", "W"],
        help='Asset to transfer (i.e. BWF or W)')
    parser_transfer.add_argument(
        'fee', type=float, help='Fee to transfer')
    parser_transfer.add_argument(
        'asset_fee',
        type=str,
        choices=["W"],
        help='Asset fee to transfer (W)')
    parser_transfer.add_argument(
        'memo', type=str, nargs="?", default="", help='Optional memo')
    parser_transfer.add_argument(
        '--account',
        type=str,
        required=False,
        default=configStorage["default_account"],
        help='Transfer from this account')
    """
        Command "convert"
    """
    parser_convert = subparsers.add_parser(
        'convert',
        help='Convert BWFDollars to Beowulf (takes a week to settle)')
    parser_convert.set_defaults(command="convert")
    parser_convert.add_argument(
        'amount', type=float, help='Amount of W to convert')
    parser_convert.add_argument(
        '--account',
        type=str,
        required=False,
        default=configStorage["default_account"],
        help='Convert from this account')
    """
        Command "balance"
    """
    parser_balance = subparsers.add_parser(
        'balance', help='Show the balance of one more more accounts')
    parser_balance.set_defaults(command="balance")
    parser_balance.add_argument(
        'account',
        type=str,
        nargs="*",
        default=configStorage["default_account"],
        help='balance of these account (multiple accounts allowed)')
    """
        Command "newaccount"
    """
    parser_newaccount = subparsers.add_parser(
        'newaccount', help='Create a new account')
    parser_newaccount.set_defaults(command="newaccount")
    parser_newaccount.add_argument(
        'accountname', type=str, help='New account name')
    parser_newaccount.add_argument(
        '--account',
        type=str,
        required=False,
        default=configStorage["default_account"],
        help='Account that pays the fee')

    """
        Command "importaccount"
    """
    parser_importaccount = subparsers.add_parser(
        'importaccount', help='Import an account using a passphrase')
    parser_importaccount.set_defaults(command="importaccount")
    parser_importaccount.add_argument('account', type=str, help='Account name')
    parser_importaccount.add_argument(
        '--roles',
        type=str,
        nargs="*",
        default=["owner"],  # no owner
        help='Import specified keys (owner, active, posting, memo)')
    """
        Command "approvesupernode"
    """
    parser_approvesupernode = subparsers.add_parser(
        'approvesupernode', help='Approve a supernodees')
    parser_approvesupernode.set_defaults(command="approvesupernode")
    parser_approvesupernode.add_argument(
        'supernode', type=str, help='Supernode to approve')
    parser_approvesupernode.add_argument(
        '--account',
        type=str,
        required=False,
        default=configStorage["default_account"],
        help='Your account')
    """
        Command "disapprovesupernode"
    """
    parser_disapprovesupernode = subparsers.add_parser(
        'disapprovesupernode', help='Disapprove a supernodees')
    parser_disapprovesupernode.set_defaults(command="disapprovesupernode")
    parser_disapprovesupernode.add_argument(
        'supernode', type=str, help='Supernode to disapprove')
    parser_disapprovesupernode.add_argument(
        '--account',
        type=str,
        required=False,
        default=configStorage["default_account"],
        help='Your account')
    """
        Command "sign"
    """
    parser_sign = subparsers.add_parser(
        'sign',
        help='Sign a provided transaction with available and required keys')
    parser_sign.set_defaults(command="sign")
    parser_sign.add_argument(
        '--file',
        type=str,
        required=False,
        help='Load transaction from file. If "-", read from ' +
             'stdin (defaults to "-")')
    """
        Command "broadcast"
    """
    parser_broadcast = subparsers.add_parser(
        'broadcast', help='broadcast a signed transaction')
    parser_broadcast.set_defaults(command="broadcast")
    parser_broadcast.add_argument(
        '--file',
        type=str,
        required=False,
        help='Load transaction from file. If "-", read from ' +
             'stdin (defaults to "-")')
    """
        Command "supernodeupdate"
    """
    parser_supernodeprops = subparsers.add_parser(
        'supernodeupdate', help='Change supernode properties')
    parser_supernodeprops.set_defaults(command="supernodeupdate")
    parser_supernodeprops.add_argument(
        '--supernode',
        type=str,
        default=configStorage["default_account"],
        help='Supernode name')
    parser_supernodeprops.add_argument(
        '--maximum_block_size',
        type=float,
        required=False,
        help='Max block size')
    parser_supernodeprops.add_argument(
        '--account_creation_fee',
        type=float,
        required=False,
        help='Account creation fee')
    parser_supernodeprops.add_argument(
        '--signing_key', type=str, required=False, help='Signing Key')
    """
        Command "supernodecreate"
    """
    parser_supernodecreate = subparsers.add_parser(
        'supernodecreate', help='Create a supernode')
    parser_supernodecreate.set_defaults(command="supernodecreate")
    parser_supernodecreate.add_argument('supernode', type=str, help='Supernode name')
    parser_supernodecreate.add_argument(
        'signing_key', type=str, help='Signing Key')
    parser_supernodecreate.add_argument(
        '--maximum_block_size',
        type=float,
        default="65536",
        help='Max block size')
    parser_supernodecreate.add_argument(
        '--account_creation_fee',
        type=float,
        default=30,
        help='Account creation fee')
    """
        Parse Arguments
    """
    args = parser.parse_args()

    # Logging
    log = logging.getLogger(__name__)
    verbosity = ["critical", "error", "warn", "info", "debug"][int(
        min(args.verbose, 4))]
    log.setLevel(getattr(logging, verbosity.upper()))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, verbosity.upper()))
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # GrapheneAPI logging
    if args.verbose > 4:
        verbosity = ["critical", "error", "warn", "info", "debug"][int(
            min((args.verbose - 4), 4))]
        gphlog = logging.getLogger("graphenebase")
        gphlog.setLevel(getattr(logging, verbosity.upper()))
        gphlog.addHandler(ch)
    if args.verbose > 8:
        verbosity = ["critical", "error", "warn", "info", "debug"][int(
            min((args.verbose - 8), 4))]
        gphlog = logging.getLogger("grapheneapi")
        gphlog.setLevel(getattr(logging, verbosity.upper()))
        gphlog.addHandler(ch)

    if not hasattr(args, "command"):
        parser.print_help()
        sys.exit(2)

    # initialize BWF instance
    options = {
        "node": args.node,
        "unsigned": args.unsigned,
        "expires": args.expires
    }
    if args.command == "sign":
        options.update({"offline": True})
    if args.no_wallet:
        options.update({"wif": []})

    beowulf = bwf.Beowulf(no_broadcast=args.no_broadcast, **options)

    if args.command == "set":
        # TODO: Evaluate this line with cli refactor.
        if (args.key in ["default_account"] and args.value[0] == "@"):
            args.value = args.value[1:]
        configStorage[args.key] = args.value

    elif args.command == "config":
        t = PrettyTable(["Key", "Value"])
        t.align = "l"
        for key in configStorage:
            # hide internal config data
            if key in availableConfigurationKeys:
                t.add_row([key, configStorage[key]])
        print(t)

    elif args.command == "info":
        if not args.objects:
            t = PrettyTable(["Key", "Value"])
            t.align = "l"
            blockchain = Blockchain(mode="head")
            info = blockchain.info()
            for key in info:
                t.add_row([key, info[key]])
            print(t.get_string(sortby="Key"))

        for obj in args.objects:
            # Block
            if re.match("^[0-9]*$", obj):
                block = Block(obj)
                if block:
                    t = PrettyTable(["Key", "Value"])
                    t.align = "l"
                    for key in sorted(block):
                        value = block[key]
                        if key == "transactions":
                            value = json.dumps(value, indent=4)
                        t.add_row([key, value])
                    print(t)
                else:
                    print("Block number %s unknown" % obj)
            # Account name
            elif re.match("^[a-zA-Z0-9\-\._]{2,16}$", obj):
                from math import log10
                account = Account(obj)
                t = PrettyTable(["Key", "Value"])
                t.align = "l"
                for key in sorted(account):
                    value = account[key]
                    if key == "json_metadata":
                        value = json.dumps(json.loads(value or "{}"), indent=4)
                    if key in ["supernode_votes", "owner"]:
                        value = json.dumps(value, indent=4)
                    if key == "reputation" and int(value) > 0:
                        value = int(value)
                        rep = (max(log10(value) - 9, 0) * 9 + 25 if value > 0
                               else max(log10(-value) - 9, 0) * -9 + 25)
                        value = "{:.2f} ({:d})".format(rep, value)
                    t.add_row([key, value])
                print(t)

                # supernode available?
                try:
                    supernode = Supernode(obj)
                    t = PrettyTable(["Key", "Value"])
                    t.align = "l"
                    for key in sorted(supernode):
                        value = supernode[key]
                        if key in ["props", "wd_exchange_rate"]:
                            value = json.dumps(value, indent=4)
                        t.add_row([key, value])
                    print(t)
                except:  # noqa FIXME
                    pass
            # Public Key
            elif re.match("^BEO.{48,55}$", obj):
                account = beowulf.commit.wallet.getAccountFromPublicKey(obj)
                if account:
                    t = PrettyTable(["Account"])
                    t.align = "l"
                    t.add_row([account])
                    print(t)
                else:
                    print("Public Key not known" % obj)
            else:
                print("Couldn't identify object to read")

    elif args.command == "changewalletpassphrase":
        beowulf.commit.wallet.changeUserPassphrase()

    elif args.command == "addkey":
        if args.unsafe_import_key:
            for key in args.unsafe_import_key:
                try:
                    beowulf.commit.wallet.add_private_key(key)
                except Exception as e:
                    print(str(e))
        else:
            import getpass
            while True:
                wifkey = getpass.getpass('Private Key (wif) [Enter to quit]:')
                if not wifkey:
                    break
                try:
                    beowulf.commit.wallet.add_private_key(wifkey)
                except Exception as e:
                    print(str(e))
                    continue

                installed_keys = beowulf.commit.wallet.getPublicKeys()
                if len(installed_keys) == 1:
                    name = beowulf.commit.wallet.getAccountFromPublicKey(
                        installed_keys[0])
                    print("=" * 30)
                    print("Would you like to make %s a default user?" % name)
                    print()
                    print("You can set it with with:")
                    print("    beowulfpy set default_account <account>")
                    print("=" * 30)

    elif args.command == "delkey":
        if confirm("Are you sure you want to delete keys from your wallet?\n"
                   "This step is IRREVERSIBLE! If you don't have a backup, "
                   "You may lose access to your account!"):
            for pub in args.pub:
                beowulf.commit.wallet.removePrivateKeyFromPublicKey(pub)

    elif args.command == "parsewif":
        if args.unsafe_import_key:
            for key in args.unsafe_import_key:
                try:
                    print(PrivateKey(key).pubkey)
                except Exception as e:
                    print(str(e))
        else:
            import getpass
            while True:
                wifkey = getpass.getpass('Private Key (wif) [Enter to quit:')
                if not wifkey:
                    break
                try:
                    print(PrivateKey(wifkey).pubkey)
                except Exception as e:
                    print(str(e))
                    continue
    elif args.command == "getkey":
        print(beowulf.commit.wallet.getPrivateKeyForPublicKey(args.pub))

    elif args.command == "listkeys":
        t = PrettyTable(["Available Key"])
        t.align = "l"
        for key in beowulf.commit.wallet.getPublicKeys():
            t.add_row([key])
        print(t)

    elif args.command == "listaccounts":
        t = PrettyTable(["Name", "Type", "Available Key"])
        t.align = "l"
        for account in beowulf.commit.wallet.getAccounts():
            t.add_row([
                account["name"] or "n/a", account["type"] or "n/a",
                account["pubkey"]
            ])
        print(t)

    elif args.command == "transfer":
        print_json(
            beowulf.commit.transfer(
                args.to,
                args.amount,
                args.asset,
                args.fee,
                args.asset_fee,
                memo=args.memo,
                account=args.account))

    elif args.command == "convert":
        print_json(beowulf.commit.convert(
            args.amount,
            account=args.account,
        ))

    elif args.command == "balance":
        if args.account and isinstance(args.account, list):
            for account in args.account:
                a = Account(account)

                print("\n%s" % a.name)
                t = PrettyTable(["Account", "BWF", "W", "M"])
                t.align = "r"
                t.add_row([
                    'Available',
                    a.balances['available']['BWF'],
                    a.balances['available']['W'],
                    a.balances['available']['M'],
                ])
                t.add_row([
                    'Rewards',
                    a.balances['rewards']['BWF'],
                    a.balances['rewards']['W'],
                    a.balances['rewards']['M'],
                ])
                t.add_row([
                    'TOTAL',
                    a.balances['total']['BWF'],
                    a.balances['total']['W'],
                    a.balances['total']['M'],
                ])
                print(t)
        else:
            print("Please specify an account: beowulfpy balance <account>")

    elif args.command == "permissions":
        account = Account(args.account)
        print_permissions(account)

    elif args.command == "newaccount":
        import getpass
        while True:
            pw = getpass.getpass("New Account Passphrase: ")
            if not pw:
                print("You cannot chosen an empty password!")
                continue
            else:
                pwck = getpass.getpass("Confirm New Account Passphrase: ")
                if pw == pwck:
                    break
                else:
                    print("Given Passphrases do not match!")
        print_json(
            beowulf.commit.create_account(
                args.accountname,
                creator=args.account,
                password=pw,
            ))

    elif args.command == "importaccount":
        from beowulfbase.account import PasswordKey
        import getpass
        password = getpass.getpass("Account Passphrase: ")
        account = Account(args.account)
        imported = False

        if "owner" in args.roles:
            owner_key = PasswordKey(args.account, password, role="owner")
            owner_pubkey = format(owner_key.get_public_key(), "BEO")
            if owner_pubkey in [x[0] for x in account["owner"]["key_auths"]]:
                print("Importing owner key!")
                owner_privkey = owner_key.get_private_key()
                beowulf.commit.wallet.add_private_key(owner_privkey)
                imported = True

        if not imported:
            print("No matching key(s) found. Password correct?")

    elif args.command == "sign":
        if args.file and args.file != "-":
            if not os.path.isfile(args.file):
                raise Exception("File %s does not exist!" % args.file)
            with open(args.file) as fp:
                tx = fp.read()
        else:
            tx = sys.stdin.read()
        tx = eval(tx)
        print_json(beowulf.commit.sign(tx))

    elif args.command == "broadcast":
        if args.file and args.file != "-":
            if not os.path.isfile(args.file):
                raise Exception("File %s does not exist!" % args.file)
            with open(args.file) as fp:
                tx = fp.read()
        else:
            tx = sys.stdin.read()
        tx = eval(tx)
        beowulf.commit.broadcast(tx)

    elif args.command == "approvesupernode":
        print_json(
            beowulf.commit.approve_supernode(args.supernode, account=args.account))

    elif args.command == "disapprovesupernode":
        print_json(
            beowulf.commit.disapprove_supernode(
                args.supernode, account=args.account))

    elif args.command == "supernodeupdate":

        supernode = Supernode(args.supernode)
        props = supernode["props"]
        if args.account_creation_fee:
            props["account_creation_fee"] = str(
                Amount("%f BWF" % args.account_creation_fee))
        if args.maximum_block_size:
            props["maximum_block_size"] = args.maximum_block_size

        print_json(
            beowulf.commit.supernode_update(
                args.signing_key or supernode["signing_key"],
                props,
                account=args.supernode))

    elif args.command == "supernodecreate":
        props = {
            "account_creation_fee":
                str(Amount("%f BWF" % args.account_creation_fee)),
            "maximum_block_size":
                args.maximum_block_size
        }
        print_json(
            beowulf.commit.supernode_update(
                args.signing_key, props, account=args.supernode))

    else:
        print("No valid command given")


def confirm(question, default="yes"):
    """ Confirmation dialog that requires *manual* input.

        :param str question: Question to ask the user
        :param str default: default answer
        :return: Choice of the user
        :rtype: bool

    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        # Python 2.7 `input` attempts to evaluate the input, while in 3+
        # it returns a string. Python 2.7 `raw_input` returns a str as desired.
        if sys.version >= '3.0':
            choice = input().lower()
        else:
            choice = click._compat.raw_input().lower()

        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_terminal(text="Password", confirm=False, allowedempty=False):
    import getpass
    while True:
        pw = getpass.getpass(text)
        if not pw and not allowedempty:
            print("Cannot be empty!")
            continue
        else:
            if not confirm:
                break
            pwck = getpass.getpass("Confirm " + text)
            if pw == pwck:
                break
            else:
                print("Not matching!")
    return pw


def format_operation_details(op, memos=False):

    if op[0] == "transfer":
        str_ = "%s -> %s %s" % (
            op[1]["from"],
            op[1]["to"],
            op[1]["amount"],
            op[1]["fee"],
        )

        if memos:
            memo = op[1]["memo"]
            if len(memo) > 0 and memo[0] == "#":
                beowulf = shared_beowulfd_instance()
                # memo = beowulf.decode_memo(memo, op[1]["from"])
                memo = beowulf.decode_memo(memo, op)
            str_ += " (%s)" % memo
        return str_
    else:
        return json.dumps(op[1], indent=4)


def print_permissions(account):
    t = PrettyTable(["Permission", "Threshold", "Key/Account"], hrules=0)
    t.align = "r"
    for permission in ["owner"]:
        auths = []
        for type_ in ["account_auths", "key_auths"]:
            for authority in account[permission][type_]:
                auths.append("%s (%d)" % (authority[0], authority[1]))
        t.add_row([
            permission,
            account[permission]["weight_threshold"],
            "\n".join(auths),
        ])
    print(t)


def print_json(tx):
    if sys.stdout.isatty():
        print(json.dumps(tx, indent=4))
    else:
        # You're being piped or redirected
        print(tx)


# this is another console script entrypoint
# also this function sucks and should be taken out back and shot
def beowulftailentry():
    parser = argparse.ArgumentParser(
        description="UNIX tail(1)-like tool for the beowulf blockchain")
    parser.add_argument(
        '-f',
        '--follow',
        help='Constantly stream output to stdout',
        action='store_true')
    parser.add_argument(
        '-n', '--lines', type=int, default=10, help='How many ops to show')
    parser.add_argument(
        '-j',
        '--json',
        help='Output as JSON instead of human-readable pretty-printed format',
        action='store_true')
    args = parser.parse_args(sys.argv[1:])

    op_count = 0
    if args.json:
        if not args.follow:
            sys.stdout.write('[')
    for op in Blockchain().reliable_stream():
        if args.json:
            sys.stdout.write('%s' % json.dumps(op))
            if args.follow:
                sys.stdout.write("\n")  # for human eyeballs
                sys.stdout.flush()  # flush after each op if live mode
        else:
            pprint.pprint(op)
        op_count += 1
        if not args.follow:
            if op_count > args.lines:
                if args.json:
                    sys.stdout.write(']')
                return
            else:
                if args.json:
                    sys.stdout.write(',')
