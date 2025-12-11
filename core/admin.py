from django.contrib import admin
from core.models import Transaction, Notification, CreditCard, Goal, Recipient, Loan

class TransactionAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'status', 'transaction_type']
    # list_display = ['user', 'amount', 'status', 'transaction_type', 'reciever', 'sender']
    list_display = ("transaction_id", "user", "sender", "reciever", "amount", "transaction_type", "status", "date")
    list_filter = ("transaction_type", "status", "date")
    search_fields = ("transaction_id", "user__username", "sender__username", "reciever__username")


class CreditCardAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'card_type']
    list_display = ['user', 'amount', 'card_type']
    

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'amount' ,'date']


class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "goal_type", "target_amount", "current_amount", "created_at")
    list_filter = ("goal_type", "created_at")
    search_fields = ("title", "user__username")


class RecipientAdmin(admin.ModelAdmin):
    list_display = ("user", "recipient_user", "date_added")
    # list_filter = ("goal_type", "date_added")
    search_fields = ("titrecipient_userle", "user__username")
    

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("loan_id", "user", "amount_requested", "amount_disbursed", "purpose", "interest_rate", "duration_months", "status", "account", "date_requested", "date_updated", "date_disbursed")
    list_filter = ("status", "interest_rate", "duration_months", "date_requested")
    search_fields = ("loan_id", "user__username", "user__email", "purpose")
    readonly_fields = ("loan_id", "date_requested", "date_updated", "date_disbursed")
 
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(Recipient, RecipientAdmin)


