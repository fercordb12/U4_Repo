"""simular_colab.py — ejecuta un cuaderno como si estuviera en Google Colab.

Monta un "MyDrive" falso en un directorio temporal, inyecta ``google.colab``
y ``google.auth`` falsos, y ejecuta las celdas del cuaderno desde un cwd que
NO es el repositorio (igual que ``/content`` en Colab). Así se reproduce el
flujo real sin subir nada a Drive ni gastar unidades de Colab.

Uso::

    python tools/simular_colab.py                       # copia de trabajo
    python tools/simular_colab.py --ref HEAD             # lo que ve el alumno
    python tools/simular_colab.py --backend local        # Apps Script falso

``--ref`` toma el cuaderno y el repositorio de un commit de git (por defecto
usa la copia de trabajo, con tus cambios sin commitear). ``--backend local``
levanta un Apps Script falso en localhost y redirige ahí el envío, para probar
el camino completo sin escribir en la hoja real.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import types
from http.server import BaseHTTPRequestHandler, HTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUADERNOS = {
    "u4_01_interpolacion": "U4_01_Interpolacion",
    "u4_02_newton_lagrange": "U4_02_Newton_Lagrange",
    "u4_03_minimos_cuadrados": "U4_03_Minimos_Cuadrados",
    "u4_04_casos": "U4_04_Casos",
}
ENLACE_CURSO = "https://github.com/ITH-MGL-MN/U4_Repo"


class _AppsScriptFalso(BaseHTTPRequestHandler):
    recibido = None

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length") or 0)
        _AppsScriptFalso.recibido = json.loads(self.rfile.read(n))
        cuerpo = json.dumps({"status": "ok", "data": {"intento": 1,
                                                      "total": 100}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *a):  # silencio
        pass


def _servidor():
    srv = HTTPServer(("127.0.0.1", 0), _AppsScriptFalso)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _copiar_material(destino, ref):
    """Deja en `destino` el repositorio tal como lo vería el alumno."""
    if ref:
        archivo = subprocess.run(["git", "-C", RAIZ, "archive", ref],
                                 capture_output=True, check=True).stdout
        tar = shutil.which("tar")
        if not tar:
            raise SystemExit("Falta tar para desempaquetar git archive.")
        os.makedirs(destino, exist_ok=True)
        subprocess.run([tar, "-x", "-C", destino], input=archivo, check=True)
    else:
        shutil.copytree(RAIZ, destino,
                        ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                      "_site", ".venv"))


def _falsos_google(email):
    """Módulos google.* mínimos: montar Drive y autenticar sin red."""
    google = types.ModuleType("google")
    google.__path__ = []
    colab = types.ModuleType("google.colab")
    colab.__path__ = []
    drive = types.ModuleType("google.colab.drive")
    drive.mount = lambda *a, **k: None
    auth_colab = types.ModuleType("google.colab.auth")
    auth_colab.authenticate_user = lambda *a, **k: None
    gauth = types.ModuleType("google.auth")
    gauth.__path__ = []
    gtrans = types.ModuleType("google.auth.transport")
    gtrans.__path__ = []
    greq = types.ModuleType("google.auth.transport.requests")
    greq.Request = object

    credenciales = types.SimpleNamespace(token="token-falso",
                                         refresh=lambda *a, **k: None)
    gauth.default = lambda *a, **k: (credenciales, None)

    gauth.transport = gtrans
    gtrans.requests = greq
    colab.drive = drive
    colab.auth = auth_colab
    google.colab = colab
    google.auth = gauth
    for nombre, modulo in {
        "google": google,
        "google.colab": colab,
        "google.colab.drive": drive,
        "google.colab.auth": auth_colab,
        "google.auth": gauth,
        "google.auth.transport": gtrans,
        "google.auth.transport.requests": greq,
    }.items():
        sys.modules[nombre] = modulo

    import requests

    class _Respuesta:
        status_code = 200

        @staticmethod
        def raise_for_status():
            return None

        @staticmethod
        def json():
            return {"user": {"emailAddress": email, "displayName": "Alumno"}}

    requests.get = lambda *a, **k: _Respuesta()


_SUFIJOS = {"/content/drive/MyDrive": "/MyDrive",
            "/content/drive": "/drive",
            "/content": ""}


def _cede(src, content):
    """Reescribe las rutas /content del cuaderno al sandbox temporal."""
    content = content.replace("\\", "/")
    return re.sub(r"/content/drive/MyDrive|/content/drive|/content",
                  lambda m: content + _SUFIJOS[m.group(0)], src)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cuaderno", default="u4_01_interpolacion",
                   choices=sorted(CUADERNOS))
    p.add_argument("--ref", default=None,
                   help="commit/rama de git que se simula (por defecto: la "
                        "copia de trabajo, con cambios sin commitear)")
    p.add_argument("--backend", default="auto", choices=["auto", "local", "real"],
                   help="auto/real usa config/config.yaml; local levanta un "
                        "Apps Script falso en localhost")
    p.add_argument("--email", default="m16330887@hermosillo.tecnm.mx")
    p.add_argument("--hasta", default="envio",
                   choices=["setup", "identidad", "envio"])
    p.add_argument("--conservar", action="store_true",
                   help="no borra el sandbox temporal")
    p.add_argument("--clonar", action="store_true",
                   help="clona de verdad desde GitHub en vez de copiar el "
                        "repositorio local (prueba el refresco de upstream)")
    p.add_argument("--retroceder", default=None, metavar="REF",
                   help="con --clonar: deja el clon atrasado en REF para "
                        "probar el refresco como un fork viejo")
    args = p.parse_args()

    import nbformat  # solo para leer las celdas sin outputs

    sandbox = tempfile.mkdtemp(prefix="mn_colab_")
    content = os.path.join(sandbox, "content")
    drive = os.path.join(content, "MyDrive")
    repo = os.path.join(drive, "CursoMN", "U4_Repo")
    os.makedirs(os.path.join(drive, "CursoMN"))
    if args.clonar:
        subprocess.run(["git", "clone", "--quiet", ENLACE_CURSO + ".git", repo],
                       check=True)
        if args.retroceder:
            subprocess.run(["git", "-C", repo, "reset", "--hard", "--quiet",
                            args.retroceder], check=True)
    else:
        _copiar_material(repo, args.ref)
    with open(os.path.join(drive, "CursoMN", "u4_repo.json"), "w",
              encoding="utf-8") as f:
        json.dump({"repo": ENLACE_CURSO}, f)

    if args.ref:
        fuente = subprocess.run(
            ["git", "-C", RAIZ, "show",
             "{}:notebooks/{}.ipynb".format(args.ref, CUADERNOS[args.cuaderno])],
            capture_output=True, check=True).stdout.decode("utf-8")
        nb = nbformat.reads(fuente, as_version=4)
    else:
        ruta_nb = os.path.join(RAIZ, "notebooks",
                               CUADERNOS[args.cuaderno] + ".ipynb")
        nb = nbformat.read(ruta_nb, as_version=4)

    _falsos_google(args.email)

    srv = None
    if args.backend == "local":
        srv = _servidor()
        os.environ["MN_APPS_URL"] = "http://127.0.0.1:{}/exec".format(
            srv.server_port)
        os.environ["MN_TOKEN"] = "token-de-prueba"
    os.environ.pop("MN_REPO", None)
    os.environ.pop("U4_REPO", None)
    import io

    sys.stdin = io.StringIO(ENLACE_CURSO + "\n")  # respuesta a input()

    codigo = [c.source for c in nb.cells if c.cell_type == "code"]
    a_ejecutar = codigo[:1]
    if args.hasta in ("identidad", "envio"):
        a_ejecutar.append(codigo[1])
    if args.hasta == "envio":
        a_ejecutar.append(next(c for c in reversed(codigo)
                               if "enviar(email)" in c))

    viejo = os.getcwd()
    os.chdir(content)  # Colab arranca en /content, no en el repositorio
    ns = {"__name__": "__main__"}
    try:
        for i, src in enumerate(a_ejecutar):
            exec(compile(_cede(src, content), "<celda{}>".format(i), "exec"), ns)
            if i == 0:
                diag = (
                    "import mn_motor.ajustes as _a, mn_motor.envio as _e\n"
                    "print('raiz() :', _a.raiz())\n"
                    "print('yaml   :', 'sí' if _e.yaml else 'NO instalado')\n"
                    "for _k, _v in _e.configuracion().items():\n"
                    "    _s = str(_v)\n"
                    "    print('  {:<6}'.format(_k), (_s[:46] + '…') if len(_s) > 46 else _s)\n"
                )
                exec(diag, ns)
    finally:
        os.chdir(viejo)
        if srv:
            srv.shutdown()
        if not args.conservar:
            shutil.rmtree(sandbox, ignore_errors=True)
        else:
            print("\nSandbox:", sandbox)


if __name__ == "__main__":
    main()
