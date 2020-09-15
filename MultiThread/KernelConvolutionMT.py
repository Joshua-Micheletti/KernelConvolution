# image editing library
from PIL import Image
# timer library
import time
# threading library
import threading
# os system calls library
import os
# filesystem manager library
import glob
# system manager library
import sys
# find the path of the custom modules
sys.path.append(os.path.abspath("../modules"))
# import the kernel generation module
import kernels

# clean the output folder
try:
  os.mkdir("./output")
except:
  print("Output folder already exists")

files = glob.glob('output/*')
for f in files:
    os.remove(f)

# calculates the pixel value after applying the kernel
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

# cicles through each pixel of the image, calculates the new pixel and stores it in the output image
def partialKernelConvolution(data, kernel, size, thread):
  excess = (kernelSize - 1) / 2
  end = int(width / threadCount)

  for i in range(end):
    for j in range(height):
      if (thread == 0):
        data.putpixel((i, j), weightedMean(i, j, size, kernel, inputs[thread]))
      elif (thread == (threadCount - 1)):
        data.putpixel((i, j), weightedMean(i + excess, j, size, kernel, inputs[thread]))
      else:
        data.putpixel((i, j), weightedMean(i + excess, j, size, kernel, inputs[thread]))

  return(data)

# thread behaviour
def thread_function(name):
  # runs the the convolution algorithm on the data it's given
  images[name] = partialKernelConvolution(images[name], kernel, kernelSize, name)
  # stores the result
  images[name].save("output/" + str(name) + ".png")
  print("Thread " + str(name) + " finished")

# inputs
print("Image directory:")
imageDir = input()

print("Threads: ")
threadCount = int(input())

print("Kernel: (box blur, gaussian blur, sharpen, emboss, outline)")
kernelType = input()

if (kernelType == "box blur" or kernelType == "gaussian blur"):
  print("Kernel size: ")
  kernelSize = int(input())
else:
  kernelSize = 3

# kernel generation
if (kernelType == "box blur"):
  kernel = kernels.generateBlurKernel(kernelSize)
elif (kernelType == "gaussian blur"):
  kernel = kernels.gaussian2D(kernelSize)
elif (kernelType == "sharpen"):
  kernel = kernels.sharpenKernel
elif (kernelType == "emboss"):
  kernel = kernels.embossKernel
elif (kernelType == "outline"):
  kernel = kernels.outlineKernel
else:
  print("Invalid Kernel")

# image unpload
im = Image.open(imageDir)
width, height = im.size

print("picture res: (" + str(width) + ", " + str(height) + ")")

rgb_im = im.convert('RGB')

# data setup
output = Image.new(mode = "RGB", size = (width, height))

threads = []
inputs = []
images = []

# convolution algorithm
start = time.time()
for i in range(threadCount):
  # create a new empty image for the threads to save their work on
  images.append(Image.new(mode = "RGB", size = (int(width / threadCount), height)))

  # create a new empty image for the threads to get data from
  if (i == 0) or (i == (threadCount - 1)):
    inputs.append(Image.new(mode = "RGB", size = (int((width / threadCount) + (kernelSize - 1) / 2), height)))
  else:
    inputs.append(Image.new(mode = "RGB", size = (int((width / threadCount) + kernelSize - 1), height)))

  # pass the image crop to the input data for the threads
  if (i == 0):
    inputs[i] = rgb_im.crop(((width / threadCount) * i, 0, (width / threadCount) * (i + 1) + (kernelSize - 1) / 2, height))
  elif (i == threadCount - 1):
    inputs[i] = rgb_im.crop(((width / threadCount) * i - (kernelSize - 1) / 2, 0, (width / threadCount) * (i + 1), height))
  else:
    inputs[i] = rgb_im.crop(((width / threadCount) * i - (kernelSize - 1) / 2, 0, (width / threadCount) * (i + 1) + (kernelSize - 1) / 2, height))

  # create the threads
  threads.append(threading.Thread(target = thread_function, args = (i,)))
  print("Thread " + str(i) + " res: " + str(inputs[i].size))
  # launch the threads
  threads[i].start()

# wait for the threads to be done executing
for i in range(threadCount):
  threads[i].join()

# merge the results of the threads into a single image
for i in range(threadCount):
  output.paste(images[i], ((int(width / threadCount) * i), 0))

finish = time.time()
print("%.2f" % (finish - start) + "s")

# display and save the result
output.show()
output.save("output/processed.png")

input()
