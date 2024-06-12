from django.urls import include, path, reverse

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


def page_listing_more_buttons(page: Page, user, view_name=None, next_url=None):
    url = reverse(
        "bulk_translation_import:bulk_upload_files",
    )
    yield ListingButton(
        "Upload many PO files",
        url,
        priority=60,
        icon_name="wagtail-localize-language",
    )


hooks.register("register_page_header_buttons", page_listing_more_buttons)
hooks.register("register_page_listing_more_buttons", page_listing_more_buttons)
