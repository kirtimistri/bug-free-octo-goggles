from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from django .urls import reverse
from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
def profile_view(request,username=None):
    if username:
       profile=get_object_or_404(User,username=username).profile
    else:
       try:
          profile=request.user.profile
       except:
          return redirect('account_login')
    return render(request, 'users/profile.html', {'profile': profile})

@login_required
def profile_edit_view(request):
     form=ProfileForm(instance=request.user.profile)
     if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES,instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
     if request.path==reverse('profile-onboarding'):
        onboardig=True
     else:
        onboardig=False
     return render(request,'users/profile_edit.html',{'form':form,' onboardig': onboardig})

@login_required
def profile_settings_view(request):
   return render(request,'users/profile_settings.html')

@login_required
def profile_emailchange(request):
   if request.htmx:
      form=EmailForm(instance=request.user)
      return render(request,'partials/email_form.html',{'form':form})
   
   if request.method =='POST':
       form=EmailForm(request.POST,instance=request.user)
       if form.is_valid():
          # check if emailexist alredy
          email=form.cleaned_data['email']
          if User.objects.filter(email=email).exclude(id=request.user.id).exists():
             messages.warning(request,f'{email}is alredy in use .')
             return redirect('profile-settings')
          form.save()
          # then signal updates email address and set vrified to falase
          send_email_confirmation(request,request.user)# sends an confirmation email 

          return redirect ('profile-settings')
       else:
          messages.warning(request,'Form is not valid')
          return redirect('profile-settings')
   return redirect ('home')

@login_required
def profile_emailverify(request):
   send_email_confirmation(request,request.user)
   return redirect('profile-settings')

@login_required
def profile_delete_view(request):
    user=request.user
    if request.method=="POST":
       logout(request)
       user.delete()
       messages.success(request,'Account deleted, what a pitty')
       return redirect('home')

    return render(request,'users/profile_delete.html')