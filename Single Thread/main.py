from PIL import Image
import numpy as np
import time
import threading

threadCount = 2
maxKernelSize = 2

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

def weightedMean(x, y, size, weight, data):
  r = 0
  g = 0
  b = 0

  relativeSize = int((size - 1) / 2)

  borderX, borderY = data.size

  for i in range(-relativeSize, relativeSize + 1):
    for j in range(-relativeSize, relativeSize + 1):
      if ((x + i) <= (width - 1) and (x + i) >= 0) and ((y + j) <= (height - 1) and (y + j) >= 0) and ((x + i) <= borderX - 1):
        r1, g1, b1 = data.getpixel((x + i, y + j))
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


def partialKernelConvolution(data, kernel, size, thread):

  excess = (maxKernelSize - 1) / 2
  end = int(width / threadCount)

  for i in range(end):
    for j in range(height):
      if (thread == 0):
        # data.putpixel((i, j), weightedMean(i, j, size, kernel, inputs[thread]))
        data.putpixel((i, j), weightedMean(i, j, size, kernel, image1))
      elif (thread == (threadCount - 1)):
        # data.putpixel((i, j), weightedMean(i + excess, j, size, kernel, inputs[thread]))
        data.putpixel((i, j), weightedMean(i + excess, j, size, kernel, image2))
      else:
        data.putpixel((i, j), weightedMean(i + excess, j, size, kernel, inputs[thread]))

  return(data)

def thread_function(name):
  # start = time.time()
  # output = kernelConvolution(output, outlineKernel, 3)
  # finish = time.time()
  # print("%.2f" % (finish - start) + "s")
  # print()
  # output.show()
  # output.save("output/landscapeoutline.png")
  global image1
  global image2
  if (name == 0):
    image1 = partialKernelConvolution(image1, outlineKernel, 3, name)
  else:
    image2 = partialKernelConvolution(image2, outlineKernel, 3, name)
  # images[name] = partialKernelConvolution(images[name], outlineKernel, 3, name)
  # images[name].show()
  # images[name].save("output/" + str(name) + ".png")


outlineKernel = [[-1, -1, -1],
                 [-1,  8, -1],
                 [-1, -1, -1]]

sharpenKernel = [[ 0, -1,  0],
                 [-1,  5, -1],
                 [ 0, -1,  0]]

embossKernel = [[-2, -1,  0],
                [-1,  1,  1],
                [ 0,  1,  2]]


im = Image.open("img/landscape.jpg")

width, height = im.size

image1 = Image.new(mode = "RGB", size = (int((width / 2) + 1), height))
image2 = Image.new(mode = "RGB", size = (int((width / 2) + 1), height))

print("(" + str(width) + ", " + str(height) + ")")

rgb_im = im.convert('RGB')

output = Image.new(mode = "RGB", size = (width, height))

threads = []
inputs = []
images = []

start = time.time()
# for i in range(threadCount):
#   images.append(Image.new(mode = "RGB", size = (int(width / threadCount), height)))

#   if (i == 0) or (i == (threadCount - 1)):
#     inputs.append(Image.new(mode = "RGB", size = (int((width / threadCount) + (maxKernelSize - 1) / 2), height)))
#   else:
#     inputs.append(Image.new(mode = "RGB", size = (int((width / threadCount) + maxKernelSize - 1), height)))

#   if (i == 0):
#     inputs[i] = rgb_im.crop(((width / threadCount) * i, 0, (width / threadCount) * (i + 1) + (maxKernelSize - 1) / 2, height))
#   elif (i == threadCount - 1):
#     inputs[i] = rgb_im.crop(((width / threadCount) * i - (maxKernelSize - 1) / 2, 0, (width / threadCount) * (i + 1), height))
#   else:
#     inputs[i] = rgb_im.crop(((width / threadCount) * i - (maxKernelSize - 1) / 2, 0, (width / threadCount) * (i + 1) + (maxKernelSize - 1) / 2, height))

#   threads.append(threading.Thread(target = thread_function, args = (i,)))
#   print(inputs[i].size)
#   threads[i].start()

# for i in range(threadCount):
#   threads[i].join()

# for i in range(threadCount):
#   output.paste(images[i], ((int(width / threadCount) * i), 0))


image1 = Image.new(mode = "RGB", size = (int((width / 2) + 1), height))
image2 = Image.new(mode = "RGB", size = (int((width / 2) + 1), height))

output1 = Image.new(mode = "RGB", size = (int((width / 2)), height))
output2 = Image.new(mode = "RGB", size = (int((width / 2)), height))

image1 = rgb_im.crop((0, 0, int(width / 2 + 1), height))
image2 = rgb_im.crop((int(width / 2 - 1), 0, width, height))

# image1.show()
# image2.show()

thread1 = threading.Thread(target = thread_function, args = (0,))
thread2 = threading.Thread(target = thread_function, args = (1,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

# for i in range(2):
#   output.paste(images[i], ((int(width / threadCount) * i), 0))

output.paste()



finish = time.time()
print("%.2f" % (finish - start) + "s")
print()

output.show()

# start = time.time()
# output = kernelConvolution(output, outlineKernel, 3)
# finish = time.time()
# print("%.2f" % (finish - start) + "s")
# print()
# output.show()
# output.save("output/landscapeoutline.png")

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




