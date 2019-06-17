import os
import subprocess

import cv2
from PIL import Image, ImageDraw, ImageFont

class VideoToTxt:
    def __init__(self, file_path, flag=0):
        self.file_path = file_path
        self.cache_dir = os.path.join(os.path.split(file_path)[0], "Cache")
        self.file_name = os.path.split(file_path)[1]
        self.flag = flag
        # 像素对应ascii码
        self.ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:oa+>!:+. ")

    # 将视频拆分成图片
    def video2txt_jpg(self):
        # LOG.info('开始将视频拆分成图片!')
        # cache_dir = os.path.join(os.path.split(file_path)[0], "Cache")
        vc = cv2.VideoCapture(self.file_path)
        c = 1
        if vc.isOpened():
            r, frame = vc.read()
            if not os.path.exists(self.cache_dir):
                os.mkdir(self.cache_dir)
            os.chdir(self.cache_dir)
        else:
            r = False
            frame = False
        while r:
            # LOG.debug("--->生成第" + str(c) + "张图片")
            # TODO 耗时长的可以用多线程解决程序无响应问题-->无法使用多线程?
            """
            视频每一帧图片是连续的
            """
            cv2.imwrite(str(c) + '.jpg', frame)
            """ 同时转换为ascii图 """
            self.txt2image(str(c) + '.jpg')
            r, frame = vc.read()
            c += 1
        os.chdir('..')
        # LOG.info('视频处理完毕!')
        return vc

    # 将txt转换为图片
    def txt2image(self, txt_file_name):
        # LOG.info('将txt转换成图片')
        im = Image.open(txt_file_name).convert('RGB')
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
                    txt += self.get_char(pixel[0], pixel[1], pixel[2], pixel[3])
                else:
                    txt += self.get_char(pixel[0], pixel[1], pixel[2])
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
        name = txt_file_name
        # LOG.info('txt图片处理完毕!')
        im_txt.save(name)

    # 将像素转换为ascii码
    def get_char(self, r, g, b, alpha=256):
        if alpha == 0:
            return ''
        length = len(self.ascii_char)
        gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
        unit = (256.0 + 1) / length
        return self.ascii_char[int(gray / unit)]

    # 将图片合成视频
    def jpg2video(self, fps):
        # LOG.info('将图片合成视频!')
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        images = os.listdir(self.cache_dir)
        self.cache_dir += "\\"
        im = Image.open(self.cache_dir + images[0])
        outfile_name = os.path.join(self.cache_dir, self.file_name.split(".")[0])
        # TODO 耗时长的可以用多线程解决程序无响应问题
        vw = cv2.VideoWriter(outfile_name + '.avi', fourcc, fps, im.size)

        os.chdir(self.cache_dir)
        for image in range(len(images)):
            # Image.open(str(image)+'.jpg').convert("RGB").save(str(image)+'.jpg')
            frame = cv2.imread(str(image + 1) + '.jpg')
            vw.write(frame)
        os.chdir('..')
        vw.release()
        # LOG.info("txt视频处理完毕!")

    # 调用ffmpeg获取mp3音频文件
    def video2mp3(self):
        # LOG.info("开始获取音频文件!")
        outfile_name = os.path.join(self.cache_dir, self.file_name.split(".")[0]) + '.mp3'
        result = subprocess.call('ffmpeg -i ' + self.file_path + ' -f mp3 ' + outfile_name, shell=True)
        if "不是内部或外部命令" in result:
            raise Exception("ffmpeg未安装!")
        # LOG.info('获取完毕!')
    
    # 合成音频和视频文件
    def video_add_mp3(self, avi_file, mp3_file):
        outfile_name = os.path.join(os.path.split(self.file_path)[0], 'output-txt.mp4')
        # outfile_name = os.path.join(CACHE_DIR, outfile_name.split('\\')[-1])
        subprocess.call('ffmpeg -i ' + avi_file + ' -i ' + mp3_file + ' -strict -2 -f mp4 ' + outfile_name, shell=True)
        # LOG.info("已合成完整视频文件!")

    # 递归删除目录
    def remove_dir(self):
        # LOG.info("开始删除缓存文件!")
        if os.path.exists(self.cache_dir):
            if os.path.isdir(self.cache_dir):
                dirs = os.listdir(self.cache_dir)
                for d in dirs:
                    if os.path.isdir(self.cache_dir + '/' + d):
                        self.cache_dir += '/' + d
                        self.remove_dir()
                    elif os.path.isfile(self.cache_dir + '/' + d):
                        os.remove(self.cache_dir + '/' + d)
                os.rmdir(self.cache_dir)
                return
            elif os.path.isfile(self.cache_dir):
                os.remove(self.cache_dir)
            return

    def main(self):
        vc = self.video2txt_jpg()
        fps = vc.get(cv2.CAP_PROP_FPS)
        vc.release()
        self.jpg2video(fps)
        mp3_flag = True
        try:
            self.video2mp3()
            temp_path = os.path.join(self.cache_dir, self.file_name.split(".")[0])
            self.video_add_mp3(temp_path + '.avi', temp_path + '.mp3')
        except Exception as e:
            mp3_flag = False
            # print('获取音频文件失败,请先安装ffmpeg')
            # print('DOWNLOAD_ADDRESS: https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20190518-c61d16c-win64-static.zip')
        finally:
            # TODO为何没有删除缓存文件夹
            if not self.flag:
                self.remove_dir()
            return mp3_flag

if __name__ == '__main__':
    VideoToTxt(r"C:\Users\hzw\Desktop\output\KO_12_动漫东东资源团.avi").main()


