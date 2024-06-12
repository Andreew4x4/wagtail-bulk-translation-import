import polib
import tempfile

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from wagtail_localize.models import Translation
from wagtail.admin.views.pages.utils import get_valid_next_url_from_request


@require_POST
def bulk_upload_pofile(request):
    files = request.FILES.getlist("file")
    for f in files:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(f.read())
                tmp.flush()
                po = polib.pofile(tmp.name)
            translation_id = po.metadata["X-WagtailLocalize-TranslationID"]
            translation = Translation.objects.get(uuid=translation_id)
            translation.import_po(po)
            messages.success(
                request,
                _(
                    f"Successfully imported translations from PO File "
                    f"({translation.target_locale})."
                ),
            )
        except (OSError, UnicodeDecodeError):
            # Annoyingly, POLib uses OSError for parser exceptions...
            messages.error(request, _("Please upload a valid PO file."))
        except Translation.DoesNotExist:
            messages.error(request, _("There is no translation for uploaded PO file."))
    # Work out where to redirect to
    next_url = get_valid_next_url_from_request(request)
    if not next_url:
        # Note: You should always provide a next URL when using this view!
        next_url = reverse("wagtailadmin_home")

    return redirect(next_url)


class BulkUploadView(TemplateView):
    template_name = "translation_bulk_import/admin/bulk_upload.html"
    title = "Upload many PO files"
