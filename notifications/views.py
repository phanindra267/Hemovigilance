from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from notifications.models import Notification

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    unread_only = request.GET.get('unread')
    if unread_only:
        notifications = notifications.filter(is_read=False)

    paginator = Paginator(notifications, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
        'unread_only': unread_only,
    })

@login_required
def mark_read_view(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_as_read()
    if notif.link_url:
        return redirect(notif.link_url)
    return redirect('notifications:list')

@login_required
def mark_all_read_view(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return redirect('notifications:list')
