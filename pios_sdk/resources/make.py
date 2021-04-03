from denverapi.autopyb import *

from pios_sdk import ppk

auto = BuildTasks()


@auto.task()
def build():
    """Build the app with all of the dependencies resolved"""
    app = ppk.PPK()
    app.load_using_toml()
    app.build()


@auto.task()
def package():
    """Package the app after it has been built, (Calling 'build' before this is necessary)"""
    ppk.PPK.package()


@auto.task()
def clean():
    ppk.main(["--cleanup"])


auto.interact()
