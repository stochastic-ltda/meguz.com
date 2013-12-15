from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from main.models import Offer, Meguz

from pyes import *

def Home(request):
	return render_to_response('boss/index.html', {}, context_instance=RequestContext(request))

def PrizePendingApproval(request):
	prizes = Offer.objects.filter(status="B")

	context = {"prizes":prizes}
	return render_to_response('boss/prize/pending.html', context, context_instance=RequestContext(request))

def PrizeApprove(request, prize_id):

	es = ES("localhost:9200") # ES connection

	# Get prize and update status
	prize = Offer.objects.get(pk=prize_id)
	prize.status = "C"

	# Insert into elasticsearch
	obj = es.index({"id":prize.id,"title": prize.title,"slug":prize.slug,"thumbnail":prize.media_thumb,"description": prize.description + prize.conditions,"publish_date": prize.publish_date.strftime('%Y-%m-%d'),"status": prize.status,"url": "/"+prize.company.slug+"/premios/"+str(prize.id)+"/"+prize.slug+"/","vote_limit":prize.vote_limit,"vote_source":prize.vote_source, "category":prize.category.name}, "prize","prize", prize.id)
	es.indices.refresh("prize")

	# Save database record	
	prize.save()	

	return HttpResponseRedirect("/boss/premios/pendientes")

def PrizeReject(request, prize_id):
	
	# Get prize and update status
	prize = Offer.objects.get(pk=prize_id)
	prize.status = "D"
	prize.save()

	# TODO: Generate HTML with text explaining why was rejected
	# TODO: Send email with explanaition
	# TODO: Update status after sent the email

	return HttpResponseRedirect("/boss/premios/pendientes")


def MeguzPendingApproval(request):
	meguz = Meguz.objects.filter(status="B")

	context = {"meguz":meguz}
	return render_to_response('boss/meguz/pending.html', context, context_instance=RequestContext(request))

def MeguzApprove(request, meguz_id):

	es = ES("localhost:9200") # ES connection

	# Get meguz and update status
	meguz = Meguz.objects.get(pk=meguz_id)
	meguz.status = "C"

	# Insert into elasticsearch
	obj = es.index({"id":meguz.id,"prize_id":meguz.prize.id,"title": meguz.title,"slug":meguz.slug,"description": meguz.description,"publish_date": meguz.publish_date.strftime('%Y-%m-%d'),"status": meguz.status,"url": "/meguz/"+str(meguz.id)+"/"+meguz.slug+"/","video_thumb":meguz.video_thumb, "user_avatar":meguz.user.avatar}, "meguz","meguz", meguz.id)
	es.indices.refresh("meguz")

	# Save database record	
	meguz.save()	

	return HttpResponseRedirect("/boss/meguz/pendientes")

def MeguzReject(request, meguz_id):
	
	# Get meguz and update status
	meguz = Meguz.objects.get(pk=meguz_id)
	meguz.status = "D"
	meguz.save()

	# TODO: Generate HTML with text explaining why was rejected
	# TODO: Send email with explanaition
	# TODO: Update status after sent the email

	return HttpResponseRedirect("/boss/meguz/pendientes")