// Workflow Timeline Integration
// Handles workflow action buttons in the form timeline

frappe.templates["workflow_state_card"] = `
    <div class="workflow-state-card journey-state-card {%= status %}-state" data-status="{%= status %}">
        <div class="state-card-body">
            <div class="state-card-left">
                <div class="state-info">
                    <div class="state-title {%= status %}-text">{%= state %}</div>
                    {% if (timestamp) { %}
                        <div class="state-timestamp text-muted small">{%= timestamp %}</div>
                    {% } %}
                </div>
            </div>
            {% if (users && users.length > 0) { %}
            <div class="state-card-right">
                <div class="journey-avatar-group">
                    {% for (let i=0; i < users.length; i++) { %}
                        <div class="journey-avatar journey-avatar-click" 
                             style="cursor: pointer;"
                             title="{%= users[i].full_name %}"
                             data-email="{%= users[i].email %}"
                             data-name="{%= users[i].full_name %}">
                            {% if (users[i].user_image) { %}
                                <img src="{%= users[i].user_image %}" alt="{%= users[i].abbr %}">
                            {% } else { %}
                                <span class="avatar-text">{%= users[i].abbr %}</span>
                            {% } %}
                        </div>
                    {% } %}
                </div>
            </div>
            {% } %}
        </div>
    </div>
`;

// Avatar Click -> Email Dialog
$(document).on("click", ".journey-avatar-click", function (e) {
    e.stopPropagation();
    const email = $(this).data("email");
    const name = $(this).data("name");

    if (email) {
        new frappe.views.CommunicationComposer({
            recipients: email,
            subject: __("Workflow Action Required"),
            doc: cur_frm.doc
        });
    } else {
        frappe.msgprint(__("No email address found for {0}", [name]));
    }
});

// Keep other templates for potential reference or separate sections, 
// but the main timeline will now use workflow_state_card.

// Function to apply status classes to timeline items
var refresh_workflow_styles = function () {
    $(".journey-state-card").each(function () {
        const $card = $(this);
        const status = $card.data("status");
        const $item = $card.closest(".timeline-item");
        if (status && !$item.hasClass(status + "-state")) {
            $item.addClass(status + "-state");
        }
    });
};

// Extend FormTimeline to handle workflow state card styling
$(document).on("render_timeline", function () {
    setTimeout(refresh_workflow_styles, 100);
});

// Also run once on page load and when form reloads
$(document).on("form_render", function () {
    setTimeout(refresh_workflow_styles, 500);
});

// Standard Workflow Action Btn handler
$(document).on("click", ".workflow-action-btn", function (e) {
    e.preventDefault();
    e.stopPropagation();

    const $btn = $(this);
    const action = $btn.data("action");
    const doctype = $btn.data("doctype");
    const docname = $btn.data("docname");

    if (!action || !doctype || !docname) {
        frappe.throw(__("Invalid workflow action data"));
        return;
    }

    // Disable button to prevent double-clicks
    $btn.prop("disabled", true);

    // Execute the workflow action
    frappe.xcall("frappe.model.workflow.apply_workflow", {
        doc: {
            doctype: doctype,
            name: docname
        },
        action: action
    }).then((updated_doc) => {
        frappe.show_alert({
            message: __("Workflow action applied successfully"),
            indicator: "green"
        });

        // Reload the form to show updated state
        if (cur_frm && cur_frm.doctype === doctype && cur_frm.docname === docname) {
            cur_frm.reload_doc();
        }
    }).catch((error) => {
        frappe.msgprint({
            title: __("Workflow Action Failed"),
            message: error.message || __("An error occurred while applying the workflow action"),
            indicator: "red"
        });

        // Re-enable button on error
        $btn.prop("disabled", false);
    });
});
