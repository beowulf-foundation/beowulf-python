from beowulf.beowulfd import Beowulfd
from beowulfbase import operations
from beowulfbase.transactions import SignedTransaction, fmt_time_from_now_to_epoch, fmt_time_from_now, get_block_params

if __name__ == '__main__':
    wif = "5Kxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    bwfd = Beowulfd()
    expiration = fmt_time_from_now(60)
    ref_block_num, ref_block_prefix = get_block_params(bwfd)
    created_time = fmt_time_from_now_to_epoch()

    op = operations.AccountCreate(
        **{
            "fee": "0.10000 W",
            "creator": "jayce",
            "new_account_name": "test",
            "owner": {
                "weight_threshold": 1,
                "account_auths": [],
                "key_auths": [
                    [
                        "BEO5V7Jzrm6mX7kuFcWt31YMYDhjWeYHuq4TpLYiePgY8C8nhA3aB",
                        1
                    ]
                ]
            },
            "json_metadata": ""
        })

    ops = [operations.Operation(op)]

    tx = SignedTransaction(
        ref_block_num=ref_block_num,
        ref_block_prefix=ref_block_prefix,
        expiration=expiration,
        operations=ops,
        created_time=created_time)

    tx = tx.sign([wif], chain=bwfd.chain_params)

    response = bwfd.broadcast_transaction_synchronous(tx.json())
