from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from accounts import models as account_model
from core import models as core_model
from core import forms as core_form


# ✅ View to show all credit cards belonging to the logged-in user
@login_required
def all_cards(request):
    # Get the logged-in user’s account
    account = account_model.Account.objects.get(user=request.user)
    
    # Get all credit cards linked to the user
    credit_card = core_model.CreditCard.objects.filter(user=request.user).order_by("-id")
    
    # Add Credit Card and check if user is authenticated
    # Check if the form was submitted (POST request)
    if request.method == 'POST':
        # Create a credit card form instance with submitted data
        card_form = core_form.CreditCardForm(request.POST)
        # validate the card form
        if card_form.is_valid():
            # Save the form temporarily without committing to the database
            new_form = card_form.save(commit=False)
            # Assign the current user to the credit card record
            new_form.user = request.user
            # Save the new credit card record
            new_form.save()

            # Create a notification for the user that a new card was added
            core_model.Notification.objects.create(
                user=request.user, notification_type="Added Credit Card"
            )
                
            # Get the ID of the newly created card (optional use)
            card_id = new_form.card_id

            # Show a success message to the user
            messages.success(request, "Card Added Successfully.")
            # Redirect the user back to the dashboard page
            return redirect("core:credit_cards",)
    else:
        # If it's not a POST request, create an empty credit card form
        card_form = core_form.CreditCardForm()
    
    context = {
        "account": account,    # Pass user’s account info to the template
        "credit_card": credit_card,  # Pass all credit cards to the template
        "card_form": card_form,  # Credit card form
    }
    return render(request, "credit_card/all-card.html", context)  # Render the list of cards


# ✅ View to display details of a specific credit card
def card_detail(request, card_id):
    account = account_model.Account.objects.get(user=request.user)  # Get the user’s account

    credit_card = core_model.CreditCard.objects.get(card_id=card_id, user=request.user)  # Get a specific credit card by ID

    context = {
        "account": account,
        "credit_card": credit_card,
    }
    return render(request, "credit_card/card-detail.html", context)  # Show the card details page


# ✅ View to fund (add money to) a credit card from main account
def fund_credit_card(request, card_id):
    # Get the credit card
    credit_card = core_model.CreditCard.objects.get(card_id=card_id, user=request.user)

    # Get user's main account
    account = request.user.account    

    if request.method == "POST":
        amount = request.POST.get("funding_amount")  # this is a STRING

        # Convert to Decimal
        amount = Decimal(amount)

        # Check if user has enough money
        if amount <= account.account_balance:
            # Deduct from account
            account.account_balance -= amount
            account.save()

            # Add to card
            credit_card.amount += amount
            credit_card.save()
            # Create notification for the funding transaction
            core_model.Notification.objects.create(
                user=request.user,
                amount=amount,
                notification_type="Funded Credit Card"
            )
            
            messages.success(request, "Funding Successfull")
            return redirect("core:credit_cards") # , credit_card.card_id -> can only do this if you are using detail page
        else:
            messages.warning(request, "Insufficient Funds")
            return redirect("core:credit_cards", credit_card.card_id)  # , credit_card.card_id -> can only do this if you are using detail page
        
        
# ✅ View to withdraw money from a credit card into the main account
def withdraw_fund(request, card_id):
    # Get the logged-in user's main Account
    account = account_model.Account.objects.get(user=request.user)

    # Get the specific CreditCard that belongs to the user 
    credit_card = core_model.CreditCard.objects.get(card_id=card_id, user=request.user)

    # Only process when the form is submitted via POST 
    if request.method == 'POST':
        amount = request.POST.get("amount")

        # Validate there is enough money on the credit card to cover the withdrawal.
        # The check `credit_card.amount >= Decimal(amount)` ensures the card has at least the requested amount.
        # The extra `credit_card.amount != 0.00` explicitly prevents processing when the card balance is exactly zero.
        if credit_card.amount >= Decimal(amount) and credit_card.amount != 0.00:
            
            # Add the withdrawal amount to the user's main account balance (crediting their account).
            # We convert amount to Decimal to avoid floating-point errors on money values.
            account.account_balance += Decimal(amount) # Add withdrawn amount to account balance
            account.save()

            # Subtract the same amount from the credit card's balance (debit the card).
            credit_card.amount -= Decimal(amount) # Deduct amount from credit card balance
            credit_card.save()

            # Create a Notification record to track this activity for the user.
            core_model.Notification.objects.create(
                user=request.user,
                amount=amount,
                notification_type= "Withdrew Credit Card Funds"
            )
            
            # Inform the user of success via Django messages, then redirect to the card detail page.
            messages.success(request, "Withdrawal Successfull")
            return redirect("core:card-detail", credit_card.card_id)  # Redirect to card detail page
        
        # If the card has zero balance, show an "Insufficient Funds" warning and redirect back.
        elif credit_card.amount == 0.00:
            messages.warning(request, "Insufficient Funds")
            return redirect("core:card-detail", credit_card.card_id)
        
        # Otherwise (card has some balance but less than requested amount), show the same warning.
        else:
            messages.warning(request, "Insufficient Funds")
            return redirect("core:card-detail", credit_card.card_id)


# ✅ View to delete a credit card (and transfer funds to main account first if any)
def delete_card(request, card_id):
    # Get the credit card to delete
    credit_card = core_model.CreditCard.objects.get(card_id=card_id, user=request.user)

    account = request.user.account # Get the user’s account
    
    # Before deleting, check if the card still has money
    if credit_card.amount > 0:
        account.account_balance += credit_card.amount # Move remaining money to main account
        account.save()

        # Notify user about card deletion
        core_model.Notification.objects.create(
            user=request.user, notification_type="Deleted Credit Card"
        )
        
        credit_card.delete()  # Delete the card
        messages.success(request, "Card Deleted Successfull and Card funds transfered into your account.")
        return redirect("core:credit_cards")
    
    
    # If card is empty, just delete and notify
    core_model.Notification.objects.create(
        user=request.user,
        notification_type="Deleted Credit Card"
    )
    credit_card.delete()
    messages.success(request, "Card Deleted Successfull")
    return redirect("core:credit_cards")


