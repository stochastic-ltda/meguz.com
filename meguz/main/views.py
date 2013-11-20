from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify

from main.models import Company, Offer
from main.forms import CompanyContactForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.core.context_processors import csrf

import Image

def Home(request):
	offers = Offer.objects.all()
	context = {'offers': offers}
	return render_to_response('home.html', context, context_instance=RequestContext(request))

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

def PrizeView(request, offer_id, offer_slug):
	prize = Offer.objects.get(pk=offer_id)
	company = Company.objects.get(pk=prize.company.id)
	context = { 'offer': prize, 'company': company }
	return render_to_response('offer.html', context, context_instance=RequestContext(request))

# def PrizeParticipate(request, offer_id):


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