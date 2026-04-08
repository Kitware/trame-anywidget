import json
import shutil
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()
WWW_CONF = json.loads(Path(__file__).with_name("www.json").read_text())

nox.needs_version = ">=2024.3.2"
nox.options.default_venv_backend = "uv|virtualenv"


@nox.session
def www(session: nox.Session) -> None:
    session.install("trame")
    for module, packages in WWW_CONF.items():
        for pkg in packages:
            session.install(pkg)
            session.run("python", "-m", "trame.tools.www", "--output", "./www", module)


@nox.session
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """

    build_path = DIR.joinpath("build")
    if build_path.exists():
        shutil.rmtree(build_path)

    session.install("build")
    session.run("python", "-m", "build")
