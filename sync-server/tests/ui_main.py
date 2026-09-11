"""The file NiceGUI's test harness runs to build the app.

It goes through the real entry point, so the UI tests exercise the same wiring
the server does; `runpy` gives this file no package, hence the absolute import.
"""

from blockurl.__main__ import launch_app

launch_app()
