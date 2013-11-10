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
	