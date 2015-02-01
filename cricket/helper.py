#some helper functions
from datetime import datetime
from django.template import Context, Template
import pdb
from django.db import transaction
from django.db.models import Sum, Count
from django.http import HttpResponse
from coupondunia.settings import NUMBER_OF_PLAYERS_ALLOWED_IN_TEAM, MAX_AMOUNT_ALLOTED_TO_TEAM, ALLOWED_TEAM_COMBINATION
from cricket.models import Team, Player, PlayerSelection, COUNTRY_ALLOWED_IN_IPL, TEAM_STATUS, Stats
from django.contrib.auth.models import User

PLAYERS_FIELD=['name','age','country', 'amount', 'profile', 'created_on', 'deleted_on', 'description', 'status', 'available']
STATS_FIELD=['player','matches', 'won', 'lost', 'draw', 'batting', 'bowling', 'wickets', 'six', 'four']

def getUserParamsForManage(user=None):
    if user is None:
        return None
    if user.is_superuser:
        teams = Team.objects.filter(status='PROC', deleted_on=None)
        players = Player.objects.filter(approved=False)
        users = User.objects.filter(is_active=False)
        playerselection = PlayerSelection.objects.filter(approved=False)
        params = { 'teams' : teams,
                   'users' : users,
                   'players' : players,
                   'playerselection' : playerselection,
                   'superuser' : True }
        return params
    else:
        team, players, desc = None, None, None
        try:
            t = Team.objects.get(user=user, deleted_on=None)
        except Exception, e:
            t = None
        pl=()
        if t:
            team = t
            players = Player.objects.filter(
                id__in=PlayerSelection.objects.values('player_id').filter(team_id=team.id, deleted_on=None)
            )
            for p in players:
                pl=pl+((str(p.id), str(p.profile)+"  "+str(p.name)+"  from "+str(p.country)+" for "+str(p.amount)),)
        params = {
            'team' : team if team else None,
            'players' : pl if pl else None,
            'superuser' : None
        }
        return params

def getPlayersList(team=None):

    players = Player.objects.filter(approved=True, available=True, deleted_on=None)

    if team:
        players = players | Player.objects.filter(
                            id__in=PlayerSelection.objects.values('player_id').filter(team_id=team.id, deleted_on=None)
                            )

    players = players.order_by('profile')
    pl=()
    if players:
        for p in players:
            pl=pl+((str(p.id), str(p.profile)+"  "+str(p.name)+"  from "+str(p.country)+" for "+str(p.amount)),)

    return pl

def getModelsInputForPlayer(params=None):
    if params is None:
        return None,"NO PARAMETERS RECIEVED"
    else:
        dict={}
        for k,v in params.items():
            if k in PLAYERS_FIELD:
                dict[k]=int(v) if isinstance(v,int) else float(v) if isinstance(v,float) else v
        return dict, None

def getModelsInputForStats(params=None):
    if params is None:
        return None,"NO PARAMETERS RECIEVED"
    else:
        dict={}
        for k,v in params.items():
            if k in STATS_FIELD:
                dict[k]=int(v) if isinstance(v,int) else float(v) if isinstance(v,float) else v
        return dict, None


def ValidateAndAllotPlayersAddedToTeam(params=None,user_id=None):
    errors=[]
    if params is None or user_id is None:
        return ["No Players Info recieved"]
    player_dict={}
    for i in range (1,NUMBER_OF_PLAYERS_ALLOWED_IN_TEAM+1):
        player_dict['player'+str(i)]=params.get('player'+str(i),None)
    if len(set(player_dict.values()))!=len(player_dict.values()) or None in player_dict.values():
        errors.append("All players had to be unique")
        print player_dict
        return errors


    print "player_dict = ", player_dict
    print "player_dict.values() = ", player_dict.values()
    player = Player.objects.filter(id__in=player_dict.values())
    print "player = ", player
    comb = {x:y for x,y in [t.values() for t in Player.objects.values('profile').filter(id__in=player_dict.values()).annotate(dcount=Count('profile'))]}
    print comb
    if comb not in ALLOWED_TEAM_COMBINATION:
        errors.append("Only Following Combination Are Allowed")
        for i in ALLOWED_TEAM_COMBINATION:
            errors.append(i)
        return errors
    try:
        player_alloted_within_team = PlayerSelection.objects.values('player_id').filter(
            team = Team.objects.get(user_id=user_id, deleted_on=None), deleted_on=None
        )
    except Exception, e:
        print e
        player_alloted_within_team=[]
    player_alloted_within_team = [x['player_id'] for x in player_alloted_within_team]

    for p in player:
        if p.approved==False:
            errors.append(p.profile+"  "+p.name+" from "+p.country+"   is DISQUALIFIED FROM IPL")
        if p.available==False and p.id not in player_alloted_within_team:
            errors.append(p.profile+"  "+p.name+" from "+p.country+"   is ALREADY ALLOTED")
    if errors:
        return errors

    teamname = params['teamname']
    t = Team.objects.filter(name=teamname, deleted_on=None)
    if t and t[0].user_id!=user_id:
        errors.append("teamname is already registered")
        return errors

    oldplayers=[]
    if t:
        t=t[0]
        print t
        prevsum = Player.objects.filter(id__in=PlayerSelection.objects.values('player_id').filter(team=t, deleted_on=None)).aggregate(Sum('amount'))['amount__sum']
        newsum = Player.objects.filter(id__in=player_dict.values()).aggregate(Sum('amount'))['amount__sum']
        print "prev sum",prevsum
        print "new sum",newsum
        if (t.amount + prevsum - newsum)>=0.0:
            t.amount=t.amount + prevsum - newsum
            t.description = params['description']
            t.status='PROC'
            t.save()
            oldplayers = Player.objects.values('id').filter(id__in=PlayerSelection.objects.values('player_id').filter(team=t, deleted_on=None))
            print "oldplayers = ",oldplayers
        else:
            errors.append("the player you requested costs more than your budget. try with other players")
            return errors
    else:
        t = Team()
        t.name = teamname
        t.description = params['description']
        t.amount = MAX_AMOUNT_ALLOTED_TO_TEAM
        newsum = Player.objects.filter(id__in=player_dict.values()).aggregate(Sum('amount'))['amount__sum']
        if (t.amount - newsum)>=0.0:
            t.amount=t.amount - newsum
            t.user=User.objects.get(id=user_id)
            t.save()
        else:
            errors.append("The PLayers you requested cost more than your budget")
            return errors

    newplayers = Player.objects.values('id').filter(id__in=player_dict.values())
    t = Team.objects.get(name=teamname, user_id=user_id, deleted_on=None)

    with transaction.commit_on_success():
        try:
            for id  in [x['id'] for x in oldplayers]:
                if id not in [x['id'] for x in newplayers]:
                    print "-->",id
                    PlayerSelection.objects.filter(team=t, player_id=id).update(deleted_on=datetime.now())
                    Player.objects.filter(id=id).update(available=True)

            for id  in [x['id'] for x in newplayers]:
                print "--------",id
                try:
                    PlayerSelection.objects.get(team=t, player_id=id)
                    PlayerSelection.objects.filter(team=t, player_id=id).update(deleted_on=None)
                except Exception, e:
                    PlayerSelection(team=t, player_id=id).save()
                Player.objects.filter(id=id).update(available=False)
        except Exception, e:
            print e
            errors.append("Error Occured, Please try Later")

    return errors

def deleteTeam(team=None):
    errors=[]
    if not team:
        errors.append("No team exist")
        return errors
    else:
        with transaction.commit_on_success():
            # PlayerSelection.objects.filter(team_id=team.id).delete()
            try:
                Player.objects.filter(
                    id__in=PlayerSelection.objects.values('player_id').filter(team=team, deleted_on=None)
                ).update(available=True)

                PlayerSelection.objects.filter(team_id=team.id).update(deleted_on=datetime.now())

                Team.objects.filter(id=team.id).update(deleted_on=datetime.now())

            except Exception, e:
                print e
                errors.append("Deletion Failed, Try Again")

    return errors

# def performActionForSuperuser(params=None):
#     errors, message, view = [],None, ""
#     if params:
#         print "params ",params
#         if params.get('showteam',None):
#             name = params.get('showteam',None).strip()
#             try:
#                 if name:
#                     team = Team.objects.filter(name=name, deleted_on=None)
#                 else:
#                     team = Team.objects.filter(deleted_on=None)
#
#                 for t in team:
#                     view=view+"\n\nTeam "+t.name+" belongs to "+t.user.first_name +" "+t.user.last_name+"   STATUS : "+{x:y for x,y in TEAM_STATUS}[t.status]+"   Amount Left : "+str(t.amount)
#                     view = view +"\n\nPlayers List are \n" +getPlayerOfTeam(team=t)
#             except Exception, e:
#                 print e
#                 view = "no team exist with name "+name
#             return errors, message, view.replace('\n','<br>')
#         if params.get('team',None) and params.get('action',None):
#             name = params.get('team', None)
#             action = params.get('action',None)
#
#             try:
#                 team = Team.objects.get(name=name, deleted_on=None)
#                 if action=='appr':
#                     if team.status=='PROC':
#                         team.status='APPR'
#                         team.save()
#                         message=team.name+"  successfully approved "
#                         return errors, message, view
#                     if team.status=='REJC':
#                         message="you have rejected  "+team.name+"\n user had to resubmit for approval"
#                         return errors, message, view
#                     if team.status=='APPR':
#                         message=team.name+"  is already approved"
#                         return errors, message, view
#                 elif action=='dec':
#                     if team.status=='PROC':
#                         team.status='REJC'
#                         team.save()
#                         message=team.name+"  successfully Rejected "
#                         return errors, message, view
#                     if team.status=='APPR':
#                         team.status='REJC'
#                         team.save()
#                         message="you have already Approved  "+team.name+"\n it is Rejected now"
#                         return errors, message, view
#                     if team.status=='REJC':
#                         message=team.name+"  is already Rejected"
#                         return errors, message, view
#                 else:
#                     view="Invalid parameters recieved"
#                     return errors, message, view
#             except Exception, e:
#                 print e
#                 view = "no team exist with name "+name
#                 return errors, message, view.replace('\n','<br>')
#         if params.get('showuser',None):
#             username = params.get('showuser',None)
#             try:
#                 print username
#                 if username and username.strip()!='':
#                     user = User.objects.filter(username=username)
#                 else:
#                     user = User.objects.all()
#
#                 for u in user:
#                     view = view +"\n\n"+u.first_name+" "+u.last_name+"  email:"+u.email+"  username:"+u.username+"  status:"+ "ACTIVE" if u.is_active else 'BLOCKED'
#             except Exception,e:
#                 print e
#                 view = "No User exist with such username"
#             return errors, message, view.replace('\n','<br>')
#
#
#     else:
#         print "params not recieved"

def getPlayerOfTeam(team=None):
    try:
        player = Player.objects.filter(
            id__in=PlayerSelection.objects.values('player_id').filter(team=team, deleted_on=None)
        )
        playerlist=""
        for p in player:
            playerlist= playerlist+"\n"+p.profile+" "+p.name+" from "+p.country+" in "+str(p.amount)

        return playerlist
    except Exception, e:
        return ""

def performAction(model=None, action=None, id=None, superuser=False):
    ACTIONS = {
        'player':['stats','disapprove','approve'],
        'user':['approve', 'disapprove', 'stats'],
        'team':['approve', 'disapprove','stats' ]
    }

    messages,errors=[], []

    if model in ACTIONS.keys() and action not in ACTIONS[model]:
        errors.append("action is not defined")
        return errors, messages

    if model=='player':
        p = Player.objects.get(id=id)
        print p
        if action=='stats':
            try:
                s = Stats.objects.filter(player_id=id)
                messages = ["STATISTIC"]+[x+" : "+str(y) for x,y in s.values()[0].items()]
            except Exception, e:
                messages.append("STATS are not defined for this player")
            return errors, messages
            print action
        elif action=='approve' and superuser:
            if p.approved==False:
                p.approved=True
                p.save()
                messages.append("Successfully Approved")
                return errors, messages
            else:
                messages.append("Already Approved")
                return errors, messages
        elif action=='disapprove' and superuser:
            if p.approved==True:
                if not PlayerSelection.objects.filter(player_id=p.id, deleted_on=None, approved=True):
                    p.approved=False
                    p.save()
                    messages.append("Successfully Blacklisted")
                else:
                    messages.append("Player is part of approved team , Reject team first to blacklist plyer")
                return errors, messages
            else:
                messages.append("Already Blacklisted")
                return errors, messages
        else:
            errors.append("You dont have access to perform this action")
            return errors, messages


    if model=='user':
        u = User.objects.get(id=id)
        if action=='stats':
            try:
                t = Team.objects.filter(user_id=id)
                messages = ["TEAM"]+[x+" : "+str(y) for x,y in t.values()[0].items()]
            except Exception, e:
                messages.append("This Uers dont own a team till Now")
            return errors, messages

        elif action=='approve' and superuser:
            if u.is_active==False:
                u.is_active=True
                u.save()
                messages.append("Successfully Approved")
                return errors, messages
            else:
                messages.append("Already Approved")
                return errors, messages
        elif action=='disapprove' and superuser:
            if u.is_active==True:
                if u.is_superuser==False:
                    u.is_active=False
                    u.save()
                    messages.append("Successfully Blacklisted")
                else:
                    messages.append("Cannot Blacklist a super user , Visit /admin for more action")
                return errors, messages
            else:
                messages.append("Already Blacklisted")
                return errors, messages
        else:
            errors.append("You dont have access to perform this action")
            return errors, messages

    if model=='team':
        t = Team.objects.get(id=id)
        if action=='stats':
            try:
                players = Player.objects.filter(
                    id__in=PlayerSelection.objects.values('player_id').filter(team=t, deleted_on=None)
                )
                tmp="""
                    {% for p in players %}
                        <a href="/player/{{ p.id }}"> {{ p.profile }} {{ p.name }} </a>  from {{ p.country }} solded for {{ p.amount }} <br>
                    {% endfor %}
                """
                template = Template(tmp)
                context = Context({'players':players})
                html = template.render(context)
                messages.append(html)
            except Exception, e:
                print e
                messages.append("Players are not yet Alloted")
            return errors, messages

        elif action=='approve' and superuser:
            if t.status in ['PROC','REJC']:
                t.status='APPR'
                PlayerSelection.objects.filter(team=t, deleted_on=None).update(approved=True)
                t.save()
                messages.append("Successfully Approved")
                return errors, messages
            else:
                messages.append("Already Approved")
                return errors, messages
        elif action=='disapprove' and superuser:
            if t.status in ['APPR','PROC']:
                t.status='REJC'
                PlayerSelection.objects.filter(team=t, deleted_on=None).update(approved=False)
                t.save()
                messages.append("Successfully Blacklisted")
                return errors, messages
            else:
                messages.append("Already Blacklisted")
                return errors, messages
        else:
            errors.append("You dont have access to perform this action")
            return errors, messages
