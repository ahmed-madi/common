// Copyright (c) 2026, Ahmed Madi and contributors
// For license information, please see license.txt

// The help lists what a formula may actually reference. It is built on the
// server from the evaluation context and from the End of Service Award's meta,
// so a new field or variable shows up here on its own.
let formula_help = null;

function escape_html(value) {
  return frappe.utils.escape_html(String(value == null ? "" : value));
}

function rows(items, render) {
  return items.map(render).join("");
}

function render_formula_help(help) {
  const variables = rows(
    help.variables,
    (v) =>
      `<tr><td><code>${escape_html(v.name)}</code></td><td>${escape_html(
        v.description
      )}</td></tr>`
  );

  const helpers = help.helpers
    .map((name) => `<code>${escape_html(name)}</code>`)
    .join(", ");

  const doc_fields = rows(
    help.doc_fields,
    (f) =>
      `<tr><td><code>doc.${escape_html(f.fieldname)}</code></td><td>${escape_html(
        f.label
      )}</td><td>${escape_html(f.fieldtype)}</td></tr>`
  );

  return `
    <p>${__(
      "The condition and the formula are each a single Python expression, evaluated against the End of Service Award. The condition is optional; when it is false the award is zero and the formula is never evaluated, so the formula can be written as if the condition always holds."
    )}</p>
    <pre>${__("Condition")}:  years &gt;= 2
${__("Formula")}:    (1 / 6) * salary * years</pre>

    <h5>${__("Variables")}</h5>
    <table class="table table-bordered table-sm">
      <thead><tr><th>${__("Variable")}</th><th>${__(
        "Meaning"
      )}</th></tr></thead>
      <tbody>${variables}</tbody>
    </table>

    <h5>${__("Functions")}</h5>
    <p>${helpers}</p>

    <h5>${__("End of Service Award fields")}</h5>
    <p class="text-muted">${__(
      "Every field below is available on <code>doc</code>. A field is only filled in if the award itself has a value for it."
    )}</p>
    <table class="table table-bordered table-sm">
      <thead><tr><th>${__("Variable")}</th><th>${__("Label")}</th><th>${__(
        "Type"
      )}</th></tr></thead>
      <tbody>${doc_fields}</tbody>
    </table>
  `;
}

frappe.ui.form.on("End of Service Award Reason", {
  async refresh(frm) {
    if (!formula_help) {
      const { message } = await frappe.call({
        method:
          "common.common_customization.doctype.end_of_service_award_reason.end_of_service_award_reason.get_formula_help",
      });
      if (!message) {
        return;
      }
      formula_help = message;
    }

    frm.get_field("formula_help").$wrapper.html(
      render_formula_help(formula_help)
    );
  },
});
