from PIL import Image, ImageDraw, ImageChops
import numpy as np
import time
import os, glob

def timer(f):
    def decorator(arg):
        t = time.time()
        f(arg)
        print("\x1b[1;32;40m[INFO]\x1b[0mTime: {time}s | Function: {function_name}".format(time = str(round(time.time() - t, 5)),function_name = f.__name__))
    return decorator

@timer
def logic_filter(arg):
    img =  arg.get('img')
    draw = ImageDraw.Draw(img)
    w, h = img.size
    pix = img.load()

    img_res = Image.new('RGB', (w, h))
    draw_res = ImageDraw.Draw(img_res)

    for y in range(1,h-1):
        for x in range(1,w-1):
            count_w = 0
            count_b = 0
            for j in range(3):
                for i in range(3):
                    if i!=1 or j!=1:
                        if img.getpixel((x-1+i,y-1+j))[0]==0:
                            count_b = count_b + 1
                        elif img.getpixel((x-1+i,y-1+j))[0]==255:
                            count_w = count_w + 1
            if count_w==0:
                draw_res.point((x,y), (0,0,0))
            elif count_b==0:
                draw_res.point((x,y), (255,255,255))
            else:
                draw_res.point((x,y), img.getpixel((x-1+i,y-1+j)))

    img_res.save("./filtered/" + img.filename)

@timer
def xor(arg):
    img =  arg.get('img')
    draw = ImageDraw.Draw(img)
    w, h = img.size

    img_filter = Image.new('RGB', (w, h))
    draw_filter = ImageDraw.Draw(img_filter)

    img_res = Image.new('RGB', (w, h))
    draw_res = ImageDraw.Draw(img_res)

    for y in range(1,h-1):
        for x in range(1,w-1):
            count_w = 0
            count_b = 0
            for j in range(3):
                for i in range(3):
                    if i!=1 or j!=1:
                        if img.getpixel((x-1+i,y-1+j))[0]==0:
                            count_b = count_b + 1
                        elif img.getpixel((x-1+i,y-1+j))[0]==255:
                            count_w = count_w + 1
            if count_w==0:
                draw_filter.point((x,y), (0,0,0))
            elif count_b==0:
                draw_filter.point((x,y), (255,255,255))
            else:
                draw_filter.point((x,y), img.getpixel((x-1+i,y-1+j)))

    img_filter.save("./filtered/" + img.filename)

    for x in range(1,w-1):
        for y in range(1,h-1):
            if img.getpixel((x,y))[0]==img_filter.getpixel((x,y))[0]:
                draw_res.point((x,y), (0,0,0))
            else:
                draw_res.point((x,y), (255,255,255))

    img_res.save("./xor/" + img.filename)

def main():
    for file in glob.glob("2.bmp"):
        print("Select " + file)
        img = Image.open(file)
        # logic_filter({'img': img})
        xor({'img': img})

if __name__ == '__main__':
    main()
