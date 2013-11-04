from django import forms

MEDIA_CHOICES 	= ( 
	('I', 'Imagen'),
	('Y', 'Video Youtube'),
)

SOCIAL_CHOICES 	= ( 
	('F', 'Facebook'),
	('T', 'Twitter'),
)

class OfferNewForm(forms.Form):
	title 			= forms.CharField(max_length=200,label='Nombre')
	description		= forms.CharField(widget=forms.Textarea)
	conditions		= forms.CharField(widget=forms.Textarea)
	#logo 			= forms.ImageField(help_text='Se recomienda subir una imagen de 250x250')
	#rut 			= forms.CharField(max_length=25,help_text='Ej: 99.888.777-6')
	#address 		= forms.CharField(max_length=200, required=False)
	#phone 			= forms.CharField(max_length=40, required=False)
	#email 			= forms.EmailField(max_length=75,initial='@', required=False)
	#website 		= forms.URLField(max_length=200,initial='http://', required=False)
	#contact_name 	= forms.CharField(max_length=40)
	#contact_phone 	= forms.CharField(max_length=40)
	#contact_email 	= forms.EmailField(max_length=75,initial='@')	
