from django.core.exceptions import ValidationError
from main.models import Company

def validate_unique_name(value):
	c = Company.objects.filter(name=value).count()
	if c > 0:
		raise ValidationError(u'Ya existe una empresa con este nombre')