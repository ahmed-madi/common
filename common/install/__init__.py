from common.install.update_configs import update_jwt_config
from common.install.create_permissions import create_custom_doc_perms
from common.install.translation import generate_translations

def after_install():
    # Add JWT config
    update_jwt_config()

    # Update required permissions
    create_custom_doc_perms()

    # Generate translations
    generate_translations()
