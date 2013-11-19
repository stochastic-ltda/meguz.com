from django import forms
from main.models import Category

MEDIA_CHOICES 	= ( 
	('Y', 'Video'),
	('I', 'Imagen'),	
)

SOCIAL_CHOICES 	= ( 
	('F', 'Facebook'),
	('T', 'Twitter'),
)

class OfferNewForm(forms.Form):
	title 			= forms.CharField(max_length=200)
	prize_name		= forms.CharField(max_length=200)
	stock	     	= forms.IntegerField()
	category		= forms.ModelChoiceField(queryset=Category.objects.all(),empty_label="Seleccione")
	description		= forms.CharField(widget=forms.Textarea)
	conditions		= forms.CharField(widget=forms.Textarea)
	vote_limit     	= forms.IntegerField()
	vote_source   	= forms.ChoiceField(choices=SOCIAL_CHOICES)


class OfferMultimediaForm(forms.Form):
	media_type		= forms.ChoiceField(choices=MEDIA_CHOICES)
	token = forms.CharField()
	file = forms.FileField()
	media_image = forms.ImageField()

# change form view to a manually print
class CompanyEditForm(forms.Form):
	name 			= forms.CharField(max_length=200,label='Nombre')
	slogan 			= forms.CharField(max_length=200, required=False)
	logo 			= forms.ImageField(help_text='Se recomienda subir una imagen de 250x250',required=False)
	rut 			= forms.CharField(max_length=25,help_text='Ej: 99.888.777-6')
	address 		= forms.CharField(max_length=200, required=False)
	phone 			= forms.CharField(max_length=40, required=False)
	email 			= forms.EmailField(max_length=75,initial='@', required=False)
	website 		= forms.URLField(max_length=200,initial='http://', required=False)
	contact_name 	= forms.CharField(max_length=40)
	contact_phone 	= forms.CharField(max_length=40)
	contact_email 	= forms.EmailField(max_length=75,initial='@',required=False)	