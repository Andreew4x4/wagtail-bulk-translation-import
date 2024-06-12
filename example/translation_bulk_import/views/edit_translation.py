import polib

from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from django.utils.translation import gettext as _

from wagtail_localize.models import Translation


@require_POST
def bulk_upload_pofile(request):
    files = request.FILES.getlist("file")
    for f in files:
        try:
            po = polib.pofile(f.read())
            translation_id = po.metadata["X-WagtailLocalize-TranslationID"]
            translation = Translation.objects.get(uuid=translation_id)
            translation.import_po(po)
            messages.success(
                request,
                _(f"Successfully imported translations from PO File ({translation})."),
            )
        except (OSError, UnicodeDecodeError):
            # Annoyingly, POLib uses OSError for parser exceptions...
            messages.error(request, _("Please upload a valid PO file."))
        except Translation.DoesNotExist:
            messages.error(request, _("Please upload a valid PO file."))


class BulkUploadView(TemplateView):
    template_name = "translation_bulk_import/admin/bulk_upload.html"
    title = "Upload many PO files"