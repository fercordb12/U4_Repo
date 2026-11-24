"""crear_cuadernos.py — genera los cuatro cuadernos de la Unidad 4.

Cada cuaderno repite el mismo bloque por método:

    1. Explicación del algoritmo
    2. Actividad a mano (datos sembrados por número de control)
    3. Programar la función (archivo de ``ejercicios/`` ya armado)
    4. Laboratorio con gráficas

y termina con las cuatro celdas de cierre: verificación de las actividades a
mano, verificación de las preguntas, envío y consulta del envío.

Uso::

    python tools/crear_cuadernos.py
"""

import os

import nbformat as nbf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "notebooks")

# Figuras del libro servidas desde el repositorio público (funcionan en Colab).
RAW = ("https://raw.githubusercontent.com/ITH-MGL-MN/U4_Repo"
       "/refs/heads/main/docs/figuras/libro/")

# ---------------------------------------------------------------------
# Celda 1: entorno (local o Colab) + repositorio + motor
# ---------------------------------------------------------------------
ENTORNO = r'''#@title ⚙️ Entorno — ejecuta esta celda PRIMERO
# ---------------------------------------------------------------
# En tu computadora usa los archivos locales, sin repositorio.
# En Google Colab pide UNA vez el enlace de tu fork, lo guarda en tu
# Drive y a partir de ahí lo reutiliza solo.
# ---------------------------------------------------------------
import json
import os
import subprocess
import sys

CUADERNO = {cuaderno!r}
TAREA_ID = {tarea_id!r}
REPO_NOMBRE = "U4_Repo"
GUARDADO = os.path.join("CursoMN", "u4_repo.json")   # relativo a MyDrive

try:
    import google.colab  # noqa: F401
    ES_COLAB = True
except ImportError:
    ES_COLAB = False


def _raiz_local():
    """Sube desde la carpeta actual hasta encontrar lib/robomat.py."""
    candidatos = []
    nb = globals().get("__vsc_ipynb_file__")
    if nb:
        candidatos.append(os.path.dirname(os.path.abspath(nb)))
    candidatos.append(os.getcwd())
    for base in candidatos:
        b = base
        for _ in range(6):
            if os.path.exists(os.path.join(b, "lib", "robomat.py")):
                return b
            padre = os.path.dirname(b)
            if padre == b:
                break
            b = padre
    return None


def _normaliza(enlace):
    enlace = (enlace or "").strip().rstrip("/")
    if enlace.endswith(".git"):
        enlace = enlace[:-4]
    if not enlace.startswith("https://github.com/"):
        raise ValueError("Necesito un enlace https://github.com/USUARIO/"
                         + REPO_NOMBRE + " (tu fork).")
    return enlace


# Repositorio del curso (upstream) y carpetas que el alumno nunca edita:
# se refrescan en cada ejecución para que el material y el motor nunca estén
# atrasados, aunque el fork se haya quedado viejo.
CURSO = "https://github.com/ITH-MGL-MN/" + REPO_NOMBRE
MATERIAL = ("lib", "grader", "config", "docs", "ejercicios", "tools")


def _git(*args):
    """Corre git dentro del clon. Devuelve (funcionó, salida)."""
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def actualizar():
    """Trae tus commits de GitHub y refresca el material del curso.

    El clon de Drive es desechable: tus respuestas viven en el cuaderno.
    Primero se actualiza el fork (lo que editaste en GitHub) y después se
    copia el material del curso desde `upstream/main`. Si tienes cambios
    locales en el clon, no se tocan: se avisa y se sigue.
    """
    ok, _ = _git("rev-parse", "--is-inside-work-tree")
    if not ok:
        print("⚠️ La carpeta no es un repositorio git: uso los archivos tal cual.")
        return
    _git("remote", "add", "upstream", CURSO + ".git")
    ok, salida = _git("fetch", "--all", "--prune", "--quiet")
    if not ok:
        print("⚠️ No pude conectar con GitHub; sigo con lo que hay en Drive.")
        return

    _git("checkout", "--", *MATERIAL)          # limpia el refresco anterior
    _, rama = _git("rev-parse", "--abbrev-ref", "HEAD")
    rama = rama or "main"
    ok, salida = _git("merge", "--ff-only", "origin/" + rama)
    if ok:
        print("Fork        : al día con tus commits de GitHub")
    else:
        print("⚠️ Tu fork no avanza en línea recta (tienes commits propios")
        print("   o cambios locales): lo dejo como está y solo refresco el")
        print("   material del curso.")

    ok, salida = _git("checkout", "upstream/main", "--", *MATERIAL)
    if ok:
        _git("reset", "--quiet")
        _, sha = _git("rev-parse", "--short", "upstream/main")
        print("Material    : actualizado al curso", sha)
    else:
        print("⚠️ No pude refrescar el material del curso:", salida.splitlines()[:1])


if not ES_COLAB:
    REPO = _raiz_local()
    if REPO is None:
        raise RuntimeError(
            "No encontré la raíz del repositorio (lib/robomat.py).\n"
            "Abre el cuaderno dentro de U4_Repo o ejecútalo desde esa carpeta.")
    print("Modo        : local (sin repositorio)")
    print("Repositorio :", REPO)
else:
    from google.colab import drive
    drive.mount("/content/drive")
    DRIVE = "/content/drive/MyDrive"
    ruta_json = os.path.join(DRIVE, GUARDADO)

    guardado = {{}}
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, encoding="utf-8") as f:
                guardado = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"No se pudo leer la configuracion de Drive: {{ruta_json}}"
            ) from exc

    enlace = (guardado.get("repo") or "").strip()
    if enlace:
        print("✅ Repositorio guardado:", enlace)
        print("   (si cambió, edita la caja de abajo y pulsa el botón)")
    else:
        try:
            enlace = input("Pega el enlace de TU fork de U4_Repo: ")
        except Exception:
            enlace = ""
        enlace = (enlace or "").strip()
        if not enlace:
            raise RuntimeError(
                "Sin repositorio no puedo continuar en Colab.\n"
                "Haz fork del repositorio del curso y pega su enlace.")

    enlace = _normaliza(enlace)
    REPO = os.path.join(DRIVE, "CursoMN", REPO_NOMBRE)

    if not os.path.exists(REPO):
        print("Clonando tu repositorio…")
        subprocess.run(["git", "clone", enlace + ".git", REPO], check=True)
    actualizar()

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump({{"repo": enlace}}, f, indent=1)
    print("Repositorio :", REPO)
    print("Actualizar  : vuelve a ejecutar esta celda cuando subas cambios a GitHub")

# Instala dependencias del repositorio solo si falta alguna.
import importlib.util

_modulos_requeridos = ("numpy", "scipy", "sympy", "matplotlib", "yaml", "requests")
_faltantes = [nombre for nombre in _modulos_requeridos
              if importlib.util.find_spec(nombre) is None]
if _faltantes:
    requisitos = os.path.join(REPO, "requirements.txt")
    if not os.path.isfile(requisitos):
        raise FileNotFoundError("Falta requirements.txt en el repositorio.")
    print("Instalando dependencias faltantes:", ", ".join(_faltantes))
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", requisitos],
                   check=True)

# Indica al motor empaquetado dónde está la configuración del repositorio.
os.environ["MN_REPO"] = REPO

# --- Motor de calificación -------------------------------------------
# Se usa el código fuente si está (rama `test`, para depurar); si no, el blob
# empaquetado de grader/, que es lo que recibe el alumno.
_ruta_modulos = os.path.join(REPO, "lib", "mn_motor")
_ruta_blob = os.path.join(REPO, "grader", CUADERNO + ".txt")

_lib = os.path.join(REPO, "lib")
if _lib not in sys.path:
    sys.path.insert(0, _lib)          # ajuste_curvas y, si está, mn_motor

if os.path.isfile(os.path.join(_ruta_modulos, "__init__.py")):
    import mn_motor as _motor
    globals().update({{n: getattr(_motor, n) for n in _motor.__all__}})
    print("Motor       : módulos de lib/mn_motor (modo profesor)")
else:
    import base64
    import zlib

    if not os.path.exists(_ruta_blob):
        raise FileNotFoundError(
            "No encuentro el motor: falta grader/" + CUADERNO + ".txt\n"
            "Clona el repositorio completo (incluye la carpeta grader/).")
    with open(_ruta_blob, encoding="utf-8") as f:
        codigo = zlib.decompress(base64.b64decode(f.read().strip())).decode("utf-8")
    _MOTOR = {{"__name__": "mn_motor_blob", "__file__": "<blob>"}}
    exec(compile(codigo, "<blob>", "exec"), _MOTOR)
    globals().update({{n: _MOTOR[n] for n in _MOTOR["__all__"]}})
    print("Motor       : blob verificado de grader/")

usar_cuaderno(CUADERNO, TAREA_ID)

# --- Preludio estilo MATLAB y herramientas de gráficas ---------------
with open(os.path.join(REPO, "lib", "robomat.py"), encoding="utf-8") as f:
    exec(f.read(), globals())

if REPO not in sys.path:
    sys.path.insert(0, REPO)          # para importar ejercicios/
sys.path.append(os.path.join(REPO, "tools"))
import importlib
import visualizar
importlib.reload(visualizar)

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (9, 4.5)
plt.rcParams["figure.dpi"] = 110
print("Preludio    : lib/robomat.py · tools/visualizar.py")
print("\nListo. Ejecuta la celda de identificación.")
'''

IDENTIFICACION = r'''#@title 👤 Identificación (número de control)
# ---------------------------------------------------------------
# En Colab se toma tu correo institucional; en local se escribe uno
# de prueba. De ahí sale el número de control que siembra tus datos.
# ---------------------------------------------------------------
if ES_COLAB:
    import requests

    from google.colab import auth
    import google.auth
    import google.auth.transport.requests

    auth.authenticate_user()
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    info = requests.get(
        "https://www.googleapis.com/drive/v3/about?fields=user",
        headers={"Authorization": "Bearer " + creds.token}, timeout=20).json()
    cuenta = info.get("user", {})
    email = cuenta.get("emailAddress", "")
    nombre = cuenta.get("displayName", "")
else:
    email = "m16330887@hermosillo.tecnm.mx"   # <-- cambia por el tuyo
    nombre = ""

if not (email and "@" in email and email.lower().endswith(".tecnm.mx")):
    from IPython.display import HTML, display
    display(HTML(
        '<p style="color:#b00020;background:#ffe0e0;padding:12px;'
        'border-radius:8px;font-weight:bold">⛔ Usa tu correo @….tecnm.mx</p>'))
    raise RuntimeError("Necesito tu correo institucional para sembrar tus datos.")

print("Alumno :", email)
print("NC     :", extraer_nc(email))
MI_TAREA = generar_tarea(email, nombre)
print("Cuaderno:", MI_TAREA["cuaderno"],
      "·", len(MI_TAREA["preguntas"]), "preguntas")
'''

CIERRE_MANO = r'''#@title ✅ 1 · Verificación de los ejercicios a mano
mano_comprueba_todos([{metodos}])
'''

CIERRE_CALIFICAR = r'''#@title 📝 2 · Verificación de todas las preguntas (no envía nada)
puntos, maximo = calificar()
'''

CIERRE_ENVIAR = r'''#@title 📤 3 · Envío de las respuestas
enviar(email)
'''

CIERRE_CONSULTAR = r'''#@title 🔎 4 · Verificación de lo que ya está enviado (no envía nada)
consultar_calificacion()
'''


def md(nb, texto):
    nb.cells.append(nbf.v4.new_markdown_cell(texto.strip()))


def code(nb, texto):
    nb.cells.append(nbf.v4.new_code_cell(texto.strip()))


def nuevo(titulo, subtitulo):
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
        "colab": {"provenance": []},
    }
    md(nb, f"# {titulo}\n\n**Métodos Numéricos · Unidad 4: Ajuste de curvas e "
            f"interpolación**\n\n{subtitulo}")
    return nb


def bloque(nb, n, metodo, titulo, teoria, archivo, args, practica=True,
           pasos=None, figuras=(), comprueba=None, preguntas=()):
    """Un método: teoría, actividad a mano, función, laboratorio y preguntas."""
    dibujos = "".join(f"\n\n![{cap}]({RAW}{img})" for img, cap in figuras)
    md(nb, f"""
---

## Método {n} · {titulo}

{teoria}{dibujos}
""")
    code(nb, f'#@title ✏️ Actividad a mano · {titulo}\nEJ_{n} = mano_enunciado("{metodo}")')
    if pasos:
        md(nb, pasos)
    code(nb, comprueba or f"""#@title ✅ Comprueba tus valores a mano · {titulo}
# Reporta los números que obtuviste, con 4 decimales.
mano_comprueba("{metodo}", [{args}])""")
    md(nb, f"""
### 💻 Programa la función

Abre `ejercicios/{archivo}` en GitHub o copia la plantilla aquí abajo.
El método completo debe **llamar** a sus piezas: no repitas la cuenta.
""")
    code(nb, f"""#@title 💻 Tu función · {titulo}
from ejercicios.{archivo.replace('/', '.').replace('.py', '')} import *
""")
    if practica:
        code(nb, f'#@title ▶️ Prueba tu función con un ejemplo\npractica("{metodo}")')
    code(nb, f'#@title 📊 Laboratorio · {titulo}\nvisualizar.laboratorio("{metodo}", EJ_{n})')
    for q in preguntas:
        preguntas_celda(nb, q, titulo)


# =====================================================================
# Cuaderno 01 — Interpolación
# =====================================================================
TAYLOR = r"""
---

## Antes de interpolar: polinomios de Taylor

Una función suave puede aproximarse cerca de un punto $a$ mediante una suma
infinita de potencias construida con sus derivadas en ese punto. La **serie de
Taylor** es

$$f(x)=\sum_{k=0}^{\infty}\frac{f^{(k)}(a)}{k!}(x-a)^k,$$

cuando la serie converge a $f(x)$ en infinitas iteraciones.

En la práctica se conservan solo los primeros $n+1$ términos: el **polinomio de
Taylor** de grado $n$,

$$T_n(x)=\sum_{k=0}^{n}\frac{f^{(k)}(a)}{k!}(x-a)^k.$$

Por ejemplo, para $e^x$ alrededor de $a=0$, $T_2(x)=1+x+\frac{x^2}{2}$. En
$x=0.2$ da $1.22$, mientras que $e^{0.2}\approx1.2214$; la diferencia es el
error de truncamiento algorítmico. Bajo las condiciones del teorema de Taylor,
ese error puede escribirse como

$$R_n(x)=f(x)-T_n(x)=\frac{f^{(n+1)}(\xi)}{(n+1)!}(x-a)^{n+1},$$

para algún punto $\xi$ entre $a$ y $x$.

**Conexión con esta unidad:** Taylor usa derivadas en un punto para aproximar
localmente; la **interpolación** usa valores conocidos en varios nodos y
construye un polinomio que pasa por ellos. Aquí trabajaremos con esta segunda
idea.
"""

PASOS_LINEAL = r"""
**🔢 Resolución paso a paso.**

1. Identifica el intervalo $[x_0,x_1]$ que contiene a $x$.
2. Anota $y_0 = f(x_0)$ y $y_1 = f(x_1)$.
3. Calcula la pendiente $m=\dfrac{y_1-y_0}{x_1-x_0}$.
4. Evalúa $y=y_0+m(x-x_0)$.
"""

PASOS_CUADRATICA = r"""
**🔢 Resolución paso a paso.**

1. Anota los tres nodos $(x_0,y_0)$, $(x_1,y_1)$, $(x_2,y_2)$ y el punto $x$.
2. Calcula las dos pendientes entre tramos consecutivos:
   $m_1=\dfrac{y_1-y_0}{x_1-x_0}$ y $m_2=\dfrac{y_2-y_1}{x_2-x_1}$.
3. Coeficientes: $b_0=y_0$, $b_1=m_1$ y $b_2=\dfrac{m_2-m_1}{x_2-x_0}$.
4. Evalúa $y=b_0+b_1(x-x_0)+b_2(x-x_0)(x-x_1)$.
"""

PASOS_ERROR = r"""
**🔢 Resolución paso a paso.**

1. Ordena los cuatro nodos de menor a mayor en $x$.
2. Calcula las pendientes de primer orden $f[x_i,x_j]=\dfrac{y_j-y_i}{x_j-x_i}$.
3. Con ellas arma las de segundo orden y, al final, la de tercer orden
   $f[x_3,x_2,x_1,x_0]$.
4. Multiplica esa diferencia por $(x-x_0)(x-x_1)(x-x_2)$: ése es $R_2$.
"""

COMPRUEBA_LINEAL = '''#@title ✅ Comprueba tus valores a mano · Interpolación lineal
# Datos de tu enunciado (no los cambies, cambian con tu número de control):
x0, y0 = EJ_1["datos"]["x0"], EJ_1["datos"]["f0"]
x1, y1 = EJ_1["datos"]["x1"], EJ_1["datos"]["f1"]
x = EJ_1["datos"]["x"]

# Haz la cuenta a mano y escribe abajo tu resultado con 4 decimales:
#   1) pendiente  m = (y1 - y0) / (x1 - x0)
#   2) evalúa     y = y0 + m * (x - x0)
y = 0.0
mano_comprueba("INTERP_LINEAL", y)'''

COMPRUEBA_CUADRATICA = '''#@title ✅ Comprueba tus valores a mano · Interpolación cuadrática
# Datos de tu enunciado (no los cambies, cambian con tu número de control):
x0, y0 = EJ_2["datos"]["x0"], EJ_2["datos"]["f0"]
x1, y1 = EJ_2["datos"]["x1"], EJ_2["datos"]["f1"]
x2, y2 = EJ_2["datos"]["x2"], EJ_2["datos"]["f2"]
x = EJ_2["datos"]["x"]

# Haz la cuenta a mano y escribe abajo tu resultado con 4 decimales:
#   1) m1 = (y1 - y0) / (x1 - x0)      2) m2 = (y2 - y1) / (x2 - x1)
#   3) b0 = y0,  b1 = m1,  b2 = (m2 - m1) / (x2 - x0)
#   4) y = b0 + b1 * (x - x0) + b2 * (x - x0) * (x - x1)
y = 0.0
mano_comprueba("INTERP_CUADRATICA", y)'''

COMPRUEBA_ERROR = '''#@title ✅ Comprueba tus valores a mano · Error con un punto extra
# Datos de tu enunciado (no los cambies, cambian con tu número de control):
x0, x1, x2 = EJ_3["datos"]["nodos"]
x3 = EJ_3["datos"]["x_todos"][3]
y0, y1, y2, y3 = EJ_3["datos"]["y"]
x = EJ_3["datos"]["x"]

# Haz la cuenta a mano y escribe abajo tu resultado con 4 decimales:
#   1) f[x1,x0] = (y1-y0)/(x1-x0)     f[x2,x1] = (y2-y1)/(x2-x1)
#      f[x3,x2] = (y3-y2)/(x3-x2)
#   2) f[x2,x1,x0] = (f[x2,x1]-f[x1,x0])/(x2-x0)
#      f[x3,x2,x1] = (f[x3,x2]-f[x2,x1])/(x3-x1)
#   3) f[x3,x2,x1,x0] = (f[x3,x2,x1]-f[x2,x1,x0])/(x3-x0)
#   4) R = f[x3,x2,x1,x0] * (x-x0) * (x-x1) * (x-x2)
R = 0.0
mano_comprueba("ERROR_INTERP", R)'''

NB01 = [
    ("INTERP_LINEAL", "Interpolación lineal",
     r"""Es unir dos puntos con una recta. Por triángulos semejantes,

$$f_1(x)=f(x_0)+\frac{f(x_1)-f(x_0)}{x_1-x_0}(x-x_0) \tag{18.2}$$

El cociente es la pendiente y, además, una aproximación a la primera derivada.
Cuanto más cerca estén los nodos, mejor representa la recta a la curva.

**Dos salidas.** La función devuelve `(y, error)`. El error sólo se puede
estimar si hay un tercer dato:

$$R_1\cong f[x_2,x_1,x_0]\,(x-x_0)(x-x_1) \tag{18.18}$$

Mientras no escribas `error_estimado_interpolacion` (método 3), regresa
`(y, None)`.""",
     "interpolacion/interpolacion_lineal.py", "0.0",
     {"pasos": PASOS_LINEAL,
      "figuras": [("fig18-2_interpolacion_lineal.jpg",
                   "Figura 18.2 del libro: interpolación lineal")],
      "comprueba": COMPRUEBA_LINEAL,
      "preguntas": (1, 2)}),

    ("INTERP_CUADRATICA", "Interpolación cuadrática",
     r"""Con tres puntos se ajusta el único polinomio de segundo grado:

$$f_2(x)=b_0+b_1(x-x_0)+b_2(x-x_0)(x-x_1) \tag{18.3}$$

Los coeficientes salen de dos pendientes:

$$m_1=\frac{y_1-y_0}{x_1-x_0} \qquad\text{y}\qquad
m_2=\frac{y_2-y_1}{x_2-x_1}$$

$$b_0=y_0 \tag{18.4}\qquad b_1=m_1 \tag{18.5}\qquad
b_2=\frac{m_2-m_1}{x_2-x_0} \tag{18.6}$$

Los dos primeros términos son la recta; $b_2$ mide cómo cambia la pendiente y
aporta la curvatura. Todo se calcula dentro de la misma función: no hace falta
un paso aparte para los coeficientes.

**Dos salidas.** Devuelve `(y, error)`, y el error sólo aparece con un cuarto
dato:

$$R_2\cong f[x_3,x_2,x_1,x_0]\,(x-x_0)(x-x_1)(x-x_2) \tag{18.18}$$""",
     "interpolacion/interpolacion_cuadratica.py", "0.0",
     {"pasos": PASOS_CUADRATICA,
      "figuras": [("fig18-4_ln2_cuadratica.jpg",
                   "Figura 18.4 del libro: parábola por tres puntos")],
      "comprueba": COMPRUEBA_CUADRATICA,
      "preguntas": (3, 4)}),

    ("ERROR_INTERP", "Error con un punto extra",
     r"""Un dato más de los necesarios sirve para **estimar** el error sin
conocer la función:

$$R_n\cong f[x_{n+1},x_n,\dots,x_0]\prod_{i=0}^{n}(x-x_i) \tag{18.18}$$

Es la diferencia entre la predicción de grado $n+1$ y la de grado $n$
(ecuación 18.19). Cuando termines esta función, vuelve a tus dos métodos y
activa el cálculo del error.""",
     "interpolacion/error_estimado_interpolacion.py", "0.0",
     {"pasos": PASOS_ERROR,
      "figuras": [("fig18-6_ln2_cubica.jpg",
                   "Figura 18.6 del libro: con un nodo extra se mide el error")],
      "comprueba": COMPRUEBA_ERROR,
      "preguntas": (5, 6)}),
]

# Celdas extra del cuaderno 01: conectar el error con los dos métodos.
CONECTAR_ERROR = r'''#@title 🔗 Conecta el error con tus métodos
# Ya tienes error_estimado_interpolacion. Vuelve a tus dos funciones y activa
# el cálculo del error: con el punto extra deben devolver (y, error).
d = EJ_3["datos"]
x0, x1, x2 = d["nodos"]
x3 = d["x_todos"][3]
y0, y1, y2, y3 = d["y"]

print("nodos:", d["x_todos"], "· valores:", d["y"])
print("punto a estimar: x =", d["x"], "\n")

try:
    print("cuadrática sin cuarto dato:", interpolacion_cuadratica(x0, y0, x1, y1, x2, y2, d["x"]))
    print("cuadrática con cuarto dato:", interpolacion_cuadratica(
        x0, y0, x1, y1, x2, y2, d["x"], x3=x3, y3=y3))
except NotImplementedError as exc:
    print("⏳ Todavía falta una de tus funciones:", exc)
except TypeError as exc:
    print("⚠️ Revisa la firma de tu función (debe aceptar x3 e y3):", exc)

print("\nEl valor de referencia de tu actividad a mano no se muestra aquí:")
print("compáralo con lo que reportaste en la celda ✅ del método 3.")
'''


# ======================================================================
# Cuaderno 02 — Newton y Lagrange
# ======================================================================
NB02 = [
    ("NEWTON_TABLA", "Tabla de diferencias divididas",
     r"""La primera diferencia dividida es una pendiente,

$$f[x_i,x_j]=\frac{f(x_i)-f(x_j)}{x_i-x_j} \tag{18.12}$$

y las siguientes se construyen con las anteriores:

$$f[x_i,x_j,x_k]=\frac{f[x_i,x_j]-f[x_j,x_k]}{x_i-x_k} \tag{18.13}$$

La tabla es triangular y su **diagonal** son los coeficientes del polinomio.""",
     "newton_lagrange/tabla_diferencias.py", "0.0, 0.0, 0.0, 0.0"),

    ("NEWTON_EVAL", "Polinomio de Newton en diferencias divididas",
     r"""La forma general agrega un término por nodo:

$$f_n(x)=b_0+b_1(x-x_0)+\cdots+b_n(x-x_0)\cdots(x-x_{n-1}) \tag{18.7}$$

Se evalúa con Horner: $p=b_n$ y luego $p\leftarrow p(x-x_k)+b_k$. Esta función
**debe llamar** a `coeficientes_newton` y a `evaluar_newton`.""",
     "newton_lagrange/interpolacion_newton.py", "0.0"),

    ("LAGRANGE", "Polinomio de Lagrange",
     r"""Es una reformulación que evita las diferencias divididas:

$$f_n(x)=\sum_{i=0}^{n}L_i(x)f(x_i),\qquad
L_i(x)=\prod_{\substack{j=0\\ j\neq i}}^{n}\frac{x-x_j}{x_i-x_j} \tag{18.20–18.21}$$

Cada peso vale 1 en su nodo y 0 en los demás. Da **el mismo** polinomio que
Newton.""",
     "newton_lagrange/interpolacion_lagrange.py", "0.0"),

    ("ERROR_NEWTON", "Error del polinomio",
     r"""El término que se agrega al subir de grado es una estimación del error
de grado $n$:

$$R_n=f_{n+1}(x)-f_n(x)=b_n\prod_{i<n}(x-x_i) \tag{18.19}$$""",
     "newton_lagrange/error_newton.py", "0.0"),
]

# ======================================================================
# Cuaderno 03 — Mínimos cuadrados
# ======================================================================
NB03 = [
    ("SUMA_RESIDUOS", "Suma de residuos al cuadrado",
     r"""El criterio de mínimos cuadrados es minimizar

$$S_r=\sum_{i=1}^{n}e_i^2=\sum_{i=1}^{n}\left(y_i-a_0-a_1x_i-\cdots\right)^2 \tag{17.3}$$

Se usan cuadrados para que los errores no se cancelen y el mínimo sea único.""",
     "minimos_cuadrados/suma_residuos_cuadrados.py", "0.0"),

    ("REG_LINEAL", "Regresión lineal",
     r"""Al derivar (17.3) e igualar a cero salen las **ecuaciones normales**:

$$n a_0+\left(\sum x_i\right)a_1=\sum y_i \tag{17.4}$$

$$\left(\sum x_i\right)a_0+\left(\sum x_i^2\right)a_1=\sum x_i y_i \tag{17.5}$$

y su solución,

$$a_1=\frac{n\sum x_iy_i-\sum x_i\sum y_i}{n\sum x_i^2-\left(\sum x_i\right)^2},\qquad
a_0=\bar y-a_1\bar x \tag{17.6–17.7}$$
""",
     "minimos_cuadrados/regresion_lineal.py", "0.0, 0.0, 0.0"),

    ("REG_CUADRATICA", "Regresión cuadrática",
     r"""Para $y=a_0+a_1x+a_2x^2$ las ecuaciones normales son un sistema $3\times3$:

$$\begin{bmatrix}n&\sum x_i&\sum x_i^2\\ \sum x_i&\sum x_i^2&\sum x_i^3\\ \sum x_i^2&\sum x_i^3&\sum x_i^4\end{bmatrix}
\begin{bmatrix}a_0\\a_1\\a_2\end{bmatrix}=\begin{bmatrix}\sum y_i\\ \sum x_iy_i\\ \sum x_i^2y_i\end{bmatrix} \tag{17.19}$$

Resolverlo es resolver un sistema lineal: aquí se ve por qué sirve el capítulo 3.""",
     "minimos_cuadrados/regresion_cuadratica.py", "0.0, 0.0, 0.0, 0.0"),

    ("ERROR_ESTANDAR", "Error estándar de la estimación",
     r"""Mide la dispersión alrededor del modelo, no alrededor de la media:

$$s_{y/x}=\sqrt{\frac{S_r}{n-(m+1)}} \tag{17.9, 17.20}$$

Se pierden $m+1$ grados de libertad porque se estimaron $m+1$ coeficientes.""",
     "minimos_cuadrados/error_estandar.py", "0.0"),

    ("COEF_DETERMINACION", "Coeficiente de determinación",
     r"""Cuánto de la incertidumbre original explica el modelo:

$$r^2=\frac{S_t-S_r}{S_t} \tag{17.10}$$

Un $r^2$ cercano a 1 **no** prueba que la forma sea la correcta: hay que
graficar.""",
     "minimos_cuadrados/coeficiente_determinacion.py", "0.0"),
]

# ======================================================================
# Cuaderno 04 — Casos (U3 + U4) y Fourier extra
# ======================================================================
NB04 = [
    ("CASO_GAUSS", "Sistema lineal por eliminación gaussiana (Unidad 3)",
     r"""Antes de ajustar hay que **resolver**. Las ecuaciones normales de un
ajuste son un sistema lineal, así que se atacan con lo de la Unidad 3:
eliminación hacia adelante y sustitución hacia atrás.

$$a_{ii}^{(k+1)} = a_{ii} - m\,a_{ki}, \qquad m=\frac{a_{ik}}{a_{kk}} \tag{U3}$$

Multiplicadores, pivoteo y costo $O(n^3)$: lo ya estudiado. Aquí sólo se
reutiliza para el caso.""",
     "casos/gauss_solve.py", "0.0, 0.0, 0.0", True),

    ("CASO_NORMALES", "Calibración: ecuaciones normales por Gauss",
     r"""El caso completo, con las dos unidades juntas:

1. Un sensor da lecturas $x$ y temperaturas $y$ con ruido.
2. Se plantean las **ecuaciones normales** (17.4)–(17.5): un sistema $2\times2$.
3. Se resuelve con **eliminación gaussiana** (Unidad 3).

$$n a_0+\left(\sum x_i\right)a_1=\sum y_i,\qquad
\left(\sum x_i\right)a_0+\left(\sum x_i^2\right)a_1=\sum x_iy_i \tag{17.4–17.5}$$

Tu función `coeficientes_calibracion` debe **llamar** a `gauss_solve`: no se
resuelve el sistema dos veces con dos métodos distintos.""",
     "casos/coeficientes_calibracion.py", "0.0, 0.0", True),

    ("FOURIER", "Serie de Fourier (tarea extra)",
     r"""Con datos igualmente espaciados que completan un periodo, los
coeficientes salen de sumas simples:

$$A_0=\frac{\sum y}{N},\qquad
A_j=\frac{2}{N}\sum y\cos(j\omega_0t),\qquad
B_j=\frac{2}{N}\sum y\operatorname{sen}(j\omega_0t) \tag{19.14–19.16}$$

El modelo es lineal en $A_j$ y $B_j$, así que es mínimos cuadrados con otra
base de funciones.""",
     "casos/coeficientes_fourier.py", "0.0, 0.0, 0.0"),
]


def preguntas_celda(nb, n, metodo):
    code(nb, f'#@title 🧪 Pregunta {n} · {metodo}\n'
             f'# Cuando tu función ya funcione, contéstala aquí.\n'
             f'pregunta({n})')


def construir(nb, metodos, prefijo, preguntas_por_metodo=True):
    for n, item in enumerate(metodos, start=1):
        metodo, titulo, teoria, archivo, args = item[:5]
        opciones = item[5] if len(item) > 5 else {}
        if isinstance(opciones, bool):
            opciones = {"practica": opciones}
        else:
            opciones = dict(opciones)
        if preguntas_por_metodo and "preguntas" not in opciones:
            opciones["preguntas"] = (n,)
        bloque(nb, n, metodo, titulo, teoria, archivo, args, **opciones)
    return nb


CASOS_U3_U4 = r'''
---

## Caso · Calibración de un sensor (mínimos cuadrados + sistemas lineales)

**El problema.** Un sensor entrega una lectura digital $x$ y se calibra contra
un patrón de temperatura $y$. El fabricante reporta ruido de $\pm0.1$ °C.

| $x$ (cuentas) | 0 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 |
|---|---|---|---|---|---|---|---|---|---|---|
| $y$ (°C) | 0.2 | 0.9 | 1.8 | 2.5 | 3.4 | 4.2 | 5.4 | 6.2 | 7.5 | 8.4 |

**¿Interpolar o ajustar?** Ajustar: hay 10 mediciones con ruido. Interpolar con
grado 9 copiaría el ruido.

**El método más efectivo aquí** es mínimos cuadrados **cuadráticos** (17.19),
porque el lineal deja estructura en los residuales. Y hay un detalle que
conecta las dos unidades: las ecuaciones normales **son un sistema lineal**, así
que se resuelven con lo de la Unidad 3.

**Otros métodos viables.** Lineal (más simple, deja curvatura); cúbico (no
mejora y no se justifica); interpolación (sobreajuste).
'''

CASO_A_CODIGO = r'''#@title 🧩 Caso A · ecuaciones normales resueltas con Gauss (Unidad 3)
from ajuste_curvas import minimos_cuadrados

x_s = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90], dtype=float)
y_s = np.array([0.2, 0.9, 1.8, 2.5, 3.4, 4.2, 5.4, 6.2, 7.5, 8.4])


def gauss_solve(A, b):
    """Eliminación gaussiana con sustitución hacia atrás (Unidad 3)."""
    A = np.array(A, dtype=float).copy()
    b = np.array(b, dtype=float).copy()
    n = len(b)
    for k in range(n - 1):
        if A[k, k] == 0:
            raise ZeroDivisionError(f"pivote cero en la columna {k + 1}")
        for i in range(k + 1, n):
            m = A[i, k] / A[k, k]
            A[i, k:] -= m * A[k, k:]
            b[i] -= m * b[k]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - A[i, i + 1:] @ x[i + 1:]) / A[i, i]
    return x


n_s = len(x_s)
A_norm = np.array([[n_s, x_s.sum(), (x_s ** 2).sum()],
                   [x_s.sum(), (x_s ** 2).sum(), (x_s ** 3).sum()],
                   [(x_s ** 2).sum(), (x_s ** 3).sum(), (x_s ** 4).sum()]])
b_norm = np.array([y_s.sum(), (x_s * y_s).sum(), (x_s ** 2 * y_s).sum()])

coef_gauss = gauss_solve(A_norm, b_norm)
coef_lib = minimos_cuadrados(x_s, y_s, 2)["coef"]
print("con Gauss (U3) :", np.round(coef_gauss, 6))
print("con la librería:", np.round(coef_lib, 6))
print("¿coinciden?     :", np.allclose(coef_gauss, coef_lib, atol=1e-9))
'''

CASO_A_CIERRE = r'''#@title 🧩 Caso A · ¿lineal o cuadrático? la evidencia
for m in (1, 2):
    r = minimos_cuadrados(x_s, y_s, m)
    print(f"grado {m}: sy/x = {r['syx']:.4f} °C · r2 = {r['r2']:.5f}")

print("\nruido del sensor = 0.1 °C")
print("El lineal queda por encima del ruido y deja curvatura;")
print("el cuadrático baja al orden del ruido: se justifica el término x^2.")
'''


def casos(nb):
    md(nb, CASOS_U3_U4)
    code(nb, CASO_A_CODIGO)
    code(nb, CASO_A_CIERRE)


def cierres(nb, metodos):
    code(nb, CIERRE_MANO.format(
        metodos=", ".join(f'"{m[0]}"' for m in metodos)))
    code(nb, CIERRE_CALIFICAR)
    code(nb, CIERRE_ENVIAR)
    code(nb, CIERRE_CONSULTAR)
    return nb


def main():
    os.makedirs(SALIDA, exist_ok=True)

    especificaciones = [
        ("U4_01_Interpolacion.ipynb", "u4_01_interpolacion",
         "U4_01_Interpolacion", "📐 Cuaderno 01 — Interpolación",
         "Tema 4.1. Cada método sigue el mismo camino: **explicación → a mano → "
         "programar → laboratorio → preguntas**.",
         NB01, False, TAYLOR),
        ("U4_02_Newton_Lagrange.ipynb", "u4_02_newton_lagrange",
         "U4_02_Newton_Lagrange", "🌳 Cuaderno 02 — Newton y Lagrange",
         "Tema 4.2. Dos formas del **mismo** polinomio, más la estimación del "
         "error.",
         NB02, False, None),
        ("U4_03_Minimos_Cuadrados.ipynb", "u4_03_minimos_cuadrados",
         "U4_03_Minimos_Cuadrados", "📉 Cuaderno 03 — Mínimos cuadrados",
         "Tema 4.3. Cuando los datos traen ruido no se interpola: se ajusta.",
         NB03, False, None),
        ("U4_04_Casos.ipynb", "u4_04_casos", "U4_04_Casos",
         "🧩 Cuaderno 04 — Casos (Unidades 3 y 4)",
         "Tema 4.4. Casos que combinan **sistemas lineales** (Unidad 3) con "
         "**ajuste de curvas** (Unidad 4), y la serie de Fourier como tarea "
         "extra.",
         NB04, True, None),
    ]

    for (archivo, cuaderno, tarea_id, titulo, subtitulo,
         metodos, con_casos, intro) in especificaciones:
        nb = nuevo(titulo, subtitulo)
        code(nb, ENTORNO.format(cuaderno=cuaderno, tarea_id=tarea_id))
        code(nb, IDENTIFICACION)
        if intro:
            md(nb, intro)
        if con_casos:
            casos(nb)
        construir(nb, metodos, cuaderno, preguntas_por_metodo=not intro)
        if intro:
            code(nb, CONECTAR_ERROR)
        cierres(nb, metodos)
        nbf.write(nb, os.path.join(SALIDA, archivo))
        print("escrito:", archivo, f"({len(nb.cells)} celdas)")


if __name__ == "__main__":
    main()
