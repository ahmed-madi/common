# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

from common.common_customization.doctype.salary_identification_letter import letter
from common.models.base_hr_document import BaseHRDocument


class SalaryIdentificationLetter(BaseHRDocument):
    def before_validate(self):
        if not self.request_date:
            self.request_date = getdate()

    def on_submit(self):
        self.send_letter_to_employee()

    def on_update_after_submit(self):
        # A workflow can carry the request to Approved after it has been
        # submitted, so submit alone is not the only moment it is approved.
        self.send_letter_to_employee()

    def send_letter_to_employee(self):
        """Email the approved letter, once, in the background.

        Queued after commit so that a failure to render or send can never roll
        back the approval itself - the approval is the decision, the letter is
        a consequence of it.
        """
        if self.status != "Approved" or self.letter_sent_on:
            return

        if not self.policy_value("auto_send_sidl"):
            return

        frappe.enqueue(
            letter.send_letter,
            queue="short",
            enqueue_after_commit=True,
            name=self.name,
        )
