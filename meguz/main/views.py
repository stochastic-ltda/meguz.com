from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify

from main.models import Company, Offer
from main.forms import CompanyContactForm

import Image

def Home(request):
	companies = Company.objects.all().order_by('name')
	context = {'companies': companies}
	return render_to_response('home.html', context, context_instance=RequestContext(request))

def SpecificOffer(request, company_slug, offer_slug):
	company = Company.objects.get(slug=company_slug)
	offer = Offer.objects.get(slug=offer_slug)
	context = {'offer': offer, 'company':company}
	return render_to_response('offer.html', context, context_instance=RequestContext(request))	

def CompanyContact(request):	
	if request.method == 'POST': 
		form = CompanyContactForm(request.POST, request.FILES)

		if(form.is_valid()):			

			# generate slug
			slug = slugify(request.POST['name']) 

			# create object and save
			c = Company(name=request.POST['name'],slug=slug,logo=request.FILES['logo'],rut=request.POST['rut'],website=request.POST['website'],contact_name=request.POST['contact_name'],contact_phone=request.POST['contact_phone'],contact_email=request.POST['contact_email'])
			c.save()

			# redirect to thanks page
			return HttpResponseRedirect('/empresa/registro/ok')
	else:
		form = CompanyContactForm()

	context = {'form': form}
	return render_to_response('company_contact.html', context, context_instance=RequestContext(request))

def CompanyThanks(request):
	return render_to_response('company_thanks.html', {}, context_instance=RequestContext(request))