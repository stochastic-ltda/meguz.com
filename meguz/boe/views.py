from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.template.defaultfilters import slugify

from main.models import Company
from django.contrib import auth

from boe.forms import OfferNewForm


def Login(request):	
	if request.method == 'POST': 
		# user authentication
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username=username, password=password)

		# user logged in
		if user is not None:
			auth.login(request, user)
			return HttpResponseRedirect("/boe/ofertas/lista")
		# authentication fail
		else:
			return HttpResponseRedirect("/boe")

	else :	
		if request.user.is_authenticated():
			return HttpResponseRedirect("/boe/ofertas/lista")
		else:
			return render_to_response('boe/login.html', {}, context_instance=RequestContext(request))

def Logout(request):	
	auth.logout(request)
	return HttpResponseRedirect("/boe")

def OfferList(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/boe")
	else: 
		return render_to_response('boe/offer/list.html', {}, context_instance=RequestContext(request))

def OfferNew(request):
	form = OfferNewForm()
	context = {'form':form}
	return render_to_response('boe/offer/new.html', context, context_instance=RequestContext(request))
