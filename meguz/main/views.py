from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify

from main.models import Company, Offer, Meguz
from main.forms import CompanyContactForm, MeguzForm, MeguzMultimediaForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.core.context_processors import csrf

import Image

# ------------------------------------------------------------------------------------------------
# General views
# ------------------------------------------------------------------------------------------------
def Home(request):
	offers = Offer.objects.all()
	context = {'offers': offers}
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
			
			# send email with login info
			plaintext = get_template('email/registrook.txt')
			htmly = get_template('email/registrook.html')

			d = Context({
				'contact_name':request.POST['contact_name'],
				'empresa':request.POST['name'],
				'contact_email':request.POST['contact_email'],
				'password':company.password,
				})

			subject, from_email, to = 'Registro de empresa en Meguz.com', 'pqzada@gmail.com', request.POST['contact_email']
			text_content = plaintext.render(d)
			html_content = htmly.render(d)
			msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
			msg.attach_alternative(html_content, "text/html")
			msg.send()

			# redirect to 'register ok' page
			return HttpResponseRedirect('/empresa/registro/ok')
	else:
		form = CompanyContactForm()

	context = {'form': form}
	return render_to_response('company/register.html', context, context_instance=RequestContext(request))

def CompanyThanks(request):
	return render_to_response('company/registerok.html', {}, context_instance=RequestContext(request))

# ------------------------------------------------------------------------------------------------
# Prize views
# ------------------------------------------------------------------------------------------------
def PrizeView(request, offer_id, offer_slug):
	prize = Offer.objects.get(pk=offer_id)
	if prize is None:
		return HttpResponseRedirect("/")
	else:
		company = Company.objects.get(pk=prize.company.id)
		context = { 'offer': prize, 'company': company }
		return render_to_response('offer.html', context, context_instance=RequestContext(request))

def PrizeParticipate(request, offer_id):

	from django.core.urlresolvers import reverse
	from django.contrib import messages
	from django_youtube.api import Api, AccessControl, ApiError

	prize = Offer.objects.get(pk=offer_id)
	if prize is None:
		return HttpResponseRedirect("/")
	else:
		# Prize exists
		from main.models import User
		user = User.objects.get(token=request.COOKIES.get('fbmgz_234778956683382'))
		if user is None:
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
					messages.add_message(request, messages.ERROR, e.message)
					return HttpResponseRedirect("/")

				# Other error
				except:
					messages.add_message(request, messages.ERROR, _('Ha ocurrido un error, por favor intenta de nuevo'))
					return HttpResponseRedirect("/")

				formVideo = MeguzMultimediaForm(initial={"token": data["youtube_token"]})	
							
				import os
				protocol = 'https' if request.is_secure() else 'http'
				next_url = "".join([protocol, ":", os.sep, os.sep, request.get_host(), "/meguz/update/multimedia/{0}/{1}".format(prize.id,request.COOKIES.get('fbmgz_234778956683382')), os.sep])

				context = { 'offer': prize, 'company': company, 'form_data': formData, 'form_video': formVideo, 'post_url': data['post_url'], 'next_url': next_url }
				return render_to_response('meguz/new.html', context, context_instance=RequestContext(request))

			else:
				# User is already participating
				return render_to_response('meguz/new_forbidden.html', {}, context_instance=RequestContext(request))

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

# ------------------------------------------------------------------------------------------------
# User views
# ------------------------------------------------------------------------------------------------
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