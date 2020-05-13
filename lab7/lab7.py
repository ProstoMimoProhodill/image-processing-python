# variant 6, matrix haralic, dispersion
# d = 3, phi = {45,135,225,315}
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import time
import os, glob
import sys
import cv2
import math
import codecs
import csv

def timer(f):
    def decorator(arg):
        t = time.time()
        f(arg)
        print("\x1b[1;32;40m[INFO]\x1b[0mTime: {time}s | Function: {function_name}".format(time = str(round(time.time() - t, 5)),function_name = f.__name__))
    return decorator

def halftone_averaging(arg):
    img =  arg.get('img')
    draw = ImageDraw.Draw(img)
    w, h = img.size
    pixels = img.load()

    for i in range(w):
        for j in range(h):
            r = pixels[i,j][0]
            g = pixels[i,j][1]
            b = pixels[i,j][2]
            avg = (r+g+b)//3
            draw.point((i,j), (avg, avg, avg))
    return img

def create_haralic_matrix(arg):
    img_name = arg.get('img_name')
    img = Image.open(img_name)
    halftone = halftone_averaging({'img': img})
    halftone_draw = ImageDraw.Draw(halftone)
    w, h = halftone.size
    pix = halftone.load()

    phi = [0, 45, 135, 225, 315]
    d = 3

    def phiToCoord(x,y,d,phi):
        if phi == 0:
            return x+d, y
        if phi == 45:
            return x+d, y+d
        if phi == 135:
            return x+d, y-d
        if phi == 225:
            return x-d, y-d
        if phi == 315:
            return x-d, y+d
        return 0, 0

    for k in range(0, len(phi)):
        haralic_matrix = [[0 for i in range(256)] for j in range(256)]
        for j in range(h):
            for i in range(w):
                x, y = phiToCoord(i,j,d,phi[k])
                if not (x < 0 or y < 0 or x > w-1 or y > h-1):
                    p1 = pix[i,j][0]
                    p2 = pix[x,y][0]
                    haralic_matrix[p1][p2] += 1

        max_v = max(max(haralic_matrix))
        min_v = min(min(haralic_matrix))

        img_matrix =  Image.new('RGB', (256, 256))
        draw_matrix = ImageDraw.Draw(img_matrix)

        if max_v == 0:
            img_matrix.save('{}-{}-{}.bmp'.format(img_name.split('.')[0], str(d), str(phi[k])))
        else:
            for j in range(256):
                for i in range(256):
                    haralic_matrix[i][j] = int((255*(haralic_matrix[i][j] - min_v))/(max_v - min_v))
                    avg = haralic_matrix[i][j]
                    draw_matrix.point((i,j), (avg,avg,avg))

            # img_matrix.save('{}-{}-{}.bmp'.format(img_name.split('.')[0], str(d), str(phi[k])))

            P_i, P_j, U_i, U_j, D_i, D_j = 0, 0, 0, 0, 0, 0
            for i in range(256):
                for j in range(256):
                    P_j += haralic_matrix[i][j]
                U_i += i * P_j
            for j in range(256):
                for i in range(256):
                    P_i += haralic_matrix[i][j]
                U_j += j * P_i
            for j in range(256):
                D_i += pow((j - U_i), 2) * P_i
            for i in range(256):
                D_j += pow((i - U_j), 2) * P_j
            print('\n{}-{}-{}.bmp\nD_i: {}\nD_j: {}\n'.format(img_name.split('.')[0], str(d), str(phi[k]),D_i, D_j))

@timer
def main(arg):
    for file in glob.glob("1.jpg"):
        print("Select " + file)
        create_haralic_matrix({'img_name': file})
        # Uncomment save method

if __name__ == '__main__':
    main({})
