from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from voting.models import Voting
from django.contrib.auth.models import User
from django.contrib import messages

from base.perms import UserIsStaff
from .models import Census


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')



def census_add(request):
    if request.user.is_staff:
        template = loader.get_template("census_add.html")
        votings = Voting.objects.all()
        users = User.objects.all()
        context = {
            'votings': votings,
            'users': users
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("result_page.html")
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({}, request), status=ST_401)


def add_to_census(request):
    template = loader.get_template("result_page.html")
    if request.user.is_staff:
        voting_id = request.POST['voting-select']
        user_id = request.POST['user-select']
        try:
            census_by_voting = Census.objects.get(voting_id=voting_id,voter_id=user_id)
        except Census.DoesNotExist:
            census_by_voting = None

        status_code=404
        if census_by_voting == None:
            census = Census(voting_id=voting_id, voter_id=user_id)
            census.save()
            messages.success(request, "User added to the voting correctly")
            status_code=ST_201

        else:
            messages.info(request, "The user was already assigned to the voting")
            status_code = 200
        
        
        return HttpResponse(template.render({}, request), status=status_code)

    else:
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({}, request), status=ST_401)


def census_remove(request):
    if request.user.is_staff:
        template = loader.get_template("census_remove.html")
        votings = Voting.objects.all()
        users = User.objects.all()
        context = {
            'votings': votings,
            'users': users
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("result_page.html")
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({'remove': True}, request), status=ST_401)

def remove_from_census(request):
    template = loader.get_template("result_page.html") 
    if request.user.is_staff:   
        voting_id = request.POST['voting-select']
        user_id = request.POST['user-select']
        try:
            census_by_voting = Census.objects.get(voting_id=voting_id,voter_id=user_id)
        except Census.DoesNotExist:
            census_by_voting = None

        status_code=404
        if census_by_voting != None:
            census_by_voting.delete()
            messages.success(request, "User removed from the voting correctly")
            status_code = 200

        else:
            messages.info(request, "The user was not part of this voting")
            status_code = 200
        
        return HttpResponse(template.render({'remove': True}, request), status=status_code)

    else:
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({'remove': True}, request), status=ST_401)

def census_gender(request):
    if request.user.is_staff:
        template = loader.get_template("census_gender.html")
        votings = Voting.objects.all()
        try:
            genders = set(u.gender for u in User.objects.all())
        except BaseException:
            genders = set()
        context = {
            'votings': votings,
            'genders': genders,
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("result_page.html")
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({}, request), status=ST_401)

def add_by_gender_to_census(request):
    template = loader.get_template("result_page.html")
    if request.user.is_staff:
        voting_id = request.POST['voting-select']
        genders = request.POST['gender-select']
        users = User.objects.filter(gender in genders)
        for user in users:
            try:
                census_by_voting = Census.objects.get(voting_id=voting_id,voter_id=user.id)
            except Census.DoesNotExist:
                census_by_voting = None
            status_code=404
            if census_by_voting == None:
                census = Census(voting_id=voting_id, voter_id=user.id)
                census.save()
                messages.success(request, "User added to the voting correctly")
                status_code=ST_201

            else:
                messages.info(request, "The user was already assigned to the voting")
                status_code = 200

            return HttpResponse(template.render({}, request), status=status_code)

    else:
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({}, request), status=ST_401)

def census_age(request):
    if request.user.is_staff:
        template = loader.get_template("census_age.html")
        votings = Voting.objects.all()
        context = {
            'votings': votings,
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("result_page.html")
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({}, request), status=ST_401)


def add_by_age_to_census(request):
    template = loader.get_template("result_page.html")
    if request.user.is_staff:
        voting_id = request.POST['voting-select']
        minAge = request.POST['minimum-age']
        maxAge = request.POST['maximum-age']
        users = User.objects.filter(age >= minAge and age<=maxAge)
        for user in users:
            try:
                census_by_voting = Census.objects.get(voting_id=voting_id,voter_id=user.id)
            except Census.DoesNotExist:
                census_by_voting = None
            status_code=404
            if census_by_voting == None:
                census = Census(voting_id=voting_id, voter_id=user.id)
                census.save()
                messages.success(request, "User added to the voting correctly")
                status_code=ST_201

            else:
                messages.info(request, "The user was already assigned to the voting")
                status_code = 200
        
        
            return HttpResponse(template.render({}, request), status=status_code)

    else:
        messages.error(request, "You must be a staff member to access this page")
        return HttpResponse(template.render({}, request), status=ST_401)