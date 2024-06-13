import io
import polib
import tempfile
import zipfile

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from wagtail.models import Locale, Page
from wagtail_localize.models import Translation
from wagtail.admin.views.pages.utils import get_valid_next_url_from_request


def handle_redirect(request):
    # Work out where to redirect to
    next_url = get_valid_next_url_from_request(request)
    if not next_url:
        # Note: You should always provide a next URL when using this view!
        next_url = reverse("wagtailadmin_home")
    return redirect(next_url)


def zip_translations(pages):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for page in pages:
            t = Translation.objects.get(
                source__object_id=page.translation_key,
                target_locale_id=page.locale_id,
            )
            arcname = f"{slugify(page.slug)}-{t.target_locale.language_code}.po"
            zip_file.writestr(arcname, str(t.export_po()))
    return zip_buffer


def bulk_download_all_pofiles(request):
    default_locale = Locale.get_default()
    translated_pages = Page.objects.exclude(depth=1).exclude(
        locale_id=default_locale.id
    )
    zip_buffer = zip_translations(translated_pages)
    response = HttpResponse(
        zip_buffer.getvalue(), content_type="application/x-zip-compressed"
    )
    response["Content-Disposition"] = "attachment; filename=all-translations.zip"
    return response


def bulk_download_pofile(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    translated_pages = page.get_translations()
    zip_buffer = zip_translations(translated_pages)
    response = HttpResponse(
        zip_buffer.getvalue(), content_type="application/x-zip-compressed"
    )
    response[
        "Content-Disposition"
    ] = f"attachment; filename={page.slug}-translations.zip"
    return response


@require_POST
def bulk_upload_pofile(request):
    files = request.FILES.getlist("file")
    success_count = 0
    for f in files:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(f.read())
                tmp.flush()
                po = polib.pofile(tmp.name)
            translation_id = po.metadata["X-WagtailLocalize-TranslationID"]
            translation = Translation.objects.get(uuid=translation_id)
            translation.import_po(po)
            success_count += 1
        except (OSError, UnicodeDecodeError):
            # Annoyingly, POLib uses OSError for parser exceptions...
            messages.error(request, _("Please upload a valid PO file."))
        except Translation.DoesNotExist:
            messages.error(request, _("There is no translation for uploaded PO file."))
    messages.success(
        request, _(f"Successfully imported {success_count} translations from PO files")
    )

    return handle_redirect(request)


class BulkUploadView(TemplateView):
    template_name = "translation_bulk_import/admin/bulk_upload.html"
    title = "Upload many PO files"
