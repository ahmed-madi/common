# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

from common.models.base_hr_document import BaseHRDocument


class ClearanceLetterRequest(BaseHRDocument):
    def on_submit(self):
        if self.status != "Approved":
            return
        self.prepare_clearance_document()

    def prepare_clearance_document(self):
        pass
