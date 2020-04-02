from PIL import Image, ImageDraw
import numpy as np
import time
import os, glob
import sys
import cv2
import math

def getG_x(A):
    G_x = np.array([[3,0,-3],[10,0,-10],[3,0,-3]])
    return G_x.dot(A)

def getG_y(A):
    G_y = np.array([[3,10,3],[0,0,0],[-3,-10,-3]])
    return G_y.dot(A)

def getG(A):
    return np.sqrt((np.power(getG_x(A), 2))+(np.power(getG_y(A), 2)))

def timer(f):
    def decorator(arg):
        t = time.time()
        f(arg)
        print("\x1b[1;32;40m[INFO]\x1b[0mTime: {time}s | Function: {function_name}".format(time = str(round(time.time() - t, 5)),function_name = f.__name__))
    return decorator

@timer
def contur(arg):
    img =  arg.get('img')
    draw = ImageDraw.Draw(img)
    w, h = img.size
    pix = img.load()
    img_array = np.array(img)

    # halftone
    for i in range(w):
        for j in range(h):
            r = pix[i,j][0]
            g = pix[i,j][1]
            b = pix[i,j][2]
            avg = (r+g+b)//3
            draw.point((i,j), (avg, avg, avg))

    img.save("halftone_" + img.filename)

    # contur
    img_res_g_x = Image.new('RGB', (w, h))
    draw_res_g_x = ImageDraw.Draw(img_res_g_x)
    img_res_g_y = Image.new('RGB', (w, h))
    draw_res_g_y = ImageDraw.Draw(img_res_g_y)
    img_res_g = Image.new('RGB', (w, h))
    draw_res_g = ImageDraw.Draw(img_res_g)
    img_res_bin_g = Image.new('RGB', (w, h))
    draw_res_bin_g = ImageDraw.Draw(img_res_bin_g)

    def norm(A):
        step = ((A.max()-A.min())/255)
        if step == 0:
            return np.absolute((A).astype(int))
        return np.absolute((A * (1/step)).astype(int))

    for y in range(2,h,3):
        for x in range(2,w,3):
            a = np.array([[img_array[y-2][x-2][0], img_array[y-2][x-1][0], img_array[y-2][x][0]], [img_array[y-1][x-2][0], img_array[y-1][x-1][0], img_array[y-1][x][0]], [img_array[y][x-2][0], img_array[y][x-1][0], img_array[y][x][0]]])
            G_x = getG_x(a)
            G_y = getG_y(a)
            G = getG(a)

            for j in range(3):
                for i in range(3):
                    a = norm(G_x)[j][i]
                    draw_res_g_x.point((x+i,y+j), (a,a,a))

                    a = norm(G_y)[j][i]
                    draw_res_g_y.point((x+i,y+j), (a,a,a))

                    a = norm(G)[j][i]
                    draw_res_g.point((x+i,y+j), (a,a,a))

                    #bin
                    if norm(G)[j][i] < 200:
                        draw_res_bin_g.point((x+i,y+j), (0,0,0))
                    else:
                        draw_res_bin_g.point((x+i,y+j), (255,255,255))

    img_res_g_x.save("g_x_" + img.filename)
    img_res_g_y.save("g_y_" + img.filename)
    img_res_g.save("g_" + img.filename)
    img_res_bin_g.save("bin_g_" + img.filename)

def main():
    img = Image.open("2.bmp")
    contur({'img': img})

if __name__ == '__main__':
    main()
