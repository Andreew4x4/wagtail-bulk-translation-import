from django.urls import include, path, reverse
from django.utils.translation import gettext as _

from urllib.parse import urlencode

from wagtail import hooks
from wagtail.models import Page
from wagtail.admin.widgets import ListingButton


from .views import edit_translation
from .models import TranslationMenuItem

@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path(
            "translate/bulk_upload/",
            edit_translation.bulk_upload_pofile,
            name="bulk_upload_pofile",
        ),
        path(
            "translate/bulk_upload_form/",
            edit_translation.BulkUploadView.as_view(),
            name="bulk_upload_files",
        ),
        path(
            "translate/bulk_download_files/<int:page_id>",
            edit_translation.bulk_download_pofile,
            name="bulk_download_pofile",
        ),
        path(
            "translate/bulk_download_all_files/",
            edit_translation.bulk_download_all_pofiles,
            name="bulk_download_all",
        ),
    ]

    return [
        path(
            "localize/",
            include(
                (urls, "wagtail_localize"),
                namespace="bulk_translation_import",
            ),
        )
    ]


@hooks.register('register_admin_menu_item')
def menu_item_upload_po_button():
    url = reverse(
        "bulk_translation_import:bulk_upload_files",
    )
    return TranslationMenuItem(
        _("Upload translations"),
        url,
        order=9999,
        icon_name="upload",
    )


@hooks.register('register_admin_menu_item')
def menu_item_download_po_button():
    url = reverse(
        "bulk_translation_import:bulk_download_all",
    )
    return TranslationMenuItem(
        _("Download translations"),
        url,
        order=9999,
        icon_name="download",
    )


def page_listing_download_po_button(page: Page, user, view_name=None, next_url=None):
    if not page.is_root() and user.has_perm("wagtail_localize.submit_translation"):
        url = reverse(
            "bulk_translation_import:bulk_download_pofile",
            args=[page.id],
        )
        if next_url is not None:
            url += "?" + urlencode({"next": next_url})
        yield ListingButton(
            _("Download .PO files for this page"),
            url,
            priority=91,
            icon_name="download",
        )


hooks.register("register_page_header_buttons", page_listing_download_po_button)
hooks.register("register_page_listing_more_buttons", page_listing_download_po_button)
