from common.common_customization.doctype.end_of_service_award_reason.seed import (
    sync_saudi_reasons,
)
from common.install.create_permissions import create_custom_doc_perms
from common.install.translation import generate_translations
from common.install.update_configs import update_jwt_config


def after_install():
    # Add JWT config
    update_jwt_config()

    # Update required permissions
    create_custom_doc_perms()

    # Generate translations
    generate_translations()

    # Seed the end of service reasons for any company already under Saudi law.
    # A fresh site has none yet, so the Company hook covers the rest.
    sync_saudi_reasons()
