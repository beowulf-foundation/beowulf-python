import re


def decodeRPCErrorMsg(e):
    """ Helper function to decode the raised Exception and give it a
        python Exception class
    """
    found = re.search(
        ("(10 assert_exception: Assert Exception\n|"
         "3030000 tx_missing_owner_auth)"
         ".*: (.*)\n"),
        str(e),
        flags=re.M)
    if found:
        return found.group(2).strip()
    else:
        return str(e)


class Error(Exception):
    error_code = None
    status_code = None

    def __init__(self, data, status_code=None, payload=None):
        Exception.__init__(self)
        self.data = data
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error_code'] = self.error_code
        rv['data'] = self.data
        return rv


class RequestError(Error):
    status_code = 400
    error_code = 400000


class RPCError(Error):
    status_code = 500
    error_code = 500000


class RPCErrorRecoverable(RPCError):
    error_code = 500001


class NoAccessApi(RPCError):
    error_code = 500002


class AlreadyTransactedThisBlock(RPCError):
    error_code = 500003


class VoteWeightTooSmall(RPCError):
    error_code = 500004


class OnlyVoteOnceEvery3Seconds(RPCError):
    error_code = 500005


class AlreadyVotedSimilarily(RPCError):
    error_code = 500006


class NoMethodWithName(RPCError):
    error_code = 500007


class PostOnlyEvery5Min(RPCError):
    error_code = 500008


class DuplicateTransaction(RPCError):
    error_code = 500009


class MissingRequiredPostingAuthority(RPCError):
    error_code = 500010


class UnhandledRPCError(RPCError):
    error_code = 500011


class ExceededAllowedBandwidth(RPCError):
    error_code = 500012


class NumRetriesReached(RequestError):
    error_code = 400001


class AccountExistsException(RequestError):
    error_code = 400002


class AccountDoesNotExistsException(RequestError):
    error_code = 400003


class InsufficientAuthorityError(RequestError):
    error_code = 400004


class MissingKeyError(RequestError):
    error_code = 400005


class BlockDoesNotExistsException(RequestError):
    error_code = 400006


class SupernodeDoesNotExistsException(RequestError):
    error_code = 400007


class InvalidKeyFormat(RequestError):
    error_code = 400008


class NoWallet(RequestError):
    error_code = 400009


class InvalidWifError(RequestError):
    error_code = 400010


class WalletExists(RequestError):
    error_code = 400011


class PostDoesNotExist(RequestError):
    error_code = 400012


class VotingInvalidOnArchivedPost(RequestError):
    error_code = 400013


class InvalidParamCreateAccount(RequestError):
    error_code = 400014