from ape import chain

MAX_UINT256 = 2**256 - 1

w3 = chain.provider.web3


def get_timestamp():
    return chain.pending_timestamp
