# 📈 Unidad 4: Ajuste de Curvas e Interpolación

## 🎯 Objetivo general

Construir, implementar y evaluar **polinomios de interpolación** y **modelos de
mínimos cuadrados** para estimar valores, describir tendencias y resolver
problemas de ingeniería, distinguiendo cuándo un dato debe interpolarse y
cuándo debe ajustarse.

---

## 🧭 Los cuatro cuadernos

La unidad se recorre en cuatro cuadernos calificables. Cada **método** repite
el mismo camino: **explicación → actividad a mano → programar la función →
laboratorio con gráficas → preguntas**. Al final hay cuatro celdas de cierre:
verificación a mano, verificación de preguntas, envío y consulta del envío.

| # | Cuaderno | Métodos |
|---|---|---|
| **01** | **Interpolación** | repaso de polinomios de Taylor · lineal · cuadrática · error con punto extra (los dos primeros devuelven `(y, error)`) |
| **02** | **Newton y Lagrange** | tabla de diferencias, coeficientes, evaluación, Lagrange, error |
| **03** | **Mínimos cuadrados** | $S_r$, regresión lineal, cuadrática, $s_{y/x}$, $r^2$ |
| **04** | **Casos (U3 + U4)** | sistema 3×3 por Gauss (repaso) · calibración con ecuaciones normales resueltas por Gauss · serie de Fourier (tarea extra) |

> 📝 **Versión v2 del cuaderno 03.** `notebooks/U4_03_Minimos_Cuadrados_v2.ipynb`
> cubre los mismos métodos con explicaciones ampliadas de cada figura
> (PT5.1, 17.2, 17.4, 17.11 y 13.6) y con **el código escrito dentro del
> cuaderno**: no hace falta editar `ejercicios/`, tener cuenta de GitHub ni usar
> Codespaces. En Colab solo se descarga el material del curso (solo lectura).

### 🔁 El flujo de cada método

1. **Explicación.** Teoría corta, ecuación numerada del libro y figura.
2. **A mano.** `mano_enunciado(...)` con datos sembrados por tu número de
   control. Reportas los valores con **4 decimales** y `mano_comprueba(...)`
   te dice si están dentro de tolerancia (no revela la respuesta).
3. **Programar.** Completas la función —en el archivo de `ejercicios/` que ya
   viene armado o, en la versión v2, en una celda del propio cuaderno— y la
   pruebas con `practica(...)`.
4. **Laboratorio.** `visualizar.laboratorio(...)` dibuja el método y tu
   resultado.
5. **Preguntas.** Una o dos preguntas **teóricas** de opción múltiple, dentro
   del mismo método. Se contestan cuando tu función ya funciona.

### 🧩 Qué se califica

- **Las preguntas de cada cuaderno son teóricas** de opción múltiple
  (6 en el 01, 4 en el 02, 5 en el 03 y 3 en el 04). El código se escribe en
  `ejercicios/` y se comprueba con `practica(...)`, así que la calificación
  evalúa el criterio, no la transcripción del algoritmo.
- Las **actividades a mano** se verifican localmente y quedan como evidencia;
  no restan puntos si te equivocas, pero sí te avisan.
- El puntaje se normaliza a **100** y **cada pregunta vale según su
  dificultad** (`peso:` en su archivo de `preguntas/`): en el cuaderno 03, por
  ejemplo, valen 15, 20, 20, 20 y 25. `calificar()` muestra el total y el
  backend recibe los pesos para guardar el mismo número.

El cuaderno 04 cierra el puente entre unidades: las **ecuaciones normales** de
un ajuste son un sistema lineal, y se resuelven con eliminación gaussiana
(Unidad 3). Por eso incluye `gauss_solve` y `coeficientes_calibracion`, que
arma el sistema y lo resuelve llamando a `gauss_solve`.

### 📦 Dónde vive el motor

`grader/<cuaderno>.txt` es un blob (base64 + zlib) con el motor y las preguntas
de ese cuaderno. El cuaderno lo carga en memoria: así funciona igual en Colab,
en Codespaces y en local, **sin** depender de la rama privada `test`.

---

## 🗺️ Mapa del repositorio

```text
U4_Repo/
├── README.md                      <-- este archivo
├── plan U4_Repo.md                <-- plan de trabajo por fases
├── requirements.txt               <-- dependencias para Codespaces/local
├── .devcontainer/                 <-- Codespaces con Python 3.12
├── .github/workflows/pages.yml    <-- publica la teoría en GitHub Pages
├── site/                          <-- plantilla HTML, CSS y guía del sitio
├── docs/
│   ├── metodos/                   <-- teoría de apoyo (el cuaderno la resume)
│   │   ├── 01_interpolacion_lineal_cuadratica.md
│   │   ├── 02_newton_diferencias_divididas.md
│   │   ├── 03_lagrange.md
│   │   ├── 04_minimos_cuadrados_lineal_cuadratico.md
│   │   └── 05_comparativa_interpolacion_regresion.md
│   └── aplicaciones/              <-- tres fichas de aplicación
│       ├── aplicaciones_index.md
│       ├── ap1_trayectoria_robot.md
│       ├── ap2_fourier_lineas_imagen.md
│       └── ap3_calibracion_sensor.md
├── docs/casos_estudio/            <-- casos con problema, método y comparación
│   ├── README.md
│   ├── caso01_interpolacion_ln2.md
│   ├── caso02_robot_trayectoria.md
│   ├── caso03_sensor_regresion.md
│   └── caso04_fourier_lineas.md
├── docs/figuras/                  <-- figuras generadas por tools/generar_figuras.py
│   └── libro/                     <-- figuras del libro (con atribución)
├── ejercicios/                    <-- una función por archivo, con __main__
│   ├── interpolacion/
│   ├── newton_lagrange/
│   ├── minimos_cuadrados/
│   └── casos/
├── grader/                        <-- un blob por cuaderno (lo que carga Colab)
├── notebooks/                     <-- los cuatro cuadernos
├── lib/
│   ├── robomat.py                 <-- biblioteca del curso (sintaxis MATLAB)
│   ├── ajuste_curvas.py           <-- funciones de la unidad
│   └── mn_motor/                  <-- motor de calificación (privado, no se publica)
├── preguntas/                     <-- preguntas teóricas (privado, no se publica)
├── tests/
│   ├── test_ajuste_curvas.py      <-- pruebas contra los ejemplos del libro
│   └── test_mn_motor.py           <-- pruebas del motor y sus solvers
├── config/
│   └── config.yaml                <-- parámetros de la unidad
└── tools/                         <-- utilidades locales
    ├── verificar.py
    ├── generar_figuras.py
    ├── build_site.py
    └── visualizar.py              <-- laboratorios gráficos (público)
```

---

## 🚀 Cómo se usan los cuadernos

### En VS Code (local)

1. Abre el cuaderno desde `notebooks/`.
2. Ejecuta la **primera celda**: detecta que estás en local y usa los archivos
   del repositorio directamente, **sin pedirte ningún enlace**.
3. Trabaja el cuaderno de arriba abajo.
4. Las preguntas se califican con el motor que trae el propio repo.

### En Google Colab

1. Haz un **fork público** del repositorio del curso y trabaja **en tu fork**:
   edita los archivos directamente en GitHub y confirma cada cambio (commit).
   No hace falta Codespaces.
2. Abre el cuaderno desde tu fork en Colab.
3. Ejecuta la **primera celda**. Monta tu Drive y te pide **una sola vez** el
   enlace de tu fork; lo guarda en `MyDrive/CursoMN/u4_repo.json` y en las
   siguientes sesiones lo reutiliza sin volver a preguntar.
4. Cada vez que ejecutes esa celda se **actualiza sola**, en dos pasos:
   - tus commits de GitHub (`merge --ff-only` con tu fork);
   - el material del curso desde `upstream/main` (`lib/`, `grader/`, `config/`,
     `docs/`, `ejercicios/`, `tools/`), aunque tu fork esté atrasado.

   Vuelve a ejecutarla después de cada commit y sigue con la celda de
   identificación.

> 📦 El motor viaja **empaquetado** en `grader/<cuaderno>.txt`: el cuaderno no
> depende de que tu fork tenga `lib/mn_motor`. Las credenciales del backend
> también viajan ahí, así que un fork viejo nunca usa un token caducado.

> 🧪 Para probar el camino de Colab sin subir nada a Drive:
> `python tools/simular_colab.py` monta un Drive falso y ejecuta las celdas
> desde un directorio que no es el repositorio (igual que `/content`).
> `--ref HEAD` simula lo último publicado, `--clonar` prueba el refresco real
> contra GitHub y `--backend local` usa un Apps Script falso, sin escribir en
> la hoja real.

### En GitHub Codespaces (opcional)

El repo conserva `.devcontainer/devcontainer.json` y `requirements.txt` por si
quieres un entorno completo, pero **el curso no usa Codespaces**: los cambios se
hacen en GitHub y los cuadernos se ejecutan en Colab.

### 🌐 Teoría en GitHub Pages

El renderizador de GitHub no es bueno para matrices dentro de tablas ni para
`\tag{}`. Por eso la teoría se publica como sitio estático:

```bash
python tools/build_site.py        # genera _site/
```

El workflow [.github/workflows/pages.yml](.github/workflows/pages.yml) construye
y publica en GitHub Pages al hacer push a `main`. Requiere elegir **GitHub
Actions** como fuente en *Settings → Pages*. Más detalles en
[site/README.md](site/README.md).

### 📤 Evaluación

| Componente | Peso | Cómo se registra |
|---|:---:|---|
| Cuadernos 01–04 (autoevaluación) | 100% | Local; el profesor puede revisar el cuaderno ejecutado |

> ⚠️ **Limitación de esta versión:** no hay autograder con backend (Apps
> Script). Las preguntas son **teóricas de opción múltiple**, así que no se
> siembran por Número de Control: sólo las actividades a mano usan tus datos.
> La autoevaluación es local en cada cuaderno y se verifica con el motor que
> trae el blob de `grader/`.

---

## 📚 Documentación teórica

Los cuadernos ya traen la teoría resumida. Estos archivos sirven para consultar
las ecuaciones sin abrir el cuaderno, o para exponer:

1. 📖 [**Interpolación lineal y cuadrática**](docs/metodos/01_interpolacion_lineal_cuadratica.md)
   * Ecuaciones (18.2)–(18.6), ejemplo de $\ln 2$ y error (18.16)–(18.18).
2. 📖 [**Newton en diferencias divididas**](docs/metodos/02_newton_diferencias_divididas.md)
   * Forma general (18.7)–(18.15), ejemplo 18.3 y algoritmo.
3. 📖 [**Lagrange**](docs/metodos/03_lagrange.md)
   * Pesos (18.20)–(18.23), ejemplo 18.6 y comparación con Newton.
4. 📖 [**Mínimos cuadrados lineal y cuadrático**](docs/metodos/04_minimos_cuadrados_lineal_cuadratico.md)
   * Criterio (17.3), ecuaciones normales (17.4)–(17.5) y (17.19), error
     (17.9)–(17.11), ejemplos 17.1, 17.2 y 17.5, y ajuste sinusoidal (19.1).
5. 🔄 [**Comparativa interpolación–regresión**](docs/metodos/05_comparativa_interpolacion_regresion.md)
   * Tabla de decisión, costo, errores y puente con optimización (13.2).

---

## 🏭 Aplicaciones

| Ficha | Qué se hace | Método |
|---|---|---|
| [🤖 Robot móvil](docs/aplicaciones/ap1_trayectoria_robot.md) | Interpolar waypoints y estimar velocidad | Newton / Lagrange |
| [🖼️ Imagen de líneas](docs/aplicaciones/ap2_fourier_lineas_imagen.md) | Reconstruir un perfil con armónicos de Fourier | Ecuaciones normales (19.12) |
| [🌡️ Calibración de sensor](docs/aplicaciones/ap3_calibracion_sensor.md) | Elegir entre modelo lineal y cuadrático | Mínimos cuadrados |

## 🧩 Casos de estudio

Formato fijo: **problema → ¿interpolar o ajustar? → método recomendado y por
qué → otros métodos → código → comparación con la librería → verificación →
figura**.

| Caso | Problema | Método recomendado |
|---|---|---|
| [01](docs/casos_estudio/caso01_interpolacion_ln2.md) | Estimar $\ln 2$ | Newton cúbico |
| [02](docs/casos_estudio/caso02_robot_trayectoria.md) | Trayectoria de un robot | Trazador cúbico (`CubicSpline`) |
| [03](docs/casos_estudio/caso03_sensor_regresion.md) | Calibración de un sensor | Mínimos cuadrados cuadráticos |
| [04](docs/casos_estudio/caso04_fourier_lineas.md) | Imagen de líneas | Fourier con $m=5$ |

Las figuras se regeneran con:

```bash
python tools/generar_figuras.py
```

---

## 🛠️ Herramientas

No hay que instalar nada adicional si ya tienes el entorno del curso. La
sintaxis base es **estilo MATLAB** gracias a `robomat.py`:

```python
from ajuste_curvas import newton, evaluar_lagrange, minimos_cuadrados

newton([1.0, 4.0, 6.0], [0.0, 1.386294, 1.791759], 2.0)   # 0.5658444
evaluar_lagrange([1.0, 4.0, 6.0], [0.0, 1.386294, 1.791759], 2.0)
minimos_cuadrados([1, 2, 3, 4, 5, 6, 7],
                  [0.5, 2.5, 2.0, 4.0, 3.5, 6.0, 5.5], grado=1)
```

### Matrices en los cuadernos

| Necesitas | Sintaxis del curso |
|---|---|
| Matriz numérica | `A = M[[1, 2], [3, 4]]` |
| Matriz exacta | `A = M.sym[[1, 2], [3, 4]]` |
| Vector columna | `b = M[[1], [2]]` |
| Mostrar en LaTeX | `mostrar(A)` |
| Resolver un sistema | `A.LUsolve(b)` (exacto) o `solve(A, b)` (numérico) |
| Comparar una respuesta | `verificar(respuesta, esperada)` |

En esta unidad las matrices aparecen sobre todo en las **ecuaciones normales**
(cuaderno 03). Las funciones de `lib/ajuste_curvas.py` reciben listas o
vectores 1-D: la matriz se usa donde el problema es matricial, no para disfrazar
un vector.

### ✅ Pruebas

```bash
python -m unittest discover -s tests -v
# o, desde cualquier carpeta:
python tools/verificar.py
```

En `main` corren las 14 pruebas de `ajuste_curvas`. En la rama `test` se
agregan las del motor y sus solvers (29 en total).

Las pruebas comparan las funciones contra los resultados publicados en el
libro (ejemplos 18.1–18.6, 17.1, 17.2, 17.5, 19.1 y 13.2).

---

### Motor de calificación (privado)

`lib/mn_motor/` y `preguntas/` están en `.gitignore`, igual que en U3: son
material del profesor y viven en la rama `test`, no en `main`. El motor ya
incluye:

- el framework completo (`tarea`, `califica`, `mcq`, `ui`, `envio`, `recursos`);
- `solvers_u4.py` con las referencias exactas de interpolación, mínimos
  cuadrados, Fourier y la parábola de optimización;
- `solvers_u3.py` con Gauss y LU para los casos que mezclan ambas unidades;
- comparación de respuestas escalares y matriciales;
- `preguntas/` con las 18 preguntas teóricas (6 + 4 + 5 + 3), una carpeta por
  cuaderno.

`tools/build_grader.py` empaqueta el motor y sus preguntas en el blob de cada
cuaderno, y verifica que un alumno perfecto saque el puntaje completo.

---

## 🌿 Ramas

- **`main`** — material público: teoría, cuadernos, casos, figuras, sitio y
  biblioteca del alumno.
- **`test`** — rama local con el **motor de calificación** (`lib/mn_motor/`) y
  las preguntas (`preguntas/`). Esos archivos están en `.gitignore` de `main`
  para no publicarse; en `test` se agregan con `git add -f`.

Flujo recomendado:

```bash
git switch main     # trabajar en teoría, cuadernos y casos
git switch test     # trabajar en el motor y las preguntas
```

`experimento/*` sólo se usa para pruebas que podrían descartarse. Los casos y
las figuras ya forman parte de la unidad, así que viven en `main`.

---

## 📖 Fuente y fidelidad

- **Libro:** *Métodos numéricos para ingenieros*, capítulo 5 (ajuste de curvas)
  y sección 13.2 del capítulo 4 (interpolación parabólica).
- **Markdown fuente:** `Contenido/Markdown/5 Ajuste de curvas` y
  `Contenido/Markdown/4 Optimizacion` (no se modificaron).
- Las ecuaciones conservan la numeración del libro. Las **extensiones**
  (robot, imagen, sensor, implementación en Python) están marcadas como tales
  en cada documento.

---

### 📩 Soporte

Si encuentras un error en los algoritmos o en los cuadernos, abre un *Issue* en
el repositorio del curso.
