from core import models as core_model

def default(request):
    try:
        notifications = core_model.Notification.objects.filter(user=request.user).order_by("-id")
    
    except:
        notifications = None
    
    return { "notifications": notifications, }
    