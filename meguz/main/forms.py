from django import forms
from validators import validate_unique_name

# change form view to a manually print
class CompanyContactForm(forms.Form):
	name 			= forms.CharField(max_length=200,label='Nombre',validators=[validate_unique_name])
	slogan 			= forms.CharField(max_length=200, required=False)
	logo 			= forms.ImageField(help_text='Se recomienda subir una imagen de 250x250')
	rut 			= forms.CharField(max_length=25,help_text='Ej: 99.888.777-6')
	address 		= forms.CharField(max_length=200, required=False)
	phone 			= forms.CharField(max_length=40, required=False)
	email 			= forms.EmailField(max_length=75,initial='@', required=False)
	website 		= forms.URLField(max_length=200,initial='http://', required=False)
	contact_name 	= forms.CharField(max_length=40)
	contact_phone 	= forms.CharField(max_length=40)
	contact_email 	= forms.EmailField(max_length=75,initial='@')	

class MeguzForm(forms.Form):
	title 			= forms.CharField(max_length=200)
	description		= forms.CharField(widget=forms.Textarea)

class MeguzMultimediaForm(forms.Form):
	token 			= forms.CharField()
	file 			= forms.FileField()

