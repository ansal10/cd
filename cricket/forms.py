from django import forms
from cricket.helper import getPlayersList
from cricket.models import COUNTRY_ALLOWED_IN_IPL, PLAYERS_PROFILE, Team
from django.utils.translation import gettext as _

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True,  widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder':'Password'}),required=True, label='Password',)

class AddPlayerForm(forms.Form):
    name=forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder':'Name of player'}))
    age=forms.IntegerField(min_value=18, max_value=36,required=True, widget=forms.TextInput(attrs={'placeholder':'Age'}))
    country=forms.ChoiceField(choices=[(x,y) for x,y in COUNTRY_ALLOWED_IN_IPL], required=True)
    amount=forms.FloatField(min_value=1.0,max_value=20.0, widget=forms.TextInput(attrs={'placeholder':'Amount to be in range 1.0 to 20.0'}))
    profile=forms.ChoiceField(choices=[(x,y) for x,y in PLAYERS_PROFILE], required=True)
    matches=forms.IntegerField(min_value=0,required=True, widget=forms.TextInput(attrs={'placeholder':'Matches'}))
    won=forms.IntegerField(min_value=0,required=True, widget=forms.TextInput(attrs={'placeholder':'Won'}))
    lost=forms.IntegerField(min_value=0,required=True, widget=forms.TextInput(attrs={'placeholder':'Lost'}))
    draw=forms.IntegerField(min_value=0,required=True, widget=forms.TextInput(attrs={'placeholder':'Draw'}))
    batting=forms.FloatField(min_value=0.0, max_value=10.0,required=True, widget=forms.TextInput(attrs={'placeholder':'Batting Rating in 10'}))
    bowling=forms.FloatField(min_value=0.0, max_value=10.0,required=True, widget=forms.TextInput(attrs={'placeholder':'Bowling Rating in 10'}))
    wickets=forms.IntegerField(min_value=0,required=True, widget=forms.TextInput(attrs={'placeholder':'Wickets taken'}))
    six=forms.IntegerField(min_value=0,required=True, widget=forms.TextInput(attrs={'placeholder':'Total six'}))
    fours=forms.IntegerField(min_value=0,required=True, widget=forms.TextInput(attrs={'placeholder':'Total fours'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'enter description about player'}))


class RegisterForm(forms.Form):
    fname = forms.CharField(max_length=255, required=True, label='First Name', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'First Name'}))
    lname = forms.CharField(max_length=255, required=True, label='Last Name', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Last Name'}))
    email = forms.EmailField(required=True, label='email address', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Email address'}))
    confirmemail = forms.EmailField(required=True, label='Confirm email address', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Confirm email address'}))
    username = forms.CharField(max_length=255, required=True, label='Username', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Password'}),required=True, label='Password')
    confirmpassword = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Confirm Password'}),required=True, label='Confirm Password')

    def clean_email(self):
        if self.data['email'] != self.data['confirmemail']:
            raise forms.ValidationError('Emails are not the same')
        return self.data['email']

    def clean_password(self):
        if self.data['password'] != self.data['confirmpassword']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

    def clean(self,*args, **kwargs):
        self.clean_email()
        self.clean_password()
        return super(RegisterForm, self).clean(*args, **kwargs)


def getRegisterTeamForm(team=None, initial=None, data=None):

    class RegisterTeamForm(forms.Form):
        teamname=forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder':'Name of the team'}))
        description = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'enter description about player'}))
        player1 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)
        player2 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)
        player3 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)
        player4 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)
        player5 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)
        player6 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)
        player7 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)
        player8 = forms.ChoiceField(choices=[(x, y) for x, y in getPlayersList(team=team)+(('', 'Select Player'),)], required=True)

        def clean_players(self):
            p=[]
            for i in range(1,9):
                p.append(self.data['player'+str(i)])
            if len(set(p))!=len(p):
                raise forms.ValidationError("All Players had to be Unique")

        def clean(self, *args, **kwargs):
            self.clean_players()
            return super(RegisterTeamForm, self).clean(*args, **kwargs)


    if initial:
        return RegisterTeamForm(initial=initial)

    elif data:
        return RegisterTeamForm(data=data)
    else:
        return RegisterTeamForm()
