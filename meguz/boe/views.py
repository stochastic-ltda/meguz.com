#--------------------------------------------------------------------------------
# BOE
#--------------------------------------------------------------------------------

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.template.defaultfilters import slugify

from main.models import Company, Offer
from django.contrib import auth
from django.contrib.auth import authenticate

from boe.forms import OfferNewForm, OfferMultimediaForm, CompanyEditForm

from pyes import *


def Login(request):	
	if request.method == 'POST': 
		# user authentication
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username=username, password=password)

		# user logged in
		if user is not None:
			auth.login(request, user)
			return HttpResponseRedirect("/epanel/premios/lista")
		# authentication fail
		else:
			return HttpResponseRedirect("/epanel/?fail")

	else :	
		if request.user.is_authenticated():
			return HttpResponseRedirect("/epanel/premios/lista") 
		else:
			return render_to_response('epanel/login.html', {}, context_instance=RequestContext(request))

def Logout(request):	
	auth.logout(request)
	return HttpResponseRedirect("/epanel")

def PrizeList(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/epanel")
	else: 
		try:
			company = Company.objects.get(contact_email=request.user.email)
			offers = Offer.objects.filter(company=company)
		except Company.DoesNotExist:
			offers = {}

		return render_to_response('epanel/offer/list.html', {'offers':offers}, context_instance=RequestContext(request))

def PrizeActivate(request, offer_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/epanel")
	else:
		offer = Offer.objects.get(pk=offer_id)
		if offer is None: 
			return HttpResponseRedirect("/epanel")
		else: 
			# TODO: Validate user (use request.user)
			if(offer.status == 'A'):
				offer.status = 'C'
				offer.save()

				es = ES("localhost:9200")
				prizeES = es.get("prize","prize",offer.id)
				prizeES.status = 'C'
				prizeES.save()

	return HttpResponseRedirect("/epanel/premios/lista")

def PrizeDeactivate(request, offer_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/epanel")
	else:
		offer = Offer.objects.get(pk=offer_id)
		if offer is None: 
			return HttpResponseRedirect("/epanel")
		else: 
			# TODO: Validate user (use request.user)
			if(offer.status == 'C'):
				offer.status = 'A'
				offer.save()

				es = ES("localhost:9200")
				prizeES = es.get("prize","prize",offer.id)
				prizeES.status = 'A'
				prizeES.save()

	return HttpResponseRedirect("/epanel/premios/lista")


def PrizeEdit(request, offer_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/epanel")
	else: 
		offer = Offer.objects.get(pk=offer_id)
		if offer is None: 
			return HttpResponseRedirect("/epanel")
		else: 
			if request.method == 'POST': 
				form = OfferNewForm(request.POST)
				if(form.is_valid()):

					new_offer = Offer(**form.cleaned_data)
					new_offer.id = offer.id
					new_offer.slug = offer.slug
					new_offer.company = offer.company	
					new_offer.media_type = offer.media_type
					new_offer.media_url = offer.media_url
					new_offer.media_image = offer.media_image
					new_offer.media_thumb = offer.media_thumb	
					new_offer.status = offer.status			
					new_offer.save()

					# update elasticsearch
					prize = Offer.objects.get(pk=offer.id)
					if(prize.status == 'C'):
						es = ES("localhost:9200")
						prizeES = es.get("prize","prize",prize.id)
						prizeES.title = prize.title
						prizeES.description = prize.description
						prizeES.vote_limit = prize.vote_limit
						prizeES.vote_source = prize.vote_source
						prizeES.category = prize.category.name
						prizeES.save()						

					# redirect to edit page
					return HttpResponseRedirect("/epanel/premios/editar/%d" % offer.id)
			else: 
				form = OfferNewForm(initial={
						'title': offer.title,
						'prize_name': offer.prize_name,
						'stock': offer.stock,
						'category': offer.category,
						'vote_limit': offer.vote_limit,
						'vote_source': offer.vote_source,
						'description': offer.description,
						'conditions': offer.conditions,
					}, auto_id=False)

		context = {'form':form, 'title': 'editar', 'submit': 'Editar premio'}
		return render_to_response('epanel/offer/new.html', context, context_instance=RequestContext(request))

def PrizeNew(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/epanel")
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
				offer.status = "B"

				offer.save()

				# redirect to media page
				return HttpResponseRedirect("/epanel/premios/multimedia/%d" % offer.id)
		else: 
			form = OfferNewForm()

		context = {'form':form, 'title': 'nuevo', 'submit': 'Guardar premio'}
		return render_to_response('epanel/offer/new.html', context, context_instance=RequestContext(request))


def PrizeMultimedia(request, offer_id):		

	if not request.user.is_authenticated():
		return HttpResponseRedirect("/epanel")
	else: 		

		from django.core.urlresolvers import reverse
		from django.contrib import messages
		from django_youtube.api import Api, AccessControl, ApiError

		offer = Offer.objects.get(id=offer_id)
		show_media = False 

		# Offer doesnt exists
		if offer is None:
			return HttpResponseRedirect("/epanel")

		# Offer exists		
		else:

			# If request.POST isset then an Image its been uploaded
			if request.method == 'POST':
				#form = OfferMultimediaForm(request.POST, request.FILES)
				offer.media_type = request.POST['media_type']
				offer.media_image = request.FILES['media_image']				
				offer.save()

				offer.media_thumb = offer.media_image.url
				offer.save()

				# update elasticsearch
				if(offer.status == 'C'):
					es = ES("localhost:9200")
					prizeES = es.get("prize","prize",offer.id)
					prizeES.thumbnail = offer.media_thumb
					prizeES.save()	

			# If request.GET isset from Youtube, update media_url with video ID
			if request.method == 'GET':
				if 'status' in request.GET:
					if request.GET['status'] == "200":
						if 'id' in request.GET:
							offer.media_url = request.GET['id']
							offer.media_thumb = "http://img.youtube.com/vi/%s/mqdefault.jpg" % request.GET['id']
							offer.media_type = 'Y'
							offer.save()

							# update elasticsearch
							if(offer.status == 'C'):
								es = ES("localhost:9200")
								prizeES = es.get("prize","prize",offer.id)
								prizeES.thumbnail = offer.media_thumb
								prizeES.save()
							return HttpResponseRedirect("/epanel/premios/multimedia/%s" % offer_id)

			# video metadata
			title = offer.title + " | Meguz.com"
			keywords = offer.category.name + "," + offer.prize_name + "," + offer.company.name
			description = offer.description + "... Visita www.meguz.com para mas informacion"

			# Try to create post_url and token
			try:
				api = Api()
				api.authenticate()

				data = api.upload(title, description=description, keywords=keywords, access_control=AccessControl.Unlisted)

			# Api error happend
			except ApiError as e:
				messages.add_message(request, messages.ERROR, e.message)
				return HttpResponseRedirect("/epanel")

			# Other error
			except:
				messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
				return HttpResponseRedirect("/epanel")

			form = OfferMultimediaForm(initial={'media_type':offer.media_type,"token": data["youtube_token"]})
						
			import os
			from django.contrib.sites.models import Site
			current_site = Site.objects.get_current()
			domain = current_site.domain

			protocol = 'https' if request.is_secure() else 'http'
			next_url = "".join([protocol, ":", os.sep, os.sep, domain, "/epanel/premios/multimedia/%d" % offer.id, os.sep])

			if offer.media_url != '' or offer.media_image != '':
				show_media = True

			context = {'form':form, 'offer':offer, 'show_media':show_media, 'post_url': data['post_url'], 'next_url': next_url}
			return render_to_response('epanel/offer/multimedia.html', context, context_instance=RequestContext(request))


def Profile(request):

	user_email = request.user.email
	company = Company.objects.get(contact_email=user_email)

	if company is None:
		HttpResponseRedirect("/epanel")
	else:
		if request.method == 'POST':
			# Proceso form
			form = CompanyEditForm(request.POST, request.FILES)
			if(form.is_valid()):
				edit_company = Company(**form.cleaned_data)
				edit_company.id = company.id
				edit_company.slug = company.slug
				edit_company.contact_email = company.contact_email

				if 'logo' not in request.FILES:
					edit_company.logo = company.logo
					
				edit_company.save()

				# TODO: Check contact_email change and update userinfo
				return HttpResponseRedirect("/epanel/perfil")
		else:
			form = CompanyEditForm(initial={
					'name': company.name,
					'slogan': company.slogan,
					'logo': company.logo,
					'rut': company.rut,
					'address': company.address,
					'phone': company.phone,
					'email': company.email,
					'website': company.website,
					'contact_name': company.contact_name,
					'contact_email': company.contact_email,
					'contact_phone': company.contact_phone,
				})

	context = {'form':form}
	return render_to_response('epanel/profile.html', context, context_instance=RequestContext(request))
