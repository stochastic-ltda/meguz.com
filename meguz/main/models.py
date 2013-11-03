from django.db import models
from thumbs import ImageWithThumbsField

class Company(models.Model):
	name 			= models.CharField(max_length=200)
	slug 			= models.SlugField(unique=True,max_length=200)
	logo 			= ImageWithThumbsField(upload_to="company/", sizes=((120,120),(250,250)))
	slogan 			= models.CharField(max_length=200, null=True)
	rut 			= models.CharField(max_length=25)
	website 		= models.URLField(max_length=200, null=True)
	address 		= models.CharField(max_length=200, null=True)
	phone 			= models.CharField(max_length=40, null=True)
	email 			= models.EmailField(max_length=75, null=True)
	contact_name 	= models.CharField(max_length=40)
	contact_phone 	= models.CharField(max_length=40)
	contact_email 	= models.EmailField(max_length=75)	
	password 		= models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

