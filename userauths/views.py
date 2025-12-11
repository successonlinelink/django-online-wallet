from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User 
from .forms import UserRegisterForm 


# Email Verification Imports
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# End of Email Verification Imports

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Register
def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Hi, you are already logged in.")
        return redirect("/")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_active = True
            new_user.save()

            # Authenticate and log in the user
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                # ✅ Send welcome email with logo and HTML formatting
                subject = "🎉 Welcome to Our Platform!"
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]

                # HTML content
                html_content = render_to_string("emails/welcome_email.html", {
                    "user": user,
                    "login_url": "https://yourwebsite.com/login",
                    "logo_url": "06.jpg?semt=ais_hybrid&w=740&q=80",  # change to your real logo URL
                })

                # Plain text fallback
                text_content = (
                    f"Hello {user.username},\n\n"
                    f"Welcome to Tin Wallet!\n\n"
                    f"Your account has been created successfully.\n"
                    f"Email: {user.email}\n"
                    f"Username: {user.username}\n\n"
                    f"Login anytime at: https://yourwebsite.com/login\n\n"
                    f"Best regards,\n"
                    f"The Support Team."
                )

                msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")

                try:
                    msg.send()
                except Exception as e:
                    messages.warning(request, f"Account created, but email could not be sent: {e}")

                return redirect("userauths:account_created")

            else:
                messages.warning(request, "Account created, but login failed. Please sign in manually.")
                return redirect("userauths:login")

        else:
            messages.error(request, "Error creating account, please try again.")
    else:
        form = UserRegisterForm()

    context = {"form": form}
    return render(request, "userauths/register.html", context)



# account_created
@login_required
def account_created(request):

    context = { }
    return render(request, "userauths/account_created.html", context)
    
   
# Login
def login_view(request):
    # Prevent logged-in users from accessing login page
    if request.user.is_authenticated:
        messages.warning(request, "Hey, you are already logged in.")
        return redirect("/")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, f"No account found with email: {email}")
            return redirect("userauths:login")

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # messages.success(request, "You are now logged in.")
                # return redirect("/")
            # Redirect them to thwheer they were after login rather than redirecting them to the home page
            next_url = request.GET.get("next", 'account:dashboard') # get the next url from the request, if it does not exist, redirect to ccount:dashboard
            return redirect(next_url) # 
        
        else:
            messages.error(request, "Invalid password. Please try again.")
            return redirect("userauths:login")
        
        
    

    return render(request, "userauths/login.html")

# Log Out
def logout_view(request):
    logout(request)
    messages.success(request, "You logged out.")
    return redirect("userauths:login")

# Forget Password
def forget_password(request):
    
    if request.method == "POST":
        email = request.POST.get("email")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Email verification
            current_site = get_current_site(request)
            mail_subject = "Reset your password."
            message = render_to_string("userauths/reset_password_email.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })

            to_email = email
            email_msg = EmailMessage(mail_subject, message, to=[to_email])
            email_msg.send()

            messages.success(request, "Password reset link has been sent to your email address.")
            return redirect("userauths:login")

        else:
            messages.error(request, f"Account with {email} does not exist.")
    return render(request, "userauths/forget_password.html")


# Reset Validate
def reset_validate(request, uidb64, token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    
    except(TypeError, OverflowError, ValueError, User.DoesNotExist):
        user = None

    # Check the token
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('userauths:reset_password')

    else:
        messages.error(request, "This link has been expired!")
        return redirect('userauths:login')


# Reset Password
def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password == confirm_password:
            uid = request.session.get('uid') # Get uid from session cos it has been stored there in reset_validate view
            user = User.objects.get(pk=uid) # Get user by primary key
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful.")
            return redirect("userauths:login")
        
        else:
            messages.error(request, "Password do not match!")
            return redirect("userauths:reset_password")
    
    return render(request, "userauths/reset_password.html")