import json
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader

from base import mods
from voting.models import Voting

def inicio(request):
    template = loader.get_template("inicio.html")
    return HttpResponse(template.render({}, request))

class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        return context

def funcionWinner(voting_id):
    votacion = Voting.objects.get(id=voting_id)
    procesado = votacion.postproc
    maxVote = max(procesado, key=lambda value:value['votes'])
    return maxVote

def funcionLoser(voting_id):
    votacion = Voting.objects.get(id=voting_id)
    procesado = votacion.postproc
    lessVote = min(procesado, key=lambda value:value['votes'])
    return lessVote

def calcPorc(x, lista):
    return int((x/sum(lista))*100)

def funcionPorcentaje(voting_id):
    votacion = Voting.objects.get(id=voting_id)
    procesado = votacion.postproc
    porcentages = []
    listaV = []
    for p in procesado:
        listaV.append(p['votes'])
    for v in listaV:
        porcentages.append(calcPorc(v, listaV))
    return porcentages
  
def graphics(request, voting_id):
    template = loader.get_template("graphics.html")
    votacion = Voting.objects.get(id=voting_id)
    procesado = Voting.objects.get(id=voting_id).postproc
    winner = funcionWinner(voting_id)
    loser = funcionLoser(voting_id)
    porcentages = zip(procesado, funcionPorcentaje(voting_id))
    context = {
        "votacion": votacion,
        "procesado": procesado,
        "winner": winner,
        "loser": loser,
        "porcentages": porcentages,
    }
    return HttpResponse(template.render(context, request))