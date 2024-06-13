from django.urls import include, path, reverse
from urllib.parse import urlencode

from wagtail import hooks
from wagtail.models import Locale, Page
from wagtail.admin.widgets import ListingButton

from .views import edit_translation


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path(
            "translate/pofile/bulk_upload/",
            edit_translation.bulk_upload_pofile,
            name="bulk_upload_pofile",
        ),
        path(
            "translate/upload_bulk_files/",
            edit_translation.BulkUploadView.as_view(),
            name="bulk_upload_files",
        ),
        path(
            "translate/download_bulk_files/<int:page_id>",
            edit_translation.BulkDownload.as_view(),
            name="bulk_download_files",
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


def page_listing_upload_po_button(page: Page, user, view_name=None, next_url=None):
    url = reverse(
        "bulk_translation_import:bulk_upload_files",
    )
    yield ListingButton(
        "Upload many PO files",
        url,
        priority=60,
        icon_name="wagtail-localize-language",
    )


hooks.register("register_page_header_buttons", page_listing_upload_po_button)
hooks.register("register_page_listing_more_buttons", page_listing_upload_po_button)


def page_listing_download_po_button(page: Page, user, view_name=None, next_url=None):
    if not page.is_root() and user.has_perm("wagtail_localize.submit_translation"):
        url = reverse(
            "bulk_translation_import:bulk_download_files",
            args=[page.alias_of_id or page.id],
        )
        if next_url is not None:
            url += "?" + urlencode({"next": next_url})
        yield ListingButton(
            "Dwonload PO files for site",
            url,
            priority=60,
            icon_name="wagtail-localize-language",
        )

hooks.register("register_page_header_buttons", page_listing_download_po_button)
hooks.register("register_page_listing_more_buttons", page_listing_download_po_button)