from django.http import JsonResponse
from django.shortcuts import render, redirect
from accounts import models as account_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from core import models as core_model



# --------------------------------------------
# ✅ APPLY FOR LOAN VIEW
# --------------------------------------------
@login_required
def apply_for_loan(request):
    user = request.user
    account = user.account  # User's bank account
    
    if request.user.is_authenticated:
        try:
            #try to get the KYC
            kyc = account_model.KYC.objects.get(user=request.user)
        
        except:
            # if the KYC does not exists
            messages.warning(request, "Please Provide Your KYC")
            return redirect("account:kyc-reg")

    if request.method == "POST":
        amount = request.POST.get("amount")
        months = request.POST.get("duration")
        purpose = request.POST.get("purpose")

        if not amount or Decimal(amount) <= 0:
            messages.warning(request, "Invalid loan amount.")
            return redirect("core:apply-loan")

        # Create Loan
        loan = core_model.Loan.objects.create(
            user=user,
            amount_requested=Decimal(amount),
            duration_months=int(months),
            purpose=purpose,
            account=account,
            status="under_review"
        )

        messages.success(request, "Loan application submitted successfully.")
        return redirect("core:loan-history") # , loan.loan_id
    
    context = {
        # "loan": loan,
        "kyc": kyc,
    }

    return render(request, "loan/apply-loan.html", context)


# --------------------------------------------
# ✅ LIST ALL USER LOANS
# --------------------------------------------
@login_required
def loan_history(request):
    loans = core_model.Loan.objects.filter(user=request.user)
    context = {"loans": loans}
    return render(request, "loan/loan-history.html", context)

# --------------------------------------------
# ✅ LOAN DETAIL PAGE
# --------------------------------------------
@login_required
def loan_detail(request, loan_id):
#     # try:
    loan = core_model.Loan.objects.get(loan_id=loan_id, user=request.user)
#     # except core_model.Loan.DoesNotExist:
#     #     messages.warning(request, "Loan record not found.")
#     #     return redirect("account:dashboard")

    context = {"loan": loan}
    return render(request, "loan/loan-detail.html", context)
