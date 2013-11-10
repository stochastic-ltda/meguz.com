from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify

from main.models import Company, Offer
from main.forms import CompanyContactForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

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
