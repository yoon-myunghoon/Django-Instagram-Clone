from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.urls import reverse
import uuid

from notifications.models import Notification


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Tag(models.Model):
    # verbose_name 속성이 머하는 거지?
    title = models.CharField(max_length=75, verbose_name='Tag')
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        # 머하는 필드들이지?
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        # reverse 가 하는 역할은?
        return reverse('tags', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # slug이 머지?
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class PostFileContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_owner')
    file = models.FileField(upload_to=user_directory_path)


class Post(models.Model):
    # 왜 id를 따로 지정해주는거지?
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 왜 다대다 관계인거지? 일대다 아닌가??
    content = models.ManyToManyField(PostFileContent, related_name='contents')
    caption = models.TextField(max_length=1500, verbose_name='Caption')
    posted = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='tags')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)

    # 왜 이렇게 하지?
    def get_absolute_url(self):
        return reverse('postdetails', args=[str(self.id)])


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='following')

    def user_follow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification(sender=sender, user=following, notification_type=3)
        notify.save()

    def user_unfollow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following

        notify = Notification.objects.filter(sender=sender, user=following, notification_type=3)
        notify.delete()


# stream을 왜 만들어주는 거지?
# 결과가 id로 나오는데 어떻게 되는거지?
class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    # 이렇게 하는 이유는?
    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like')

    # self와 instance의 차이는?
    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        notify = Notification(post=post, sender=sender, user=post.user, notification_type=1)
        notify.save()

    def user_unlike_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user

        notify = Notification.objects.filter(post=post, sender=sender, notification_type=1)
        notify.delete()


# signal을 models 에서도 줄 수 있는 듯
#Stream
post_save.connect(Stream.add_post, sender=Post)

#Likes
post_save.connect(Likes.user_liked_post, sender=Likes)
post_delete.connect(Likes.user_unlike_post, sender=Likes)

#Follow
post_save.connect(Follow.user_follow, sender=Follow)
post_delete.connect(Follow.user_unfollow, sender=Follow)

