from enum import Enum


class BankAlert(str, Enum):
    # Create user
    USER_CREATED_SUCCESSFULLY = "✅ User created successfully!"
    USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS = "Username must be between 3 and 15 characters"

    # Create account
    NEW_ACCOUNT_CREATED = "✅ New Account Created! Account Number: "

    # Deposit account
    ACCOUNT_DEPOSITED = "✅ Successfully deposited ${amount} to account {account}!"
    INVALID_AMOUNT = "❌ Please enter a valid amount."
    INVALID_AMOUNT_MORE_5000 = "❌ Please deposit less or equal to 5000$."

    # Transfer account
    MONEY_TRANSFERED = "✅ Successfully transferred ${amount} to account {account}!"

    NEGATIVE_TRANSFER = "❌ Error: Invalid transfer: insufficient funds or invalid accounts"
    EXCEED_10000_TRANSFER = "❌ Error: Transfer amount cannot exceed 10000"

    # Update profile
    NAME_UPDATED = "✅ Name updated successfully!"
    INVALID_NAME = "Name must contain two words with letters only"
