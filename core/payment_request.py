from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal
from django.contrib import messages

from core import models as core_model 
from accounts import models as account_model 


@login_required
def search_user_request(request):
    
    account = account_model.Account.objects.all()  # ✅ Get all accounts in the database
    query = request.POST.get("account_number")  # ✅ Retrieve the value entered in the form input field named "account_number"
    
    if query:
        # ✅ Filter accounts whose account number or ID matches the user's input
        account = account.filter(Q(account_number=query) | Q(account_id=query)).distinct().exclude(user=request.user)  # distinct() removes duplicates if any
        # .exclude(user=request.user) -> will exclude the currently logged in user during searching
    
    context = {
        "account": account,  # ✅ Pass the filtered account(s) to the template
        "query": query,      # ✅ Pass the search query back to the template
    }
    # ✅ Render the search result page showing matched accounts
    return render(request, 'payment_request/search-user.html', context)


# ✅ View for entering the amount to request from a selected account
def amount_request(request, account_number):
    
    account = account_model.Account.objects.get(account_number=account_number)
    context = { "account": account }
    # ✅ Show the amount request form for that user
    return render(request, "payment_request/amount-request.html", context)


# ✅ Process the payment request form after the user enters amount and description
def amount_request_process(request, account_number):
    
    account = account_model.Account.objects.get(account_number=account_number)  # ✅ Get the account that will receive the request

    sender = request.user  # ✅ The user making the request (logged-in user)
    reciever = account.user  # ✅ The person the request is being sent to

    sender_account = request.user.account  # ✅ The requester’s account (the sender)
    reciever_account = account # ✅ The receiver’s account (the one being asked for money)

    if request.method == "POST":  # ✅ Ensure the request was made via POST (form submission)
        amount = request.POST.get("amount-request")  # ✅ Get the optional description entered
        description = request.POST.get("description") # ✅ Create a new transaction record representing the request

        new_request = core_model.Transaction.objects.create(
            user = request.user,       # who initiated the request
            amount = amount,      # how much is being requested
            description = description,   # description or reason for the request
            
            sender = sender,       # requester
            reciever = reciever,      # person who will receive and settle it

            sender_account = sender_account,    # requester’s account
            reciever_account = reciever_account, # receiver’s account
            
            status = "request_processing",    # initial status before sending
            transaction_type = "request",    # identifies this as a request transaction
            
        )
        new_request.save() # ✅ Save transaction to the database

        transaction_id = new_request.transaction_id # ✅ Get the transaction’s unique ID
        
        # ✅ Redirect to confirmation page for this request
        return redirect("core:amount-request-confirmation", account.account_number, transaction_id)
    else:
        # ✅ If it’s not a POST request, show an error message and redirect back
        messages.warning(request, "Error Occured, try again later.")
        return redirect("account:dashboard")
    

# ✅ Show a confirmation page before sending the payment request
def amount_request_confirmation(request, account_number, transaction_id):
    
    account = account_model.Account.objects.get(account_number=account_number)  # ✅ Get the receiver’s account

    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)  # ✅ Get the specific transaction

    context = {
        "account": account,
        "transaction": transaction,
    }
    # ✅ Render confirmation template showing request details
    return render(request, "payment_request/amount-request-confirmation.html", context)


# ✅ Final step — confirm and send the payment request
# ✅ Final step — confirm and send the payment request
def amount_request_final_process(request, account_number, transaction_id):
    account = account_model.Account.objects.get(account_number=account_number)
    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)

    if request.method == 'POST':
        pin_number = request.POST.get("pin-number")  # User input PIN
        
        # 🔥 If PIN is correct
        if pin_number == request.user.account.pin_number:
            transaction.status = "request_sent"
            transaction.save()

            # Notification for sender
            core_model.Notification.objects.create(
                user=request.user,
                amount=transaction.amount,
                notification_type="Sent Payment Request"
            )

            # Notification for receiver
            core_model.Notification.objects.create(
                user=account.user,
                amount=transaction.amount,
                notification_type="Recieved Payment Request"
            )

            messages.success(request, "Your payment request has been sent successfully.")
            return redirect("core:amount-request-completed",
                            account.account_number,
                            transaction.transaction_id)
        
        # ❌ Incorrect PIN (THIS WAS MISSING BEFORE)
        else:
            messages.error(request, "Incorrect PIN. Please try again.")
            return redirect("core:amount-request", account.account_number)

    # ❌ Invalid method (GET, etc.)
    else:
        messages.warning(request, "An error occurred, try again later.")
        return redirect("account:dashboard")


# ✅ Display confirmation page after request has been sent
def request_completed(request, account_number, transaction_id):
    
    account = account_model.Account.objects.get(account_number=account_number)  # ✅ Get the receiver’s account

    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)  # ✅ Get the specific transaction

    context = {
        "account": account,
        "transaction": transaction,
    }
    # ✅ Render confirmation template showing request details
    return render(request, "payment_request/amount-request-completed.html", context)

################################## Settled (Receiver Paying the Request) ##########################

# ✅ Confirm before settling (paying) a received request
def settle_confirmation(request, account_number, transaction_id):
    
    account = account_model.Account.objects.get(account_number=account_number)  # ✅ Get the receiver’s account

    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)  # ✅ Get the specific transaction

    context = {
        "account": account,
        "transaction": transaction,
    }
    # ✅ Render confirmation template showing request details
    return render(request, "payment_request/settle-confirmation.html", context)

# ✅ Process the actual settlement (sending money to fulfill the request)
def settlement_processing(request, account_number, transaction_id):
    
    account = account_model.Account.objects.get(account_number=account_number) # ✅ Get the receiver’s account

    transaction = get_object_or_404(core_model.Transaction, transaction_id=transaction_id)  # ✅ Get the transaction
    # transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)  # ✅ Get the transaction

    sender = request.user  # ✅ The user who is paying (settling the request)
    sender_account = request.user.account  # ✅ Their account details
    
    if request.method == 'POST':
        pin_number = request.POST.get("pin-number") # ✅ Get the entered PIN

        if pin_number == request.user.account.pin_number: # ✅ Check if correct PIN
            # ✅ Ensure the sender has enough balance
            if sender_account.account_balance <= 0 or sender_account.account_balance <= transaction.amount:
                messages.warning(request, "Insufficient Funds, fund your account and try again.")
                
            else:
                # ✅ Deduct amount from sender’s account
                sender_account.account_balance -= transaction.amount
                sender_account.save()
                
                # ✅ Add amount to receiver’s account
                account.account_balance += transaction.amount
                account.save()
                
                # ✅ Update transaction status to settled
                transaction.status = "request_settled"
                transaction.save()

                # ✅ Show success message with receiver’s full name
                messages.success(request, f"Settled to {account.user.kyc.full_name} was successfull.")
                # ✅ Redirect to settlement completed page
                return redirect("core:settlement-completed", account.account_number, transaction.transaction_id)

        else:
            # ✅ Wrong PIN entered
            messages.warning(request, "Incorrect Pin")
            return redirect("core:settle-confirmation", account.account_number, transaction.transaction_id)
    else:
        # ✅ If not POST, show generic error
        messages.warning(request, "Error Occured")
        return redirect("account:dashboard")



# ✅ After settlement is done, show completed page
def settlement_completed(request, account_number, transaction_id):
    account = account_model.Account.objects.get(account_number=account_number)  # ✅ Get receiver account
    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)  # ✅ Get transaction
    
    context = {
        "account": account,
        "transaction": transaction,
    }
    # ✅ Render settlement completed page
    return render(request, "payment_request/settlement-completed.html", context)

                
# Delete Payment Request
def delete_payment_request(request, account_number, transaction_id):
    account = core_model.Account.objects.get(account_number=account_number)
    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)

    # check if the logged in user is the one who made the request
    if request.user == transaction.user:
        transaction.delete() # delete payment request
        messages.success(request, "Payment Request Deleted successfully.")
        return redirect("account:dashboard")

    
