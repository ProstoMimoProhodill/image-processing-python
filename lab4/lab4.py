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

def create_alphabet_images(arg):
    for i in range(len(alphabet.split())):
        symbol = alphabet.split()[i]
        font = ImageFont.truetype("Times_New_Roman.ttf", 52, encoding='UTF-8')
        image = Image.new('L', (55, 55), (255))
        draw = ImageDraw.Draw(image)
        codecs.decode(symbol.encode('UTF-8'), 'UTF-8')
        draw.text((10,-10), symbol, fill=0x000000, font=font, language="cyrl")
        image.save("./alphabet/{symbol}.bmp".format(symbol=symbol))
        image = Image.open("./alphabet/{symbol}.bmp".format(symbol=symbol)).convert('1')
        image.save("./alphabet/{symbol}.bmp".format(symbol=symbol))
        image = Image.open("./alphabet/{symbol}.bmp".format(symbol=symbol))
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
        crop.save("./alphabet/{symbol}.bmp".format(symbol=symbol))

def create_profiles(symb, profile_vert, profile_hor, im_wid, im_hei):
	arr_profile_vert = np.full((im_hei, im_wid), (255), dtype=np.uint8)
	arr_profile_hor = np.full((im_hei, im_wid), (255), dtype=np.uint8)
	for j in range(im_hei):
		own_i = 0
		for i in range(im_wid):
			if (profile_vert[j] > i):
				arr_profile_vert[j][own_i] = 0
				own_i += 1

	for i in range(im_wid):
		own_j = 0
		for j in range(im_hei):
			if (profile_hor[i] > j):
				arr_profile_hor[own_j][i] = 0
				own_j += 1

	im_profile_vert = Image.fromarray(arr_profile_vert)
	filename = "./profiles/vert/" + symb + "_vert" + ".png"
	im_profile_vert.save(filename, "PNG")

	im_profile_hor = Image.fromarray(arr_profile_hor)
	filename = "./profiles/hor/" + symb + "_hor" + ".png"
	transposed_image = im_profile_hor.transpose(Image.ROTATE_180)
	transposed_image.transpose(Image.FLIP_LEFT_RIGHT).save(filename, "PNG")

def get_info(image, symb):
	weight_black = 0
	gravity_center_x = 0
	gravity_center_y = 0

	load_image = image.load()
	im_wid, im_hei = image.size
	j = 0
	while (j < im_hei):
		i = 0
		while (i < im_wid):
			if (load_image[i, j] == 0):
				a = 1
			else:
				a = 0
			weight_black += a
			gravity_center_x += i * a
			gravity_center_y += j * a
			i += 1
		j += 1
	square = im_wid * im_hei
	weight_per_sq = float(weight_black) / square
	gravity_center_x = (gravity_center_x) / weight_black
	gravity_center_y = (gravity_center_y) / weight_black
	norm_gravity_center_x = float(gravity_center_x) / (im_wid)
	norm_gravity_center_y = float(gravity_center_y) / (im_hei)

	axis_moment_hor = 0
	axis_moment_vert = 0
	ax_45 = 0
	ax_135 = 0
	profile_hor = np.zeros(im_wid, dtype=int)
	profile_vert = np.zeros(im_hei, dtype=int)

	for j in range(im_hei):
		for i in range(im_wid):
			if (load_image[i, j] == 0):
				a = 1
			else:
				a = 0
			axis_moment_hor += ((j - gravity_center_y)**2) * a
			axis_moment_vert += ((i - gravity_center_x)**2) * a

			ax_45 += ((j - gravity_center_y - i - gravity_center_x) ** 2) * a
			ax_135 += ((j - gravity_center_y + i - gravity_center_x) ** 2) * a

			profile_vert[j] += a
			profile_hor[i] += a

	create_profiles(symb, profile_vert, profile_hor, im_wid, im_hei)
	rel_axis_moment_hor = float(axis_moment_hor) / float(((im_wid)**2 + (im_hei)**2))
	rel_axis_moment_vert = float(axis_moment_vert) / float(((im_wid)**2 + (im_hei)**2))
	norm_ax_45 = float(ax_45) / float(((im_wid)**2 + (im_hei)**2))
	norm_ax_135 = float(ax_135) / float(((im_wid)**2 + (im_hei)**2))

	weight_per_sq = round(weight_per_sq, 4)
	norm_gravity_center_x = round(norm_gravity_center_x, 5)
	norm_gravity_center_y = round(norm_gravity_center_y, 5)
	rel_axis_moment_hor = round(rel_axis_moment_hor, 3)
	rel_axis_moment_vert = round(rel_axis_moment_vert, 3)

	info = weight_black, weight_per_sq, gravity_center_x, gravity_center_y, norm_gravity_center_x, norm_gravity_center_y, axis_moment_hor, axis_moment_vert, rel_axis_moment_hor, rel_axis_moment_vert, norm_ax_45, norm_ax_135
	return info

def write_csv(info, myinfo, symb):
	for i in range(12):
		myinfo.write(str(info[i]))
		if (i <= 10):
			myinfo.write(';')
		else:
			myinfo.write(';')
			myinfo.write(symb)
			myinfo.write('\n')

@timer
def main(arg):
    create_alphabet_images({})

    myinfo = open ("info.csv", "w")
    names = ('weight','weight_per_square','gravity_center_x','gravity_center_y','norm_gc_x','norm_gc_y','axis_moment_x','axis_moment_y','rel_am_x','rel_am_y','norm_ax_45','norm_ax_135')
    for i in range(12):
        myinfo.write(str(names[i]))
        if i<=10:
            myinfo.write(';')
        else:
            myinfo.write('\n')

    for i in range(len(alphabet.split())):
        image = Image.open("./alphabet/{symbol}.bmp".format(symbol=alphabet.split()[i]))
        info = get_info(image, alphabet.split()[i])
        weight_black,weight_per_sq,gravity_center_x,gravity_center_y,norm_gravity_center_x,norm_gravity_center_y,axis_moment_hor,axis_moment_vert,rel_axis_moment_hor,rel_axis_moment_vert,norm_ax_45,norm_ax_135 = info
        write_csv(info, myinfo, alphabet.split()[i])

    myinfo.close()

if __name__ == '__main__':
    main({})
