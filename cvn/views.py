from cmath import log
from hashlib import new
from time import process_time
from turtle import pos

from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from numpy import imag
from .models import Profile, Post, PostLike, FollowUser,Comment
from itertools import chain
import random


# Create your views here.


@login_required(login_url='signin')
def index(request):
    index_user = User.objects.get(username=request.user.username)
    index_profile = Profile.objects.get(user=index_user)
    user_posts = Post.objects.filter(user=index_profile)
    index_following_list = []

    main_feed = []
    comments=[]
    index_following = FollowUser.objects.filter(follower=request.user.username)

    for users in index_following:
        index_following_list.append(users)
    for usernames in index_following_list:
        index_feed = Post.objects.filter(user=usernames)
        main_feed.append(index_feed)
    main_feed.append(user_posts)
    for i in main_feed:
        for j in i:
            comments.append(getPostComments(j.id))
    comment=list(chain(*comments))
    index_feed = list(chain(*main_feed))
    context =  {'user_profile': index_profile, 
    'posts':index_feed,'comments':comments}
    ''' for c in comments:
        for k in c:
            print(k.comment) '''
    return render(request, 'index.html',context)


def getPostComments(id):
    comments = Comment.objects.all()
    return comments


@login_required(login_url='signin')
def search(request):
    user_obje = User.objects.get(username=request.user.username)
    user_profil = Profile.objects.get(user=user_obje)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profil, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def follow(request):

    if request.method =='POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowUser.objects.filter(follower=follower,user=user).first():
            unfollow = FollowUser.objects.get(follower=follower,user=user)
            unfollow.delete()
            return redirect('/profile/'+user)
        else:
            follow_user = FollowUser.objects.create(follower=follower,user=user)
            follow_user.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')
@login_required(login_url='signin')
def comment(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    com = []
    if request.method == 'POST':
        com = request.POST['comment']
        new_comment = Comment.objects.create(post_id=post_id,username=username,comment=com)
        #post.no_of_comment=post.no_of_comment+1
        new_comment.save()
        return redirect('/')
    elif request.method == "DELETE":
        my_comment = Comment.objects.filter(post_id=post_id,username=username)
        #post.no_of_comment = post.no_of_comment-1
        my_comment.delete()
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_check = PostLike.objects.filter(post_id=post_id,username=username).first()

    if like_check == None:
        new_like = PostLike.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.like_count = post.like_count+1
        post.save()
        return redirect('/')
    else:
        
        post.like_count = post.like_count-1
        like_check.delete()
        post.save()
        return redirect('/')
@login_required(login_url='signin')
def profile(request,pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowUser.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowUser.objects.filter(user=pk))
    user_following = len(FollowUser.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method=='POST':
        if request.FILES.get('image')==None:
            image = user_profile.profileimg
            about_user = request.POST['bio']
            
            user_profile.profileimg = image
            user_profile.about_user=about_user
            user_profile.save()
        if request.FILES.get('image'):
            image = request.FILES.get('image')
            about_user = request.POST['bio']
            user_profile.profileimg = image
            user_profile.about_user=about_user
            user_profile.save()
        return redirect('settings')
    
    return render(request,'setting.html',{'user_profile':user_profile})



@login_required(login_url='signin')
def upload(request):
    if request.method =='POST':
        user = request.user.username
        post_message = request.POST['message']

        new_post = Post.objects.create(user=user,post_message=post_message)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


#Signup with password &username & email check
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Exists')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Exists')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')


def signin(reqest):
    if reqest.method =='POST':
        username = reqest.POST['username']
        password = reqest.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(reqest,user)
            return redirect('/')
        else:
            messages.info(reqest,'Invalid Username or Password')
            return redirect('signin')
    else:
        return render(reqest,'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

