import numpy as np

def mapValue(value, input_start, input_end, output_start, output_end):
  return(output_start + ((output_end - output_start) / (input_end - input_start)) * (value - input_start))


def generateBlurKernel(size):
  blurKernel = [[0 for i in range(size)] for j in range(size)]

  value = 1 / (size * size)

  for i in range(size):
    for j in range(size):
      blurKernel[i][j] = value

  return(blurKernel)

def gaussian2D(size):
  x, y = np.meshgrid(np.linspace(-1,1,size), np.linspace(-1,1,size))
  d = np.sqrt(x*x+y*y)
  sigma, mu = 0.5, 0.0
  g = np.exp(-( (d-mu)**2 / ( 2.0 * sigma**2 ) ) )

  total = 0

  for i in range(size):
    for j in range(size):
      total += g[i][j]

  for i in range(size):
    for j in range(size):
      g[i][j] = mapValue(g[i][j], 0, total, 0, 1)

  return(g)

outlineKernel = [[-1, -1, -1],
                 [-1,  8, -1],
                 [-1, -1, -1]]

sharpenKernel = [[ 0, -1,  0],
                 [-1,  5, -1],
                 [ 0, -1,  0]]

embossKernel = [[-2, -1,  0],
                [-1,  1,  1],
                [ 0,  1,  2]]