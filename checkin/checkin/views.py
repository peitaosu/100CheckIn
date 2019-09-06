from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os
import sys
import subprocess
import json
import sqlite3
import hashlib
from sqlite3 import OperationalError
from . import models

def hash_code(source):
    hash = hashlib.sha256()
    hash.update(source.encode())
    return hash.hexdigest()

def if_not_login(request):
    if "email" not in request.session:
        return True
    return False

def show_login_user(request, context):
    if "email" in request.session:
        current_user = models.User.objects.get(email=request.session["email"])
        if current_user.name != "":
            context["user_login"] = current_user.name
        else:
            context["user_login"] = request.session["email"]
    return context

def event(request, action):
    if settings.MAINTENANCE_MODE:
        return redirect("/")
    context = {
        "all": [],
        "detail": None
    }
    if if_not_login(request):
        return redirect("/")
    context = show_login_user(request, context)
    current_user = models.User.objects.get(email=request.session["email"])
    if action == "/add":
        return render(request, 'add.html', context)
    elif action == "/new":
        eid = 0
        if len(models.Event.objects.all()) > 0:
            eid = models.Event.objects.all().last().eid + 1
        new_event = models.Event(eid=eid, ueid=(models.User_Event.objects.all().filter(user=current_user).count() + 1), title=request.POST["title"], description=request.POST["description"])
        new_event.save()
        new_user_event = models.User_Event(user=current_user, event=new_event)
        new_user_event.save()
        return redirect("/event")
    elif action == "/delete":
        event = models.Event.objects.get(eid=request.GET["eid"])
        user_event = models.User_Event.objects.get(user=current_user, event=event)
        user_event.delete()
        return redirect("/event")
    elif action == "/detail":
        event = models.Event.objects.get(eid=request.GET["eid"])
        context["detail"] = event
        return render(request, 'detail.html', context)
    elif action == "/update":
        event = models.Event.objects.get(eid=request.POST["eid"])
        event.picture = request.POST["img_save"]
        event.note = request.POST["note"]
        event.save()
        context["detail"] = event
        return render(request, 'detail.html', context)
    elif action == "/link":
        link_user = models.User.objects.get(email=request.session["email"])
        link_events = models.User_Event.objects.all().filter(user=link_user)
        for link_event in link_events:
            new_link = models.User_Event(user=current_user, event=link_event)
            new_link.save()
        return redirect("/event")
    else:
        all_events = models.User_Event.objects.all().filter(user=current_user)
        if current_user.link != "":
            linked_user_all_events = models.User_Event.objects.all().filter(user=models.User.objects.get(email=current_user.link))
            all_events.append(linked_user_all_events)
        total = len(all_events)
        complete = 0
        for user_event in all_events:
            context["all"].append(user_event.event)
            if user_event.event.status == "DONE":
                complete += 1
        if complete == 0:
            context["complete"] = 0
        else:
            context["complete"] = int(complete/total * 100)
        return render(request, 'event.html', context)

def user(request, action):
    if settings.MAINTENANCE_MODE:
        return redirect("/")
    if action == "/register":
        if models.User.objects.filter(email=request.POST["email"]).count() > 0:
            context = {
                "has_alert": True,
                "alertclass": "alert-danger",
                "alertmessage": "You email address was already registered, please check again."
            }
            return render(request, 'index.html', context)
        new_user = models.User(email=request.POST["email"], password=hash_code(request.POST["password"]))
        if "name" in request.POST:
            new_user.name = request.POST["name"]
        new_user.save()
        request.session["email"] = new_user.email
        request.session["user_login"] = True
        return redirect("/user")
    elif action == "/login":
        if models.User.objects.filter(email=request.POST["email"]).count() == 0:
            context = {
                "has_alert": True,
                "alertclass": "alert-danger",
                "alertmessage": "You email was not registered, please check again or register this email."
            }
            return render(request, 'index.html', context)
        user = models.User.objects.get(email=request.POST["email"])
        if user.password == hash_code(request.POST["password"]):
            request.session["email"] = user.email
            request.session["user_login"] = True
            if user.name != "":
                return redirect("/")
    elif action == "/update":
        if if_not_login(request):
            return redirect("/")
        user = models.User.objects.get(email=request.session["email"])
        user.name = request.POST["name"]
        if request.POST["link"] != "":
            user.link = request.POST["link"]
            if models.User.objects.filter(email=user.link).count() == 0:
                context = {
                    "has_alert": True,
                    "alertclass": "alert-danger",
                    "alertmessage": "The user email you want to link {} is not exists. Please check the email again.".format(user.link)
                }
                context = show_login_user(request, context)
                return render(request, 'index.html', context)
        user.save()
    elif action == "/logout":
        request.session.flush()
        return redirect("/")
    elif action == "/link":
        if if_not_login(request):
            return redirect("/")
        user = models.User.objects.get(email=request.session["email"])
        if user.link == "":
            context = {
                "has_alert": True,
                "alertclass": "alert-danger",
                "alertmessage": "You haven't link a user. Please link a user with email in your profile page."
            }
            context = show_login_user(request, context)
            return render(request, 'index.html', context)
        linked_user = models.User.objects.get(email=user.link)
        if linked_user.link != user.email:
            context = {
                "has_alert": True,
                "alertclass": "alert-danger",
                "alertmessage": "The user you linked haven't link you yet. Please ask him\her to link you with your email in his\her profile page."
            }
            context = show_login_user(request, context)
            return render(request, 'index.html', context)
        context["profile"] = linked_user
        context["can_modify"] = False
        return render(request, 'user.html', context)
    context = show_login_user(request, {})
    context["profile"] = models.User.objects.get(email=request.session["email"])
    return render(request, 'user.html', context)

def index(request):
    context = {}
    context["MAINTENANCE_MODE"] = settings.MAINTENANCE_MODE
    context = show_login_user(request, context)
    return render(request, 'index.html', context)
