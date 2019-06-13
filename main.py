import os
import subprocess

import cv2
from PIL import Image, ImageDraw, ImageFont

# 像素对应ascii码
ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:oa+>!:+. ")


# 将视频拆分成图片
def video2txt_jpg(file_path):
    # LOG.info('开始将视频拆分成图片!')
    cache_dir = os.path.join(os.path.split(file_path)[0], "Cache")
    vc = cv2.VideoCapture(file_path)
    c = 1
    if vc.isOpened():
        r, frame = vc.read()
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        os.chdir(cache_dir)
    else:
        r = False
    while r:
        # LOG.debug("--->生成第" + str(c) + "张图片")
        cv2.imwrite(str(c) + '.jpg', frame)
        """ 同时转换为ascii图 """
        txt2image(str(c) + '.jpg')
        r, frame = vc.read()
        c += 1
    os.chdir('..')
    # LOG.info('视频处理完毕!')
    return vc

# 将txt转换为图片
def txt2image(file_name):
    # LOG.info('将txt转换成图片')
    im = Image.open(file_name).convert('RGB')
    # gif拆分后的图像，需要转换，否则报错，由于gif分割后保存的是索引颜色
    raw_width = im.width
    raw_height = im.height
    width = int(raw_width / 6)
    height = int(raw_height / 15)
    im = im.resize((width, height), Image.NEAREST)

    txt = ""
    colors = []
    for i in range(height):
        for j in range(width):
            pixel = im.getpixel((j, i))
            colors.append((pixel[0], pixel[1], pixel[2]))
            if len(pixel) == 4:
                """ 将像素转换为ascii码 """
                txt += get_char(pixel[0], pixel[1], pixel[2], pixel[3])
            else:
                txt += get_char(pixel[0], pixel[1], pixel[2])
        txt += '\n'
        colors.append((255, 255, 255))
    im_txt = Image.new("RGB", (raw_width, raw_height), (255, 255, 255))
    dr = ImageDraw.Draw(im_txt)
    # font = ImageFont.truetype(os.path.join("fonts","汉仪楷体简.ttf"),18)
    font = ImageFont.load_default().font
    x = y = 0
    # 获取字体的宽高
    font_w, font_h = font.getsize(txt[1])
    font_h *= 1.37  # 调整后更佳
    # ImageDraw为每个ascii码进行上色
    for i in range(len(txt)):
        if txt[i] == '\n':
            x += font_h
            y = -font_w
        # self, xy, text, fill = None, font = None, anchor = None,
        # *args, ** kwargs
        dr.text((y, x), txt[i], fill=colors[i])
        # dr.text((y, x), txt[i], font=font, fill=colors[i])
        y += font_w
    name = file_name
    # LOG.info('txt图片处理完毕!')
    im_txt.save(name)

# 将像素转换为ascii码
def get_char(r, g, b, alpha=256):
    if alpha == 0:
        return ''
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
    unit = (256.0 + 1) / length
    return ascii_char[int(gray / unit)]

# 将图片合成视频
def jpg2video(outfile_first_name, fps):
    # LOG.info('将图片合成视频!')
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    cache_dir = os.path.join(outfile_first_name, "Cache")
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    images = os.listdir(cache_dir)
    cache_dir += "\\"
    im = Image.open(cache_dir + images[0])
    outfile_name = os.path.join(cache_dir, cache_dir.split('\\')[-1])
    vw = cv2.VideoWriter(outfile_name + '.avi', fourcc, fps, im.size)

    os.chdir(cache_dir)
    for image in range(len(images)):
        # Image.open(str(image)+'.jpg').convert("RGB").save(str(image)+'.jpg')
        frame = cv2.imread(str(image + 1) + '.jpg')
        vw.write(frame)
    os.chdir('..')
    vw.release()
    # LOG.info("txt视频处理完毕!")

# 调用ffmpeg获取mp3音频文件
def video2mp3(file_path):
    # LOG.info("开始获取音频文件!")
    outfile_name = file_path.split('.')[0] + '.mp3'
    cache_dir = os.path.join(os.path.split(file_path)[0], "Cache")
    outfile_name = os.path.join(cache_dir, outfile_name.split('\\')[-1])
    subprocess.call('ffmpeg -i ' + file_path + ' -f mp3 ' + outfile_name, shell=True)
    # LOG.info('获取完毕!')

# 合成音频和视频文件
def video_add_mp3(file_path, avi_file, mp3_file):
    outfile_name = os.path.join(file_path, 'output-txt.mp4')
    # outfile_name = os.path.join(CACHE_DIR, outfile_name.split('\\')[-1])
    subprocess.call('ffmpeg -i ' + avi_file + ' -i ' + mp3_file + ' -strict -2 -f mp4 ' + outfile_name, shell=True)
    # LOG.info("已合成完整视频文件!")



def main(file_path):
    vc = video2txt_jpg(file_path)
    fps = vc.get(cv2.CAP_PROP_FPS)
    vc.release()
    jpg2video(os.path.split(file_path)[0], fps)
    try:
        video2mp3(file_path)
        video_add_mp3(os.path.split(file_path)[0], file_path.split('.')[0] + '.avi', file_path.split('.')[0] + '.mp3')
    except Exception as e:
        print('获取音频文件失败,请先安装ffmpeg')
        print('DOWNLOAD_ADDRESS: https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20190518-c61d16c-win64-static.zip')

if __name__ == '__main__':
    main(r"C:\Users\hzw\Desktop\output\KO_12_动漫东东资源团.avi")


