import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse
import re
import base64
import mimetypes
import binascii

class TextToImageEncryptor:
    def __init__(self, block_width=9, block_height=16, base=2):
        """
        初始化加密器
        :param block_width: 每个位的宽度（像素）
        :param block_height: 每个位的高度（像素）
        :param base: 进制，支持2-16
        """
        self.block_width = block_width
        self.block_height = block_height
        self.base = base
        
        # 定义不同进制的颜色映射
        self.base_colors = {
            2: {  # 二进制
                '0': 'white',
                '1': 'black'
            },
            3: {  # 三进制
                '0': 'white',
                '1': 'blue',
                '2': 'red'
            },
            4: {  # 四进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'red'
            },
            5: {  # 五进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'yellow',
                '4': 'red'
            },
            6: {  # 六进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'red'
            },
            7: {  # 七进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'red'
            },
            8: {  # 八进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'red'
            },
            9: {  # 九进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'red'
            },
            10: {  # 十进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'red'
            },
            11: {  # 十一进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red'
            },
            12: {  # 十二进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred'
            },
            13: {  # 十三进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon'
            },
            14: {  # 十四进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon',
                'D': 'crimson'
            },
            15: {  # 十五进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon',
                'D': 'crimson',
                'E': 'firebrick'
            },
            16: {  # 十六进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon',
                'D': 'crimson',
                'E': 'firebrick',
                'F': 'black'
            }
        }
        
    def text_to_binary(self, text):
        """
        将文本转换为指定进制的表示
        :param text: 要转换的文本
        :return: 指定进制的字符串
        """
        # 将文本转换为UTF-8编码的字节
        bytes_data = text.encode('utf-8')
        
        # 将每个字节转换为指定进制的表示
        result = ""
        for byte in bytes_data:
            # 转换为指定进制
            base_str = ""
            value = byte
            if value == 0:
                base_str = "0"
            else:
                while value > 0:
                    remainder = value % self.base
                    if remainder < 10:
                        base_str = str(remainder) + base_str
                    else:
                        # 对于大于9的值，使用A-F表示
                        base_str = chr(ord('A') + remainder - 10) + base_str
                    value = value // self.base
            
            # 确保每个字节至少有两位（对于大于2的进制）
            if self.base <= 16:
                min_length = 2
            else:
                min_length = 1
                
            while len(base_str) < min_length:
                base_str = "0" + base_str
                
            result += base_str
            
        return result
    
    def create_binary_image(self, binary_string, ignore_pixel_limit=False):
        """
        根据进制字符串创建图像
        :param binary_string: 进制字符串
        :param ignore_pixel_limit: 是否忽略像素限制
        :return: PIL图像对象
        """
        # 计算图像尺寸
        max_width = 800  # 默认最大宽度
        chars_per_row = max_width // self.block_width
        rows = (len(binary_string) + chars_per_row - 1) // chars_per_row
        
        # 创建白色背景图像
        img_width = min(chars_per_row * self.block_width, len(binary_string) * self.block_width)
        img_height = rows * self.block_height
        
        # 安全检查：防止创建过大的图片
        max_pixels = 50000000  # 50兆像素
        total_pixels = img_width * img_height
        if total_pixels > max_pixels and not ignore_pixel_limit:
            raise ValueError(f"要创建的图片尺寸过大 ({img_width}x{img_height} = {total_pixels} 像素)，可能存在安全风险。请减少文本长度或增加块大小。")
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 获取当前进制的颜色映射
        colors = self.base_colors.get(self.base, self.base_colors[2])
        
        # 绘制每个字符
        for i, char in enumerate(binary_string):
            row = i // chars_per_row
            col = i % chars_per_row
            
            x = col * self.block_width
            y = row * self.block_height
            
            # 根据字符选择颜色
            color = colors.get(char.upper(), 'black')  # 默认黑色
            
            # 绘制矩形
            draw.rectangle([x, y, x + self.block_width - 1, y + self.block_height - 1], fill=color)
        
        return img
    
    def encrypt_to_image(self, text, output_path, max_width=800, ignore_pixel_limit=False):
        """
        将文本加密为图片
        :param text: 要加密的文本
        :param output_path: 输出图片路径
        :param max_width: 图片最大宽度，超过时会自动换行
        :param ignore_pixel_limit: 是否忽略像素限制
        :return: 二进制字符串, 实际保存路径
        """
        # 确保生成的图片目录存在
        output_dir = os.path.join(os.getcwd(), "生成的图片")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 如果output_path不是绝对路径，则将其放在"生成的图片"目录中
        if not os.path.isabs(output_path):
            output_path = os.path.join(output_dir, output_path)
        
        # 检查文件是否已存在，如果存在则添加序号
        actual_output_path = output_path
        counter = 1
        while os.path.exists(actual_output_path):
            # 分离文件名和扩展名
            base_name, ext = os.path.splitext(output_path)
            actual_output_path = f"{base_name}_{counter}{ext}"
            counter += 1
        
        # 将文本转换为进制字符串
        base_string = self.text_to_binary(text)
        print(f"进制({self.base})表示: {base_string}")
        print(f"原始文本: {text}")
        
        # 创建图像
        img = self.create_binary_image(base_string, ignore_pixel_limit)
        
        # 保存图像
        img.save(actual_output_path)
        print(f"加密完成! 图像已保存到: {actual_output_path}")
        
        return base_string, actual_output_path


class ImageToTextDecryptor:
    def __init__(self, block_width=9, block_height=16, base=None, ignore_pixel_limit=False):
        """
        初始化解密器
        :param block_width: 每个位的宽度（像素）
        :param block_height: 每个位的高度（像素）
        :param base: 进制，支持2-16，如果为None则自动识别
        :param ignore_pixel_limit: 是否忽略像素限制
        """
        self.block_width = block_width
        self.block_height = block_height
        self.base = base
        self.ignore_pixel_limit = ignore_pixel_limit
        
        # 定义不同进制的颜色映射
        self.base_colors = {
            2: {  # 二进制
                '0': 'white',
                '1': 'black'
            },
            3: {  # 三进制
                '0': 'white',
                '1': 'blue',
                '2': 'red'
            },
            4: {  # 四进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'red'
            },
            5: {  # 五进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'yellow',
                '4': 'red'
            },
            6: {  # 六进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'red'
            },
            7: {  # 七进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'red'
            },
            8: {  # 八进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'red'
            },
            9: {  # 九进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'red'
            },
            10: {  # 十进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'red'
            },
            11: {  # 十一进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red'
            },
            12: {  # 十二进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred'
            },
            13: {  # 十三进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon'
            },
            14: {  # 十四进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon',
                'D': 'crimson'
            },
            15: {  # 十五进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon',
                'D': 'crimson',
                'E': 'firebrick'
            },
            16: {  # 十六进制
                '0': 'white',
                '1': 'blue',
                '2': 'green',
                '3': 'cyan',
                '4': 'yellow',
                '5': 'magenta',
                '6': 'orange',
                '7': 'purple',
                '8': 'pink',
                '9': 'brown',
                'A': 'red',
                'B': 'darkred',
                'C': 'maroon',
                'D': 'crimson',
                'E': 'firebrick',
                'F': 'black'
            }
        }
        
        # 创建反向颜色映射，用于自动识别进制
        self.color_to_base = {}
        for base, colors in self.base_colors.items():
            for char, color in colors.items():
                if color not in self.color_to_base:
                    self.color_to_base[color] = set()
                self.color_to_base[color].add(base)
        
    def extract_binary_from_image(self, img_path):
        """
        从图片中提取进制数据
        :param img_path: 图片路径
        :return: (进制字符串, 识别出的进制)
        """
        # 打开图片
        img = Image.open(img_path)
        img = img.convert('RGB')
        
        # 获取图片尺寸
        img_width, img_height = img.size
        
        # 安全检查：防止处理过大的图片
        max_pixels = 50000000  # 50兆像素
        total_pixels = img_width * img_height
        if total_pixels > max_pixels and not self.ignore_pixel_limit:
            raise ValueError(f"图片尺寸过大 ({img_width}x{img_height} = {total_pixels} 像素)，可能存在安全风险。请使用小于 {max_pixels} 像素的图片。")
        
        # 计算每行可以容纳的字符数
        chars_per_row = img_width // self.block_width
        
        # 计算总行数
        rows = img_height // self.block_height
        
        # 调试信息
        print(f"图像尺寸: {img_width}x{img_height}")
        print(f"块尺寸: {self.block_width}x{self.block_height}")
        print(f"每行字符数: {chars_per_row}")
        print(f"总行数: {rows}")
        
        # 如果没有指定进制，则自动识别
        if self.base is None:
            # 收集图像中出现的所有颜色
            colors_in_image = set()
            rgb_values = []  # 用于调试
            
            # 遍历图像中的每个块
            for row in range(rows):
                for col in range(chars_per_row):
                    x = col * self.block_width + self.block_width // 2
                    y = row * self.block_height + self.block_height // 2
                    
                    # 确保坐标在图像范围内
                    if x < img_width and y < img_height:
                        # 获取像素颜色
                        r, g, b = img.getpixel((x, y))
                        rgb_values.append((r, g, b))  # 用于调试
                        
                        # 简化颜色判断，将RGB值转换为颜色名称
                        color = self._rgb_to_color_name(r, g, b)
                        # 忽略白色背景
                        if color != 'white':
                            colors_in_image.add(color)
            
            # 调试信息
            print(f"识别到的颜色: {colors_in_image}")
            print(f"前10个RGB值: {rgb_values[:10]}")
            print(f"颜色到进制映射: {self.color_to_base}")
            
            # 根据颜色识别进制
            possible_bases = set()  # 初始化为空集合
            
            for color in colors_in_image:
                if color in self.color_to_base:
                    possible_bases.update(self.color_to_base[color])
                    print(f"颜色 '{color}' 对应的进制: {self.color_to_base[color]}")
                else:
                    print(f"警告: 颜色 '{color}' 不在颜色到进制映射中")
            
            print(f"所有可能的进制: {possible_bases}")
            
            if possible_bases:
                # 找出最大的进制
                self.base = max(possible_bases)
                print(f"选择的最大进制: {self.base}")
            else:
                # 无法识别，默认使用二进制
                self.base = 2
                print("无法识别进制，默认使用二进制")
        
        # 获取当前进制的颜色映射
        colors = self.base_colors.get(self.base, self.base_colors[2])
        
        # 创建反向颜色映射（颜色到字符）
        color_to_char = {color: char for char, color in colors.items()}
        
        # 提取进制字符串
        base_string = ""
        
        # 遍历图像中的每个块
        for row in range(rows):
            for col in range(chars_per_row):
                x = col * self.block_width + self.block_width // 2
                y = row * self.block_height + self.block_height // 2
                
                # 确保坐标在图像范围内
                if x < img_width and y < img_height:
                    # 获取像素颜色
                    r, g, b = img.getpixel((x, y))
                    
                    # 简化颜色判断，将RGB值转换为颜色名称
                    color = self._rgb_to_color_name(r, g, b)
                    
                    # 忽略白色背景
                    if color == 'white':
                        continue
                    
                    # 根据颜色获取字符
                    if color in color_to_char:
                        base_string += color_to_char[color]
                    else:
                        # 如果颜色不匹配，尝试找到最接近的颜色
                        closest_char = self._find_closest_color(r, g, b, colors)
                        base_string += closest_char
        
        return base_string, self.base
    
    def _rgb_to_color_name(self, r, g, b):
        """
        将RGB值转换为颜色名称
        :param r: 红色值
        :param g: 绿色值
        :param b: 蓝色值
        :return: 颜色名称
        """
        # 定义一些常见颜色的RGB值
        color_thresholds = {
            'white': (245, 245, 245),
            'black': (10, 10, 10),
            'blue': (0, 0, 200),
            'red': (200, 0, 0),
            'green': (0, 200, 0),
            'yellow': (200, 200, 0),
            'cyan': (0, 200, 200),
            'magenta': (200, 0, 200),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'pink': (255, 192, 203),
            'brown': (165, 42, 42),
            'darkred': (139, 0, 0),
            'maroon': (128, 0, 0),
            'crimson': (220, 20, 60),
            'firebrick': (178, 34, 34)
        }
        
        # 计算与每种颜色的距离
        min_distance = float('inf')
        closest_color = 'white'  # 默认白色
        
        for color_name, (cr, cg, cb) in color_thresholds.items():
            distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        # 如果距离太大，可能是白色背景
        if min_distance > 100:
            return 'white'
        
        return closest_color
    
    def _find_closest_color(self, r, g, b, colors):
        """
        找到与给定RGB值最接近的颜色字符
        :param r: 红色值
        :param g: 绿色值
        :param b: 蓝色值
        :param colors: 颜色映射
        :return: 最接近的颜色字符
        """
        # 将RGB值转换为颜色名称
        color_name = self._rgb_to_color_name(r, g, b)
        
        # 如果颜色在映射中，直接返回对应的字符
        for char, color in colors.items():
            if color == color_name:
                return char
        
        # 如果没有找到，返回默认字符
        return '0'
    
    def binary_to_text(self, base_string):
        """
        将进制字符串转换为文本
        :param base_string: 进制字符串
        :return: 解密后的文本
        """
        # 确定进制
        base = self.base if self.base else 2
        
        # 将进制字符串转换为字节
        byte_data = bytearray()
        
        # 根据进制确定每个字节需要的字符数
        if base <= 4:
            chars_per_byte = 2
        elif base <= 16:
            chars_per_byte = 2
        else:
            chars_per_byte = 1
        
        # 将进制字符串转换为字节
        for i in range(0, len(base_string), chars_per_byte):
            byte_str = base_string[i:i+chars_per_byte]
            if len(byte_str) < chars_per_byte:  # 忽略不完整的字节
                break
            
            try:
                # 将进制字符串转换为整数值
                byte_value = int(byte_str, base)
                byte_data.append(byte_value)
            except ValueError:
                # 如果转换失败，跳过这个字符
                continue
        
        try:
            # 使用UTF-8解码字节
            decoded_text = byte_data.decode('utf-8')
            # 移除可能的空字符
            return decoded_text.replace('\x00', '')
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用其他方式
            text = ""
            for i in range(0, len(base_string), chars_per_byte):
                byte_str = base_string[i:i+chars_per_byte]
                if len(byte_str) < chars_per_byte:
                    break
                try:
                    char_code = int(byte_str, base)
                    if char_code > 0:  # 忽略空字符
                        text += chr(char_code)
                except ValueError:
                    continue
            return text
    
    def decrypt_from_image(self, img_path):
        """
        从图片中解密文本
        :param img_path: 图片路径
        :return: 解密后的文本
        """
        # 提取进制数据
        base_string, base = self.extract_binary_from_image(img_path)
        print(f"提取的进制({base})数据: {base_string}")
        
        # 将进制转换为文本
        text = self.binary_to_text(base_string)
        
        return text
    
    def decrypt_from_image_with_binary(self, img_path):
        """
        从图片中解密文本并返回进制字符串
        :param img_path: 图片路径
        :return: (解密后的文本, 进制字符串, 识别出的进制)
        """
        base_string, base = self.extract_binary_from_image(img_path)
        decrypted_text = self.binary_to_text(base_string)
        return decrypted_text, base_string, base


class FileToImageEncryptor(TextToImageEncryptor):
    """
    文件到图片的加密器，继承自TextToImageEncryptor
    将文件转换为Base64编码，然后使用文本加密方法进行加密
    """
    
    def __init__(self, block_width=9, block_height=16, base=16):
        """
        初始化文件加密器
        :param block_width: 每个位的宽度（像素）
        :param block_height: 每个位的高度（像素）
        :param base: 进制，支持2-16
        """
        super().__init__(block_width, block_height, base)
    
    def encrypt_file_to_image(self, file_path, output_img_path, max_width=800, ignore_pixel_limit=False):
        """
        将文件加密为图片
        :param file_path: 要加密的文件路径
        :param output_img_path: 输出图片路径
        :param max_width: 图片最大宽度
        :param ignore_pixel_limit: 是否忽略像素限制
        :return: (base64字符串, 实际保存路径)
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检查文件大小
        max_file_size = 10 * 1024 * 1024  # 10MB
        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            raise ValueError(f"文件过大 ({file_size / (1024*1024):.2f} MB)，请使用小于 {max_file_size / (1024*1024):.2f} MB 的文件。")
        
        # 获取文件名和扩展名
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1]
        
        # 读取文件内容
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # 将文件内容转换为Base64编码
        base64_data = base64.b64encode(file_data).decode('utf-8')
        
        # 添加文件信息头，格式为: FILEINFO:filename:extension:base64data
        file_info = f"FILEINFO:{file_name}:{file_ext}:{base64_data}"
        
        # 使用父类的文本加密方法
        base_string, actual_path = self.encrypt_to_image(file_info, output_img_path, max_width, ignore_pixel_limit)
        
        return base_string, actual_path


class ImageToFileDecryptor(ImageToTextDecryptor):
    """
    图片到文件的解密器，继承自ImageToTextDecryptor
    从图片中解密Base64编码的文件数据，并还原为原始文件
    """
    
    def __init__(self, block_width=9, block_height=16, base=None, ignore_pixel_limit=False):
        """
        初始化文件解密器
        :param block_width: 每个位的宽度（像素）
        :param block_height: 每个位的高度（像素）
        :param base: 进制，支持2-16，如果为None则自动识别
        :param ignore_pixel_limit: 是否忽略像素限制，默认为False
        """
        super().__init__(block_width, block_height, base, ignore_pixel_limit)
    
    def decrypt_image_to_file(self, img_path, output_dir=None):
        """
        从图片中解密文件
        :param img_path: 包含加密信息的图片路径
        :param output_dir: 输出目录，如果为None则使用当前目录
        :return: (文件路径, 文件名, 文件扩展名, 解密文本, 二进制表示)
        """
        # 使用父类的解密方法获取文本
        decrypted_text, base_string, detected_base = self.decrypt_from_image_with_binary(img_path)
        
        # 检查是否是文件信息格式
        if not decrypted_text.startswith("FILEINFO:"):
            raise ValueError("图片中不包含有效的文件加密信息")
        
        # 解析文件信息
        try:
            parts = decrypted_text.split(":", 3)
            if len(parts) != 4:
                raise ValueError("文件信息格式不正确")
            
            _, file_name, file_ext, base64_data = parts
        except Exception as e:
            raise ValueError(f"解析文件信息失败: {str(e)}")
        
        # 将Base64数据解码为二进制
        try:
            file_data = base64.b64decode(base64_data)
        except Exception as e:
            raise ValueError(f"Base64解码失败: {str(e)}")
        
        # 确定输出目录
        if output_dir is None:
            output_dir = os.getcwd()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建输出文件路径
        output_file_path = os.path.join(output_dir, file_name)
        
        # 如果文件已存在，添加序号
        counter = 1
        while os.path.exists(output_file_path):
            name_without_ext = os.path.splitext(file_name)[0]
            output_file_path = os.path.join(output_dir, f"{name_without_ext}_{counter}{file_ext}")
            counter += 1
        
        # 写入文件
        with open(output_file_path, 'wb') as file:
            file.write(file_data)
        
        return output_file_path, file_name, file_ext, decrypted_text, base_string


def is_image_file(file_path):
    """
    判断文件是否为图片文件
    :param file_path: 文件路径
    :return: 是否为图片文件
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('image/'):
        return True
    return False


def is_text_file(file_path):
    """
    判断文件是否为文本文件
    :param file_path: 文件路径
    :return: 是否为文本文件
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('text/'):
        return True
    
    # 检查常见文本文件扩展名
    text_extensions = ['.txt', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.md', '.log']
    ext = os.path.splitext(file_path)[1].lower()
    return ext in text_extensions


def create_sample_carrier_image(output_path, width=800, height=600):
    """
    创建一个示例载体图片
    :param output_path: 输出路径
    :param width: 图片宽度
    :param height: 图片高度
    """
    # 创建一个简单的渐变背景图片
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 添加一些简单的图形和文字
    for i in range(0, width, 50):
        color_value = int(255 * (i / width))
        color = (color_value, color_value, 255)
        draw.line([(i, 0), (i, height)], fill=color, width=2)
    
    for i in range(0, height, 50):
        color_value = int(255 * (i / height))
        color = (255, color_value, color_value)
        draw.line([(0, i), (width, i)], fill=color, width=2)
    
    # 添加文字
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2 - 100, height//2 - 12), "Carrier Image", fill='black', font=font)
    
    img.save(output_path)
    print(f"示例载体图片已创建: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="文本到图片的加密解密工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 加密命令
    encrypt_parser = subparsers.add_parser('encrypt', help='将文本加密为图片')
    encrypt_parser.add_argument('text', help='要加密的文本')
    encrypt_parser.add_argument('output_img', help='输出图片路径')
    encrypt_parser.add_argument('--block-width', type=int, default=9, 
                               help='每个位的宽度（像素），默认为9')
    encrypt_parser.add_argument('--block-height', type=int, default=16, 
                               help='每个位的高度（像素），默认为16')
    encrypt_parser.add_argument('--max-width', type=int, default=800, 
                               help='图片最大宽度，超过时会自动换行，默认为800')
    encrypt_parser.add_argument('--base', type=int, default=2, choices=range(2, 17),
                               help='进制，支持2-16，默认为2（二进制）')
    
    # 解密命令
    decrypt_parser = subparsers.add_parser('decrypt', help='从图片中解密文本')
    decrypt_parser.add_argument('img_path', help='包含加密信息的图片路径')
    decrypt_parser.add_argument('--block-width', type=int, default=9, 
                              help='每个位的宽度（像素），默认为9')
    decrypt_parser.add_argument('--block-height', type=int, default=16, 
                              help='每个位的高度（像素），默认为16')
    decrypt_parser.add_argument('--base', type=int, default=None, choices=range(2, 17), nargs='?',
                              help='进制，支持2-16，如果不指定则自动识别')
    
    # 文件加密命令
    file_encrypt_parser = subparsers.add_parser('file_encrypt', help='将文件加密为图片')
    file_encrypt_parser.add_argument('file_path', help='要加密的文件路径')
    file_encrypt_parser.add_argument('output_img', help='输出图片路径')
    file_encrypt_parser.add_argument('--block-width', type=int, default=9, 
                                   help='每个位的宽度（像素），默认为9')
    file_encrypt_parser.add_argument('--block-height', type=int, default=16, 
                                   help='每个位的高度（像素），默认为16')
    file_encrypt_parser.add_argument('--max-width', type=int, default=800, 
                                   help='图片最大宽度，超过时会自动换行，默认为800')
    file_encrypt_parser.add_argument('--base', type=int, default=16, choices=range(2, 17),
                                   help='进制，支持2-16，默认为16（十六进制）')
    
    # 文件解密命令
    file_decrypt_parser = subparsers.add_parser('file_decrypt', help='从图片中解密文件')
    file_decrypt_parser.add_argument('img_path', help='包含加密信息的图片路径')
    file_decrypt_parser.add_argument('--output-dir', help='输出目录，默认为当前目录')
    file_decrypt_parser.add_argument('--block-width', type=int, default=9, 
                                   help='每个位的宽度（像素），默认为9')
    file_decrypt_parser.add_argument('--block-height', type=int, default=16, 
                                   help='每个位的高度（像素），默认为16')
    file_decrypt_parser.add_argument('--base', type=int, default=None, choices=range(2, 17), nargs='?',
                                   help='进制，支持2-16，如果不指定则自动识别')
    
    # 创建示例图片命令
    create_parser = subparsers.add_parser('create', help='创建示例载体图片')
    create_parser.add_argument('output_path', help='输出图片路径')
    create_parser.add_argument('--width', type=int, default=800, help='图片宽度，默认为800')
    create_parser.add_argument('--height', type=int, default=600, help='图片高度，默认为600')
    
    args = parser.parse_args()
    
    if args.command == 'encrypt':
        encryptor = TextToImageEncryptor(args.block_width, args.block_height, args.base)
        base_string = encryptor.encrypt_to_image(
            args.text, 
            args.output_img, 
            args.max_width
        )
        print(f"原始文本: {args.text}")
        print(f"进制({args.base})表示: {base_string}")
        print(f"加密完成!")
    
    elif args.command == 'decrypt':
        decryptor = ImageToTextDecryptor(args.block_width, args.block_height, args.base)
        text = decryptor.decrypt_from_image(args.img_path)
        print(f"解密结果: {text}")
    
    elif args.command == 'file_encrypt':
        encryptor = FileToImageEncryptor(args.block_width, args.block_height, args.base)
        base_string, actual_path = encryptor.encrypt_file_to_image(
            args.file_path, 
            args.output_img, 
            args.max_width
        )
        print(f"原始文件: {args.file_path}")
        print(f"进制({args.base})表示: {base_string[:50]}..." if len(base_string) > 50 else f"进制({args.base})表示: {base_string}")
        print(f"加密图片已保存到: {actual_path}")
        print(f"文件加密完成!")
    
    elif args.command == 'file_decrypt':
        decryptor = ImageToFileDecryptor(args.block_width, args.block_height, args.base)
        try:
            output_path, file_name, file_ext = decryptor.decrypt_image_to_file(
                args.img_path, 
                args.output_dir
            )
            print(f"解密文件已保存到: {output_path}")
            print(f"文件名: {file_name}")
            print(f"文件类型: {file_ext}")
            print(f"文件解密完成!")
        except Exception as e:
            print(f"解密失败: {str(e)}")
    
    elif args.command == 'create':
        create_sample_carrier_image(args.output_path, args.width, args.height)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()