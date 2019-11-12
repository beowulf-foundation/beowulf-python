import importlib
import json
import re
import struct
from collections import OrderedDict
from beowulf.utils import compat_bytes
from beowulfbase.extensionids import extension_types, extension_type_names
from .account import PublicKey
from .operationids import operations
from .types import (Uint8, Uint16, Uint32, Uint64, String, Bytes,
                    Array, Bool, Optional, Map, Id, JsonObj, Int64, TypeExt)

default_prefix = "BEO"

asset_precision = {
    "BWF": 5,
    "M": 5,
    "W": 5,
}
asset_tokens = {}


class Operation:
    def __init__(self, op):
        if isinstance(op, list) and len(op) == 2:
            if isinstance(op[0], int):
                self.opId = op[0]
                name = self.get_operation_name_for_id(self.opId)
            else:
                self.opId = operations.get(op[0], None)
                name = op[0]
                if self.opId is None:
                    raise ValueError("Unknown operation")

            # convert method name like feed_publish to class
            # name like FeedPublish
            self.name = self.to_class_name(name)
            try:
                klass = self.get_class(self.name)
            except:  # noqa FIXME
                raise NotImplementedError(
                    "Unimplemented Operation %s" % self.name)
            else:
                self.op = klass(op[1])
        else:
            self.op = op
            # class name like FeedPublish
            self.name = type(self.op).__name__
            self.opId = operations[self.to_method_name(self.name)]

    @staticmethod
    def get_operation_name_for_id(_id):
        """ Convert an operation id into the corresponding string
        """
        for key, value in operations.items():
            if value == int(_id):
                return key

    @staticmethod
    def to_class_name(method_name):
        """ Take a name of a method, like feed_publish and turn it into
        class name like FeedPublish. """
        return ''.join(map(str.title, method_name.split('_')))

    @staticmethod
    def to_method_name(class_name):
        """ Take a name of a class, like FeedPublish and turn it into
        method name like feed_publish. """
        words = re.findall('[A-Z][^A-Z]*', class_name)
        return '_'.join(map(str.lower, words))

    @staticmethod
    def get_class(class_name):
        """ Given name of a class from `operations`, return real class. """
        module = importlib.import_module('beowulfbase.operations')
        return getattr(module, class_name)

    def __bytes__(self):
        return compat_bytes(Id(self.opId)) + compat_bytes(self.op)

    def __str__(self):
        return json.dumps(
            [self.get_operation_name_for_id(self.opId),
             self.op.json()])


class GrapheneObject(object):
    """ Core abstraction class

        This class is used for any JSON reflected object in Graphene.

        * ``instance.__json__()``: encodes data into json format
        * ``bytes(instance)``: encodes data into wire format
        * ``str(instances)``: dumps json object as string

    """

    def __init__(self, data=None):
        self.data = data

    def __bytes__(self):
        if self.data is None:
            return bytes()
        b = b""
        for name, value in self.data.items():
            if isinstance(value, str):
                b += compat_bytes(value, 'utf-8')
            else:
                b += compat_bytes(value)
        return b

    def __json__(self):
        if self.data is None:
            return {}
        d = {}  # JSON output is *not* ordered
        for name, value in self.data.items():
            if isinstance(value, Optional) and value.isempty():
                continue

            if isinstance(value, String):
                d.update({name: str(value)})
            else:
                d.update({name: JsonObj(value)})
        return d

    def __str__(self):
        return json.dumps(self.__json__())

    def toJson(self):
        return self.__json__()

    def json(self):
        return self.__json__()


class Permission(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            prefix = kwargs.pop("prefix", default_prefix)

            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            # Sort keys (FIXME: ideally, the sorting is part of Public
            # Key and not located here)
            kwargs["key_auths"] = sorted(
                kwargs["key_auths"],
                key=lambda x: repr(PublicKey(x[0], prefix=prefix)),
                reverse=False,
            )

            kwargs["account_auths"] = sorted(
                kwargs["account_auths"],
                key=lambda x: x[0],
                reverse=False,
            )

            accountAuths = Map([[String(e[0]), Uint16(e[1])]
                                for e in kwargs["account_auths"]])

            keyAuths = Map([[PublicKey(e[0], prefix=prefix),
                             Uint16(e[1])] for e in kwargs["key_auths"]])
            super(Permission, self).__init__(
                OrderedDict([
                    ('weight_threshold', Uint32(
                        int(kwargs["weight_threshold"]))),
                    ('account_auths', accountAuths),
                    ('key_auths', keyAuths),
                ]))


class Memo(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            prefix = kwargs.pop("prefix", default_prefix)

            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super(Memo, self).__init__(
                OrderedDict([
                    # ('from', PublicKey(kwargs["from"], prefix=prefix)),
                    # ('to', PublicKey(kwargs["to"], prefix=prefix)),
                    ('nonce', Uint64(int(kwargs["nonce"]))),
                    ('check', Uint32(int(kwargs["check"]))),
                    ('encrypted', Bytes(kwargs["encrypted"])),
                ]))


class Amount:
    def __init__(self, d):
        self.amount, self.asset = d.strip().split(" ")
        self.amount = float(self.amount)

        if self.asset in asset_precision:
            self.precision = asset_precision[self.asset]
        elif self.asset in asset_tokens:
            self.precision = asset_tokens[self.asset]
        else:
            raise Exception("Asset unknown")

    def __bytes__(self):
        # padding
        amount = round(float(self.amount) * 10 ** self.precision)
        asset_name = self.asset + "\x00" * (9 - len(self.asset))
        return (struct.pack("<q", amount) + struct.pack("<I", self.precision)
                + compat_bytes(asset_name, "ascii"))

    def __str__(self):
        return '{:.{}f} {}'.format(self.amount, self.precision, self.asset)


class ExchangeRate(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super(ExchangeRate, self).__init__(
                OrderedDict([
                    ('base', Amount(kwargs["base"])),
                    ('quote', Amount(kwargs["quote"])),
                ]))


class SupernodeProps(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super(SupernodeProps, self).__init__(
                OrderedDict([
                    ('account_creation_fee',
                     Amount(kwargs["account_creation_fee"])),
                    ('maximum_block_size',
                     Uint32(kwargs["maximum_block_size"])),
                ]))


class Symbol(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super(Symbol, self).__init__(
                OrderedDict([
                    ('decimals', Uint8(kwargs["decimals"])),
                    ('name', String(kwargs["name"]))
                ]))

    def __bytes__(self):
        decimals = int(str(self.data['decimals']))
        asset_name = str(self.data['name']) + "\x00" * (9 - len(str(self.data['name'])))
        return struct.pack("<I", decimals) + compat_bytes(asset_name, "ascii")


class Extension(GrapheneObject):
    def __init__(self, ex):
        if isinstance(ex, dict):
            self.typeName = ex['type']
            self.typeId = extension_types[self.typeName]
            self.data = ex['value']['data']
        elif isinstance(ex, str):
            if len(ex) == 0:
                self.typeId = 0
            else:
                self.typeId = 1
            self.typeName = extension_type_names[self.typeId]
            self.data = ex
        else:
            raise ValueError("Unknown Extension Type")
        super(Extension, self).__init__(
            OrderedDict([
                ('type', TypeExt(self.typeId)),
                ('value', ValueExtension(self.data))
            ]))


class ValueExtension(GrapheneObject):
    def __init__(self, d):
        self.data = d
        super(ValueExtension, self).__init__(
            OrderedDict([
                ('data', String(self.data))
            ]))


########################################################
# Actual Operations
########################################################


class AccountCreate(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.pop("prefix", default_prefix)

            assert len(kwargs["new_account_name"]
                       ) <= 16, "Account name must be at most 16 chars long"

            meta = ""
            if "json_metadata" in kwargs and kwargs["json_metadata"]:
                if isinstance(kwargs["json_metadata"], dict):
                    meta = json.dumps(kwargs["json_metadata"])
                else:
                    meta = kwargs["json_metadata"]

            super(AccountCreate, self).__init__(
                OrderedDict([
                    ('fee', Amount(kwargs["fee"])),
                    ('creator', String(kwargs["creator"])),
                    ('new_account_name', String(kwargs["new_account_name"])),
                    ('owner', Permission(kwargs["owner"], prefix=prefix)),
                    ('json_metadata', String(meta)),
                ]))


class AccountUpdate(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.pop("prefix", default_prefix)

            meta = ""
            if "json_metadata" in kwargs and kwargs["json_metadata"]:
                if isinstance(kwargs["json_metadata"], dict):
                    meta = json.dumps(kwargs["json_metadata"])
                else:
                    meta = kwargs["json_metadata"]

            owner = Permission(
                kwargs["owner"], prefix=prefix) if "owner" in kwargs else None

            super(AccountUpdate, self).__init__(
                OrderedDict([
                    ('account', String(kwargs["account"])),
                    ('owner', Optional(owner)),
                    ('json_metadata', String(meta)),
                    ('fee', Amount(kwargs["fee"])),
                ]))


class Transfer(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "memo" not in kwargs:
                kwargs["memo"] = ""
            super(Transfer, self).__init__(
                OrderedDict([
                    ('from', String(kwargs["from"])),
                    ('to', String(kwargs["to"])),
                    ('amount', Amount(kwargs["amount"])),
                    ('fee', Amount(kwargs["fee"])),
                    ('memo', String(kwargs["memo"])),
                ]))


class SmtCreate(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super(SmtCreate, self).__init__(
                OrderedDict([
                    ('control_account', String(kwargs["control_account"])),
                    ('symbol', Symbol(kwargs["symbol"])),
                    ('creator', String(kwargs["creator"])),
                    ('smt_creation_fee', Amount(kwargs["smt_creation_fee"])),
                    ('precision', Uint8(kwargs["precision"])),
                    ('extensions', Array([])),
                    ('max_supply', Uint64(kwargs["max_supply"])),
                ]))


class TransferToVesting(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super(TransferToVesting, self).__init__(
                OrderedDict([
                    ('from', String(kwargs["from"])),
                    ('to', String(kwargs["to"])),
                    ('amount', Amount(kwargs["amount"])),
                    ('fee', Amount(kwargs["fee"])),
                ]))


class WithdrawVesting(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super(WithdrawVesting, self).__init__(
                OrderedDict([
                    ('account', String(kwargs["account"])),
                    ('vesting_shares', Amount(kwargs["vesting_shares"])),
                    ('fee', Amount(kwargs["fee"])),
                ]))


class SupernodeUpdate(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.pop("prefix", default_prefix)

            if not kwargs["block_signing_key"]:
                kwargs[
                    "block_signing_key"] = \
                    "BEO1111111111111111111111111111111114T1Anm"
            super(SupernodeUpdate, self).__init__(
                OrderedDict([
                    ('owner', String(kwargs["owner"])),
                    ('block_signing_key',
                     PublicKey(kwargs["block_signing_key"], prefix=prefix)),
                    ('fee', Amount(kwargs["fee"])),
                ]))


class AccountSupernodeVote(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super(AccountSupernodeVote, self).__init__(
                OrderedDict([
                    ('account', String(kwargs["account"])),
                    ('supernode', String(kwargs["supernode"])),
                    ('approve', Bool(bool(kwargs["approve"]))),
                    ('votes', Int64(kwargs["votes"])),
                    ('fee', Amount(kwargs["fee"])),
                ]))


def isArgsThisClass(self, args):
    return len(args) == 1 and type(args[0]).__name__ == type(self).__name__
