# Change Log — Version 16 Migration

Brings the `common` app onto **Frappe v16**, **ERPNext v16**, **HRMS v16** and **Lending v16**
(audited against frappe 16.53, erpnext 16.52, hrms 16.52 and lending `version-16`).
Everything below targets the `version-16` branch; v15 sites should stay on `main`.

## Breaking issues fixed

| Area | Problem on v16 | Fix |
| --- | --- | --- |
| `overrides/notification.py` | v16 calls `Notification.create_system_notification(doc, context, template_content)`. The override only took two arguments, so every System Notification raised and was swallowed ("Failed to send Notification"). | Accepts `template_content`; ports v16 behaviour (Email Template content, `notification_type`, `app`, `title`, `restrict_globals` rendering). Keeps push notifications, `base_*` fields and the single-attachment payload. |
| `custom/loan_application.json` | Lending v16 added a standard `loan_purpose` field (Link → Loan Purpose) and removed `description`. The custom `loan_purpose` (Small Text) duplicates it, so `bench migrate` fails with *Fieldname loan_purpose appears multiple times*. | Custom field removed; `field_order` no longer lists `description`. New `pre_model_sync` patch `common.patches.v16.move_loan_purpose_to_remarks` copies existing purpose text into `remarks`, clears the column and deletes the old Custom Field before Lending syncs its schema. |
| Query fields | v16's query engine rejects SQL functions written as strings (`"sum(total_days) as sum"`, `"count(name) as cnt"`) and backticked `order_by` names. | Switched to dict syntax `{"SUM": "total_days", "as": "sum"}` / `{"COUNT": "name", "as": "cnt"}` in Remote Work, Work Outside Office, Work From Home, Leave Permission and the company org chart. Salary Identification Letter now orders by `default desc`. |
| `overrides/energy_point_log.py` | Energy Point Log was removed from Frappe v16; the file failed to import. It wasn't hooked anywhere. | Deleted. |
| Desk icons | v16 no longer loads FontAwesome, so `fa fa-*` icons rendered blank. | Employee attendance header, HR Request Tracking and Attendance Viewer pages now use `frappe.utils.icon(...)` (lucide set shipped with v16). |

## Monkey patches

- **API routes** (`monkey_patch/api_handle.py`): no longer replaces `frappe.api.handle`. Only `frappe.api.API_URL_MAP` is rebuilt with the app's routes, so v16's API request logging and app monitoring keep working. The patch is guarded against applying twice.
- **Failed-email notification** (`monkey_patch/email_queue.py`): now patches `SendMailContext` in `frappe.email.doctype.email_queue.email_queue`, where `EmailQueue.send()` actually uses it. The old target (`frappe.email.queue`) never referenced it, so the patch had no effect. `base_variables` is built with `json.dumps`.
- **`get_link_to_form` / `bold`** (`monkey_patch/frappe_utils.py`): matches v16's signature (`name` optional, label falls back to the doctype). Also patches `frappe.utils.data.bold` / `frappe.utils.bold`, where v16 defines `bold`.
- **Half-day holidays** (`monkey_patch/v16/holiday_list.py`): removed. `is_half_holiday` and `Holiday.is_half_day` ship natively in ERPNext v16 and the backport was identical.

## Overrides and hooks

- `override_doctype_class` → **`extend_doctype_class`** (the v16 hook). Classes are unchanged and still subclass the standard controller, so method resolution is identical. Frappe now layers them on top of the controller instead of replacing it, so another app's override of the same doctype keeps working.
- `overrides/whitelisted/user.py` (impersonate): uses v16's `User` *impersonate* permission instead of Administrator-only. Sends v16's security-alert email. Keeps the translatable `base_*` notification fields.
- `overrides/submission_queue.py`: realtime link points to `/desk/...` (v16 moved the desk from `/app`).
- `hooks.py`: `required_apps = ["frappe/erpnext", "frappe/hrms"]`.

## Data and API behaviour

- **Task dates**: ERPNext v16 made `exp_start_date` / `exp_end_date` *Datetime*. The REST date filter (`f_date` / `t_date`) now treats Task as a datetime field and covers whole days. Also fixed the datetime filter string, which raised a `TypeError` (`date + str`) and was silently dropped for Company Newsletter, Event and Employee Checkin.
- **Links**: `/app/...` → `/desk/...` in Overtime Pay Request's message and in the Employee Tasks and Employee Attendance workspace shortcuts.

## Desk JavaScript

- `public/js/attendance_list.js`: rebuilt on HRMS v16's list settings. Adds the *create*-permission check on **Mark Attendance**, v16 date handling and the server-side employee access check. Keeps the app's *Work Outside Office* status and the "up to yesterday" date limits.
- `end_of_service_award.js`: `cur_frm.add_fetch` at load time (`cur_frm` is null then, which stopped the whole script registering) moved to `setup(frm)`.
- `allowance_request.js`: fixed the `has_jv_entries` method path (`common.common_customization...`).
- Remote Work / Work From Home / Work Outside Office forms: `diffInDays` declared with `let` (reassigning a `const` threw when the limit was exceeded).
- `public/js/project.js`: undefined `installedApps` replaced with the fetched app list.

## App structure (v16 conventions)

- `pyproject.toml`: `requires-python = ">=3.14"` (Frappe v16 runs on Python 3.14). Adds `[tool.bench.frappe-dependencies]` pinning frappe / erpnext / hrms `>=16,<17`, plus the `[deploy.dependencies.apt]` section.
- Tests: `frappe.tests.utils.FrappeTestCase` (deprecated in v16) → `frappe.tests.IntegrationTestCase`.
- Patches: v16 patches live in `common/patches/v16/`.

## Verification

- Static checks on every Python module against the v16 sources: imports, dotted hook paths, upstream signatures, query fields / `order_by`, custom fields vs. standard fields, workspace links, and doctypes or fields removed upstream.
- All app modules imported on Python 3.14 with frappe / erpnext / hrms / lending v16 installed. Every hook path resolves, the `extend_doctype_class` MRO builds, the API map contains the app's routes, and the monkey patches apply.
- Not run: `bench migrate` and the test suite on a live v16 site. Run both on staging before production.

## Known items not changed (worth a follow-up)

- `loan_purpose` is now a Link to **Loan Purpose** and is optional. Create Loan Purpose records, and mark the field mandatory with a Property Setter if the old rule should stay. API clients that sent free text in `loan_purpose` must send a Loan Purpose name.
- Broken on v15 too, left untouched:
  - `form_timeline_workflow.js` listens to events Frappe never triggers, and the `data-template` CSS selectors never match.
  - `overtime_pay_request.js` sets `fields_dict.<x>.onchange`, which Frappe never calls, and calls a module-level function with `doc:`.
- The `Helpdesk` module folder isn't in `modules.txt`, so its workspace never syncs. The Employee Attendance workspace references the **Attendance Count v2** chart, which isn't shipped with the app.
- Not authored yet: per-module sidebars (`<module>/sidebar/`) and a dock (`dock/common/common.json`). v16 falls back to generated sidebars. To curate them, author in the UI on a developer-mode site and use *Export to App*.
- `.addClass("btn-primary")` on custom form buttons may not show as primary under v16's button styles. If so, use `frm.change_custom_button_type(label, null, "primary")`.
