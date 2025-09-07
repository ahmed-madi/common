from frappe.utils import cint
import string


def validate_iban(iban):
    iban = iban.replace(" ", "").upper()
    if len(iban) < 15 or len(iban) > 34:
        return False

    rearranged_iban = iban[4:] + iban[:4]
    letters = {ch: str(10 + i) for i, ch in enumerate(string.ascii_uppercase)}

    converted_iban = ""
    for ch in rearranged_iban:
        if ch.isdigit():
            converted_iban += ch
        elif ch.isalpha():
            converted_iban += letters[ch]
        else:
            # Invalid character found
            return False

    iban_int = cint(converted_iban)
    return iban_int % 97 == 1
