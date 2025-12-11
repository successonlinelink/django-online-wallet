# goals/views.py
from django.shortcuts import render, redirect, get_object_or_404
from core import models as core_model
from core import forms as core_form
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal


@login_required
def my_goals(request):
    # goal
    goal = core_model.Goal.objects.filter(user=request.user)
    
    if request.method == "POST":
        form = core_form.GoalForm(request.POST, request.FILES)
        if form.is_valid():
            goal_form = form.save(commit=False)
            goal_form.user = request.user
            goal_form.save()
        
            # OPTIONAL: Create Notification
            core_model.Notification.objects.create(
                user=request.user,
                notification_type="Goal Created"
            )

            messages.success(request, "Goal created successfully.")
            return redirect("core:goal")
        
        
        else:
            messages.error(request, "Something went wrong.")
            return redirect("core:goal")

    else:
        form = core_form.GoalForm()
        
    context = {
        "goal": goal,
        "form": form,
    }
    return render(request, "goals/my-goal.html", context)


@login_required
def goal_detail(request, gid):
    goal = get_object_or_404(core_model.Goal, gid=gid, user=request.user)
    return render(request, "goals/goal-detail.html", {"goal": goal})


# ✅ View to fund (add money to) a goal from main account
def fund_goal(request, gid):
    goal = core_model.Goal.objects.get(gid=gid, user=request.user)
    account = request.user.account

    if request.method == 'POST':
        current_amount = Decimal(request.POST.get("current_amount"))

        # 1. Check if goal is already fully funded
        if goal.current_amount >= goal.target_amount:
            messages.warning(request, "Goal is already fully funded!")
            return redirect("core:goal-detail", goal.gid)

        # 2. Prevent going beyond target
        if goal.current_amount + current_amount > goal.target_amount:
            messages.warning(request, "You cannot fund more than the goal target amount.")
            return redirect("core:goal-detail", goal.gid)

        # 3. Check user balance
        if current_amount > account.account_balance:
            messages.warning(request, "Insufficient Funds")
            return redirect("core:goal-detail", goal.gid)

        # 4. Deduct from main account
        account.account_balance -= current_amount
        account.save()

        # 5. Add to goal
        goal.current_amount += current_amount
        goal.save()

        core_model.Notification.objects.create(
            user=request.user, notification_type="Goal Amount Added"
        )

        messages.success(request, "Goal funded successfully!")
        return redirect("core:goal-detail", goal.gid)

    messages.warning(request, "Something went wrong!")
    return redirect("account:dashboard")

# def fund_goal(request, gid):
    goal = core_model.Goal.objects.get(gid=gid, user=request.user) 
    account = core_model.Goal.objects.get(gid=gid, user=request.user) 

    account = request.user.account

    if request.method == 'POST':
        current_amount = request.POST.get("current_amount")

        # Check if user has enough balance in main account to fund the goal
        if Decimal(current_amount) <= account.account_balance:
            account.account_balance -= Decimal(current_amount) # Deduct amount from main account
            account.save()
            
            # Prevent funding beyond target
            if goal.current_amount + Decimal(current_amount) > goal.target_amount:
                messages.warning(request, "You cannot fund more than the target amount.")
                return redirect("core:goal-detail", goal.gid)

            # Add same amount to goal balance
            goal.current_amount += Decimal(current_amount) # Add the money in the users target account
            goal.save()
            
            core_model.Notification.objects.create(
                user=request.user, notification_type="Goal Amount Added"
            )
            
            messages.success(request, "Funding Goal Successfull")
            return redirect("core:goal-detail", goal.gid)

        else:
            messages.warning(request, "Insufficient Funds")
            return redirect("core:goal-detail", goal.gid)
    
    else:
        messages.warning(request, "Something went wrong!")
        return redirect("account:dashboard")

            
# Delete card
@login_required
def delete_goal(request, gid):
    goal = get_object_or_404(core_model.Goal, gid=gid, user=request.user)
    account = request.user.account # Get the user’s account

    # Before deleting, check if the goal still has money
    if goal.current_amount > 0:
        account.account_balance += goal.current_amount # move the money to your account for withdrawal
        account.save()

        # Create Notification
        core_model.Notification.objects.create(
            user=request.user,
            notification_type="Goal Deleted"
        )
        
        goal.delete() # delete the goal
        messages.success(request, "Goal deleted and funds added to Account Balance successfully.")
        return redirect("core:goal")

    
    # If goal is empty just delete and notify
    core_model.Notification.objects.create(
        user=request.user,
        notification_type="Goal Deleted"
    )
    
    goal.delete() # delete the goal
    messages.success(request, "Goal deleted successfully.")
    return redirect("core:goal")