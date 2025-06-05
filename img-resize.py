#!/usr/bin/env python3
from PIL import Image, ImageOps
import os
from collections import Counter

def get_dominant_edge_color(img):
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        return None  # transparent image
    pixels = img.convert('RGB').load()
    width, height = img.size
    edge_pixels = []

    for x in range(width):
        edge_pixels.append(pixels[x, 0])           # top
        edge_pixels.append(pixels[x, height - 1])  # bottom
    for y in range(height):
        edge_pixels.append(pixels[0, y])           # left
        edge_pixels.append(pixels[width - 1, y])   # right

    most_common = Counter(edge_pixels).most_common(1)
    return most_common[0][0] if most_common else (255, 255, 255)

def make_square(img, fill_color=(255, 255, 255)):
    width, height = img.size
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        if len(fill_color) == 3:
            fill_color = (*fill_color, 0)
        img = img.convert("RGBA")

    if width > height:
        delta = width - height
        padding = (0, delta // 2, 0, delta - delta // 2)
        img = ImageOps.expand(img, padding, fill_color)
    elif height > width:
        delta = height - width
        extra = max(10, delta // 10)  # add a bit more margin to top/bottom
        padding = (delta // 2 + extra, 0, delta - delta // 2 + extra, 0)
        img = ImageOps.expand(img, padding, fill_color)

    return img
input_dir = "originals/"
output_dir = "resized/"

os.makedirs(output_dir, exist_ok=True)

for root, _, files in os.walk(input_dir):
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            input_path = os.path.join(root, filename)
            rel_path = os.path.relpath(root, input_dir)
            output_subdir = os.path.join(output_dir, rel_path)
            os.makedirs(output_subdir, exist_ok=True)
            output_path = os.path.join(output_subdir, filename)

            with Image.open(input_path) as img:
                if img.size == (600, 600):
                    print(f"⏭️ {filename} on jo oikean kokoinen, ohitetaan")
                    continue
                fill = get_dominant_edge_color(img)
                if fill is None:
                    fill = (255, 255, 255, 0)
                square_img = make_square(img, fill_color=fill)
                resized_img = square_img.resize((600, 600), Image.LANCZOS)
                resized_img.save(output_path, optimize=True, quality=90)
                print(f"✅ {filename} käsitelty → {output_path}")