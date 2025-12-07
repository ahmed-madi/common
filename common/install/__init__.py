from common.install.create_permissions import create_custom_doc_perms
from common.install.translation import generate_translations


def after_install():
    create_custom_doc_perms()
    generate_translations()
