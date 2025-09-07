# Copyright (c) 2025, Ahmed Madi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_files_path
from frappe.utils.file_manager import delete_file

from PIL import Image, ImageDraw


class FestiveGreetingCardRequest(Document):
    def validate(self):
        self.build_festive_card()

    def on_submit(self):
        self.build_festive_card(final_version=True)

    def delete_all_versions(self):
        filters = {
            "attached_to_doctype": "Festive Greeting Card Request",
            "attached_to_name": self.name,
            "attached_to_field": "request_festive_image",
            "file_url": ["!=", self.request_festive_image],
        }
        files = frappe.get_all(
            "File",
            filters=filters,
            fields=["name", "file_type", "file_name", "file_url"],
            limit_page_length=999999,
        )
        for file in files:
            frappe.get_doc("File", file.name).delete()
        frappe.db.commit()

        del filters["file_url"]
        files = frappe.get_all(
            "File",
            filters=filters,
            fields=["name", "file_type", "file_name", "file_url"],
        )
        if len(files) <= 1:
            return
        for file in files[1:]:
            frappe.get_doc("File", file.name).delete()
        frappe.db.commit()

    def build_festive_card(self, final_version=False):
        if self.origin_festive_image and self.festive_greeting:
            text = f"{self.festive_greeting_for}\n{self.person_name}"
            filters = {
                "attached_to_doctype": "Festive Greeting Card",
                "attached_to_name": self.festive_greeting,
                "attached_to_field": "festive_image",
                "file_url": self.origin_festive_image,
            }
            file = frappe.db.get_value("File", filters, ["name"])

            if file is None:
                return

            # open origin image
            file = frappe.get_doc("File", filters)
            full_path = file.get_full_path()
            img = Image.open(full_path)

            image_draw = ImageDraw.Draw(img)
            image_draw.text(
                (self.position_left, self.position_top),
                text,
                fill=self.font_color,
                align="center",
                # language="ar",
                font_size=self.font_size,
            )

            # save a copy
            filename = f"{self.name}.{file.file_type}"
            full_path = get_files_path()
            path_to_save = f"{full_path}/{filename}"
            delete_file(path_to_save)
            img.save(path_to_save)

            # add to system
            doc_dict = {
                "doctype": "File",
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "attached_to_field": "request_festive_image",
                "folder": "Festive Greeting Cards",
                "file_name": filename,
                "is_private": 0,
                "file_url": f"/files/{filename}",
            }
            file = frappe.get_doc(doc_dict)
            file.flags.ignore_links = True
            file.flags.ignore_validate = True
            file.save(ignore_permissions=True)

            if final_version:
                self.db_set(
                    "request_festive_image", file.file_url, update_modified=False
                )
                # at some points it will be long proccess!
                # delete all old version on_submit
                frappe.enqueue(self.delete_all_versions, queue="long")
            else:
                self.request_festive_image = file.file_url
