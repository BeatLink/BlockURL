"""The dashboard: metrics, blocked-page settings, import and export, and the URL list."""

from datetime import datetime, timezone

from nicegui import app, run, ui

from . import theme
from .database import in_connection

IMPORT_BATCH_SIZE = 5000

SETTING_FIELDS = [
    ('blocked_page_heading_text', 'Heading Text', 'Blocked'),
    ('blocked_page_body_text', 'Body Text', 'This Page has been blocked by BlockURL'),
    ('blocked_page_button_text', 'Button Text', 'Unblock'),
]

ALERT_ICONS = {
    'info': 'info_outline',
    'success': 'check_circle_outline',
    'danger': 'error_outline',
}

# The browser knows the reader's time zone and the server does not, so the
# timestamp is sent as UTC and turned into a local date on the client.
CREATED_AT_CELL = '''
    <q-td :props="props">
        <span class="halon-cell-muted">{{ new Date(props.value).toLocaleString() }}</span>
    </q-td>
'''

URL_CELL = '''
    <q-td :props="props">
        <a class="halon-cell-url" :href="props.value" target="_blank" rel="noreferrer">{{ props.value }}</a>
    </q-td>
'''

UNBLOCK_CELL = '''
    <q-td :props="props" class="text-right">
        <q-btn dense flat icon="delete_outline"
               class="halon-btn halon-btn-flat halon-icon-btn halon-btn-danger"
               @click="() => $parent.$emit('unblock', props.row)" />
    </q-td>
'''


async def _db(call, *args, **kwargs):
    """Run a database call on a worker thread, off the event loop."""
    return await run.io_bound(in_connection, call, *args, **kwargs)


def _format_count(value):
    return f'{value:,}' if isinstance(value, int) else '0'


def _as_utc_iso(stamp):
    """Normalise a stored timestamp so the browser parses it as UTC."""
    try:
        moment = datetime.fromisoformat(stamp)
    except (TypeError, ValueError):
        return stamp
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat()


def _field(label_text):
    """A field column with its label above it, because a bare input is invisible."""
    column = ui.column().classes('halon-field halon-grow')
    with column:
        ui.label(label_text).classes('halon-label')
    return column


def _stat(label_text):
    with ui.column().classes('halon-stat'):
        value = ui.label('-').classes('halon-stat-value')
        ui.label(label_text).classes('halon-stat-label')
    return value


def _theme_toggle(remember):
    """A button cycling the page between the system theme, light and dark."""
    modes = [None, False, True]
    looks = {
        None: ('brightness_auto', 'Theme: follow system'),
        False: ('light_mode', 'Theme: light'),
        True: ('dark_mode', 'Theme: dark'),
    }
    start = app.storage.user.get('dark_mode') if remember else None
    dark = ui.dark_mode(start if start in modes else None)
    button = ui.button(color=None).classes('halon-btn halon-btn-flat halon-icon-btn')
    with button:
        tooltip = ui.tooltip('')

    def show():
        icon, text = looks[dark.value]
        button.props(f'icon={icon}')
        tooltip.set_text(text)

    def cycle():
        dark.value = modes[(modes.index(dark.value) + 1) % len(modes)]
        if remember:
            app.storage.user['dark_mode'] = dark.value
        show()

    button.on_click(cycle)
    show()


def register_pages(database, api_key):
    """Attach the dashboard to the NiceGUI app."""

    @ui.page('/')
    async def dashboard():
        theme.apply_theme()

        # Frame ---------------------------------------------------------------------------------------------------
        with ui.header().classes('halon-frame'):
            ui.label('BlockURL').classes('halon-brand')
            ui.space()
            _theme_toggle(remember=bool(api_key))
            if api_key:
                ui.button('Sign out', color=None, on_click=lambda: ui.navigate.to('/logout')) \
                    .classes('halon-btn halon-btn-flat')

        unblock_url = None
        with ui.dialog() as unblock_dialog, ui.column().classes('halon-dialog'):
            ui.label('Unblock this URL?').classes('halon-dialog-title')
            unblock_label = ui.label('').classes('halon-dialog-body')
            with ui.row().classes('halon-dialog-actions'):
                ui.button('Cancel', color=None, on_click=unblock_dialog.close) \
                    .classes('halon-btn halon-btn-flat')
                ui.button('Unblock', color=None, on_click=lambda: unblock()) \
                    .classes('halon-btn halon-btn-danger-filled').mark('confirm-unblock')

        with ui.column().classes('halon-page'):

            # Overview --------------------------------------------------------------------------------------------
            with ui.column().classes('halon-section'):
                ui.label('Overview').classes('halon-section-label')
                with ui.card().classes('halon-card'):
                    with ui.row().classes('halon-stats'):
                        total_urls = _stat('Blocked URLs')
                        unique_domains = _stat('Unique Domains')

            # Blocked page settings -------------------------------------------------------------------------------
            with ui.column().classes('halon-section'):
                ui.label('Blocked Page Settings').classes('halon-section-label')
                with ui.card().classes('halon-card'):
                    setting_inputs = {}
                    with ui.row().classes('halon-row'):
                        for key, label_text, placeholder in SETTING_FIELDS:
                            with _field(label_text):
                                setting_inputs[key] = ui.input(placeholder=placeholder) \
                                    .props('outlined dense').classes('halon-input w-full').mark(key)
                    with ui.row().classes('halon-row'):
                        ui.button('Save Settings', color=None, on_click=lambda: save_settings()) \
                            .classes('halon-btn halon-btn-filled').mark('save-settings')

            # Import and export -----------------------------------------------------------------------------------
            with ui.column().classes('halon-section'):
                ui.label('Import & Export').classes('halon-section-label')
                with ui.card().classes('halon-card'):
                    ui.label('Import a .txt or .csv file with one URL per line.').classes('halon-hint')
                    upload = ui.upload(label='Choose a file', auto_upload=True,
                                       on_upload=lambda e: import_file(e)) \
                        .props('accept=".csv,.txt,text/csv,text/plain" flat') \
                        .classes('halon-upload')
                    import_status = ui.row().classes('halon-alert')
                    with import_status:
                        import_icon = ui.icon(ALERT_ICONS['info'])
                        import_message = ui.label('')
                    import_status.set_visibility(False)
                    with ui.row().classes('halon-row'):
                        ui.button('Export URLs', icon='download', color=None, on_click=lambda: export_urls()) \
                            .classes('halon-btn').mark('export-urls')

            # URL list --------------------------------------------------------------------------------------------
            with ui.column().classes('halon-section'):
                ui.label('Blocked URLs').classes('halon-section-label')
                with ui.card().classes('halon-card'):
                    with ui.row().classes('halon-row'):
                        with _field('Add URL'):
                            add_entry = ui.input(placeholder='https://example.com/page') \
                                .props('outlined dense').classes('halon-input w-full').mark('add-url')
                            add_entry.on('keydown.enter', lambda: add_url())
                        ui.button('Add URL', color=None, on_click=lambda: add_url()) \
                            .classes('halon-btn halon-btn-filled').mark('add-url-button')

                    with ui.row().classes('halon-row'):
                        with _field('Search'):
                            search = ui.input(placeholder='Filter by URL or domain') \
                                .props('outlined dense').classes('halon-input w-full').mark('search')
                        with _field('Domain'):
                            domain_filter = ui.select({None: 'All domains'}, value=None) \
                                .props('outlined dense options-dense') \
                                .classes('halon-input halon-select w-full').mark('domain-filter')

                    table = ui.table(
                        rows=[],
                        columns=[
                            {'name': 'url', 'label': 'URL', 'field': 'url', 'sortable': True, 'align': 'left'},
                            {'name': 'domain', 'label': 'Domain', 'field': 'domain',
                             'sortable': True, 'align': 'left'},
                            {'name': 'created_at', 'label': 'Added', 'field': 'created_at',
                             'sortable': True, 'align': 'left'},
                            {'name': 'actions', 'label': '', 'field': 'url', 'sortable': False, 'align': 'right'},
                        ],
                        row_key='url',
                        pagination={'rowsPerPage': 50, 'sortBy': 'created_at', 'descending': True},
                    ).classes('halon-table w-full')
                    table.props('flat :rows-per-page-options="[25, 50, 100, 250]" '
                                'no-data-label="No URLs blocked yet"')
                    table.add_slot('body-cell-url', URL_CELL)
                    table.add_slot('body-cell-created_at', CREATED_AT_CELL)
                    table.add_slot('body-cell-actions', UNBLOCK_CELL)
                    table.bind_filter_from(search, 'value', backward=lambda value: value or '')
                    table.on('unblock', lambda e: confirm_unblock(e.args['url']))

        # Behaviour -----------------------------------------------------------------------------------------------
        def show_import_status(message, kind='info'):
            import_status.classes(replace='halon-alert' if kind == 'info' else f'halon-alert halon-alert-{kind}')
            import_icon.props(f'name={ALERT_ICONS[kind]}')
            import_message.set_text(message)
            import_status.set_visibility(True)

        async def load_metrics():
            stats = await _db(database.get_stats)
            total_urls.set_text(_format_count(stats['total_urls']))
            unique_domains.set_text(_format_count(stats['unique_domains']))

        async def load_domains():
            domains = await _db(database.get_domains_with_counts)
            options = {None: 'All domains'}
            options.update({name: f'{name} ({count:,})' for name, count in domains if name})
            chosen = domain_filter.value if domain_filter.value in options else None
            domain_filter.set_options(options, value=chosen)

        async def load_urls():
            rows = await _db(database.get_urls_sorted, order_by='created_at',
                             descending=True, domain=domain_filter.value)
            table.rows = [
                {'url': url, 'domain': domain or '', 'created_at': _as_utc_iso(created_at)}
                for url, domain, created_at in rows
            ]
            table.update()

        async def load_settings():
            values = dict(await _db(database.get_all_settings))
            for key, _, _ in SETTING_FIELDS:
                setting_inputs[key].value = values.get(key, '')

        async def save_settings():
            for key, _, _ in SETTING_FIELDS:
                await _db(database.set_setting, key, setting_inputs[key].value or '')
            ui.notify('Settings saved')

        async def add_url():
            url = (add_entry.value or '').strip().rstrip('/')
            if not url:
                ui.notify('Enter a URL first')
                return
            result = await _db(database.set_urls, [url])
            add_entry.value = ''
            ui.notify('URL blocked' if result['added'] else 'Already blocked')
            await refresh()

        def confirm_unblock(url):
            nonlocal unblock_url
            unblock_url = url
            unblock_label.set_text(url)
            unblock_dialog.open()

        async def unblock():
            unblock_dialog.close()
            await _db(database.delete_urls, [unblock_url])
            ui.notify('URL unblocked')
            await refresh()

        async def export_urls():
            rows = await _db(database.get_urls_sorted, order_by='created_at', descending=True, domain=None)
            ui.download.content('\n'.join(url for url, _, _ in rows), 'urls.txt', 'text/plain')

        async def import_file(event):
            name = event.file.name
            show_import_status(f'Importing {name}...')
            text = await event.file.text()
            upload.reset()
            urls = [line.strip().rstrip('/') for line in text.splitlines()]
            urls = [url for url in urls if url]
            if not urls:
                show_import_status(f'{name} contains no URLs.', 'danger')
                return
            totals = {'received': 0, 'added': 0, 'merged': 0}
            for start in range(0, len(urls), IMPORT_BATCH_SIZE):
                result = await _db(database.set_urls, urls[start:start + IMPORT_BATCH_SIZE])
                for key in totals:
                    totals[key] += result[key]
            show_import_status(
                f'Imported {_format_count(totals["received"])} URLs from {name}: '
                f'{_format_count(totals["added"])} added, {_format_count(totals["merged"])} '
                'merged (already blocked or repeated).',
                'success',
            )
            await refresh()

        async def refresh():
            await load_metrics()
            await load_domains()
            await load_urls()

        domain_filter.on_value_change(lambda: load_urls())

        await load_settings()
        await refresh()
