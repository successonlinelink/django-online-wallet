from django.http import JsonResponse
from django.shortcuts import render, redirect
from accounts import models as account_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from core import models as core_model


@login_required
def search_user_account_number(request):
    # Fetch all accounts (could also be filtered by active status if needed)
    # account = Account.objects.filter(account_status="active")
    # The reason am not restricting in-active users is because you will provide KYC before withdrawing the money
    
    if request.user.is_authenticated:
        try:
            #try to get the KYC
            kyc = account_model.KYC.objects.get(user=request.user)
        
        except:
            # if the KYC does not exists
            messages.warning(request, "Please Provide Your KYC")
            return redirect("account:kyc-reg")
        
    account = account_model.Account.objects.all()
    
    # Get the account number entered by the user in the search form (POST request)
    query = request.POST.get('account_number')
    
    # If a search query was entered
    if query:
        # Filter accounts that match either the account_number or account_id exactly
        # Q objects allow OR conditions in Django queries
        account = account.filter(Q(account_number=query) | Q(account_id=query)).distinct().exclude(user=request.user) # Remove duplicates just in case of overlapping results
        # .exclude(user=request.user) -> will exclude the currently logged in user when searching
        
    #* Recipients History
    recipients = core_model.Recipient.objects.filter(user=request.user)


    # Prepare context data to send to the template
    context = {
        "account": account,  # Filtered or all accounts
        "query": query,      # The searched value (for displaying back in UI)
        "recipients": recipients,
        "kyc": kyc,

    }
    
    # Render the template that shows the search results
    return render(request, 'transfer/search_user_account_number.html', context)


###################################################
# Get all theActive Accounts
# @login_required
# def account_holders(request):
    
#     # account = account_model.Account.objects.all()
#     account = account_model.Account.objects.exclude(user=request.user)
    
#     # If account exists, prepare the context data
#     context = { "account": account, }

#     # Render the amount transfer page with the selected account details
#     return render(request, "transfer/account-holders.html", context)


###################################################
# ✅ View for transferring amount to a specific account
@login_required
def ammount_to_transfer(request, account_number):
    try: # after searching the account number, this guy grabs it for transfer when you click choose
        # Try to fetch the account using the provided account number in the URL
        account = account_model.Account.objects.get(account_number=account_number)
    except:
        # If no matching account is found, show a warning and redirect to the search page
        messages.warning(request, "Account does not exist.")
        return redirect("core:search-account")
    
    # If account exists, prepare the context data
    context = { "account": account, }

    # Render the amount transfer page with the selected account details
    return render(request, "transfer/amount-transfer.html", context)


################################
@login_required
def amount_tranfer_process(request, account_number):
    
    # ✅ Get the receiver's account using the provided account number from the URL
    account = account_model.Account.objects.get(account_number=account_number)

    # ✅ Identify the sender and receiver users
    sender = request.user # The currently logged-in user (who is sending the money)
    reciever = account.user # The user who owns the account that will receive the money

    # ✅ Get the sender’s and receiver’s account objects
    sender_account = request.user.account  # The sender’s account (attached to the logged-in user)
    reciever_account = account  # The receiver’s account (the one fetched from the DB above)
    
    # ✅ Process only when the request method is POST (form submission)
    if request.method == 'POST':
        # Get the transfer amount and description from the submitted form
        amount = request.POST.get("amount-send")
        description = request.POST.get("description")
        
        # ✅ Check if the sender has enough balance to send the amount
        if sender_account.account_balance >= Decimal(amount):
            # ✅ Create a new Transaction record
            new_transaction = core_model.Transaction.objects.create(
                user = request.user, # The user performing the transaction
                amount = amount, # The transfer amount
                description = description, # Optional description (reason for transfer)
                reciever = reciever, # The user receiving the money
                sender = sender, # The user sending the money
                sender_account = sender_account, # The sender’s account
                reciever_account = reciever_account, # The receiver’s account
                status = "processing", # Initial transaction status
                transaction_type = "transfer", # Type of transaction (transfer)
            )
            new_transaction.save()  # Save the transaction to the database

            # ✅ Retrieve the unique transaction ID (auto-generated)
            transaction_id = new_transaction.transaction_id

            # ✅ Redirect to the transfer confirmation page with account number and transaction ID
            return redirect("core:transfer-confirmation", account.account_number, transaction_id)

        else:
            # ❌ If sender doesn’t have enough money, show a warning message
            messages.warning(request, "Insufficient Fund.")
            return redirect("core:amount-transfer", account.account_number)

    else:
        # ❌ If the request wasn’t a POST request (e.g., GET), show an error
        messages.warning(request, "Error Occured, Try again later.")
        return redirect("account:dashboard")

##############################################################
@login_required
def transfer_confirmation(request, account_number, transaction_id):
    try:
        # ✅ Fetch the receiver’s account using the account number from the URL
        account = account_model.Account.objects.get(account_number=account_number)

        # ✅ Fetch the transaction details using the unique transaction ID from the URL
        transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)
    
    except:
        # ❌ If either the account or transaction doesn’t exist, show a warning and redirect the user
        messages.warning(request, "Transaction does not exist.")
        return redirect("account:dashboard")
    
    context = {
        "account": account, 
        "transaction": transaction
    }
    return render(request, 'transfer/transfer-confirmation.html', context)

####################################
@login_required
def transfer_process(request, account_number, transaction_id):
    # Get the receiver's account
    account = account_model.Account.objects.get(account_number=account_number)

    # Get the transaction
    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)

    # Identify sender & receiver
    sender = request.user                
    reciever = account.user              

    # Sender & Receiver accounts
    sender_account = request.user.account
    reciever_account = account

    if request.method == "POST":

        pin_number = request.POST.get("pin-number")

        # Check if PIN is correct
        if pin_number == sender_account.pin_number:

            # Mark transaction as completed
            transaction.status = "completed"
            transaction.save()

            # Deduct from sender
            sender_account.account_balance -= transaction.amount
            sender_account.save()

            # Credit receiver
            reciever_account.account_balance += transaction.amount
            reciever_account.save()

            # ---------------------------
            #* ✅ AUTO-ADD RECIPIENT HERE
            # ---------------------------
            from core.models import Recipient

            # Only add if not already saved
            if not Recipient.objects.filter(user=sender, recipient_user=reciever).exists():

                Recipient.objects.create(
                    user=sender,
                    recipient_user=reciever,
                    account=reciever_account,
                    nickname=reciever.get_full_name() or reciever.username
                )

                # Notification: new recipient added
                core_model.Notification.objects.create(
                    user=sender,
                    notification_type="New Recipient Added",
                    amount=0
                )
            #* ---------------------------


            # Debit notification
            core_model.Notification.objects.create(
                user=sender, 
                amount=transaction.amount, 
                notification_type="Debit Alert"
            )
            
            # Credit notification
            core_model.Notification.objects.create(
                user=reciever, 
                amount=transaction.amount, 
                notification_type="Credit Alert"
            )

            messages.success(request, "Transfer Successful")
            return redirect("core:transfer-completed", account.account_number, transaction.transaction_id)

        else:
            messages.warning(request, "Incorrect Pin")
            return redirect("core:transfer-confirmation", account.account_number, transaction.transaction_id)

    else:
        messages.warning(request, "An error occured, Try again later.")
        return redirect('account:account')

 
##############################################################
@login_required
def transfer_completed(request, account_number, transaction_id):
    
    try:
        # ✅ Fetch the receiver’s account using the account number from the URL
        account = account_model.Account.objects.get(account_number=account_number)

        # ✅ Fetch the completed transaction using the transaction ID from the URL
        transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)

    except:
        # ❌ If either the account or transaction doesn’t exist, show a warning message
        # and redirect the user back to their account dashboard
        messages.warning(request, "Transfer does not exist.")
        return redirect("account:account")

    # ✅ Prepare context data to send to the template
    context = {
        "account": account,          # The receiver’s account details
        "transaction": transaction,  # The specific transaction that was just completed
    }
    return render(request, "transfer/transfer-completed.html", context)

# Cancel Transfer
def transfer_cancel(request, account_number, transaction_id):
    try:
        transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)

        # Only allow cancel if still processing
        if transaction.status != "processing":
            messages.warning(request, "You cannot cancel this transaction anymore.")
            return redirect("account:dashboard")

        sender_account = transaction.sender_account
        amount = transaction.amount

        # REFUND if money was deducted earlier
        # (Only refund if sender balance was reduced already)
        sender_account.account_balance += amount
        sender_account.save()

        # Mark the transaction as failed
        transaction.status = "failed"
        transaction.save()

        # NOTIFICATION: For sender (you)
        core_model.Notification.objects.create(
            user = transaction.sender,
            amount = transaction.amount,
            notification_type = "Transfer Cancelled"
        )

        # NOTIFICATION: For receiver
        # core_model.Notification.objects.create(
        #     user = transaction.reciever,
        #     amount = transaction.amount,
        #     notification_type = "Transfer Cancelled"
        # )

        messages.success(request, "Transfer cancelled successfully.")
        return redirect("account:dashboard")

    except core_model.Transaction.DoesNotExist:
        messages.error(request, "Transaction not found.")
        return redirect("account:dashboard")


# List Recipient
@login_required
def my_recipients(request):
    recipients = core_model.Recipient.objects.filter(user=request.user)

    context = { "recipients": recipients }
    return render(request, "transfer/recipient-list.html", context)


# Delete Recipient
@login_required
def delete_recipient(request, pk):
    try:
        recipient = core_model.Recipient.objects.get(id=pk, user=request.user)
        recipient.delete()
        messages.success(request, "Recipient deleted successfully")
    except core_model.Recipient.DoesNotExist:
        messages.error(request, "Recipient not found")
    
    return redirect("core:my-recipient")

