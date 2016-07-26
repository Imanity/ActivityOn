# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from datetime import datetime 
from django.http import HttpResponse
from django.template import RequestContext
from app.models import error
from .models import *
from django.contrib.auth import authenticate
from django.template import loader
import json
import os
# Create your views here.

def index(request):
    request.META["CSRF_COOKIE_USED"] = True
    context = {
        'role': request.session.get('role', 1)
    }
    return render_to_response('index.html', RequestContext(request, context))
        
def test(request):
    return HttpResponse('test')

def ChangeAvatar(request):
    UID = request.GET.get('UID')
    f = request.FILES['file']
    destination = open('static/images/'+str(UID)+'.png', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return HttpResponse({})

def server_time(request):
    import time
    re = dict()
    re['error'] = error(1, 'ok')
    re['current_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time() + 8 * 60 * 60))
    return HttpResponse(json.dumps(re), content_type = 'application/json')

def register(request):
    try :
        user = UserBase.objects.get(UPrivateEmail = request.POST.get('privateemail'))
    except UserBase.DoesNotExist:
        try: 
            user = UserBase.objects.get(UName = request.POST.get('nickname'))
        except UserBase.DoesNotExist:
            p = request.POST
            base = UserBase(UAvatar=p.get('Avatar'),UPrivateEmail = p.get('privateemail'),UPublicEmail = p.get('openemail'),UName = p.get('nickname'),UPassword = p.get('password'))
            base.save()
            ac = UserActivity(UId = base.UId, UInAct = '',UInActNum = 0,UOrganizedAct = '', UOrganizedNum = 0, UTags = '')
            ac.save()
            at = UserTimeline(UId = base.UId)
            at.save()
            return HttpResponse(json.dumps({"ErrorCode":1,"UID":base.UId}))
            pass
        else :
            return HttpResponse(json.dumps({"ErrorCode":-1}))
            pass
    else :
        return HttpResponse(json.dumps({"ErrorCode":0}))
        pass

def login(request):
    try:
        user = UserBase.objects.get(UPrivateEmail = request.POST.get('user_name'), UPassword = request.POST.get('user_password'))
    except UserBase.DoesNotExist:
        return  HttpResponse(json.dumps({"ErrorCode":0}))
    else :
        return  HttpResponse(json.dumps({"ErrorCode":1,"UID":user.UId,'Avatar':user.UAvatar}))
    
def logout(request):
    return  render(request,'index.html',{})

def ReturnNone(request):
    return render(request,'index.html',{})

def info(request):
    try:
        user = UserBase.objects.get(UId = request.GET.get('UID'))
    except UserBase.DoesNotExist:
        return HttpResponse(json.dumps({'ErrorCode':0}))
    else:
        return HttpResponse(json.dumps({'ErrorCode':1, 'UName':user.UName, 'UID':user.UId, 'UPrivateEmail':user.UPrivateEmail, 'UPublicEmail':user.UPublicEmail, 'UAvatar': user.UAvatar, 'UInfo':user.UInfo, 'UStatus':user.UStatus, 'UFollow':user.UFollow, 'UFollowed':user.UFollowed, 'UMessage':user.UMessage}))

def modify(request):
    try:
        user = UserBase.objects.get(UId = request.POST.get('UID'))
    except UserBase.DoesNotExist:
        return HttpResponse(json.dumps({'ErrorCode':0}))
    else:
        if 'UName' in request.POST:
            user.UName = request.POST.get('UName')
        if 'UInfo' in request.POST:
            print(request.POST.get('UInfo'))
            user.UInfo = request.POST.get('UInfo')
        if 'UPublicEmail' in request.POST:
            user.UPublicEmail = request.POST.get('UPublicEmail')
        user.save()
        return HttpResponse(json.dumps({'ErrorCode':1}))


def modifyPassword(request):
    try:
        user = UserBase.objects.get(UId = request.POST.get('UID'),UPassword = request.POST.get('UPassword'))
    except UserBase.DoesNotExist:
        return HttpResponse(json.dumps({'ErrorCode':0}))
    else:
        user.UPassword = request.POST.get('NewUPassword')
        user.save()
        return HttpResponse(json.dumps({'ErrorCode':1}))


def Create_Activity(request):
    re = dict()
    if request.method == 'POST':
        act = Activity()
        p = request.POST
        act.AStatus = int(0)
        act.AType = int(p.get('Type'))
        act.AAdmin = int(p.get('Admin'))
        act.AMaxRegister = p.get('MaxRegister')
        act.AEntryDDL = p.get('EntryDDL')
        act.AStartTime = p.get('StartTime')
        act.AEndTime = p.get('EndTime')
        act.ATitle = p.get('Title')
        act.ALocation = p.get('Location')
        act.AInfo = p.get('Info')
        act.ASummary = p.get('Summary')
        act.save()
        UActivity = UserActivity.objects.get(UId = p.get('Admin'))
        UActivity.UOrganizedAct += ','+str(act.AId)
        UActivity.UOrganizedNum +=1
        UActivity.save()
        re['ErrorCode'] = 1
        re["AID"] = act.AId
        user = UserBase.objects.get(UId = act.AAdmin)
        if len(user.UFollowed) != 0:
            followedList = list(map(int,user.UFollowed[1:].split(',')))
            for i in followedList:
                ut = UserTimeline.objects.get(UId = i)
                ut.UTimelineFrom += ',' +str(user.UId)
                ut.UTimelineAct += ',' + str(act.AId)
                ut.UTimelineType += ',0'
                ut.save()
                    
    else :
        re['ErrorCode']=0 
    return HttpResponse(json.dumps(re))

def modify_Activity(request):
    re = dict()
    if request.method == 'POST':
        act = Activity.objects.get(AId = request.POST.get('AID'))
        if 'Type' in request.POST:
            act.AType = request.POST.get('Type')    
        if 'EntryDDL' in request.POST:
            act.AEntryDDL = request.POST.get('EntryDDL')       
        if 'StartTime' in request.POST:
            act.AStartTime = request.POST.get('StartTime')   
        if 'EndTime' in request.POST:
            act.AEndTime = request.POST.get('EndTime')   
        if 'Title' in request.POST:
            act.ATitle = request.POST.get('Title')   
        if 'Location' in request.POST:
            act.ALocation = request.POST.get('Location')   
        if 'Info' in request.POST:
            act.AInfo = request.POST.get('Info')
        if 'Summary' in request.POST:
            act.ASummary = request.POST.get('Summary')
        act.save()
        re['ErrorCode'] = 1
        return HttpResponse(json.dumps(re))
    else :
        re['ErrorCode'] = 0
        return HttpResponse(json.dumps(re))

def Get_Activity(request):
    try:
        act = Activity.objects.get(AId = request.GET.get('AID'))

    except Activity.DoesNotExist:
        return HttpResponse(json.dumps({'ErrorCode':0}))
    else:
        return HttpResponse(json.dumps({'ErrorCode':1,'Admin':act.AAdmin,'Type':act.AType,'Register':act.ARegister,'Unregister':act.AUnregister, 'MaxRegister':act.AMaxRegister,'StartTime':act.AStartTime, 'EntryDDL':act.AEntryDDL,'EndTime':act.AEndTime,'Title':act.ATitle, 'Location':act.ALocation, 'Info':act.AInfo, 'Summary':act.ASummary})) 

def participate(request):
    re = dict()
    if request.method == 'POST':
        try:

            useractivity = UserActivity.objects.get(UId = request.POST.get('UID'))
            activity = Activity.objects.get(AId = request.POST.get('AID'))
        except :
            re['ErrorCode']=0
        else:
            if useractivity.UInAct.find(','+str(activity.AId)) == -1:
                useravtivity.UInAct+=','+str(activity.AId)
                useractivity.UInActNum+=1
                activity.Unregister+= ','+str(useractivity.UId)
                useractivity.save()
                activity.save()
                re['ErrorCode']=1
                user = UserBase.objects.get(UId = useravtivity.UId)
                if len(user.UFollowed) != 0:
                    followedList = list(map(int,user.UFollowed[1:].split(',')))
                    for i in followedList:
                        ut = UserTimeline.objects.get(UId = i)
                        ut.UTimelineFrom += ',' +str(user.UId)
                        ut.UTimelineAct += ',' + str(act.AId)
                        ut.UTimelineType += ',1'
                        ut.save()
            else:
                re['ErrorCode'] = -1
    else :
        re['ErrorCode']=0
    return HttpResponse(json.dumps(re))

def Accept(request):
    re = dict()
    if request.method == 'POST':
        try:
            activity = Activity.objects.get(AId = request.POST.get('AID'))
        except:
            re['ErrorCode']=0
        else:
            activity.ARegister+=','+ str(request.POST.get('UID'))
            activity.AUnregister.replace(','+ str(request.POST.get('UID')),'')
            activity.save()
            re['ErrorCode']=1
    else:
        re['ErrorCode']=0
    return HttpResponse(json.dumps(re))

def Reject(request):
    re = dict()
    if request.method == 'POST':
        try:
            activity = Activity.objects.get(AId = request.POST.get('AID'))
        except:
            re['ErrorCode']=0
        else:
            activity.AUnregister.replace(','+ str(request.POST.get('UID')),'')
            activity.save()
            re['ErrorCode']=1
    else:
        re['ErrorCode']=0
    return HttpResponse(json.dumps(re))


def Get_UserActivity(request):
    re = dict()
    uact = UserActivity.objects.get(UId = request.GET.get('UID'))
    OAct = []
    if uact.UOrganizedAct!='':
        OActList = list(map(int,(uact.UOrganizedAct[1:]).split(',')))
        for i in OActList:
            act = Activity.objects.get(AId = i)
            OAct.append({'AID':act.AId,'Title':act.ATitle,'StartTime':act.AStartTime,'EndTime':act.AEndTime, 'Location':act.ALocation, 'Summary':act.ASummary})
    IAct = []
    if uact.UInAct != '':
        IActList = list(map(int,uact.UInAct[1:].split(',')))
        for i in IActList:
            act = Activity.objects.get(AId = i)
            IAct.append({'AID':act.AId,'Title':act.ATitle,'StartTime':act.AStartTime,'EndTime':act.AEndTime, 'Location':act.ALocation, 'Summary':act.ASummary})
    re['ErrorCode']=1
    re['InActivity'] = IAct 
    re['OrganizedActivity'] = OAct 
    return HttpResponse(json.dumps(re))

def Get_Register(request):
    re =dict()
    act = Activity.objects.get(AId = request.GET.get('AID'))
    Register = []
    if act.ARegister != '':
        RegisterList = list(map(int,act.ARegister[1:].split(',')))
        for i in RegisterList:
            user = UserBase.objects.get(UId = i)
            Register.append({'UID':user.UId,'Name':user.UName,'Avator':user.UAvator})
    Unregister = []
    if act.AUnregister != '':
        UnregisterList = list(map(int,act.AUnregister[1:].split(',')))
        for i in UnregisterList:
            user = UserBase.objects.get(UId = i)
            Unregister.append({'UID':user.UId,'Name':user.UName,'Avator':None})
    re['ErrorCode']=1
    re['Register'] = Register 
    re['Unregister'] = Unregister 
    return HttpResponse(json.dumps(re))

def Delete_Activity(request):
    re = dict()
    act = Activity.objects.get(AId = request.GET.get('AID'))
    if act.ARegister != '':
        RegisterList = list(map(int,act.ARegister[1:].split(',')))
        for i in RegisterList:
            uact = UserActivity.objects.get(UId = i)
            uact.UInAct.replace(','+str(request.GET.get('AID')),'')
            uact.UInActNum -=1
            uact.save()
    if act.AUnregister != '':
        UnregisterList = list(map(int,act.AUnregister[1:].split(',')))
        for i in UnregisterList:
            uact = UserActivity.objects.get(UId = i)
            uact.UInAct.replace(','+str(request.GET.get('AID')),'')
            uact.UInActNum -=1
            uact.save()
    uact = UserActivity.objects.get(UId = act.AAdmin)
    uact.UOrganizedAct.replace(','+str(request.GET.get('AID')),'')
    uact.UOrganizedNum -=1
    uact.save()
    act.delete()
    re['ErrorCode']=1
    return HttpResponse(json.dumps(re))
   
def GetFollow(request):
    re = dict()
    print( request.GET.get('UID'))
    user = UserBase.objects.get(UId = request.GET.get('UID'))
    follow = []
    if len(user.UFollow) != 0:
        followList = list(map(int,user.UFollow[1:].split(',')))
        for i in followList:
            u = UserBase.objects.get(UId = i)
            follow.append({'UID':u.UId,'Avatar':'static/images/admin.png','Name':u.UName})
    followed = []
    if len(user.UFollowed) != 0:
        followedList = list(map(int,user.UFollowed[1:].split(',')))
        for i in followedList:
            u = UserBase.objects.get(UId = i)
            followed.append({'UID':u.UId,'Avatar':'static/images/admin.png','Name':u.UName})
    re['ErrorCode'] = 1
    re['Follow'] = follow 
    re['Followed'] = followed 
    return HttpResponse(json.dumps(re))

def Follow(request):
    re = dict()
    user = UserBase.objects.get(UId = request.POST.get('UID'))
    if user.UFollow.find( ','+str(request.POST.get('FollowID'))) == -1:
        user.UFollow += ','+str(request.POST.get('FollowID'))
        user.save()
    fo = UserBase.objects.get(UId = request.POST.get('FollowID'))
    if fo.UFollowed.find( ','+str(user.UId)) == -1:
        fo.UFollowed += ','+str(user.UId)
    fo.save()
    re['ErrorCode'] = 1
    if len(user.UFollowed) != 0:
        followedList = list(map(int,user.UFollowed[1:].split(',')))
        for i in followedList:
            ut = UserTimeline.objects.get(UId = i)
            ut.UTimelineFrom += ',' +str(user.UId)
            ut.UTimelineAct += ',' + str(fo.UId)
            ut.UTimelineType += ',2'
            ut.save()
       
    return HttpResponse(json.dumps(re))

def Unfollow(request):
    re = dict()
    user = UserBase.objects.get(UId = request.POST.get('UID'))
    if user.UFollow.find(','+str(request.POST.get('UnfollowID')))!=-1: 
        user.UFollow = user.UFollow.replace(','+str(request.POST.get('UnfollowID')),'')   
        print(user.UFollow)
        user.save()
        re['ErrorCode'] = 1
    else:
        re['ErrorCode'] = 0
    uf = UserBase.objects.get(UId = request.POST.get('UnfollowID'))
    if uf.UFollowed.find(','+str(request.POST.get('UID'))) != -1:
        uf.UFollowed = uf.UFollowed.replace(','+str(request.POST.get('UID')),'')
        uf.save()
        re['ErrorCode']=1
    else:
        re['ErrorCode']=0
    return HttpResponse(json.dumps(re))

def GetTimeline(request):
    timeline = UserTimeline.objects.get(UId = request.POST.get('UID'))
    time = datetime.now()
    re = dict()
    tl = []
    if len(timeline.UTimelineFrom) != 0:
        fromList = list(map(int,timeline.UTimelineFrom[1:].split(',')))
        actList = list(map(int,timeline.UTimelineAct[1:].split(',')))
        typeList = list(map(int,timeline.UTimelineType[1:].split(',')))
        start = int(request.POST.get('Start'))
        end = int(request.POST.get('End'))
        for i in range(len(fromList)-start-1 ,len(fromList)-end-2 if (len(fromList)-end-2 > 0 )else -1,-1):
            if typeList[i] != 2:
                user = UserBase.objects.get(UId = fromList[i])
                act = Activity.objects.get(AId = actList[i])
                t = (time-act.ACreateTime)
                if t.days >1:
                    DetTime = str(t.days)+'d'
                elif t.hours >1:
                    DetTime = str(t.hours)+'h'
                else :
                    DetTime = str(t.seconds)+'s'
                tl.append({'UID':user.UId,'Avatar':user.UAvatar,'Name':user.UName,'AID':act.AId,'Type':typeList[i],'Title':act.ATitle,'Summary':act.ASummary,'Location':act.ALocation,'Time':DetTime})
            else :
                user = UserBase.objects.get(UId = fromList[i])
                act = UserBase.objects.get(UId = actList[i])
                DetTime = '100s'
                tl.append({'UID':user.UId,'Avatar':user.UAvatar,'Name':user.UName,'AID':act.UId,'Type':typeList[i],'AAvatar':user.UAvatar,'AName':act.UName,'Time':DetTime})
    re['ErrorCode']=1
    re['Timeline'] = tl
    return HttpResponse(json.dumps(re))
