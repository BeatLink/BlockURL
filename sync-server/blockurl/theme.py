"""The Halon theme, ported to Quasar and NiceGUI.

The token values come straight from Halon's design guide and must not be edited
here; only the rules that spend them belong in this file. Dark mode keys off
Quasar's own `body--dark` class, which Quasar sets for a manual toggle and for
the system preference alike.
"""

from nicegui import ui

# Tokens ---------------------------------------------------------------------------------------------------------------
TOKENS = '''
:root {
    /* Surfaces - a two-step ladder (recessed, raised), plus the frame's hover and the overlay */
    --surface-root:              #f1f5f9;
    --surface-default:           #ffffff;
    --surface-secondary:         #f1f5f9;  /* sidebars, the frame, footers, fills */
    --surface-navigation-hover:  #e2e8f0;
    --surface-overlay:           rgba(15, 23, 42, 0.45);

    /* Text on surfaces */
    --text-heading:              #0f172a;
    --text-body:                 #1a1a2e;
    --text-secondary:            #475569;
    --text-tertiary:             #64748b;
    --text-on-navigation:        #475569;

    /* Text on fills - one token per class of fill */
    --text-on-fill:              #fff;
    --text-on-light:             #0f172a;

    /* Lines */
    --border-default:            #e2e8f0;
    --border-hover:              #cbd5e1;
    --border-control:            #8792a3;

    /* Interaction */
    --accent:                    #2563eb;
    --focus-ring:                rgba(37, 99, 235, 0.15);

    /* Status */
    --status-success:            #047857;
    --status-warning:            #f59e0b;
    --status-warning-text:       #c2410c;
    --status-danger:             #dc2626;
    --badge-experimental:        #7c3aed;

    /* Elevation */
    --shadow-opacity:            0.15;
}

/* Tokens that derive from other tokens live here rather than on :root. A
   custom property resolves its var() against the element it is declared on,
   and the dark values arrive one level down, on the body. */
body {
    --surface-navigation: var(--surface-secondary);
    --border-focus:       var(--accent);

    /* Quasar's brand colours, pointed at the tokens so they follow the scheme */
    --q-primary:   var(--accent);
    --q-positive:  var(--status-success);
    --q-negative:  var(--status-danger);
    --q-warning:   var(--status-warning);
    --q-info:      var(--accent);
    --q-dark:      var(--surface-default);
    --q-dark-page: var(--surface-root);
}

body.body--dark {
    --surface-root:              #060b14;
    --surface-default:           #16213a;
    --surface-secondary:         #060b14;
    --surface-navigation-hover:  #101b2d;
    --surface-overlay:           rgba(0, 0, 0, 0.6);

    --text-heading:              #f8fafc;
    --text-body:                 #e2e8f0;
    --text-secondary:            #cbd5e1;
    --text-tertiary:             #94a3b8;
    --text-on-navigation:        #ffffff;

    --text-on-fill:              #0b1220;

    --border-default:            #334155;
    --border-hover:              #475569;
    --border-control:            #64748b;

    --accent:                    #60a5fa;
    --focus-ring:                rgba(96, 165, 250, 0.28);

    --status-success:            #10b981;
    --status-warning-text:       #f59e0b;
    --status-danger:             #f87171;
    --badge-experimental:        #a78bfa;

    --shadow-opacity:            0.5;
}

:root {
    --font-family-interface:
        system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        "Noto Sans", Cantarell, "Helvetica Neue", Arial, sans-serif,
        "Apple Color Emoji", "Segoe UI Emoji";

    /* Spacing - a 4px scale, and nothing may use a value that is off it */
    --space-1:  2px;
    --space-2:  4px;
    --space-3:  6px;
    --space-4:  8px;
    --space-5: 12px;
    --space-6: 16px;
    --space-7: 24px;
    --space-8: 32px;

    /* Geometry - one control height, so everything on a row lines up */
    --control-height:       32px;
    --control-padding-x:    14px;
    --icon-button-size:     30px;
    --row-height:           28px;
    --frame-height:         34px;
    --border-width:          1px;
    --focus-ring-width:      3px;

    /* Radii - proportional to what they round */
    --radius-small:    4px;
    --radius-row:      6px;
    --radius-default:  8px;
    --radius-window:  10px;
    --radius-pill:  9999px;

    /* Type scale */
    --text-label:    11px;
    --text-caption:  12px;
    --text-control:  13px;
    --text-body-size: 14px;
    --text-h3:       15px;
    --text-h2:       19px;
    --text-h1:       26px;

    --line-height-body: 1.55;
    --line-height-ui:   1.2;
    --measure:          68ch;

    /* Elevation - always slate-900 at low alpha, never neutral black */
    --shadow-item:     0 1px 2px rgba(15, 23, 42, 0.12);
    --shadow-card:     0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.06);
    --shadow-floating: 0 2px 8px rgba(15, 23, 42, 0.20);
    --shadow-modal:    0 8px 32px rgba(15, 23, 42, 0.25);
}
'''

# Components -------------------------------------------------------------------------------------------------------------
COMPONENTS = '''
/* Page ground and type ---------------------------------------------------------------------------- */
body, .q-page-container, body .nicegui-content {
    background: var(--surface-root);
    color: var(--text-body);
    font-family: var(--font-family-interface);
    font-size: var(--text-control);
    line-height: var(--line-height-ui);
}

body .nicegui-content { padding: 0; gap: 0; align-items: stretch; }

::selection { background: var(--focus-ring); }

h1, h2, h3 { color: var(--text-heading); font-weight: 600; letter-spacing: -0.01em; }
h1 { font-size: var(--text-h1); }
h2 { font-size: var(--text-h2); }
h3 { font-size: var(--text-h3); }

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Layout ------------------------------------------------------------------------------------------ */
.halon-page {
    width: 100%;
    max-width: 1120px;
    margin: 0 auto;
    padding: 28px var(--space-8);
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-7);
}

.halon-section {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    gap: var(--space-5);
}

.halon-section-label {
    font-size: var(--text-label);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-secondary);
}

.halon-row {
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    width: 100%;
    gap: var(--space-4);
    flex-wrap: wrap;
}

.halon-field {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-2);
    min-width: 0;
}
.halon-grow { flex: 1 1 220px; }

.halon-label {
    font-size: var(--text-control);
    font-weight: 500;
    color: var(--text-secondary);
    line-height: var(--line-height-ui);
}

.halon-hint { font-size: var(--text-caption); color: var(--text-tertiary); }

/* Frame - the recessed navigation chrome ---------------------------------------------------------- */
.q-header.halon-frame {
    background: var(--surface-navigation);
    color: var(--text-on-navigation);
    border-bottom: var(--border-width) solid var(--border-default);
    box-shadow: none;
    min-height: var(--frame-height);
    padding: var(--space-1) var(--space-4);
    gap: var(--space-4);
    align-items: center;
}

.halon-frame .q-btn { color: var(--text-on-navigation); }
.halon-frame .q-btn:hover { color: var(--text-heading); }

.halon-brand {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    font-size: var(--text-control);
    font-weight: 600;
    color: var(--text-heading);
}

.halon-brand::before {
    content: '';
    width: var(--space-4);
    height: var(--space-4);
    border-radius: var(--radius-pill);
    background: var(--accent);
    flex-shrink: 0;
}

/* Cards and panels -------------------------------------------------------------------------------- */
.q-card.halon-card {
    width: 100%;
    background: var(--surface-default);
    color: var(--text-body);
    border: var(--border-width) solid var(--border-default);
    border-radius: var(--radius-default);
    box-shadow: var(--shadow-card);
    padding: 14px var(--space-6);
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
}

/* Stat tiles -------------------------------------------------------------------------------------- */
.halon-stats { display: flex; flex-direction: row; width: 100%; gap: var(--space-8); flex-wrap: wrap; }

.halon-stat {
    flex: 0 1 auto;
    min-width: 160px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
}

.halon-stat-value {
    font-size: var(--text-h1);
    font-weight: 600;
    color: var(--text-heading);
    font-variant-numeric: tabular-nums;
    line-height: var(--line-height-ui);
}

.halon-stat-label {
    font-size: var(--text-label);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-secondary);
}

/* Buttons - three weights, and the accent is spent only on the top one ---------------------------- */
.q-btn.halon-btn {
    min-height: var(--control-height);
    height: var(--control-height);
    padding: var(--space-4) var(--control-padding-x);
    border-radius: var(--radius-default);
    border: var(--border-width) solid var(--border-default);
    background: transparent;
    color: var(--text-body);
    font-family: var(--font-family-interface);
    font-size: var(--text-control);
    font-weight: 500;
    line-height: 1;
    text-transform: none;
    letter-spacing: normal;
    box-shadow: none;
}

.q-btn.halon-btn .q-btn__content { gap: var(--space-2); }
.q-btn.halon-btn:hover { border-color: var(--accent); }
.q-btn.halon-btn .q-focus-helper { display: none; }
.q-btn.halon-btn[disabled], .q-btn.halon-btn.disabled { opacity: 0.5; }

.q-btn.halon-btn-flat {
    border-color: transparent;
    color: var(--text-secondary);
}
.q-btn.halon-btn-flat:hover { border-color: var(--border-default); color: var(--text-heading); }

.q-btn.halon-btn-filled {
    background: var(--accent);
    border-color: var(--accent);
    color: var(--text-on-fill);
}
.q-btn.halon-btn-filled:hover { opacity: 0.85; border-color: var(--accent); }

.q-btn.halon-btn-danger { color: var(--status-danger); }
.q-btn.halon-btn-danger:hover { border-color: var(--status-danger); color: var(--status-danger); }

.q-btn.halon-btn-danger-filled {
    background: var(--status-danger);
    border-color: var(--status-danger);
    color: var(--text-on-fill);
}
.q-btn.halon-btn-danger-filled:hover { opacity: 0.85; border-color: var(--status-danger); }

.q-btn.halon-icon-btn {
    width: var(--icon-button-size);
    height: var(--icon-button-size);
    min-height: var(--icon-button-size);
    padding: var(--space-3);
    border-radius: var(--radius-row);
}
.q-btn.halon-icon-btn .q-icon { font-size: 17px; }

.q-btn:focus-visible {
    outline: var(--focus-ring-width) solid var(--focus-ring);
    outline-offset: 0;
}

/* Inputs - the hairline at rest, the accent the moment you engage --------------------------------- */
.halon-input .q-field__control {
    min-height: var(--control-height);
    height: var(--control-height);
    padding: 0 11px;
    border-radius: var(--radius-default);
    background: var(--surface-default);
}

.halon-input .q-field__control:before {
    border: var(--border-width) solid var(--border-default);
    border-radius: var(--radius-default);
}

.halon-input .q-field__control:after { display: none; }
.halon-input:hover .q-field__control:before { border-color: var(--border-focus); }

.halon-input.q-field--focused .q-field__control:before {
    border-color: var(--border-focus);
    box-shadow: 0 0 0 var(--focus-ring-width) var(--focus-ring);
}

.halon-input .q-field__native,
.halon-input .q-field__input {
    font-family: var(--font-family-interface);
    font-size: var(--text-control);
    color: var(--text-body);
    padding: 0;
}

.halon-input .q-field__native::placeholder { color: var(--text-tertiary); opacity: 1; }
.halon-input .q-field__marginal { height: var(--control-height); color: var(--text-secondary); }
.halon-input .q-field__marginal .q-icon { font-size: 16px; }
.halon-input .q-field__append .q-btn { color: var(--text-secondary); }
.halon-input .q-field__append .q-btn:hover { color: var(--accent); }

/* Selects are an action affordance, so they are ghosted like a button ----------------------------- */
.halon-select .q-field__control { background: transparent; }
.halon-select .q-field__native { color: var(--accent); font-weight: 500; }
.halon-select .q-field__append .q-icon { color: var(--accent); }

.q-menu {
    background: var(--surface-default);
    color: var(--text-body);
    border: var(--border-width) solid var(--border-default);
    border-radius: var(--radius-default);
    box-shadow: var(--shadow-floating);
    padding: 5px;
}

.q-menu .q-item {
    min-height: var(--icon-button-size);
    padding: var(--space-3) 9px;
    border-radius: var(--radius-small);
    font-size: var(--text-control);
    color: var(--text-body);
}

.q-menu .q-item:hover { background: var(--surface-navigation-hover); }
.q-menu .q-item.q-manual-focusable--focused > .q-focus-helper { opacity: 0; }
.q-menu .q-item--active { background: var(--accent); color: var(--text-on-fill); }

/* Table ------------------------------------------------------------------------------------------- */
.q-table__container.halon-table {
    background: var(--surface-default);
    color: var(--text-body);
    border: var(--border-width) solid var(--border-default);
    border-radius: var(--radius-default);
    box-shadow: none;
}

.halon-table .q-table thead th {
    background: var(--surface-default);
    color: var(--text-secondary);
    font-size: var(--text-label);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 9px var(--space-5);
    border-bottom: var(--border-width) solid var(--border-default);
}

.halon-table .q-table tbody td {
    padding: 9px var(--space-5);
    font-size: var(--text-control);
    color: var(--text-body);
    border-bottom: var(--border-width) solid var(--border-default);
}

.halon-table .q-table tbody tr:last-child td { border-bottom: none; }
.halon-table .q-table tbody tr:hover > td { background: var(--surface-navigation-hover); }
.halon-table .q-table__bottom {
    border-top: var(--border-width) solid var(--border-default);
    color: var(--text-secondary);
    font-size: var(--text-caption);
    min-height: var(--frame-height);
    padding: 0 var(--space-5);
}

.halon-table .q-table__top { padding: 0; min-height: 0; }
.halon-table .q-table__sort-icon { color: var(--text-tertiary); }
.halon-table .q-table tbody td .halon-cell-url { color: var(--accent); }
.halon-table .q-table tbody td .halon-cell-muted { color: var(--text-tertiary); }
.halon-table .q-table__grid-content { color: var(--text-body); }
.halon-table .q-table__bottom .q-btn { color: var(--text-secondary); }

/* Badges - every solid fill takes the on-fill colour ---------------------------------------------- */
.halon-badge {
    display: inline-flex;
    align-items: center;
    padding: var(--space-1) var(--space-4);
    border-radius: var(--radius-pill);
    font-size: var(--text-label);
    font-weight: 600;
    background: var(--surface-secondary);
    color: var(--text-secondary);
}

/* Status regions are tinted, status fills are solid ----------------------------------------------- */
.halon-alert {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4) var(--space-5);
    border-radius: var(--radius-default);
    font-size: var(--text-control);
    color: var(--text-body);
    background: var(--surface-secondary);
}

.halon-alert .q-icon { font-size: 16px; color: var(--text-secondary); }
.halon-alert-success { background: color-mix(in srgb, var(--status-success) 15%, transparent); }
.halon-alert-success .q-icon { color: var(--status-success); }
.halon-alert-warning { background: color-mix(in srgb, var(--status-warning) 15%, transparent); }
.halon-alert-warning .q-icon { color: var(--status-warning-text); }
.halon-alert-danger { background: color-mix(in srgb, var(--status-danger) 15%, transparent); }
.halon-alert-danger .q-icon { color: var(--status-danger); }

/* Upload ------------------------------------------------------------------------------------------ */
.halon-upload {
    border: var(--border-width) dashed var(--border-hover);
    border-radius: var(--radius-default);
    background: var(--surface-default);
    box-shadow: none;
    width: 100%;
}

.halon-upload .q-uploader__header {
    background: transparent;
    color: var(--text-secondary);
    min-height: var(--frame-height);
}

.halon-upload .q-uploader__list { background: transparent; color: var(--text-body); min-height: 0; }

.halon-upload .q-uploader__header .q-btn {
    background: transparent;
    color: var(--text-secondary);
    border-radius: var(--radius-row);
}

.halon-upload .q-uploader__header .q-btn:hover { color: var(--accent); }
.halon-upload .q-uploader__title { font-size: var(--text-control); font-weight: 500; }

/* The byte counter says nothing useful here; the import status line reports the result. */
.halon-upload .q-uploader__subtitle { display: none; }

/* Dialogs and toasts ------------------------------------------------------------------------------ */
.q-dialog__backdrop { background: var(--surface-overlay); }

.halon-dialog {
    background: var(--surface-default);
    color: var(--text-body);
    border: var(--border-width) solid var(--border-default);
    border-radius: var(--radius-default);
    box-shadow: var(--shadow-modal);
    padding: var(--space-6);
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
    max-width: 420px;
}

.halon-dialog-title { font-size: var(--text-h3); font-weight: 600; color: var(--text-heading); }
.halon-dialog-body { font-size: var(--text-control); color: var(--text-body); word-break: break-all; }
.halon-dialog-actions { display: flex; justify-content: flex-end; gap: var(--space-4); }

.q-notification {
    background: var(--surface-navigation);
    color: var(--text-heading);
    border: var(--border-width) solid var(--border-default);
    border-radius: var(--radius-default);
    box-shadow: var(--shadow-floating);
    font-size: var(--text-control);
}

.q-tooltip {
    background: var(--surface-navigation);
    color: var(--text-heading);
    border: var(--border-width) solid var(--border-default);
    border-radius: var(--radius-row);
    box-shadow: var(--shadow-floating);
    font-size: var(--text-caption);
}

/* Scrollbars -------------------------------------------------------------------------------------- */
* { scrollbar-color: var(--border-hover) transparent; scrollbar-width: thin; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--border-hover);
    border: 3px solid transparent;
    background-clip: padding-box;
    border-radius: var(--radius-pill);
}
::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); background-clip: padding-box; }

/* Login ------------------------------------------------------------------------------------------- */
.halon-login {
    width: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-6);
}

.halon-login-card { width: 100%; max-width: 360px; }
'''


def apply_theme() -> None:
    """Put the Halon tokens and component rules on the current page."""
    ui.add_css(TOKENS + COMPONENTS)
