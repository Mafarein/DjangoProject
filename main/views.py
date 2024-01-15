from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Post, Topic, Comment, User
from .forms import PostForm, UserForm, MyUserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.http import JsonResponse

# Create your views here.

def verify_email_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified.')
        return redirect('verify-email-complete')   
    else:
        messages.warning(request, 'The link is invalid.')
    return render(request, 'main/verify_email_confirm.html')

def verify_email(request):
    if request.method == "POST":
        if request.user.email_is_verified != True:
            current_site = get_current_site(request)
            user = request.user
            email = request.user.email
            subject = "Verify Email"
            message = render_to_string('main/verify_email_message.html', {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            email = EmailMessage(
                subject, message, to=[email]
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('verify-email-done')
        else:
            return redirect('signup')
    return render(request, 'main/verify_email.html')

def verify_email_done(request):
    return render(request, 'main/verify_email_done.html')

def verify_email_complete(request):
    return render(request, 'main/verify_email_complete.html')

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, 'Email or Password does not exist')


    context = {'page':page}
    return render(request, 'main/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        next = request.GET.get('next')
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password1 = form.cleaned_data.get('password1')
            user.username = user.username.lower()
            user.save()
            new_user = authenticate(email=user.email, password=password1)
            login(request, new_user)
            if next:
                return redirect(next)
            else:
                return redirect('verify-email')
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'main/login_register.html', {'form':form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    posts= Post.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q)
    |Q(description__icontains=q))

    topics = Topic.objects.all()
    post_comments = Comment.objects.filter(Q(post__topic__name__icontains=q))

    context = {'posts': posts, 'topics': topics, 'post_comments' : post_comments}
    return render(request, 'main/home.html', context)


def post(request, pk):
    post = Post.objects.get(id=pk)
    post_comments = post.comment_set.all()

    if request.method == 'POST':
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            body=request.POST.get('body')
        )
        return redirect('post', pk=post.id)
    context = {'post': post, 'post_comments':post_comments}
    return render(request, 'main/post.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    posts = user.post_set.all()
    post_comments = user.comment_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'posts': posts, 'post_comments': post_comments, 'topics':topics}
    return render(request, 'main/profile.html', context)

@login_required(login_url='login')
def createPost(request):
    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'main/post_form.html', context)

@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)

    if request.user != post.created_by:
        return HttpResponse('You are not allowed to do that')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', pk=post.id)

    context = {'form': form}
    return render(request, 'main/post_form.html', context)

@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)

    if request.user != post.created_by:
        return HttpResponse('You are not allowed to do that')
    
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'main/delete.html', {'obj':post})

@login_required(login_url='login')
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse('You are not allowed to do that')
    
    if request.method == 'POST':
        comment.delete()
        return redirect('home')
    return render(request, 'main/delete.html', {'obj':comment})

@login_required(login_url='login')
def updateProfile(request):
    user = request.user
    form = UserForm(instance=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'main/update_profile.html', {'form': form})


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = User.objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string(
                    "main/template_password_reset.html",{
                        'user': associated_user,
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                        'token': account_activation_token.make_token(associated_user),
                        'protocol': 'https' if request.is_secure() else 'http'
                    })
                email = EmailMessage(subject, message, to=[associated_user])
                if email.send():
                    messages.success(request, "Password reset sent")
                else:
                    messages.error(request, 'Problem sending reset password email')
                  

            return redirect('home')


    form = PasswordResetForm()
    return render(request , 'main/password_reset_form.html', context={'form': form})

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. Now you can login your account.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        form = SetPasswordForm(user)
        return render(request, 'main/password_reset_confirm.html', {'form': form})

    else:
        messages.error(request, "Link is expired.")


    messages.error(request, 'Something went wrong')
    return redirect('home')
