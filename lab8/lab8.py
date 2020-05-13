import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time
import os, glob
import sys
import math
import statistics

image_name = '2.bmp'

img = Image.open('../{}'.format(image_name))
draw_img = ImageDraw.Draw(img)
hist = Image.new('RGB', (256, 256))
draw_hist= ImageDraw.Draw(hist)
w, h = img.size
pixels = img.load()

hist_array = [0 for i in range(256)]
for i in range(w):
    for j in range(h):
        r = pixels[i,j][0]
        g = pixels[i,j][1]
        b = pixels[i,j][2]
        avg = (r+g+b)//3
        hist_array[avg] += 1
        draw_img.point((i, j), (avg, avg, avg))

img.save('{}-halftone.bmp'.format(image_name.split('.')[0]))
# print(hist_array)


# From lecture
# L = 256
# mean = int((255*(int(statistics.mean(hist_array)) - min(hist_array)))/(max(hist_array) - min(hist_array)))
# min_v = 0
# max_v = 255
# print(mean, min_v, max_v)
#
# positive_range = max(2, max_v - mean)
# negative_range = max(2, mean - min_v)
# print(positive_range, negative_range)
#
# positive_alpha = (pow(2, L-1))/(np.log(positive_range))
# negative_alpha = (pow(2, L-1))/(np.log(negative_range))
#
# positive_alpha = float(str(positive_alpha)[:6])
# negative_alpha = float(str(negative_alpha)[:6])
# print(positive_alpha, negative_alpha)
#
# res = Image.new('RGB', (w, h))
# draw_res= ImageDraw.Draw(res)
# for j in range(h):
#     for i in range(w):
#         r = pixels[i,j][0]
#         g = pixels[i,j][1]
#         b = pixels[i,j][2]
#         avg = (r+g+b)//3
#
#         g = 0
#         f = avg - mean
#         if f >= 1:
#             g = mean + int(positive_alpha * np.log(f))
#         elif f <= -1:
#             g = mean - int(negative_alpha * np.log(abs(f)))
#         else:
#             g = mean
#         draw_res.point((i,j), (g, g, g))
#
# res.save('{}-log.bmp'.format(image_name.split('.')[0]))

# From internet
# g = c * log(1 + f)
# c = 255 / log(L)

L = 256
c = 255 / (np.log(L))
res = Image.new('RGB', (w, h))
draw_res= ImageDraw.Draw(res)
for j in range(h):
    for i in range(w):
        r = pixels[i,j][0]
        g = pixels[i,j][1]
        b = pixels[i,j][2]
        avg = (r+g+b)//3

        r = int(c * np.log(1 + r))
        g = int(c * np.log(1 + g))
        b = int(c * np.log(1 + b))

        draw_res.point((i,j), (r, g, b))

res.save('{}-log.bmp'.format(image_name.split('.')[0]))
