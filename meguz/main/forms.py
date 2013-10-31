from django import forms
from validators import validate_unique_name

class CompanyContactForm(forms.Form):
	name 			= forms.CharField(max_length=200,label='Nombre',validators=[validate_unique_name])
	logo 			= forms.ImageField(help_text='Se recomienda subir una imagen de 250x250')
	rut 			= forms.CharField(max_length=25,help_text='Ej: 99.888.777-6')
	website 		= forms.URLField(max_length=200,initial='http://')
	contact_name 	= forms.CharField(max_length=40)
	contact_phone 	= forms.CharField(max_length=40)
	contact_email 	= forms.EmailField(max_length=75,initial='@')	
