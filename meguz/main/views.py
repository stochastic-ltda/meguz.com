#--------------------------------------------------------------------------------
# MAIN
#--------------------------------------------------------------------------------

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from main.models import Company, Offer, Meguz, Category
from main.forms import CompanyContactForm, MeguzForm, MeguzMultimediaForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from pyes import *

import Image

# ------------------------------------------------------------------------------------------------
# General views
# ------------------------------------------------------------------------------------------------
def Home(request):
	from pyes.queryset import generate_model
	prize_model = generate_model("prize","prize")
	prizes = prize_model.objects.exclude(status='a').exclude(status='b').exclude(status='d').exclude(status='e').order_by('publish_date')

	facets = prize_model.objects.facet("category").size(0).facets

	meguz_model = generate_model("meguz","meguz")
	meguzs = meguz_model.objects.exclude(status='a').exclude(status='b').exclude(status='d').exclude(status='e').order_by('-publish_date')

	context = {'prizes':prizes, 'facets':facets, 'meguzs':meguzs}
	return render_to_response('home.html', context, context_instance=RequestContext(request))

def SearchCategory(request, category_slug):
	category = Category.objects.get(slug=category_slug);
	if category is None:
		HttpResponseRedirect("/")
	else:
		from pyes.queryset import generate_model
		prize_model = generate_model("prize","prize")
		prizes = prize_model.objects.filter(category=category.name).order_by('-publish_date')

		facets = prize_model.objects.facet("category").size(0).facets

		context = {'prizes':prizes, 'facets':facets}
		return render_to_response('home.html', context, context_instance=RequestContext(request))


# ------------------------------------------------------------------------------------------------
# Company views
# ------------------------------------------------------------------------------------------------
def CompanyList(request):
	companies = Company.objects.all()
	context = {'companies':companies}
	return render_to_response('company/list.html', context, context_instance=RequestContext(request))

def CompanyContact(request):	
	import string, random

	if request.method == 'POST': 
		form = CompanyContactForm(request.POST, request.FILES)

		if(form.is_valid()):						
			company = Company(**form.cleaned_data)
			
			# set slug
			slug = slugify(request.POST['name'])						
			company.slug = slug
			
			# set randomin password
			chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
			company.password = ''.join(random.choice(chars) for x in range(15))
			company.save()

			# create user
			from django.contrib.auth.models import User
			user = User.objects.create_user(company.contact_email, company.contact_email, company.password)
			user.first_name = company.name
			user.save()

			user = User.objects.filter(username=company.contact_email)
			user = user[0]
			user.set_password(company.password)
			user.save()
			
			# send email with login info
			try:
				plaintext = get_template('email/registrook.txt')
				htmly = get_template('email/registrook.html')

				d = Context({
					'contact_name':request.POST['contact_name'],
					'empresa':request.POST['name'],
					'contact_email':request.POST['contact_email'],
					'password':company.password,
					})

				subject, from_email, to = 'Registro de empresa en Meguz.com', 'like@meguz.com', request.POST['contact_email']
				text_content = plaintext.render(d)
				html_content = htmly.render(d)
				msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
				msg.attach_alternative(html_content, "text/html")
				msg.send()

				# redirect to 'register ok' page
				return HttpResponseRedirect('/empresa/registro/ok')

			except Exception, e:
				return render_to_response('company/contact.html', {"e":e}, context_instance=RequestContext(request))							
	else:
		form = CompanyContactForm()

	context = {'form': form}
	return render_to_response('company/register.html', context, context_instance=RequestContext(request))

def CompanyThanks(request):
	return render_to_response('company/registerok.html', {}, context_instance=RequestContext(request))

# ------------------------------------------------------------------------------------------------
# Prize views
# ------------------------------------------------------------------------------------------------
def PrizeView(request, company_slug, offer_id, offer_slug):
	prize = Offer.objects.get(pk=offer_id)
	if prize is None:
		return HttpResponseRedirect("/")
	else:
		company = Company.objects.get(pk=prize.company.id)

		from pyes.queryset import generate_model

		prize_model = generate_model("prize","prize")
		prizes = prize_model.objects.exclude(status='a').exclude(status='b').exclude(status='d').exclude(status='e').exclude(id=prize.id).order_by('publish_date')

		meguz_model = generate_model("meguz","meguz")
		meguzs = meguz_model.objects.exclude(status='a').exclude(status='b').exclude(status='d').exclude(status='e').filter(prize_id=prize.id).order_by('-publish_date')

		winners = {}
		if prize.status == 'F' :
			winners = Meguz.objects.filter(prize=prize).filter(status='F')

		context = { 'offer': prize, 'company': company, 'prizes':prizes, 'meguzs':meguzs, 'winners':winners }
		return render_to_response('offer.html', context, context_instance=RequestContext(request))

def PrizeParticipate(request, offer_id):

	from django.core.urlresolvers import reverse
	from django.contrib import messages
	from django_youtube.api import Api, AccessControl, ApiError

	prize = Offer.objects.get(pk=offer_id)
	if prize is None:
		messages.add_message(request, messages.ERROR, _('Prize is None'))
		return HttpResponseRedirect("/")
	else:
		# Prize exists
		from main.models import User
		user = User.objects.get(token=request.COOKIES.get('fbmgz_234778956683382'))
		if user is None:
			messages.add_message(request, messages.ERROR, _('User is none'))
			return HttpResponseRedirect("/")		
		else:
			# User exists
			prize = Offer.objects.get(pk=offer_id)
			meguz = Meguz.objects.filter(user=user,prize=prize)
			if meguz.count() == 0:

				# User is not participating
				company = Company.objects.get(pk=prize.company.id)
				formData = MeguzForm()		

				# video metadata
				title = prize.title + " | Meguz.com"
				keywords = prize.category.name + "," + prize.prize_name + "," + prize.company.name
				description = prize.description + "... Visita www.meguz.com para mas informacion"

				# Try to create post_url and token
				try:
					api = Api()
					api.authenticate()

					data = api.upload(title, description=description, keywords=keywords, access_control=AccessControl.Unlisted)

				# Api error happend
				except ApiError as e:
					messages.add_message(request, messages.ERROR, _('Api error happend'))
					messages.add_message(request, messages.ERROR, e.message)
					return HttpResponseRedirect("/")

				# Other error
				except Error as e:
					messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
					return HttpResponseRedirect("/")

				formVideo = MeguzMultimediaForm(initial={"token": data["youtube_token"]})	
							
				import os
				from django.contrib.sites.models import Site
				current_site = Site.objects.get_current()
				domain = current_site.domain

				protocol = 'https' if request.is_secure() else 'http'
				next_url = "".join([protocol, ":", os.sep, os.sep, domain, "/meguz/update/multimedia/{0}/{1}".format(prize.id,request.COOKIES.get('fbmgz_234778956683382')), os.sep])

				context = { 'offer': prize, 'company': company, 'form_data': formData, 'form_video': formVideo, 'post_url': data['post_url'], 'next_url': next_url }
				return render_to_response('meguz/new.html', context, context_instance=RequestContext(request))

			else:
				# User is already participating
				context = { 'offer': prize }
				return render_to_response('meguz/new_forbidden.html', context, context_instance=RequestContext(request))

def PrizeParticipateForm(request, prize_id, user_token):

	if request.method == 'POST': 
		meguzForm = MeguzForm(request.POST)

		if(meguzForm.is_valid()):

			# Load model with form
			meguz = Meguz(**meguzForm.cleaned_data)
			slug = slugify(request.POST['title'])						
			meguz.slug = slug
			meguz.status = 'B'
			meguz.prize_id = prize_id
			meguz.vote_count = 0

			# Load user id
			from main.models import User
			user = User.objects.get(token=user_token)
			if user is None:
				context = {'response':'Forbidden'}	
			else:
				meguz.user_id = user.id
				meguz.save()
				context = {'response':meguz.id}
		else:
			context = {'response':'fail'}

	else:			
		context = {'response': 'invalid'}

	return render_to_response('meguz/participate.html', context, context_instance=RequestContext(request))

# ------------------------------------------------------------------------------------------------
# Meguz views
# ------------------------------------------------------------------------------------------------
def MeguzView(request, meguz_id, meguz_slug):
	meguz = Meguz.objects.get(pk=meguz_id)

	from pyes.queryset import generate_model
	meguz_model = generate_model("meguz","meguz")
	meguzs = meguz_model.objects.exclude(status='a').exclude(status='b').exclude(status='d').exclude(status='e').filter(prize_id=meguz.prize.id).order_by('-publish_date')

	context = {"meguz":meguz, "meguzs":meguzs}
	return render_to_response('meguz.html', context, context_instance=RequestContext(request))


def MeguzUpdateMultimedia(request, prize_id, user_token):
	from django.core.urlresolvers import reverse
	from django.contrib import messages
	from django_youtube.api import Api, AccessControl, ApiError	

	from main.models import User

	prize = Offer.objects.get(pk=prize_id)
	user = User.objects.get(token=user_token)
	meguz = Meguz.objects.get(prize=prize,user=user)
	if meguz is None:
		return HttpResponseRedirect("/")
	else:		

		# If request.GET isset from Youtube, update media_url with video ID
		if request.method == 'GET':
			if 'status' in request.GET:
				if request.GET['status'] == "200":
					if 'id' in request.GET:

						# Update database info
						meguz.video_id = request.GET['id']
						meguz.video_thumb = "http://img.youtube.com/vi/%s/1.jpg" % request.GET['id']
						meguz.save()

						# Update youtube metadata
						try:
							api = Api()
							api.authenticate()

							title = meguz.title + " | Meguz.com"
							description = meguz.description + "... Visita www.meguz.com para mas informacion"
							keywords = meguz.prize.category.name + "," + meguz.prize.prize_name + "," + meguz.prize.company.name
							api.update_video(meguz.video_id, title, description, keywords)

						# Api error happend
						except ApiError as e:
							messages.add_message(request, messages.ERROR, e.message)
							return HttpResponseRedirect("/")

						# Other error
						except:
							messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
							return HttpResponseRedirect("/")


						return HttpResponseRedirect("/usuario/mis-meguz") # /meguz/{id}/{slug}

def MeguzEdit(request,meguz_id):

	from django.core.urlresolvers import reverse
	from django.contrib import messages
	from django_youtube.api import Api, AccessControl, ApiError	

	from main.models import User
	user = User.objects.get(token=request.COOKIES.get('fbmgz_234778956683382'))
	if user is None:
		HttpResponseRedirect("/")		
	else:
		# Check meguz existence
		meguz = Meguz.objects.get(pk=meguz_id)
		if meguz is None:
			HttpResponseRedirect("/")
		else:
			# Check is user's meguz
			if meguz.user.token != user.token:
				HttpResponseRedirect("/")
			else:
				# Load MeguzForm, MeguzMultimediaForm
				formData = MeguzForm(initial={"title":meguz.title, "description":meguz.description})

				# Check video status	
				title = meguz.title + " | Meguz.com"
				keywords = meguz.prize.category.name + "," + meguz.prize.prize_name + "," + meguz.prize.company.name
				description = meguz.description + "... Visita www.meguz.com para mas informacion"

				try:
					api = Api()
					api.authenticate()						

					#if meguz.video_id is not None:
					#	status = api.check_upload_status(meguz.video_id)

					data = api.upload(title, description=description, keywords=keywords, access_control=AccessControl.Unlisted)			
				except:
					messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
					return HttpResponseRedirect("/")

				formVideo = MeguzMultimediaForm(initial={"token": data["youtube_token"]})	

				import os
				protocol = 'https' if request.is_secure() else 'http'
				next_url = "".join([protocol, ":", os.sep, os.sep, request.get_host(), "/meguz/update/multimedia/{0}/{1}".format(meguz.prize.id,request.COOKIES.get('fbmgz_234778956683382')), os.sep])

				context = {'meguz':meguz,'form_data':formData, 'form_video':formVideo, 'post_url': data['post_url'], 'next_url': next_url }
				return render_to_response('meguz/edit.html', context, context_instance=RequestContext(request))

def MeguzEditForm(request, meguz_id, user_token):

	from django.core.urlresolvers import reverse
	from django.contrib import messages
	from django_youtube.api import Api, AccessControl, ApiError	

	if request.method == 'POST':
		meguzForm = MeguzForm(request.POST)

		if(meguzForm.is_valid()):

			# Load model with form
			meguz = Meguz.objects.get(pk=meguz_id)
			meguz.title = request.POST['title']
			meguz.description = request.POST['description']
			meguz.id = meguz_id

			# Load user id
			from main.models import User
			user = User.objects.get(token=user_token)
			if user is None:
				context = {'response':'Forbidden'}	
			else:
				meguz.save()

				if meguz.status == 'C':
					es = ES("localhost:9200")
					meguzES = es.get("meguz","meguz",meguz.id)
					meguzES.title = meguz.title
					meguzES.description = meguz.description
					meguzES.save()

				# Update youtube data
				try:
					api = Api()
					api.authenticate()

					title = meguz.title + " | Meguz.com"
					description = meguz.description + "... Visita www.meguz.com para mas informacion"
					keywords = meguz.prize.category.name + "," + meguz.prize.prize_name + "," + meguz.prize.company.name
					
					if meguz.video_id != '':
						api.update_video(meguz.video_id, title, description, keywords)

				# Api error happend
				except ApiError as e:
					messages.add_message(request, messages.ERROR, e.message)
					return HttpResponseRedirect("/")

				# Other error
				except:
					messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
					return HttpResponseRedirect("/")


				context = {'response':meguz.id}
		else:
			context = {'response':'fail'}

	else:			
		context = {'response': 'invalid'}

	return render_to_response('meguz/edit_form.html', context, context_instance=RequestContext(request))

def MeguzDelete(request, meguz_id):
	from django.core.urlresolvers import reverse
	from django.contrib import messages
	from django_youtube.api import Api, AccessControl, ApiError	

	from main.models import User
	user = User.objects.get(token=request.COOKIES.get('fbmgz_234778956683382'))
	if user is None:
		HttpResponseRedirect("/")		
	else:
		# Check meguz existence
		meguz = Meguz.objects.get(pk=meguz_id)
		if meguz is None:
			HttpResponseRedirect("/")
		else:
			# Check is user's meguz
			if meguz.user.token != user.token:
				HttpResponseRedirect("/")
			else:

				try:
					api = Api()
					api.authenticate()						
					
					if api.delete_video(meguz.video_id) is True:
						if meguz.status == 'C':
							try: 
								es = ES('127.0.0.1:9200')
								es.delete('meguz','meguz',meguz.id)
							except:
								messages.add_message(request, messages.ERROR, _('Aviso no se encuentra en es'))

						meguz.delete()						

						HttpResponseRedirect("/usuario/mis-meguz")
				except:
					messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
					return HttpResponseRedirect("/")

	return render_to_response('meguz/delete.html', {}, context_instance=RequestContext(request))

def MeguzDeleteVideo(request, meguz_id):
	from django.core.urlresolvers import reverse
	from django.contrib import messages
	from django_youtube.api import Api, AccessControl, ApiError	

	from main.models import User
	user = User.objects.get(token=request.COOKIES.get('fbmgz_234778956683382'))
	if user is None:
		HttpResponseRedirect("/")		
	else:
		# Check meguz existence
		meguz = Meguz.objects.get(pk=meguz_id)
		if meguz is None:
			HttpResponseRedirect("/")
		else:
			# Check is user's meguz
			if meguz.user.token != user.token:
				HttpResponseRedirect("/")
			else:

				try:
					api = Api()
					api.authenticate()						
					
					if meguz.video_id != '':
						if api.delete_video(meguz.video_id) is True:
							meguz.video_id = '';
							meguz.video_thumb = '';
							meguz.save()
							HttpResponseRedirect("/usuario/mis-meguz")
				except:
					messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
					return HttpResponseRedirect("/")

	return render_to_response('meguz/delete.html', {}, context_instance=RequestContext(request))

@csrf_exempt
def MeguzValidateFinish(request):
	if request.method == 'POST':

		meguz_id = request.POST['meguz_id']
		url = request.POST['url']

		meguz = Meguz.objects.get(pk=meguz_id)
		if meguz is None:
			response = "Error al validar: Meguz no encontrado"
		else:

			# Database vote count
			dbCount = meguz.vote_count

			# Facebook vote count
			import requests
			r = requests.get("https://graph.facebook.com/fql?q=SELECT like_count FROM link_stat WHERE url='"+url+"'")
			if r.status_code == 200:
				json = r.json()
				fbCount = json["data"][0]["like_count"]

				if(dbCount >= fbCount):

					# Meguz update
					meguz.vote_count = fbCount

					es = ES("localhost:9200")
					meguzES = es.get("meguz","meguz",meguz.id)
					meguzES.vote_count = meguz.vote_count

					# Check if meguz wins
					if(meguz.vote_count >= meguz.prize.vote_limit):

						# If prize is not finish
						if meguz.prize.status != 'F':

							# If prize stock is avalaible
							if(meguz.prize.stock > 0):

								meguz.status = 'F'
								meguzES.status = 'F'

								prize = Offer.objects.get(pk=meguz.prize.id)
								prize.stock = prize.stock-1
								prize.save()

								# If is last prize, finish the Offer
								if(prize.stock == 0):

									prize.status = 'F'
									prize.save()

									prizeES = es.get("prize","prize",prize.id)
									prizeES.status = 'F'
									prizeES.save()

									response = "Se completa el stock"

								else:
									response = "Aun queda stock"

							else:
								response = "No hay stock disponible"

						else:
							response = "El premio ya ha finalizado"

					else:
						response = "Aun no se cumple la meta"

					meguz.save()
					meguzES.save()
					
				else:
					response = "Hack detected"

			else:
				response = "Ha ocurrido un problema al intentar validar la informacion"
	else:
		response = "Forbidden"

	return render_to_response('meguz/validate_finish.html', {'response': response}, context_instance=RequestContext(request))

# ------------------------------------------------------------------------------------------------
# User views
# ------------------------------------------------------------------------------------------------

@csrf_exempt
def UserSuscribe(request, meguz_id):
	meguz = Meguz.objects.get(pk=meguz_id)
	if meguz is None:
		response = 'NOT_FOUND'
	else:		

		meguz.vote_count = meguz.vote_count + 1
		meguz.save()
		response = 'DONE'

		es = ES("localhost:9200")
		meguzES = es.get("meguz","meguz",meguz.id)
		if meguzES.vote_count is None:
			meguzES.vote_count = 1
		else:
			meguzES.vote_count = meguz.vote_count + 1
		meguzES.save()

		if(meguz.vote_count >= meguz.prize.vote_limit):
			response = "FINISH"		

	context = {"response": response}
	return render_to_response('meguz/suscribe.html', context, context_instance=RequestContext(request))

@csrf_exempt
def UserLogin(request):
	if request.method == 'POST':
		from main.models import User

		# Find if User already exists
		newUser = User()
		oldUser = User.objects.filter(facebook_id=request.POST['id'])
		if len(oldUser) > 0:
			newUser.id = oldUser[0].id

		# Update user data
		if 'name' in request.POST:
			newUser.name = request.POST['name']

		if 'first_name' in request.POST:
			newUser.first_name = request.POST['first_name']

		if 'last_name' in request.POST:
			newUser.last_name = request.POST['last_name']

		if 'username' in request.POST:
			newUser.username = request.POST['username']

		if 'email' in request.POST:
			newUser.email = request.POST['email']

		if 'gender' in request.POST:
			newUser.gender = request.POST['gender']

		#if 'birthday' in request.POST:
		#	user.birthday = request.POST['birthday']

		newUser.avatar = 'http://graph.facebook.com/' + request.POST['id'] + '/picture'
		newUser.facebook_id = request.POST['id']

		import string, random
		chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
		newUser.token = ''.join(random.choice(chars) for x in range(40))

		newUser.save()

		context = { 'token': newUser.token }		
	else:
		context = { 'token': 'Forbidden' }

	return render_to_response('login.html', context, context_instance=RequestContext(request))

def UserMisMeguz(request):
	from models import User
	user = User.objects.get(token=request.COOKIES.get('fbmgz_234778956683382'))
	if user is None:
		HttpResponseRedirect("/")
	else:

		meguz = Meguz.objects.filter(user=user).order_by('-publish_date')
		context = { 'meguz':meguz }
		return render_to_response('user/mis_meguz.html', context, context_instance=RequestContext(request))

def UserMisDatos(request):
	from models import User
	user = User.objects.get(token=request.COOKIES.get('fbmgz_234778956683382'))
	if user is None:
		HttpResponseRedirect("/")
	else:
		context = { 'user':user }
		return render_to_response('user/mis_datos.html', context, context_instance=RequestContext(request))
