from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
from django.views.generic import TemplateView, FormView
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
import json
import requests
from allauth.socialaccount.models import SocialToken
from users.models import *
from etc.models import *
from django.utils import timezone

def _getNotifications(kyprofile):
    notifications = Notifications.objects.filter(users=kyprofile.caprofile,
                                                recieved_date__lte=timezone.now())
    context = {
        'notifications': notifications.order_by('recieved_date'),
        'count': notifications.count(),
    }
    return context

class IndexView(TemplateView):
    template_name = 'index.html'


@login_required(login_url="/login")
def CaFormView(request):#ca-form
    template_name='ca-form.html'
    kyprofile = request.user
    if request.method == 'POST':
        post = request.POST
        collegeName = post.get('college', None)
        year = post.get('year', None)
        whatsapp_number = post.get('whatsapp_number', None)
        postal_address = post.get('postal_address', None)
        pincode = post.get('pincode', None)
        mobile_number = post.get('mobile_number', None)
        if collegeName and whatsapp_number and mobile_number and \
                                        postal_address and pincode and year:

            ca, created = CAProfile.objects.get_or_create(kyprofile=kyprofile)
            if created:
                ca.whatsapp_number=whatsapp_number,
                ca.postal_address=postal_address,
                ca.pincode=pincode
                ca.save()

            welcome_note = Notifications.objects.all().order_by('id')[0]
            welcome_note.users.add(ca)
            welcome_note.save()
            college, created = College.objects.get_or_create(
                                            collegeName=collegeName)

            kyprofile.mobile_number = mobile_number
            kyprofile.college = college
            kyprofile.year = year
            kyprofile.has_ca_profile = True
            kyprofile.save()
            return redirect('/dashboard')
        else:
            return HttpResponse("Invalid form submission")#sth to be done
    else:
        context = {
        'email': kyprofile.email,
        'full_name': kyprofile.full_name,
        'all_colleges': College.objects.all(),
        }
        return render(request, template_name, context)


@login_required(login_url="/login")
def DashboardView(request):
    kyprofile = request.user
    if kyprofile.has_ca_profile:
        template_name = 'ca-dashboard/dashboard.html'
        context = _getNotifications(kyprofile)
        context['posts'] = Post.objects.all().order_by('-id')[:9]

        return render(request, template_name, context)
    else:
        return redirect('/ca-form')


@login_required(login_url="/login")
def CAProfileUpdateView(request):
    kyprofile = request.user
    ca_profile_object = CAProfile.objects.get(kyprofile=kyprofile)

    if request.method == 'POST':
        post = request.POST
        kyprofile.mobile_number = post.get('mobile_number', None)
        kyprofile.save()
        ca_profile_object.whatsapp_number = post.get('whatsapp_number', None)
        ca_profile_object.postal_address = post.get('address', None)
        ca_profile_object.pincode = post.get('pincode', None)
        ca_profile_object.save()

    context = {
        "email": kyprofile.email,
        "fullname": kyprofile.full_name,
        "year": kyprofile.year,
        "gender": kyprofile.gender,
        "mobile_number": kyprofile.mobile_number,
        "college": kyprofile.college,
        "whatsapp_number": ca_profile_object.whatsapp_number,
        "pincode": ca_profile_object.pincode,
        "address": ca_profile_object.postal_address,

    }

    if kyprofile.has_ca_profile:
        template_name = 'ca-dashboard/user.html'
        notices = _getNotifications(kyprofile)
        #new_context = context + notices
        new_context = context.copy()
        new_context.update(notices)
        return render(request, template_name, new_context)
    else:
        return redirect('/ca-form')

@login_required(login_url="/login")
def LeaderBoardView(request):
    kyprofile = request.user
    print(kyprofile)
    if kyprofile.has_ca_profile:
        template_name = 'ca-dashboard/leaderboard.html'
        context = _getNotifications(kyprofile)
        return render(request, template_name, context)
    else:
        return redirect('/ca-form')


@login_required(login_url="/login")
def NotificationsView(request):
    kyprofile = request.user
    print(kyprofile)
    if kyprofile.has_ca_profile:
        template_name = 'ca-dashboard/notifications.html'
        context = _getNotifications(kyprofile)
        return render(request, template_name, context)
    else:
        return redirect('/ca-form')

def PrivacyPolicyView(request):
    template_name = 'privacy_policy.html'
    return render(request, template_name, {})

def LogoutView(request):
    logout(request)
    return redirect('/')
