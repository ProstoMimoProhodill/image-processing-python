from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import time
import os, glob
import sys
import cv2
import math
import codecs
import csv

alphabet = "a b c d e f g h i j k l m n o p q r s t u v w x y z"

def timer(f):
    def decorator(arg):
        t = time.time()
        f(arg)
        print("\x1b[1;32;40m[INFO]\x1b[0mTime: {time}s | Function: {function_name}".format(time = str(round(time.time() - t, 5)),function_name = f.__name__))
    return decorator

def create_text_images(arg):
    text = str(arg.get('text'))
    font_size = int(arg.get('font_size'))
    filename = str(arg.get('filename'))

    if filename is None:
        filename = text

    font = ImageFont.truetype("Times_New_Roman.ttf", font_size, encoding='UTF-8')
    image = Image.new('L', (5000, 5000), (255))
    draw = ImageDraw.Draw(image)
    codecs.decode(text.encode('UTF-8'), 'UTF-8')
    draw.text((10,-10), text, fill=0x000000, font=font, language="cyrl")
    image.save("./{symbol}.bmp".format(symbol=filename))
    image = Image.open("./{symbol}.bmp".format(symbol=filename)).convert('1')
    image.save("./{symbol}.bmp".format(symbol=filename))
    image = Image.open("./{symbol}.bmp".format(symbol=filename))
    w, h = image.size
    img_array = np.array(image).astype(int)
    min_w, max_w, min_h, max_h = w, -1, h, -1
    for y in range(0,h):
        if img_array[y].min() == 0 and max_h == -1:
            min_h = y
            max_h = min_h
        elif img_array[y].min() == 0:
            max_h = y
    for y in range(min_h,max_h):
        for x in range(0,w):
            if img_array[y][x].min() == 0 and x < min_w:
                min_w = x
            if img_array[y][x].min() == 0 and x > max_w:
                max_w = x
    crop = image.crop((min_w,min_h,max_w,max_h))
    crop.save("./{symbol}.bmp".format(symbol=filename))

def create_profiles(arg):
    image_name = arg.get("image_name")
    img = Image.open(image_name + ".bmp")
    pix = img.load()
    w, h = img.size
    profile_hor = np.zeros(w, dtype=int)
    profile_vert = np.zeros(h, dtype=int)

    for j in range(h):
        for i in range(w):
            if (pix[i, j] == 0):
                a = 1
            else:
                a = 0
            profile_hor[i] += a
            profile_vert[j] += a

    arr_profile_vert = np.full((h,w), (255), dtype=np.uint8)
    arr_profile_hor = np.full((h,w), (255), dtype=np.uint8)
    for j in range(h):
        own_i = 0
        for i in range(w):
            if (profile_vert[j] > i):
                arr_profile_vert[j][own_i] = 0
                own_i += 1

    for i in range(w):
        own_j = 0
        for j in range(h):
            if (profile_hor[i] > j):
                arr_profile_hor[own_j][i] = 0
                own_j += 1

    im_profile_vert = Image.fromarray(arr_profile_vert)
    filename = "./profiles_" + image_name + "_hor" + ".png"
    im_profile_vert.save(filename, "PNG")

    im_profile_hor = Image.fromarray(arr_profile_hor)
    filename = "./profiles_" + image_name + "_vert" + ".png"
    transposed_image = im_profile_hor.transpose(Image.ROTATE_180)
    transposed_image.transpose(Image.FLIP_LEFT_RIGHT).save(filename, "PNG")

def segmentation(arg):
    image_name = arg.get('image_name')
    img_profile_vert = Image.open("profiles_{name}_vert.png".format(name=image_name))
    w, h = img_profile_vert.size
    pix = img_profile_vert.load()

    arr = [0]*w
    for i in range(w):
        sum = 0
        for j in range(h):
            if pix[i, j] == 0:
                sum += 1
        arr[i] = sum

    top_x, top_y, bottom_x,  bottom_y = 0,0,0,0
    bounds = []
    bounds_open = True

    def bool_separator(element, arr, thrashhold):
        if element == min(arr) or element <= min(arr) + thrashhold:
            return True
        return False

    thrashhold = 0
    for i in range(w):
        if i == w-1 and bounds_open:
            bounds.append([top_x, top_y, i, h])
            bounds_open = False
        if bool_separator(arr[i], arr, thrashhold) and bounds_open:
            bounds.append([top_x, top_y, i, h])
            bounds_open = False
        if i != 0 and not bool_separator(arr[i], arr, thrashhold) and bool_separator(arr[i-1], arr, thrashhold) and not bounds_open:
            bounds_open = True
            top_x = i
            top_y = 0

    img = Image.open(image_name + ".bmp")
    img_res = Image.new('RGB', img.size, (255, 255, 255))
    img_res.paste(img)
    draw_res = ImageDraw.Draw(img_res)
    for i in range(len(bounds)):
        draw_res.rectangle(bounds[i], fill=None, outline='red')
    img_res.save(image_name + "_bounds.bmp")

    measure_of_close({'image_name': image_name, 'bounds': bounds})


def measure_of_close(arg):
    def euclidean_distance(first_parameters, second_parameters):
        sum = 0
        for i in range(len(first_parameters)):
            sum += (((first_parameters[i] - second_parameters[i])**2))
        return 1 - math.sqrt(sum)

    def parameters(img_profile_vert):
        w, h = img_profile_vert.size
        pix = img_profile_vert.load()
        weight_black, gravity_center_x, gravity_center_y, axis_moment_vert, axis_moment_hor = 0,0,0,0,0
        weight_rel, norm_gravity_center_x, norm_gravity_center_ym, norm_axis_moment_vert, norm_axis_moment_hor = 0,0,0,0,0
        for j in range(h):
            for i in range(w):
                if pix[i,j] == 0:
                    a = 1
                else:
                    a = 0
                weight_black += a
                gravity_center_x += i*a
                gravity_center_y += j*a
        weight_rel = round(float(float(weight_black) / (h*w)), 5)
        gravity_center_x = gravity_center_x / weight_black
        gravity_center_y = gravity_center_y / weight_black
        for j in range(h):
            for i in range(w):
                if pix[i,j] == 0:
                    a = 1
                else:
                    a = 0
                axis_moment_vert += ((j - gravity_center_y)**2)*a
                axis_moment_hor += ((i - gravity_center_x)**2)*a
        norm_axis_moment_vert = round(float(float(axis_moment_vert)/float((w)**2+(h)**2))/weight_black, 5)
        norm_axis_moment_hor = round(float(float(axis_moment_hor)/float((w)**2+(h)**2))/weight_black, 5)
        norm_gravity_center_x = round(float(gravity_center_x)/w, 5)
        norm_gravity_center_y = round(float(gravity_center_y)/h, 5)
        return weight_rel, norm_gravity_center_x, norm_gravity_center_y, norm_axis_moment_hor, norm_axis_moment_vert

    def sort_criteria(x):
        return x[1]

    image_name = arg.get('image_name')
    bounds = arg.get('bounds')
    file = open('classifiction_{name}.txt'.format(name=image_name), 'w')
    file.write("")
    file = open('classifiction_{name}.txt'.format(name=image_name), 'a')
    for i in range(len(bounds)):
        res = []
        img_profile_vert = Image.open("profiles_{name}_vert.png".format(name=image_name)).crop(bounds[i])
        img_profile_vert_parameters = parameters(img_profile_vert)
        for j in range(len(alphabet.split())):
            alphabet_profile = Image.open("./profiles/vert/{letter}_vert.png".format(letter=alphabet.split()[j]))
            alphabet_profile_parameters = parameters(alphabet_profile)
            distance = euclidean_distance(img_profile_vert_parameters, alphabet_profile_parameters)
            res.append((alphabet.split()[j], round(distance,2)))
        res = sorted(res, key=sort_criteria, reverse=True)
        file.write(str((i+1, res)))
        file.write('\n')
        print("{count}:{res}".format(count=i+1,res=res[0:3]))
    file.close()

def experiment(arg):
    image_name = arg.get('image_name')
    font_size = int(arg.get('font_size'))

    create_text_images({'filename': "{name}_{size}".format(name=image_name, size=font_size), 'text': image_name, 'font_size': font_size})
    create_profiles({'image_name': "{name}_{size}".format(name=image_name, size=font_size)})
    segmentation({'image_name': "{name}_{size}".format(name=image_name, size=font_size)})

@timer
def main(arg):
    # create_text_images({'filename': "mars_52", 'text': "mars", 'font_size': 52})
    # create_profiles({'image_name': "mars"})
    # segmentation({'image_name': "mars"})
    # experiment({'image_name': "mars", 'font_size': 75})


    create_text_images({'filename': "cat", 'text': "cat", 'font_size': 52})
    create_profiles({'image_name': "cat"})
    segmentation({'image_name': "cat"})
    # experiment({'image_name': "alphabet", 'font_size': 75})

if __name__ == '__main__':
    main({})
