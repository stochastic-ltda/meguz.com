from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.template.defaultfilters import slugify

from main.models import Company, Offer
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
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/boe")
	else: 
		if request.method == 'POST': 
			form = OfferNewForm(request.POST)
			if(form.is_valid()):
				offer = Offer(**form.cleaned_data)

				# set slug
				slug = slugify(request.POST['title'])						
				offer.slug = slug

				# set company_id
				user_email = request.user.email
				company = Company.objects.get(contact_email=user_email)
				offer.company_id = company.id

				offer.save()

				# redirect to media page
				return HttpResponseRedirect("/boe/ofertas/multimedia/%d" % offer.id)
		else: 
			form = OfferNewForm()

		context = {'form':form}
		return render_to_response('boe/offer/new.html', context, context_instance=RequestContext(request))


def OfferMultimedia(request, offer_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/boe")
	else: 
		context = {'id':offer_id}
		return render_to_response('boe/offer/multimedia.html', context, context_instance=RequestContext(request))
