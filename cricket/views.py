from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout, login as django_login, authenticate
from coupondunia.settings import NUMBER_OF_PLAYERS_ALLOWED_IN_TEAM
# Create your views here.
from cricket.forms import LoginForm, RegisterForm, AddPlayerForm, getRegisterTeamForm
from cricket.helper import getUserParamsForManage, getModelsInputForPlayer, getModelsInputForStats, \
    ValidateAndAllotPlayersAddedToTeam, deleteTeam, performAction
from cricket.models import  Player, Stats, Team, COUNTRY_ALLOWED_IN_IPL, PlayerSelection

STATUS_DESCRIPTION={
    'PROC':'your approval had been sended to Admin, meanwhile you can edit your team',
    'APPR':'Your Team had been approved, if you do any modification , it will again need admin approval',
    'REJC':'Your team had been rejected, try editing your description or modify players'
}






def index(request):
    user = None
    if request.session.get('user_id',None):
        try:
            user = User.objects.get(id=request.session['user_id'])
        except Exception,e:
            user=None
    if user is not None:
        loggedin=True
    else:
        loggedin=None

    return render(request, 'index.html',{'loggedin':loggedin,
                                         'user':user
                                })

def logout(request):
    django_logout(request)
    return HttpResponseRedirect("/")

def login(request):
    if request.method=='GET':
        loginform = LoginForm()
        next = request.REQUEST.get('next',"")
        return render(request, 'login.html' , {'loginform':loginform,'next':next})
    elif request.method=='POST':
        loginform = LoginForm(data=request.POST)
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        next = request.POST.get('next',"")
        errors , loggedin = [], False
        user = authenticate(username=username, password=password)
        if user:
            if  user.is_active:
                django_login(request, user)
                request.session['user_id'] = user.id
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect("/dashboard")
            else:
                errors.append("Your account is not yet approved")

        else:
            errors.append("Authentication error , Username and password not matched")

        return render(request,'login.html', {'loginform':loginform,
                                             'errors':errors,
                                             'next':next
                                             })
    else:
        return HttpResponseBadRequest()

def register(request):
    if request.method=='GET':
        registerform = RegisterForm()
        return render(request, 'register.html' , {'registerform':registerform})
    elif request.method=='POST':
        errors, registered = [],False
        registerform = RegisterForm(data=request.POST)
        if registerform.is_valid():
            #check for unique mail
            if User.objects.filter(email=request.POST.get('email')).__len__()!=0:
                errors.append("Email is already registered")

            #check for unique username
            if User.objects.filter(username=request.POST.get('username')).__len__()!=0:
                errors.append("Username is already registered")

            if errors.__len__()==0:
                try:
                    with transaction.commit_on_success():
                        user = User()
                        user.first_name = request.POST.get('fname')
                        user.last_name = request.POST.get('lname')
                        user.email = request.POST.get('email')
                        user.username = request.POST.get('username')
                        user.set_password(request.POST.get('password'))
                        user.is_superuser=False
                        user.is_active=False
                        user.save()
                        registered=True
                except Exception, e:
                    print e
                    errors.append("Registration Failed , Please try again later")
        return render(request, 'register.html', {'registerform':registerform,
                                                 'registered':registered,
                                                 'errors':errors})

@login_required
def dashboard(request):
    user = User.objects.get(id=request.session['user_id'])
    params=getUserParamsForManage(user=user)
    print params
    errors=[]
    if request.method=='GET':
        if params is None:
            return HttpResponseBadRequest()
        if params['superuser']:
            return render(request, 'dashboard.html', params)
        else:
            p={}
            try:
                t = Team.objects.get(user=user, deleted_on=None)
                for i in range(1,NUMBER_OF_PLAYERS_ALLOWED_IN_TEAM+1):
                    p['player'+str(i)]=params['players'][i-1][0]
                p['teamname']=params['team'].name
                p['description'] = params['team'].description
                params['status']=STATUS_DESCRIPTION.get(t.status)

            except Exception, e:
                print e
                t=None

            form=getRegisterTeamForm(initial=p, team=t)
            params['form']=form
            return render(request, 'dashboard.html', params)

    elif request.method=='POST':
        try:
            t = Team.objects.get(user=user, deleted_on=None)
        except Exception, e:
            t=None

        form = getRegisterTeamForm(data=request.POST, team=t)

        e=ValidateAndAllotPlayersAddedToTeam(params=request.POST, user_id=request.session['user_id'])
        print e

        if form.is_valid() and not e  :
            return HttpResponse("Weldone ! your request had been qued for approval")
        else:
            params['errors'] = errors+e
            params['form']=form

            return render(request, 'dashboard.html', params)
    else:
        return HttpResponseBadRequest()

@login_required
def addplayer(request):
    user = User.objects.get(id=request.session['user_id'])
    message=None
    if user and user.is_superuser:
        if request.method=='GET':
            addplayerform = AddPlayerForm()
            return render(request, 'addnewplayer.html', {'forms':addplayerform,
                                                         'message':message
            })
        elif request.method=='POST':
            addplayerform = AddPlayerForm(data=request.POST)
            errors=[]
            if addplayerform.is_valid():
                try:
                    with transaction.commit_on_success():
                        dict,error = getModelsInputForPlayer(request.POST)
                        print dict
                        print error
                        if error:
                            errors.append(error)
                        print dict
                        if Player.objects.filter(**dict):
                            errors.append("A player already exist with matching params")
                            raise Exception("player already exist")
                        player = Player(**dict)
                        player.save()
                        dict,error = getModelsInputForStats(request.POST)
                        if error:
                            errors.append(error)
                        dict.update({'player':player})
                        stats = Stats(**dict)
                        stats.save()
                        message="New Player had been added successfully"
                except Exception, e:
                    print e
                    errors.append("Exception  adding player")
            else:
                errors.append("Sorry ! Player Cannot be added")
            return render(request, 'addnewplayer.html', {'forms':addplayerform,
                                                         'message':message,
                                                         'errors':errors
            })
    else:
        return HttpResponseBadRequest("you are not allowed to view this page")


@login_required
def delete(request):
    user = User.objects.get(id=request.session['user_id'])

    if user.is_superuser==False:
        team = Team.objects.get(user_id=user.id, deleted_on=None)
        errors = deleteTeam(team)
        message=None
        if not errors:
            message = "Your team had been successfully deleted"

        return render(request, 'delete.html', { 'message' : message,
                                                'errors' : errors})
    else:
        return Http404("You are not allowed to perform this action")

@login_required
def player(request, id=None):
    message,errors=[], []
    if id:
        try:
            p = Player.objects.filter(id=id)
            action = request.GET.get("action",None)
            if action:
                superuser=User.objects.get(id=request.session['user_id']).is_superuser
                print superuser
                errors, message = performAction(model='player', action=action, id=id, superuser=superuser)
        except Exception, e:
            print e
            errors.append("INVALID ID Or the player STATS had been deleted")
    else:
        p = Player.objects.all()

    return render(request, 'player.html', {'errors':errors,
                                           'players':p,
                                           'dict':{x:y for x,y in COUNTRY_ALLOWED_IN_IPL},
                                           'superuser':User.objects.get(id=request.session['user_id']).is_superuser,
                                           'messages':message
                                        })


@login_required
def user(request, id=None):
    message,errors=[], []
    if id:
        try:
            u = User.objects.filter(id=id)
            action = request.GET.get("action",None)
            if action:
                superuser=User.objects.get(id=request.session['user_id']).is_superuser
                print superuser
                errors, message = performAction(model='user', action=action, id=id, superuser=superuser)
        except Exception, e:
            print e
            errors.append("INVALID ID Or the User does not EXIST")
    else:
        u = User.objects.all()

    return render(request, 'user.html', {'errors':errors,
                                           'users':u,
                                           'superuser':User.objects.get(id=request.session['user_id']).is_superuser,
                                           'messages':message
                                        })

@login_required
def team(request, id=None):
    message,errors=[], []
    if id:
        try:
            team = Team.objects.filter(id=id, deleted_on=None)

            action = request.GET.get("action",None)
            if action:
                superuser=User.objects.get(id=request.session['user_id']).is_superuser
                print superuser
                errors, message = performAction(model='team', action=action, id=id, superuser=superuser)
        except Exception, e:
            print e
            errors.append("INVALID ID Or the User does not EXIST")
    else:
        team = Team.objects.filter(deleted_on=None)


    return render(request, 'team.html', {'errors':errors,
                                           'teams':team,
                                           'superuser':User.objects.get(id=request.session['user_id']).is_superuser,
                                           'messages':message
                                        })

