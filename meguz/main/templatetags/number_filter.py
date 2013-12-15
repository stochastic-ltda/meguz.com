from django import template
from decimal import *

register = template.Library()

def mini_number(value):	

	if(value >= 10000):
		getcontext().prec = 3
		return str(Decimal(value)/Decimal(1000)) + 'k'

	if(value >= 1000):
		getcontext().prec = 2
		return str(Decimal(value)/Decimal(1000)) + 'k'

	return value

register.filter('mini_number', mini_number)