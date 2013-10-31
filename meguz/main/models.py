from django.db import models
from thumbs import ImageWithThumbsField

SOCIAL_CHOICES = (
	('F', 'Facebook'),
	('T', 'Twitter'),
)

MEDIA_CHOICES = (
	('I', 'Image'),
	('Y', 'Youtube'),
)

class Company(models.Model):
	name 			= models.CharField(max_length=200)
	slug 			= models.SlugField(unique=True,max_length=200)
	logo 			= ImageWithThumbsField(upload_to="company/", sizes=((120,120),(250,250)))
	rut 			= models.CharField(max_length=25)
	contact_name 	= models.CharField(max_length=40)
	contact_phone 	= models.CharField(max_length=40)
	contact_email 	= models.EmailField(max_length=75)
	website 		= models.URLField(max_length=200)

	def __unicode__(self):
		return self.name


class Offer(models.Model):
	title 			= models.CharField(max_length=200)
	slug 			= models.SlugField(unique=True, max_length=200)
	company 		= models.ForeignKey("Company")
	shortname		= models.CharField(max_length=40)
	stock			= models.IntegerField()
	vote_limit 		= models.IntegerField()
	vote_source 	= models.CharField(max_length=1, choices=SOCIAL_CHOICES)
	media_url 		= models.CharField(max_length=200)
	media_type 		= models.CharField(max_length=1, choices=MEDIA_CHOICES)
	description 	= models.TextField(blank=False)
	start_date 		= models.DateTimeField(auto_now=True)
	end_date 		= models.DateTimeField(auto_now=False)

	def __unicode__(self):
		return self.title


class Challenge(models.Model):
	title 			= models.CharField(max_length=200)
	slug 			= models.SlugField(unique=True, max_length=200)
	offer 			= models.ForeignKey("Offer")
	user			= models.ForeignKey("User")
	media_url		= models.CharField(max_length=200)
	media_type 		= models.CharField(max_length=1, choices=MEDIA_CHOICES)
	vote_count		= models.IntegerField()
	creation_date	= models.DateTimeField(auto_now=True)
	description 	= models.TextField(blank=False)

	def __unicode__(self):
		return self.title

class User(models.Model):
	name 			= models.CharField(max_length=80)
	email 			= models.EmailField(max_length=74)
	avatar			= models.ImageField(upload_to="/media/avatar")
	country			= models.CharField(max_length=200)
	birthday 		= models.DateField(auto_now=False)

	def __unicode__(self):
		return self.name


