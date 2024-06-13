from django.db import models
from wagtail.admin.menu import MenuItem

# Create your models here.
class TranslationMenuItem(MenuItem):
    def is_shown(self, request):
        return (
                request.user.has_perm('wagtail_localize.submit_translation')
        )