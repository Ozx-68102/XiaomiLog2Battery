import zoneinfo

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx, no_update
from dash.development.base_component import Component

dash.register_page(__name__, path="/settings", order=99, name="Settings")

TIMEZONE_LIST = sorted(list(zoneinfo.available_timezones()))
TZ_OPTIONS = [{"label": tz, "value": tz} for tz in TIMEZONE_LIST]


def get_store() -> list[dcc.Store]:
    return [
        dcc.Store(id="settings-browser-timezone"),
        dcc.Store(id="settings-backup-store"),
    ]


def layout() -> list[Component]:
    return [
        *get_store(),
        dbc.Card([
            dbc.CardHeader(html.H5("System Preferences", className="m-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Timezone", className="fw-bold"),
                        dcc.Dropdown(
                            id="settings-timezone-dropdown",
                            options=TIMEZONE_LIST,
                            placeholder="Detecting local timezone...",
                            disabled=True,
                            searchable=True,
                            clearable=False,
                        ),
                    ], width=12),
                ], class_name="g-3"),
                html.Br(),
                dbc.Col([
                    html.Div([
                        dbc.Button(
                            [html.I(className="bi bi-x-circle me-2"), "Cancel"],
                            id="settings-cancel-btn",
                            color="secondary",
                            outline=True,
                            n_clicks=0,
                            style={"display": "none"},
                        ),
                        dbc.Button(
                            [html.I(className="bi bi-pencil-square me-2"), "Edit"],
                            id="settings-action-btn",
                            color="primary",
                            outline=True,
                            n_clicks=0,
                        ),
                    ], className="d-flex justify-content-end gap-2"),
                ], width=12),
            ], class_name="g-3"),
            html.Br(),
            dbc.Alert(
                id="settings-alert",
                is_open=False,
                dismissable=True,
                color=None,
                fade=True,
                class_name="m-3 mb-0"
            ),
        ], class_name="shadow-sm"),
    ]

dash.clientside_callback(
    "(trigger) => Intl.DateTimeFormat().resolvedOptions().timeZone;",
    Output("settings-browser-timezone", "data"),
    Input("settings-timezone-dropdown", "id"),
)

dash.clientside_callback(
    """
    (n_clicks) => {
        if (!n_clicks) return window.dash_clientside.no_update;
        
        const btn = document.getElementById('settings-action-btn');
        if (!btn) return window.dash_clientside.no_update;
        
        btn.disabled = true;
        
        setTimeout(() => {
            btn.disabled = false;
        }, 2000);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("settings-action-btn", "id"),
    Input("settings-action-btn", "n_clicks"),
)


@dash.callback(
    [
        Output("settings-timezone-dropdown", "options"),
        Output("settings-timezone-dropdown", "value"),
    ],
    [
        Input("settings-browser-timezone", "data"),
        Input("global-timezone", "data"),
    ]
)
def init_dropdown(browser_tz: str, saved_tz: str) -> tuple[list[dict[str, str | bool]], str]:
    top_tz = ["UTC"]
    if browser_tz and browser_tz in TIMEZONE_LIST and browser_tz != "UTC":
        top_tz.insert(0, browser_tz)

    final_options = [{"label": "Recommended", "value": "disabled", "disabled": True}]
    final_options.extend([{"label": tz, "value": tz} for tz in top_tz])
    final_options.append({"label": "-" * 15, "value": "disabled", "disabled": True})
    final_options.extend([opt for opt in TZ_OPTIONS if opt["value"] not in top_tz])

    if saved_tz:
        current_tz = saved_tz
    elif browser_tz:
        current_tz = browser_tz
    else:
        current_tz = "UTC"

    return final_options, current_tz


@dash.callback(
    [
        # Dropdown status
        Output("settings-timezone-dropdown", "disabled"),
        Output("settings-timezone-dropdown", "value", allow_duplicate=True),

        # Save or Edit Button status
        Output("settings-action-btn", "children"),
        Output("settings-action-btn", "color"),
        Output("settings-action-btn", "outline"),

        # Cancel Button status
        Output("settings-cancel-btn", "style"),

        # backup/save timezone
        Output("settings-backup-store", "data"),
        Output("global-timezone", "data"),

        # Alert status
        Output("settings-alert", "is_open"),
        Output("settings-alert", "children"),
        Output("settings-alert", "color"),
    ],
    [
        Input("settings-action-btn", "n_clicks"),
        Input("settings-cancel-btn", "n_clicks"),
    ],
    [
        State("settings-timezone-dropdown", "value"),
        State("settings-action-btn", "children"),
        State("settings-backup-store", "data"),
    ],
    prevent_initial_call=True
)
def toggle_action(
        _1, _2,
        current_val: str,
        action_children: list[Component | str],
        backup_val: str
) -> tuple[
    bool, str, list[Component | str], str, bool, dict[str, str], str | None, str, bool, str, str
]:
    current_mode = "Edit" if "Edit" in str(action_children) else "Save"

    triggered = ctx.triggered_id
    if triggered == "settings-cancel-btn":
        return (
            True, backup_val,

            [html.I(className="bi bi-pencil-square me-2"), "Edit"], "primary", True,

            {"display": "none"},

            no_update, no_update,

            False, no_update, no_update,
        )

    if triggered == "settings-action-btn":
        if current_mode == "Edit":
            return (
                False, no_update,

                [html.I(className="bi bi-check-lg me-2"), "Save"], "success", False,

                {"display": "block"},

                current_val, no_update,

                False, no_update, no_update
            )

        if not current_val or current_val == "disabled":
            return (no_update, ) * 11

        return (
            True, current_val,

            [html.I(className="bi bi-pencil-square me-2"), "Edit"], "primary", True,

            {"display": "none"},

            None, current_val,

            True, f"Saved successfully.", "success"
        )

    return (no_update, ) * 11
