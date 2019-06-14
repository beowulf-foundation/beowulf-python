# beowulf_protocol::transfer: 0
# beowulf_protocol::transfer_to_vesting: 1
# beowulf_protocol::withdraw_vesting: 2
# beowulf_protocol::account_create: 3
# beowulf_protocol::account_update: 4
# beowulf_protocol::supernode_update: 5
# beowulf_protocol::account_supernode_vote: 6
# beowulf_protocol::smt_create: 7
# beowulf_protocol::fill_vesting_withdraw: 8
# beowulf_protocol::shutdown_supernode: 9
# beowulf_protocol::hardfork: 10
# beowulf_protocol::producer_reward: 11
# beowulf_protocol::clear_null_account_balance: 12

op_names = [
    'transfer',
    'transfer_to_vesting',
    'withdraw_vesting',
    'account_create',
    'account_update',
    'supernode_update',
    'account_supernode_vote',
    'smt_create',
    'fill_vesting_withdraw',
    'shutdown_supernode',
    'hardfork',
    'producer_reward',
    'clear_null_account_balance',
]

#: assign operation ids
operations = dict(zip(op_names, range(len(op_names))))
