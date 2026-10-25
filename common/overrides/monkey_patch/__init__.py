from common.overrides.monkey_patch.email_queue import patch_send_mail_context
from common.overrides.monkey_patch.api_handle import patch_api_handle
from common.overrides.monkey_patch.frappe_utils import patch_frappe_utils
from common.overrides.monkey_patch.notify_assignment import patch_notify_assignment
from common.overrides.monkey_patch.notify_mentions import patch_notify_mentions


def apply_patches():
    patch_send_mail_context()
    patch_api_handle()
    patch_frappe_utils()
    patch_notify_assignment()
    patch_notify_mentions()
