from django.contrib import admin
from .models import Finch, Feeding, Seed, Photo

# Register your models here.
admin.site.register(Finch)
admin.site.register(Feeding)
admin.site.register(Seed)
admin.site.register(Photo)