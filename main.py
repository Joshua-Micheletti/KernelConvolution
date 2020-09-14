from PIL import Image
import numpy as np
import time

def mapValue(value, input_start, input_end, output_start, output_end):
  return(output_start + ((output_end - output_start) / (input_end - input_start)) * (value - input_start))

def mean(x, y, size):
  counter = 0

  r = 0
  g = 0
  b = 0

  relativeSize = int((size - 1) / 2)

  for i in range(-relativeSize, relativeSize):
    for j in range(-relativeSize, relativeSize):
      if x + i < width and x + 1 > 0 and y + j < height and y + j > 0:
        r1, g1, b1 = rgb_im.getpixel((x + i, y + j))
        r += r1
        g += g1
        b += b1
        counter += 1
  
  if counter != 0:
    r = r / counter
    g = g / counter
    b = b / counter

  return int(r), int(g), int(b)

def blur(data, size):
  for i in range(width):
    for j in range(height):
      data.putpixel((i, j), mean(i, j, size))

  return(data)


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

  print("Kernel:")
  print(g)

  return(g)

def weightedMean(x, y, size, weight):
  r = 0
  g = 0
  b = 0

  relativeSize = int((size - 1) / 2)
  for i in range(-relativeSize, relativeSize + 1):
    for j in range(-relativeSize, relativeSize + 1):
      if ((x + i) <= (width - 1) and (x + i) >= 0) and ((y + j) <= (height - 1) and (y + j) >= 0):
        r1, g1, b1 = rgb_im.getpixel((x + i, y + j))
        r += r1 * weight[relativeSize + i][relativeSize + j]
        g += g1 * weight[relativeSize + i][relativeSize + j]
        b += b1 * weight[relativeSize + i][relativeSize + j]

  return int(r), int(g), int(b)

def gaussianBlur(data, size):
  g = gaussian2D(size)

  for i in range(width):
    for j in range(height):
      data.putpixel((i, j), weightedMean(i, j, size, g))

  return(data)


def kernelConvolution(data, kernel, size):
  for i in range(width):
    for j in range(height):
      data.putpixel((i, j), weightedMean(i, j, size, kernel))

  return(data)

def normalizeKernel(kernel):

  total = 0

  for i in range(3):
    for j in range(3):
      total += kernel[i][j]

  for i in range(3):
    for j in range(3):
      kernel[i][j] = mapValue(kernel[i][j], 0, total, 0, 1)

  return(kernel)


outlineKernel = [[-1, -1, -1],
                 [-1,  8, -1],
                 [-1, -1, -1]]

sharpenKernel = [[ 0, -1,  0],
                 [-1,  5, -1],
                 [ 0, -1,  0]]

embossKernel = [[-2, -1,  0],
                [-1,  1,  1],
                [ 0,  1,  2]]

unsharpKernel = [[1,  4,    6,  4, 1],
                 [4, 16,   24, 16, 4],
                 [6, 24, -476, 24, 6],
                 [4, 16,   24, 16, 4],
                 [1,  4,    6,  4, 1]]


im = Image.open("img/landscape.jpg")

width, height = im.size

print("(" + str(width) + ", " + str(height) + ")")

rgb_im = im.convert('RGB')

output = Image.new(mode = "RGB", size = (width, height))

# start = time.time()
# output = blur(output, 7)
# finish = time.time()
# print("%.2f" % (finish - start) + "s")
# print()
# output.save("output/meanBlur.png")

# start = time.time()
# output = gaussianBlur(output, 7)
# finish = time.time()
# print("%.2f" % (finish - start) + "s")
# print()
# output.save("output/gaussianBlur.png")

# start = time.time()
# output = kernelConvolution(output, outlineKernel, 3)
# finish = time.time()
# print("%.2f" % (finish - start) + "s")
# print()
# output.show()
# output.save("output/landscapeoutline.png")

# start = time.time()
# output = kernelConvolution(output, sharpenKernel, 3)
# finish = time.time()
# print("%.2f" % (finish - start) + "s")
# print()
# output.show()
# output.save("output/landscapesharpen.png")

# start = time.time()
# output = kernelConvolution(output, embossKernel, 3)
# finish = time.time()
# print("%.2f" % (finish - start) + "s")
# print()
# output.show()
# output.save("output/landscapeemboss.png")

start = time.time()
output = kernelConvolution(output, unsharpKernel, 5)
finish = time.time()
print("%.2f" % (finish - start) + "s")
print()
output.show()
output.save("output/landscapeunsharpen.png")




