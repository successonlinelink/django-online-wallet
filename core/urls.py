from django.urls import path
from core import views, transfer, transaction, payment_request, credit_card, goal, loan


app_name = "core"

urlpatterns = [
    path("", views.home, name="index"),

    # Transfers
    path("search-account/", transfer.search_user_account_number, name="search-account"),
    path("amount-transfer/<account_number>/", transfer.ammount_to_transfer, name="amount-transfer"),

    # this guy will process the transfer and check if its valid, if its valid, then you will move to the next page
    path("amount-transfer-process/<account_number>/", transfer.amount_tranfer_process, name="amount-transfer-process"),

    path("transfer-confirmation/<account_number>/<transaction_id>/", transfer.transfer_confirmation, name="transfer-confirmation"),
    
    path("transfer-process/<account_number>/<transaction_id>/", transfer.transfer_process, name="transfer-process"),
    
    path("transfer-completed/<account_number>/<transaction_id>/", transfer.transfer_completed, name="transfer-completed"),

    # Cancel Transger
    path('transfer-cancel/<account_number>/<transaction_id>/', transfer.transfer_cancel, name="transfer-cancel"), 

    # Recipient - 
    path("my-recipients/", transfer.my_recipients, name="my-recipient"),
    path('recipients/delete/<int:pk>/', transfer.delete_recipient, name='delete_recipient'),


    # # transactions
    path("transactions/", transaction.transaction_list, name="transactions"),
    path("transaction-detail/<transaction_id>/", transaction.transaction_detail, name="transaction-detail"),

    # # Payment Request
    path("request-search-account/", payment_request.search_user_request, name="request-search-account"),
    path("amount-request/<account_number>/", payment_request.amount_request, name="amount-request"),
    path("amount-request-proccess/<account_number>/", payment_request.amount_request_process, name="amount-request-proccess"),
    path("amount-request-confirmation/<account_number>/<transaction_id>/", payment_request.amount_request_confirmation, name="amount-request-confirmation"),
    path("amount-request-final-process/<account_number>/<transaction_id>/", payment_request.amount_request_final_process, name="amount-request-final-process"),
    path("amount-request-completed/<account_number>/<transaction_id>/", payment_request.request_completed, name="amount-request-completed"),


    # # Request Settlement
    path("settlement-confirmation/<account_number>/<transaction_id>/", payment_request.settle_confirmation, name="settlement-confirmation"),
    path("settlement-processing/<account_number>/<transaction_id>/", payment_request.settlement_processing, name="settlement-processing"),
    path("settlement-completed/<account_number>/<transaction_id>/", payment_request.settlement_completed, name="settlement-completed"),
    path("delete-request/<account_number>/<transaction_id>/", payment_request.delete_payment_request, name="delete-request"),


    # # Credit Card URLS
    path("my-cards/", credit_card.all_cards, name="credit_cards"),
    path("card/<card_id>/", credit_card.card_detail, name="card-detail"),
    path("fund-credit-card/<card_id>/", credit_card.fund_credit_card, name="fund-credit-card"),
    path("withdraw_fund/<card_id>/", credit_card.withdraw_fund, name="withdraw_fund"),
    path("delete_card/<card_id>/", credit_card.delete_card, name="delete_card"),


    # Goal
    path("my-goals/", goal.my_goals, name="goal"),
    path("my-goals-detail/<gid>/", goal.goal_detail, name="goal-detail"),
    path("delete-goal/<gid>/", goal.delete_goal, name="delete-goal"),
    path("fund-goal/<gid>/", goal.fund_goal, name="fund-goal"),
    
    
    # Loan
    path("loan/apply/", loan.apply_for_loan, name="apply-loan"),
    path("loan/loan_history/<loan_id>/", loan.loan_detail, name="loan-detail"),
    path("loan/history/", loan.loan_history, name="loan-history"),
]


