from django.contrib import admin
from main.models import Company

class CompanyAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}

#class OfferAdmin(admin.ModelAdmin):
#	prepopulated_fields = {'slug': ('title',)}

admin.site.register(Company, CompanyAdmin)
#admin.site.register(Offer, OfferAdmin)
#admin.site.register(Challenge)
#admin.site.register(User)