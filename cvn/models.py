from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()
# Create your models here.


class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    id_user = models.IntegerField()
    about_user = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images',default='empty_profile.png')

    def __str__(self):
        return self.user.username


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    post_message = models.TextField(max_length=250)
    created_at = models.DateField(default=datetime.now)
    like_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user

class PostLike(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowUser(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user

class Comment(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)
    comment = models.TextField(max_length=250)
    comment_date = models.DateField(default=datetime.now)

    def __str__(self):
        return self.username