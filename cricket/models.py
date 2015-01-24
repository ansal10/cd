from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
# Create your models here.

# Associate all the Country Players
COUNTRY_ALLOWED_IN_IPL = (
    ('NZ', _('New Zealand')),
    ('IN', _('India')),
    ('AU', _('Australia')),
    ('UK', _('England')),
    ('SA', _('South Africa')),
)

PLAYERS_PROFILE = (
    ('BATSMEN', _('Batsmen')),
    ('BOWLER', _('Bowler')),
    ('WKEEPER', _('Wicket Keeper')),
    ('ALLROUND', _('All Rounder')),
)

class Team(models.Model):
    name=models.CharField(max_length=255, null=False)
    created_on = models.DateTimeField(auto_now_add=True, null=False)
    deleted_on = models.DateTimeField(blank=True, null=True, default=None)
    amount = models.FloatField(null=False, default=100.0)
    models.TextField()



class Profile(models.Model):
    user=models.OneToOneField(User, null=False, unique=True)
    team = models.ForeignKey(Team, null=False)


class Player(models.Model):
    name = models.CharField(max_length=255, null=False)
    age = models.IntegerField(null=False, default=25)
    country = models.CharField(max_length=255, null=False, choices=COUNTRY_ALLOWED_IN_IPL)
    team=models.ForeignKey(Team)
    amount = models.FloatField(null=False, default=10.0)
    profile=models.CharField(max_length=255, null=False, choices=PLAYERS_PROFILE)
    created_on=models.DateTimeField(auto_now_add=True, null=False)
    deleted_on=models.DateTimeField(blank=True, null=True, default=None)
    description = models.TextField()


class PlayerSelection(models.Model):
    team=models.ForeignKey(Team, null=False)
    player=models.ForeignKey(Player, null=False)
    deleted_on=models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        unique_together = (('team','player'))


class Stats(models.Model):
    matches=models.IntegerField(max_length=255)
    won=models.IntegerField(max_length=255)
    lost=models.IntegerField(max_length=255)
    draw=models.IntegerField(max_length=255)
    batting=models.FloatField(default=0.0)
    bowling=models.FloatField(default=0.0)
    wickets=models.IntegerField(default=0)
    s6 = models.IntegerField(default=0)
    s4 = models.IntegerField(default=0)


