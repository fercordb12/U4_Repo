# Configuración de la unidad U4

Este archivo explica `config.yaml`.

## Qué contiene

| Bloque | Uso |
|---|---|
| `unidad` | Identificación y lista de temas del programa |
| `evaluacion` | Tolerancia de las celdas de autoevaluación; sin backend |
| `datos` | Datasets de los ejemplos del libro usados en los cuadernos |
| `aplicaciones` | Datos de las fichas de robot y sensor |

## Cómo se usa

Los cuadernos leen los datos directamente de sus celdas para que sean
autosuficientes; `config.yaml` es la **fuente de verdad** para el profesor y
para los scripts de verificación. Si cambias un dataset aquí, actualízalo
también en el cuaderno y en `tests/test_ajuste_curvas.py`.

## Backend

Las credenciales del Apps Script **no se publican** en `main`: aquí
`evaluacion.webhook_token` va vacío y `apps_script_url` sí (la URL no es
secreta). El valor real del token vive en la rama `test` y
`tools/build_grader.py` lo **empaqueta dentro de cada `grader/<cuaderno>.txt`**
al construir los blobs.

Para rotar el token:

1. edita `config/config.yaml` en la rama `test`;
2. `python tools/build_grader.py` (reconstruye y verifica los 4 blobs);
3. copia `grader/*.txt` a `main` y publica.

El motor resuelve las credenciales en este orden: variables de entorno
(`MN_APPS_URL`, `MN_TOKEN`) → blob empaquetado → `config/config.yaml`. Así un
fork atrasado nunca usa un token viejo.
