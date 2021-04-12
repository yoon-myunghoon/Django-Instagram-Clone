from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse

from notifications.models import Notification


def ShowNotifications(request):
    user = request.user
    # 자신이 단 댓글도 notification에 보이게 됨, 안보이도록 만드는 것이 좋지않을까?
    notifications = Notification.objects.filter(user=user).order_by('-date')
    # 확인한 공지들은 안보이도록 해주는 처리가 없는데 이 부분은 왜하는 거지? 배지에서 쓰는건가..
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)

    template = loader.get_template('notifications.html')

    context = {
        'notifications': notifications,
    }

    return HttpResponse(template.render(context, request))


def DeleteNotification(request, noti_id):
    user = request.user
    # 여기서 없애주는 작업을 하기전에 언팔이나 좋아요취소, 댓글 삭제 등의 작업으로
    # 이미 notification 객체가 사라지면 해당 id의 객체가 없어서 문제가 생기지 않을까?
    # 생각해보니까 이미 그런 작업이 일어났을 경우에는 notifications 리스트에서 사라져서
    # 해당 페이지에서 안보이니까 해당 id로 요청을 보낼 수가 없어서 문제가 발생하지않을듯
    # 반대의 경우에는 문제 생기지 않을까 생각했는데, 생각해보니까 filter는 객체가 없으면 어떤 것을 반환하지?
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('show-notifications')


def CountNotifications(request):
    count_notifications = 0
    if request.user.is_authenticated:
        count_notifications = Notification.objects.filter(user=request.user, is_seen=False).count()

    return {'count_notifications': count_notifications}