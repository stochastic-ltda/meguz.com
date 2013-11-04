from django.db import models
from thumbs import ImageWithThumbsField

MEDIA_CHOICES 	= ( 
	('I', 'Imagen'),
	('Y', 'Video Youtube'),
)

SOCIAL_CHOICES 	= ( 
	('F', 'Facebook'),
	('T', 'Twitter'),
)

STATUS_CHOICES 	= (
	('A', 'Inactivo'),
	('B', 'Pendiente aprobacion'),
	('C', 'Publicado'),
	('E', 'Eliminado'),
)

# Empresas
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

# Categorias de oferta
class Category(models.Model):
	name 			= models.CharField(max_length=200)
	slug 			= models.SlugField(unique=True, max_length=200)
	def __unicode__(self):
		return self.name

# Ofertas de empresas
class Offer(models.Model):
	title       	= models.CharField(max_length=200)
	slug       		= models.SlugField(unique=True,max_length=200)
	description   	= models.TextField(blank=False)
	conditions   	= models.TextField(blank=True)
	media_type     	= models.CharField(max_length=1, choices=MEDIA_CHOICES)
	media_url     	= models.CharField(max_length=200)
	vote_limit     	= models.IntegerField()
	vote_source   	= models.CharField(max_length=1, choices=SOCIAL_CHOICES)
	prize_name    	= models.CharField(max_length=40)
	stock      		= models.IntegerField()
	publish_date    = models.DateTimeField(auto_now=True)
	status			= models.CharField(max_length=1, choices=STATUS_CHOICES)
	company     	= models.ForeignKey("Company")
	category		= models.ForeignKey("Category")   

	def __unicode__(self):
		return self.title 
       
   