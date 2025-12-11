from django.db import models
import uuid
from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from django.db.models.signals import post_save


ACCOUNT_STATUS = (
    ("active", "Active"),
    ("pending", "Pending"),
    ("in-active", "In-active")
)

MARITAL_STATUS = (
    ("married", "Married"),
    ("single", "Single"),
    ("other", "Other")
)

GENDER = (
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other")
)


IDENTITY_TYPE = (
    ("national_id_card", "National ID Card"),
    ("drivers_licence", "Drives Licence"),
    ("international_passport", "International Passport")
)


# This function defines the path where a user's uploaded file will be saved
def user_directory_path(instance, filename):
    # Get the file extension (e.g., 'jpg', 'png', 'pdf') from the filename
    ext = filename.split(".")[-1]
    
    # Create a new filename using the instance ID and the file extension
    # Example: if instance.id = 5 and ext = 'jpg', filename becomes "5_jpg"
    filename = "%s_%s" % (instance.id, ext)
    
    # Return the full upload path where the file should be stored
    # Example: "user_12/5_jpg" if instance.user.id = 12
    return "user_{0}/{1}".format(instance.user.id, filename)

class Account(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user =  models.OneToOneField(User, on_delete=models.CASCADE)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00) #123 345 789 102
    account_number = ShortUUIDField(unique=True,length=10, max_length=25, prefix="0", alphabet="123456789") #2175893745837
    account_id = ShortUUIDField(unique=True,length=7, max_length=25, prefix="TIN", alphabet="1234567890") #2175893745837
    pin_number = ShortUUIDField(unique=True,length=4, max_length=10, alphabet="1234567890") #2737
    red_code = ShortUUIDField(unique=True,length=10, max_length=20, alphabet="ABCDEFGHIJ1234567890") #2737
    account_status = models.CharField(max_length=100, choices=ACCOUNT_STATUS, default="in-active")
    date = models.DateTimeField(auto_now_add=True)
    kyc_submitted = models.BooleanField(default=False)
    kyc_confirmed = models.BooleanField(default=False)
    # recommended_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="recommended_by")
    recommended_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="recommended_by")
    review = models.CharField(max_length=100, null=True, blank=True, default="Review")
    
    
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user}"


### KYC
class KYC(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user =  models.OneToOneField(User, on_delete=models.CASCADE)
    account =  models.OneToOneField(Account, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=1000)
    image = models.ImageField(upload_to="kyc", default="avatar.png")
    marrital_status = models.CharField(choices=MARITAL_STATUS, max_length=40)
    gender = models.CharField(choices=GENDER, max_length=40)
    identity_type = models.CharField(choices=IDENTITY_TYPE, max_length=140)
    identity_image = models.ImageField(upload_to="kyc", null=True, blank=True)
    date_of_birth = models.DateTimeField(auto_now_add=False)
    signature = models.ImageField(upload_to="kyc")

    # Address
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    # Contact Detail
    mobile = models.CharField(max_length=1000)
    fax = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user}"    

    
    class Meta:
        ordering = ['-date']


# This is the signal that automatically creates an account when a new creates an account
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)

def save_account(sender, instance,**kwargs):
    instance.account.save()

post_save.connect(create_account, sender=User)
post_save.connect(save_account, sender=User)


