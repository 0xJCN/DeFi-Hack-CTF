from ape import accounts, project


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy token and vault contracts
    print("\n--- Deploying Tokens and Challenge contracts ---\n")
    khinkal = project.KhinkalToken.deploy(sender=deployer)
    lp_token = project.LPToken.deploy(sender=deployer)

    lp_token.mint(attacker.address, 1000, sender=deployer)

    challenge = project.MainChef.deploy(
        khinkal.address,
        deployer.address,
        200_000,
        0,
        0,
        deployer.address,
        sender=deployer,
    )
    khinkal.mint(challenge.address, 100_000, sender=deployer)
    khinkal.transferOwnership(challenge.address, sender=deployer)

    challenge.addToken(lp_token.address, sender=deployer)

    # define initial balances for attacker and challenge
    attacker_initial_bal = khinkal.balanceOf(attacker.address)
    challenge_initial_bal = khinkal.balanceOf(challenge.address)

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Challenge: {challenge_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.MainChefAttacker.deploy(
        challenge.address, sender=attacker
    )
    attacker_contract.start_attack(sender=attacker)
    attacker_contract.finish_attack(sender=attacker)

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Stole all khinkal tokens from Challenge contract ---\n")

    # define ending balances for attacker and vault
    attacker_final_bal = khinkal.balanceOf(attacker.address)
    challenge_final_bal = khinkal.balanceOf(challenge.address)

    print(
        f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n⇒ Challenge: {challenge_final_bal}\n---\n"
    )

    assert khinkal.balanceOf(challenge.address) == 0

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
