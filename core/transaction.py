from django.shortcuts import redirect, render
from core import models as core_model
from accounts import models as account_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from itertools import chain

# ✅ Ensure that only logged-in users can access the transaction list page
@login_required
def transaction_list(request):
    # Transfers sent by current user
    sender_transaction = core_model.Transaction.objects.filter(sender=request.user, transaction_type="transfer").order_by("-id")

    # Transfers received by current user
    reciever_transaction = core_model.Transaction.objects.filter(reciever=request.user, transaction_type="transfer").order_by("-id")

    # Money requests sent by current user
    request_sender_transaction = core_model.Transaction.objects.filter(sender=request.user, transaction_type="request")

    # Money requests received by current user
    request_reciever_transaction = core_model.Transaction.objects.filter(reciever=request.user, transaction_type="request")

    # -------------------------------------------------------------
    # 5. Combine ALL four different transaction groups into ONE LIST.
    #    `chain()` merges multiple QuerySets into one iterable.
    #
    #    Then `sorted()` sorts the combined list by date field.
    #    reverse=True → newest transactions appear first.
    #
    #    Final result: A SINGLE clean timeline of all the user's activity:
    #        - transfers they sent
    #        - transfers they received
    #        - requests they sent
    #        - requests they received
    # -------------------------------------------------------------
    all_transactions = sorted(
        chain( sender_transaction, reciever_transaction, request_sender_transaction, request_reciever_transaction), key=lambda x: x.date, reverse=True)

    context = { "all_transactions": all_transactions }
    return render(request, "transaction/transaction-list.html", context)


# ✅ Ensure that only logged-in users can access the transaction detail page
@login_required
def transaction_detail(request, transaction_id):
    # ✅ Fetch a single transaction by its unique transaction ID
    transaction = core_model.Transaction.objects.get(transaction_id=transaction_id)
    
    # ✅ Prepare data to send to the transaction detail template
    context = {
        "transaction": transaction,  # The specific transaction record
    }

    # ✅ Render the transaction detail page with the selected transaction information
    return render(request, "transaction/transaction-detail.html", context)
