from PIL import Image, ImageDraw
import numpy as np
import time
import os, glob
import sys
import cv2

def timer(f):
    def decorator(arg):
        t = time.time()
        f(arg)
        print("\x1b[1;32;40m[INFO]\x1b[0mTime: {time}s | Function: {function_name}".format(time = str(round(time.time() - t, 5)),function_name = f.__name__))
    return decorator

# oversampling
@timer
def upsampling(arg):
    img =  arg.get('img')
    m =  arg.get('m')
    w, h = img.size
    pix = img.load()

    img_res = Image.new('RGB', (w*m, h*m))
    draw = ImageDraw.Draw(img_res)

    i, j = 0, 0
    new_pix_x, new_pix_y = 0, 0
    for x in range(w*m):
        j = 0
        new_pix_y = 0
        for y in range(h*m):
            if i==m:
                i = 0
                new_pix_x = new_pix_x + 1
            if j==m:
                j = 0
                new_pix_y = new_pix_y + 1

            draw.point((x, y), pix[new_pix_x, new_pix_y])

            j = j + 1
        i = i + 1

    img_res.save("./upsampling/" + img.filename)

@timer
def downsampling(arg):
    img =  arg.get('img')
    n =  arg.get('n')
    w, h = img.size
    pix = img.load()

    img_res = Image.new('RGB', (round(w/n), round(h/n)))
    draw = ImageDraw.Draw(img_res)

    for x in range(0,w,n):
        for y in range(0,h,n):
            draw.point((round(x/n), round(y/n)), pix[x, y])

    img_res.save("./downsampling/" + img.filename)

@timer
def upsampling_and_downsampling(arg):
    img =  arg.get('img')
    m =  arg.get('m')
    n =  arg.get('n')
    w, h = img.size
    pix = img.load()

    img_res = Image.new('RGB', (w*m, h*m))
    draw = ImageDraw.Draw(img_res)

    i, j = 0, 0
    new_pix_x, new_pix_y = 0, 0
    for x in range(w*m):
        j = 0
        new_pix_y = 0
        for y in range(h*m):
            if i==m:
                i = 0
                new_pix_x = new_pix_x + 1
            if j==m:
                j = 0
                new_pix_y = new_pix_y + 1

            draw.point((x, y), pix[new_pix_x, new_pix_y])

            j = j + 1
        i = i + 1

    w, h = img_res.size
    pix = img_res.load()
    img_res_second = Image.new('RGB', (round(w/n), round(h/n)))
    draw = ImageDraw.Draw(img_res_second)

    for x in range(0,w,n):
        for y in range(0,h,n):
            draw.point((round(x/n), round(y/n)), pix[x, y])

    img_res_second.save("./upsampling_and_downsampling/" + img.filename)

@timer
def oversampling(arg):
    img =  arg.get('img')
    k =  arg.get('k')
    w, h = img.size
    pix = img.load()

    img_res = Image.new('RGB', (round(w*k), round(h*k)))
    draw = ImageDraw.Draw(img_res)

    if k <= 1:
        for x in range(0,w,round(1/k)):
            for y in range(0,h,round(1/k)):
                draw.point((round(x*k), round(y*k)), pix[x, y])
    elif k > 1:
        i, j = 0, 0
        new_pix_x, new_pix_y = 0, 0
        for x in range(round(w*k)):
            j = 0
            new_pix_y = 0
            for y in range(round(h*k)):
                if i==round(k):
                    i = 0
                    new_pix_x = new_pix_x + 1
                if j==round(k):
                    j = 0
                    new_pix_y = new_pix_y + 1

                draw.point((x, y), pix[new_pix_x, new_pix_y])

                j = j + 1
            i = i + 1

    img_res.save("./oversampling/" + img.filename)

# halftone reduction
@timer
def halftone_select_chanel(arg):
    img =  arg.get('img')
    chanel = int(arg.get('chanel'))
    w, h = img.size
    try:
        img.split()[chanel].save("./halftone_select_chanel/" + img.filename)
    except Exception as e:
        print("\x1b[1;31;40m[ERROR]\x1b[0mNot chanel")

@timer
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
    img.save("./halftone_averaging/" + img.filename)

@timer
def improved_burnsen_algorithm(arg):
    img =  arg.get('img')
    draw = ImageDraw.Draw(img)
    s =  arg.get('s')
    t =  arg.get('t')
    w, h = img.size
    pix = img.load()

    img_halftone = Image.new('RGB', (w, h))
    draw_halftone = ImageDraw.Draw(img_halftone)

    img_integral = Image.new('RGB', (w, h))
    draw_integral = ImageDraw.Draw(img_integral)

    img_res = Image.new('RGB', (w, h))
    draw_res = ImageDraw.Draw(img_res)

    # halftone
    for i in range(w):
        for j in range(h):
            avg = (pix[i,j][0]+pix[i,j][1]+pix[i,j][2])//3
            draw_halftone.point((i,j), (avg, avg, avg))
    # integral
    integral_table = cv2.integral(np.array(img_halftone))[1:,1:]
    img_integral_table = Image.fromarray(integral_table.astype('uint8'), 'RGB')
    # result
    min_sum = 10000000
    max_sum = -1
    for y in range(s,h-s,s):
        for x in range(s,w-s,s):
            sum = integral_table[y][x][0] + integral_table[y+s][x+s][0] - integral_table[y][x+s][0] - integral_table[y+s][x][0]
            if sum < min_sum:
                min_sum = sum
            if sum > max_sum:
                max_sum = sum

    step = int((max_sum - min_sum) / 255)
    # print("Step: ", step)

    sum = 0
    for y in range(s,h-s,s):
        for x in range(s,w-s,s):
            sum = integral_table[y][x][0] + integral_table[y+s][x+s][0] - integral_table[y][x+s][0] - integral_table[y+s][x][0]
            for j in range(y,y+s,1):
                for i in range(x,x+s,1):
                    if sum==0:
                        a = int(integral_table[j][i][0]) / step
                    else:
                        a = int(((integral_table[j][i][0]/sum))) / step
                        # print("a: ", a)
                        # input()
                    if a < t:
                        draw_res.point((i,j), (0,0,0))
                    else:
                        draw_res.point((i,j), (255,255,255))
    img_res.save("./burnsen/" + img.filename)

def main():
    for file in glob.glob("cell.bmp"):
        print("Select " + file)
        img = Image.open(file)

        # upsampling({'img': img, 'm': 2})
        # downsampling({'img': img, 'n': 2})
        # upsampling_and_downsampling({'img': img, 'm': 6,'n': 2})
        # oversampling({'img': img, 'k': 4})
        #
        # halftone_averaging({'img': img})
        # halftone_select_chanel({'img': img, 'chanel': 2})

        improved_burnsen_algorithm({'img': img, 's': 3, 't': 200})


if __name__ == '__main__':
    main()
