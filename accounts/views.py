from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts import models as account_model
from accounts import forms as account_forms
from core import models as core_model


from itertools import chain



# Create your views here.
@login_required
def account(request):
    
    if request.user.is_authenticated:
        try:
            #try to get the KYC
            kyc = account_model.KYC.objects.get(user=request.user)
        
        except:
            # if the KYC does not exists
            messages.warning(request, "Please Provide Your KYC")
            return redirect("account:kyc-reg")
    
        # If KYC exists, get the Account record that belongs to the logged-in user
        account = account_model.Account.objects.get(user=request.user)
        
    else:
        # if the user is not logged in
        messages.warning(request, "Please Login to access this Page!")
        return redirect("userauths:login")
    

    context = {
        "account": account,
        "kyc": kyc,
    }
    return render(request, 'accounts/account.html', context)

# Profile
@login_required
def profile(request):
    if request.user.is_authenticated:
        try:
            #try to get the KYC
            kyc = account_model.KYC.objects.get(user=request.user)
        
        except:
            # if the KYC does not exists
            messages.warning(request, "Please Provide Your KYC")
            return redirect("account:kyc-reg")
    
        # If KYC exists, get the Account record that belongs to the logged-in user
        account = account_model.Account.objects.get(user=request.user)
        
    else:
        # if the user is not logged in
        messages.warning(request, "Please Login to access this Page!")
        return redirect("userauths:login")
    
    context = {
        "account": account,
        "kyc": kyc,
    }
    return render(request, 'accounts/profile.html', context)

# Create your views here.
@login_required
def kyc_registration(request):
    
    # get the current user logged in
    user = request.user
    
    # get the user account details from the Account
    account  = account_model.Account.objects.get(user=user)

    try:
        # try to get the existing KYC
        kyc = account_model.KYC.objects.get(user=user)
    except:
        # if the KYC does not exist, set to none
        kyc = None

    # check if the for was submitted
    if request.method == 'POST':
        # Create a KYC with the submitted data else Update it
        form = account_forms.KYCForm(request.POST, request.FILES, instance=kyc)

        # check if the requirements are met
        if form.is_valid():
            # Don't save yet, cos we want to add other things
            new_form = form.save(commit=False)
            
            # Link the KYC to the currently logged in user
            new_form.user = user
            
            # also Link it to the user account
            new_form.account = account
            
            # now save
            new_form.save()
            messages.success(request, "KYC Submmitted Succesfully!")
            return redirect("account:kyc_under_review")
            # 
            
        
        else: 
            messages.info(request, "Something went wrong")
            return redirect("account:kyc-reg")
        
    else:
        # If the request is not a POST (i.e., it's a GET), show the form page
        # If KYC already exists, it will pre-fill the form with existing data
        form = account_forms.KYCForm(instance=kyc)
    

    context = {
        "account": account,
        "kyc": kyc,
        "form": form,
    }
    return render(request, 'accounts/kyc-reg.html', context)


# KYC Under Review
@login_required
def kyc_under_review(request):

    context = {  }
    return render(request, 'accounts/kyc_under_review.html', context)


# Dashboard
@login_required
def dashboard(request):
   
    if request.user.is_authenticated:
        # Get the user's account information - 
        account = account_model.Account.objects.get(user=request.user)
        # Get other users except the currently logged in user
        recipients = core_model.Recipient.objects.filter(user=request.user)[:1] # [:1] means get only the latest one
        
        

        # Get the most recent transfer received by the user (as receiver) - just recent alone
        recent_recieved_transfer = core_model.Transaction.objects.filter(reciever=request.user, transaction_type="transfer").order_by("-id")[:1] # [:1] means get only the latest one

        # Get the most recent completed transfer made by the user (as sender) - just recent alone
        recent_transfer = core_model.Transaction.objects.filter(sender=request.user, transaction_type="transfer", status="Completed").order_by("-id")[:1] # [:1] means get only the latest one
        
        # Get all transfer transactions where the user is the sender
        sender_transaction = core_model.Transaction.objects.filter(sender=request.user, transaction_type="transfer").order_by("-id")[:1] # [:1] means get only the latest one
        
        # Get all transfer transactions where the user is the receiver
        reciever_transaction = core_model.Transaction.objects.filter(reciever=request.user, transaction_type="transfer").order_by("-id")[:1] # [:1] means get only the latest one

        # Get all "request" type transactions where the user is the sender
        request_sender_transaction = core_model.Transaction.objects.filter(sender=request.user, transaction_type="request").order_by("-id")[:1] # [:1] means get only the latest one
        
        # Get all "request" type transactions where the user is the receiver
        request_reciever_transaction = core_model.Transaction.objects.filter(reciever=request.user, transaction_type="request").order_by("-id")[:1] # [:1] means get only the latest one

        # Chain them
        all_transactions = sorted(
            chain( sender_transaction, reciever_transaction, request_sender_transaction, request_reciever_transaction), key=lambda x: x.date, reverse=True)

        # goal
        goal = core_model.Goal.objects.filter(user=request.user).order_by("-id")[:2]

        
    else: 
        messages.warning(request, "Please login to Access this Page")
        return redirect("userauths:login")


    context = {
        "account": account,
        "recipients": recipients,
        
        # "form": form,  # Credit card form
        # "credit_card": credit_card,  # List of user's credit cards
        
        # "sender_transaction": sender_transaction,  # Transactions sent by user
        # "reciever_transaction": reciever_transaction,  # Transactions received by user

        # 'request_sender_transaction': request_sender_transaction,  # Request transactions sent by user
        # 'request_reciever_transaction': request_reciever_transaction,  # Request transactions received by user
        
        'recent_transfer': recent_transfer,  # Most recent transfer sent
        'recent_recieved_transfer': recent_recieved_transfer,  # Most recent transfer received

        "goal": goal,
        
        "all_transactions": all_transactions ,
        
    }
    return render(request, 'accounts/dashboard.html', context)


# Notification
@login_required
def notification(request):
   
    context = { }
    return render(request, 'accounts/notification.html', context)


# Market
@login_required
def market(request):
    account = account_model.Account.objects.get(user=request.user)
    
    context = {
        "account": account,
    }
    return render(request, 'accounts/market.html', context)








