from PIL import Image, ImageDraw
import numpy as np
import time
import os, glob
import sys
import cv2
import math
from matplotlib import cm

sys.setrecursionlimit(15000)


def getG_x(A):
    G_x = np.array([[3,0,-3],[10,0,-10],[3,0,-3]])
    return G_x.dot(A)

def getG_y(A):
    G_y = np.array([[3,10,3],[0,0,0],[-3,-10,-3]])
    return G_y.dot(A)

def getG(A):
    # print("x",getG_x(A))
    # print("y",getG_y(A))
    #
    # print("x2", np.power(getG_x(A), 2))
    # print("y2", np.power(getG_y(A), 2))

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

    def norm(A):
        step = ((A.max()-A.min())/255)
        if step == 0:
            return np.absolute((A).astype(int))
        return np.absolute((A * (1/step)).astype(int))

    for y in range(2,h,3):
        res = 0
        for x in range(2,w,3):
            a = np.array([[img_array[y-2][x-2][0], img_array[y-2][x-1][0], img_array[y-2][x][0]], [img_array[y-1][x-2][0], img_array[y-1][x-1][0], img_array[y-1][x][0]], [img_array[y][x-2][0], img_array[y][x-1][0], img_array[y][x][0]]])
            # print('x  ', x, 'y  ',y)
            # print(a)
            G_x = getG_x(a)
            G_y = getG_y(a)
            G = getG(a)
            # res = G

            # print(G_x)
            # print(G_y)
            # print(G)

            # print(norm(G_x))
            # print(norm(G_y))
            res = norm(G_x)
            # print(res)

            # input()

        # print(res)
        # input()

        for j in range(3):
            for i in range(3):
                a = res[j][i]
                draw.point((x+i,y+j), (a,a,a))

                #bin
                # if res[j][i] < 200:
                #     draw.point((x+i,y+j), (0,0,0))
                # else:
                #     draw.point((x+i,y+j), (255,255,255))

    img.save("test.bmp")


def main():
    img = Image.open("2.bmp")
    contur({'img': img})

if __name__ == '__main__':
    main()
