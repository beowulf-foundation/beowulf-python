import sys
from functools import partial
from pprint import pprint

from funcy.colls import where, pluck
from funcy.seqs import first, distinct, flatten
from beowulf import Beowulf


api_methods = [
    {
        'api': 'database_api',
        'method': 'get_block_header',
        'params': [('block_num', 'int')],
    },
    {
        'api': 'database_api',
        'method': 'get_block',
        'params': [('block_num', 'int')],
    },
    {
        'api': 'database_api',
        'method': 'get_ops_in_block',
        'params': [('block_num', 'int'), ('virtual_only', 'bool')],
    },
    {
        'api': 'database_api',
        'method': 'get_config',
        'params': [],
    },
    {
        'api': 'database_api',
        'method': 'get_dynamic_global_properties',
        'params': [],
    },
    {
        'api': 'database_api',
        'method': 'get_supernode_schedule',
        'params': [],
    },
    {
        'api': 'database_api',
        'method': 'get_hardfork_version',
        'params': [],
    },
    {
        'api': 'database_api',
        'method': 'get_next_scheduled_hardfork',
        'params': [],
    },
    {
        'api': 'database_api',
        'method': 'get_accounts',
        'params': [('account_names', 'list')],
    },
    {
        'api': 'database_api',
        'method': 'lookup_account_names',
        'params': [('account_names', 'list')],
    },
    {
        'api': 'database_api',
        'method': 'lookup_accounts',
        'params': [('after', 'str'), ('limit', 'int')],
    },
    {
        'api': 'database_api',
        'method': 'get_account_count',
        'params': [],
    },
    {
        'api': 'database_api',
        'method': 'get_account_history',
        'params': [('account', 'str'), ('index_from', 'int'), ('limit',
                                                               'int')],
    },
    {
        'api': 'database_api',
        'method': 'get_owner_history',
        'params': [('account', 'str')],
    },
    {
        'api': 'database_api',
        'method': 'get_transaction_hex',
        'params': [('signed_transaction', 'object')],
    },
    {
        'api': 'database_api',
        'method': 'get_transaction',
        'params': [('transaction_id', 'str')],
    },
    {
        'api': 'database_api',
        'method': 'get_required_signatures',
        'params': [('signed_transaction', 'object'), ('available_keys',
                                                      'list')],
    },
    {
        'api': 'database_api',
        'method': 'get_potential_signatures',
        'params': [('signed_transaction', 'object')],
    },
    {
        'api': 'database_api',
        'method': 'verify_authority',
        'params': [('signed_transaction', 'object')],
    },
    {
        'api': 'database_api',
        'method': 'get_account_votes',
        'params': [('account', 'str')],
    },
    {
        'api': 'database_api',
        'method': 'get_supernodes',
        'params': [('supernode_ids', 'list')]
    },
    {
        'api': 'database_api',
        'method': 'get_supernode_by_account',
        'params': [('account', 'str')],
    },
    {
        'api': 'database_api',
        'method': 'get_supernodes_by_vote',
        'params': [('from_account', 'str'), ('limit', 'int')],
    },
    {
        'api': 'database_api',
        'method': 'lookup_supernode_accounts',
        'params': [('from_account', 'str'), ('limit', 'int')],
    },
    {
        'api': 'database_api',
        'method': 'get_supernode_count',
        'params': [],
    },
    {
        'api': 'database_api',
        'method': 'get_active_supernodes',
        'params': [],
    },
    {
        'api': 'network_broadcast_api',
        'method': 'broadcast_transaction',
        'params': [('signed_transaction', 'object')],
    },
    {
        'api': 'network_broadcast_api',
        'method': 'broadcast_transaction_with_callback',
        'params': [('callback', 'object'), ('signed_transaction', 'object')]
    },
    {
        'api': 'network_broadcast_api',
        'method': 'broadcast_transaction_synchronous',
        'params': [('signed_transaction', 'object')],
    },
    {
        'api': 'network_broadcast_api',
        'method': 'broadcast_block',
        'params': [('block', 'object')],
    },
    {
        'api': 'account_by_key_api',
        'method': 'get_key_references',
        'params': [('public_keys', 'List[str]')],
    },
]

method_template = """
def {method_name}(self{method_arguments}){return_hints}:
    return self.exec('{method_name}'{call_arguments}, api='{api}')

"""


def beowulfd_codegen():
    """ Generates Python methods from beowulfd JSON API spec. Prints to stdout. """
    for endpoint in api_methods:
        method_arg_mapper = partial(map, lambda x: ', %s: %s' % (x[0], x[1]))
        call_arg_mapper = partial(map, lambda x: ', %s' % x[0])

        # skip unspecified calls
        if endpoint['params'] == 0:
            continue

        return_hints = ''
        if endpoint.get('returns'):
            return_hints = ' -> %s' % endpoint.get('returns')

        # generate method code
        fn = method_template.format(
            method_name=endpoint['method'],
            method_arguments=''.join(method_arg_mapper(endpoint['params'])),
            call_arguments=''.join(call_arg_mapper(endpoint['params'])),
            return_hints=return_hints,
            api=endpoint['api'])
        sys.stdout.write(fn)


def find_api(method_name):
    """ Given a method name, find its API. """
    endpoint = first(where(api_methods, method=method_name))
    if endpoint:
        return endpoint.get('api')


def inspect_beowulfd_implementation():
    """ Compare implemented methods with current live deployment of beowulfd. """
    _apis = distinct(pluck('api', api_methods))
    _methods = set(pluck('method', api_methods))

    avail_methods = []
    s = Beowulf(re_raise=False)
    for api in _apis:
        err = s.exec('nonexistentmethodcall', api=api)
        [
            avail_methods.append(x)
            for x in err['data']['stack'][0]['data']['api'].keys()
        ]

    avail_methods = set(avail_methods)

    # print("\nMissing Methods:")
    pprint(avail_methods - _methods)

    # print("\nLikely Deprecated Methods:")
    pprint(_methods - avail_methods)


if __name__ == '__main__':
    beowulfd_codegen()
    inspect_beowulfd_implementation()
