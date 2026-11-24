"""coeficientes_newton — cuaderno 02.

Libro: ecuaciones (18.8) a (18.11). Llama a ``tabla_diferencias``.
"""

from ejercicios.newton_lagrange.tabla_diferencias import tabla_diferencias


def tabla_diferencias(x, y):
  n = len(x)
  T = [[0.0] * n for _ in range(n)]

  for i in range(n):
    T[i][0] = float(y[i])

  for j in range(1, n):
    for i in range(j, n):
      T[i][j] = (T[i][j - 1] - T[i - 1][j - 1]) / (x[i] - x[i - j])

  return T



if __name__ == "__main__":
    print(coeficientes_newton([1, 4, 6], [0, 1.386294, 1.791759]))
    # esperado: [0, 0.4620981, -0.0518731]
