from common.install.create_permissions import create_custom_doc_perms


def after_install():
    create_custom_doc_perms()
