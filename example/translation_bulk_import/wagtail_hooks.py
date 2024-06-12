from django.urls import include, path

from wagtail import hooks

from .views import edit_translation


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path(
            "translate/pofile/bulk_upload/",
            edit_translation.bulk_upload_pofile,
            name="upload_pofile",
        ),
    ]

    return [
        path(
            "localize/",
            include(
                (urls, "wagtail_localize"),
                namespace="wagtail_localize",
            ),
        )
    ]
