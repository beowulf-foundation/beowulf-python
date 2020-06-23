from beowulf.beowulfd import Beowulfd
from beowulfbase import operations
from beowulfbase.transactions import SignedTransaction, fmt_time_from_now_to_epoch, fmt_time_from_now, get_block_params
from beowulfbase.types import Array

if __name__ == '__main__':
    wif1 = "5Jppppppppppppppppppppppppppppppppppppppppppppppppp"
    wif2 = "5Kxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    bwfd = Beowulfd()
    expiration = fmt_time_from_now(60)
    ref_block_num, ref_block_prefix = get_block_params(bwfd)
    created_time = fmt_time_from_now_to_epoch()

    op = operations.Transfer(
        **{'memo': 'Create Transfer Multi_signs',
           'amount': '10.00000 BWF',
           'from': 'orgd',
           'to': 'alice',
           'fee': '0.10000 W'})

    ops = [operations.Operation(op)]

    tx = SignedTransaction(
        ref_block_num=ref_block_num,
        ref_block_prefix=ref_block_prefix,
        expiration=expiration,
        operations=ops,
        created_time=created_time)

    first_tx = tx.sign([wif1], chain=bwfd.chain_params)
    first_sign = first_tx.json()["signatures"][0]
    # print(first_tx.json())

    second_tx = tx.sign([wif2], chain=bwfd.chain_params)
    second_sign = second_tx.json()["signatures"][0]
    # print(second_tx.json())

    final_tx = tx
    sigs = [first_sign, second_sign]

    final_tx.data["signatures"] = Array(sigs)
    # print(final_tx.json())

    response = bwfd.broadcast_transaction_synchronous(final_tx.json())
    # print(response)
