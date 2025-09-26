#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像加密解密工具的图形用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import queue
import time
import math
from image_encryptor import TextToImageEncryptor, ImageToTextDecryptor, FileToImageEncryptor, ImageToFileDecryptor, is_image_file, is_text_file


class ImageEncryptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本到图片加密解密工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置默认路径
        self.default_output_dir = os.path.join(os.getcwd(), "生成的图片")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TFrame", padding=10)
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=5)
        self.style.configure("TEntry", padding=5)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建加密选项卡
        self.encrypt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.encrypt_tab, text="加密")
        self.create_encrypt_tab()
        
        # 创建解密选项卡
        self.decrypt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.decrypt_tab, text="解密")
        self.create_decrypt_tab()
        
        # 创建文件加密选项卡
        self.file_encrypt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.file_encrypt_tab, text="文件加密")
        self.create_file_encrypt_tab()
        
        # 创建文件解密选项卡
        self.file_decrypt_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.file_decrypt_tab, text="文件解密")
        self.create_file_decrypt_tab()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=100, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.progress_bar.pack_forget()  # 初始隐藏进度条
        
        # 创建消息队列，用于线程间通信
        self.message_queue = queue.Queue()
        
        # 定期检查消息队列
        self.root.after(100, self.process_message_queue)
    
    def create_encrypt_tab(self):
        """创建加密选项卡"""
        # 左侧控制面板
        control_frame = ttk.Frame(self.encrypt_tab)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 文本输入
        ttk.Label(control_frame, text="要加密的文本:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 创建文本输入框架和滚动条
        text_frame = ttk.Frame(control_frame)
        text_frame.grid(row=1, column=0, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_input = tk.Text(text_frame, width=40, height=10, yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_input.yview)

        # 添加文本长度显示
        self.text_input.bind("<KeyRelease>", self.update_text_length)
        self.text_length_label = ttk.Label(control_frame, text="文本长度: 0 字符")
        self.text_length_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # 参数设置
        ttk.Label(control_frame, text="参数设置:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(control_frame, text="最大宽度:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.max_width_var = tk.IntVar(value=800)
        ttk.Entry(control_frame, textvariable=self.max_width_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="块宽度:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.block_width_var = tk.IntVar(value=9)
        ttk.Entry(control_frame, textvariable=self.block_width_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="块高度:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.block_height_var = tk.IntVar(value=16)
        ttk.Entry(control_frame, textvariable=self.block_height_var, width=10).grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # 添加推荐值按钮
        ttk.Button(control_frame, text="应用推荐值", command=self.apply_recommended_encrypt_values).grid(row=5, column=2, rowspan=2, padx=5, pady=2)
        
        ttk.Label(control_frame, text="进制:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.base_var = tk.IntVar(value=16)
        base_frame = ttk.Frame(control_frame)
        base_frame.grid(row=7, column=1, sticky=tk.W, pady=2)
        
        # 创建进制选择下拉菜单
        base_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        self.base_combo = ttk.Combobox(base_frame, textvariable=self.base_var, values=base_values, width=8, state="readonly")
        self.base_combo.current(14)  # 默认选择16进制
        self.base_combo.pack(side=tk.LEFT)
        
        # 添加进制说明标签
        self.base_info_label = ttk.Label(base_frame, text="(16进制支持更多字符)")
        self.base_info_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 按钮区域
        ttk.Button(control_frame, text="选择保存路径", command=self.select_encrypt_save_path).grid(row=8, column=0, pady=10)
        self.encrypt_save_path_var = tk.StringVar(value="encrypted_image.png")
        ttk.Entry(control_frame, textvariable=self.encrypt_save_path_var, width=40).grid(row=9, column=0, columnspan=2, pady=5)
        
        # 添加设置默认路径按钮
        ttk.Button(control_frame, text="设置默认输出路径", command=self.set_default_output_path).grid(row=10, column=0, pady=5)
        self.default_path_label = ttk.Label(control_frame, text=f"当前默认路径: {self.default_output_dir}")
        self.default_path_label.grid(row=11, column=0, columnspan=2, pady=5)
        
        ttk.Button(control_frame, text="加密", command=self.encrypt_text).grid(row=12, column=0, pady=10)
        
        # 右侧预览面板
        preview_frame = ttk.Frame(self.encrypt_tab)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(preview_frame, text="加密结果预览:").pack(anchor=tk.W, pady=5)
        
        # 图像预览
        self.encrypt_preview_label = ttk.Label(preview_frame)
        self.encrypt_preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 二进制显示
        ttk.Label(preview_frame, text="二进制表示:").pack(anchor=tk.W, pady=5)
        self.encrypt_binary_text = tk.Text(preview_frame, height=5, width=50)
        self.encrypt_binary_text.pack(fill=tk.X, pady=5)
    
    def update_text_length(self, event=None):
        """更新文本长度显示"""
        text_length = len(self.text_input.get("1.0", tk.END).strip())
        self.text_length_label.config(text=f"文本长度: {text_length} 字符")
    
    def process_message_queue(self):
        """处理消息队列中的消息"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                if msg[0] == "status":
                    self.status_var.set(msg[1])
                elif msg[0] == "progress":
                    self.progress_var.set(msg[1])
                elif msg[0] == "show_progress":
                    self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)
                elif msg[0] == "hide_progress":
                    self.progress_bar.pack_forget()
                elif msg[0] == "message":
                    if msg[1] == "info":
                        messagebox.showinfo(msg[2], msg[3])
                    elif msg[1] == "warning":
                        messagebox.showwarning(msg[2], msg[3])
                    elif msg[1] == "error":
                        messagebox.showerror(msg[2], msg[3])
                elif msg[0] == "pixel_limit_error":
                    # 处理像素限制错误
                    error_message = msg[1]
                    param1 = msg[2]
                    param2 = msg[3]
                    
                    # 创建自定义对话框
                    dialog = tk.Toplevel(self.root)
                    dialog.title("警告")
                    dialog.geometry("500x200")
                    dialog.resizable(False, False)
                    
                    # 错误信息
                    error_label = ttk.Label(dialog, text=error_message, wraplength=450)
                    error_label.pack(pady=20)
                    
                    # 按钮框架
                    button_frame = ttk.Frame(dialog)
                    button_frame.pack(pady=10)
                    
                    # 取消按钮
                    cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy)
                    cancel_button.pack(side=tk.LEFT, padx=10)
                    
                    # 无视风险继续生成按钮
                    def ignore_and_continue():
                        dialog.destroy()
                        # 判断是文本加密还是文件加密
                        if isinstance(param1, str) and len(param1) > 100:  # 可能是文本
                            # 重新启动文本加密线程，但这次忽略像素限制
                            threading.Thread(target=self._encrypt_text_thread, args=(param1, param2, True), daemon=True).start()
                            # 显示进度条
                            self.message_queue.put(("show_progress",))
                            self.message_queue.put(("status", "正在加密（无视风险）..."))
                            # 禁用加密按钮
                            for widget in self.encrypt_tab.winfo_children():
                                if isinstance(widget, ttk.Frame):
                                    for child in widget.winfo_children():
                                        if isinstance(child, ttk.Button) and child.cget("text") == "加密":
                                            child.config(state=tk.DISABLED)
                        else:  # 文件加密
                            # 重新启动文件加密线程，但这次忽略像素限制
                            threading.Thread(target=self._encrypt_file_thread, args=(param1, param2, True), daemon=True).start()
                            # 显示进度条
                            self.message_queue.put(("show_progress",))
                            self.message_queue.put(("status", "正在加密文件（无视风险）..."))
                            # 禁用加密按钮
                            for widget in self.file_encrypt_tab.winfo_children():
                                if isinstance(widget, ttk.Frame):
                                    for child in widget.winfo_children():
                                        if isinstance(child, ttk.Button) and child.cget("text") == "加密文件":
                                            child.config(state=tk.DISABLED)
                    
                    continue_button = ttk.Button(button_frame, text="无视风险继续生成", command=ignore_and_continue)
                    continue_button.pack(side=tk.LEFT, padx=10)
                    
                    # 设置对话框为模态
                    dialog.transient(self.root)
                    dialog.grab_set()
                    self.root.wait_window(dialog)
                elif msg[0] == "pixel_limit_error_decrypt":
                    # 处理解密过程中的像素限制错误
                    error_message = msg[1]
                    image_path = msg[2]
                    save_path = msg[3] if len(msg) > 3 else None
                    
                    # 创建自定义对话框
                    dialog = tk.Toplevel(self.root)
                    dialog.title("警告")
                    dialog.geometry("500x200")
                    dialog.resizable(False, False)
                    
                    # 错误信息
                    error_label = ttk.Label(dialog, text=error_message, wraplength=450)
                    error_label.pack(pady=20)
                    
                    # 按钮框架
                    button_frame = ttk.Frame(dialog)
                    button_frame.pack(pady=10)
                    
                    # 取消按钮
                    cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy)
                    cancel_button.pack(side=tk.LEFT, padx=10)
                    
                    # 无视风险继续解密按钮
                    def ignore_and_continue_decrypt():
                        dialog.destroy()
                        # 判断是文本解密还是文件解密
                        if save_path:  # 文件解密
                            # 重新启动文件解密线程，但这次忽略像素限制
                            threading.Thread(target=self._decrypt_file_thread_ignore_limit, args=(image_path, save_path), daemon=True).start()
                            # 显示进度条
                            self.message_queue.put(("show_progress",))
                            self.message_queue.put(("status", "正在解密文件（无视风险）..."))
                            # 禁用解密按钮
                            for widget in self.file_decrypt_tab.winfo_children():
                                if isinstance(widget, ttk.Frame):
                                    for child in widget.winfo_children():
                                        if isinstance(child, ttk.Button) and child.cget("text") == "解密文件":
                                            child.config(state=tk.DISABLED)
                        else:  # 文本解密
                            # 重新启动解密线程，但这次忽略像素限制
                            threading.Thread(target=self._decrypt_image_thread_ignore_limit, args=(image_path,), daemon=True).start()
                            # 显示进度条
                            self.message_queue.put(("show_progress",))
                            self.message_queue.put(("status", "正在解密（无视风险）..."))
                            # 禁用解密按钮
                            for widget in self.decrypt_tab.winfo_children():
                                if isinstance(widget, ttk.Frame):
                                    for child in widget.winfo_children():
                                        if isinstance(child, ttk.Button) and child.cget("text") == "解密":
                                            child.config(state=tk.DISABLED)
                    
                    continue_button = ttk.Button(button_frame, text="无视风险继续解密", command=ignore_and_continue_decrypt)
                    continue_button.pack(side=tk.LEFT, padx=10)
                    
                    # 设置对话框为模态
                    dialog.transient(self.root)
                    dialog.grab_set()
                    self.root.wait_window(dialog)
        except queue.Empty:
            pass
        finally:
            # 继续定期检查消息队列
            self.root.after(100, self.process_message_queue)
    
    def create_decrypt_tab(self):
        """创建解密选项卡"""
        # 左侧控制面板
        control_frame = ttk.Frame(self.decrypt_tab)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 图片选择
        ttk.Label(control_frame, text="选择加密图片:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Button(control_frame, text="选择图片", command=self.select_decrypt_image).grid(row=1, column=0, pady=5)
        self.decrypt_image_path_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.decrypt_image_path_var, width=40).grid(row=2, column=0, pady=5)
        
        # 参数设置
        ttk.Label(control_frame, text="参数设置:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(control_frame, text="块宽度:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.decrypt_block_width_var = tk.IntVar(value=9)
        ttk.Entry(control_frame, textvariable=self.decrypt_block_width_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="块高度:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.decrypt_block_height_var = tk.IntVar(value=16)
        ttk.Entry(control_frame, textvariable=self.decrypt_block_height_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # 添加推荐值按钮
        ttk.Button(control_frame, text="应用推荐值", command=self.apply_recommended_decrypt_values).grid(row=4, column=2, rowspan=2, padx=5, pady=2)
        
        ttk.Label(control_frame, text="进制:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.decrypt_base_var = tk.StringVar(value="自动识别")
        decrypt_base_frame = ttk.Frame(control_frame)
        decrypt_base_frame.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # 创建解密进制选择下拉菜单，包含自动识别选项
        decrypt_base_values = ["自动识别", 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        self.decrypt_base_combo = ttk.Combobox(decrypt_base_frame, textvariable=self.decrypt_base_var, values=decrypt_base_values, width=12, state="readonly")
        self.decrypt_base_combo.current(0)  # 默认选择自动识别
        self.decrypt_base_combo.pack(side=tk.LEFT)
        
        # 添加进制说明标签
        self.decrypt_base_info_label = ttk.Label(decrypt_base_frame, text="(自动识别或手动选择)")
        self.decrypt_base_info_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 按钮
        ttk.Button(control_frame, text="解密", command=self.decrypt_image).grid(row=7, column=0, pady=10)
        
        # 右侧结果面板
        result_frame = ttk.Frame(self.decrypt_tab)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(result_frame, text="图片预览:").pack(anchor=tk.W, pady=5)
        
        # 图像预览
        self.decrypt_preview_label = ttk.Label(result_frame)
        self.decrypt_preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 解密结果
        ttk.Label(result_frame, text="解密结果:").pack(anchor=tk.W, pady=5)
        self.decrypt_result_text = tk.Text(result_frame, height=5, width=50)
        self.decrypt_result_text.pack(fill=tk.X, pady=5)
        
        # 二进制显示
        ttk.Label(result_frame, text="二进制表示:").pack(anchor=tk.W, pady=5)
        self.decrypt_binary_text = tk.Text(result_frame, height=5, width=50)
        self.decrypt_binary_text.pack(fill=tk.X, pady=5)
    
    def create_file_encrypt_tab(self):
        """创建文件加密选项卡"""
        # 左侧控制面板
        control_frame = ttk.Frame(self.file_encrypt_tab)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 文件选择
        ttk.Label(control_frame, text="要加密的文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Button(control_frame, text="选择文件", command=self.select_file_to_encrypt).grid(row=1, column=0, pady=5)
        self.file_to_encrypt_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_to_encrypt_var, width=40).grid(row=2, column=0, pady=5)
        
        # 文件信息显示
        ttk.Label(control_frame, text="文件信息:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.file_info_text = tk.Text(control_frame, width=40, height=4)
        self.file_info_text.grid(row=4, column=0, pady=5)
        
        # 参数设置
        ttk.Label(control_frame, text="参数设置:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(control_frame, text="最大宽度:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.file_max_width_var = tk.IntVar(value=800)
        ttk.Entry(control_frame, textvariable=self.file_max_width_var, width=10).grid(row=6, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="块宽度:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.file_block_width_var = tk.IntVar(value=9)
        ttk.Entry(control_frame, textvariable=self.file_block_width_var, width=10).grid(row=7, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="块高度:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.file_block_height_var = tk.IntVar(value=16)
        ttk.Entry(control_frame, textvariable=self.file_block_height_var, width=10).grid(row=8, column=1, sticky=tk.W, pady=2)
        
        # 添加推荐值按钮
        ttk.Button(control_frame, text="应用推荐值", command=self.apply_recommended_file_encrypt_values).grid(row=7, column=2, rowspan=2, padx=5, pady=2)
        
        ttk.Label(control_frame, text="进制:").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.file_base_var = tk.IntVar(value=16)
        file_base_frame = ttk.Frame(control_frame)
        file_base_frame.grid(row=9, column=1, sticky=tk.W, pady=2)
        
        # 创建进制选择下拉菜单
        file_base_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        self.file_base_combo = ttk.Combobox(file_base_frame, textvariable=self.file_base_var, values=file_base_values, width=8, state="readonly")
        self.file_base_combo.current(14)  # 默认选择16进制
        self.file_base_combo.pack(side=tk.LEFT)
        
        # 添加进制说明标签
        self.file_base_info_label = ttk.Label(file_base_frame, text="(16进制支持更多字符)")
        self.file_base_info_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 按钮区域
        ttk.Button(control_frame, text="选择保存路径", command=self.select_file_encrypt_save_path).grid(row=10, column=0, pady=10)
        self.file_encrypt_save_path_var = tk.StringVar(value="encrypted_file.png")
        ttk.Entry(control_frame, textvariable=self.file_encrypt_save_path_var, width=40).grid(row=11, column=0, columnspan=2, pady=5)
        
        ttk.Button(control_frame, text="加密文件", command=self.encrypt_file).grid(row=12, column=0, pady=10)
        
        # 右侧预览面板
        preview_frame = ttk.Frame(self.file_encrypt_tab)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(preview_frame, text="加密结果预览:").pack(anchor=tk.W, pady=5)
        
        # 图像预览
        self.file_encrypt_preview_label = ttk.Label(preview_frame)
        self.file_encrypt_preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 二进制显示
        ttk.Label(preview_frame, text="二进制表示:").pack(anchor=tk.W, pady=5)
        self.file_encrypt_binary_text = tk.Text(preview_frame, height=5, width=50)
        self.file_encrypt_binary_text.pack(fill=tk.X, pady=5)
    
    def create_file_decrypt_tab(self):
        """创建文件解密选项卡"""
        # 左侧控制面板
        control_frame = ttk.Frame(self.file_decrypt_tab)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 图片选择
        ttk.Label(control_frame, text="选择加密图片:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Button(control_frame, text="选择图片", command=self.select_file_decrypt_image).grid(row=1, column=0, pady=5)
        self.file_decrypt_image_path_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_decrypt_image_path_var, width=40).grid(row=2, column=0, pady=5)
        
        # 参数设置
        ttk.Label(control_frame, text="参数设置:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(control_frame, text="块宽度:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.file_decrypt_block_width_var = tk.IntVar(value=9)
        ttk.Entry(control_frame, textvariable=self.file_decrypt_block_width_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="块高度:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.file_decrypt_block_height_var = tk.IntVar(value=16)
        ttk.Entry(control_frame, textvariable=self.file_decrypt_block_height_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # 添加推荐值按钮
        ttk.Button(control_frame, text="应用推荐值", command=self.apply_recommended_file_decrypt_values).grid(row=4, column=2, rowspan=2, padx=5, pady=2)
        
        ttk.Label(control_frame, text="进制:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.file_decrypt_base_var = tk.StringVar(value="自动识别")
        file_decrypt_base_frame = ttk.Frame(control_frame)
        file_decrypt_base_frame.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # 创建解密进制选择下拉菜单，包含自动识别选项
        file_decrypt_base_values = ["自动识别", 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        self.file_decrypt_base_combo = ttk.Combobox(file_decrypt_base_frame, textvariable=self.file_decrypt_base_var, values=file_decrypt_base_values, width=12, state="readonly")
        self.file_decrypt_base_combo.current(0)  # 默认选择自动识别
        self.file_decrypt_base_combo.pack(side=tk.LEFT)
        
        # 添加进制说明标签
        self.file_decrypt_base_info_label = ttk.Label(file_decrypt_base_frame, text="(自动识别或手动选择)")
        self.file_decrypt_base_info_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 按钮
        ttk.Button(control_frame, text="选择保存路径", command=self.select_file_decrypt_save_path).grid(row=7, column=0, pady=10)
        self.file_decrypt_save_path_var = tk.StringVar(value="decrypted_file")
        ttk.Entry(control_frame, textvariable=self.file_decrypt_save_path_var, width=40).grid(row=8, column=0, columnspan=2, pady=5)
        
        ttk.Button(control_frame, text="解密文件", command=self.decrypt_file).grid(row=9, column=0, pady=10)
        
        # 右侧结果面板
        result_frame = ttk.Frame(self.file_decrypt_tab)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(result_frame, text="图片预览:").pack(anchor=tk.W, pady=5)
        
        # 图像预览
        self.file_decrypt_preview_label = ttk.Label(result_frame)
        self.file_decrypt_preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 解密结果
        ttk.Label(result_frame, text="解密结果:").pack(anchor=tk.W, pady=5)
        self.file_decrypt_result_text = tk.Text(result_frame, height=5, width=50)
        self.file_decrypt_result_text.pack(fill=tk.X, pady=5)
        
        # 二进制显示
        ttk.Label(result_frame, text="二进制表示:").pack(anchor=tk.W, pady=5)
        self.file_decrypt_binary_text = tk.Text(result_frame, height=5, width=50)
        self.file_decrypt_binary_text.pack(fill=tk.X, pady=5)
    
    def select_encrypt_save_path(self):
        """选择加密图片保存路径"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialdir=self.default_output_dir
        )
        if file_path:
            self.encrypt_save_path_var.set(file_path)
    
    def set_default_output_path(self):
        """设置默认输出路径"""
        dir_path = filedialog.askdirectory(
            title="选择默认输出路径",
            initialdir=self.default_output_dir
        )
        if dir_path:
            self.default_output_dir = dir_path
            self.default_path_label.config(text=f"当前默认路径: {self.default_output_dir}")
            messagebox.showinfo("成功", f"默认输出路径已设置为: {self.default_output_dir}")
    
    def select_decrypt_image(self):
        """选择要解密的图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")],
            initialdir=self.default_output_dir
        )
        if file_path:
            self.decrypt_image_path_var.set(file_path)
            self.preview_decrypt_image(file_path)
    
    def preview_decrypt_image(self, image_path):
        """预览要解密的图片"""
        try:
            image = Image.open(image_path)
            # 调整图片大小以适应预览区域
            image.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(image)
            self.decrypt_preview_label.configure(image=photo)
            self.decrypt_preview_label.image = photo  # 保持引用
        except Exception as e:
            messagebox.showerror("错误", f"无法预览图片: {str(e)}")
    
    def encrypt_text(self):
        """加密文本 - 启动后台线程"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入要加密的文本")
            return
        
        save_path = self.encrypt_save_path_var.get()
        if not save_path:
            messagebox.showwarning("警告", "请选择保存路径")
            return
        
        # 禁用加密按钮，防止重复点击
        for widget in self.encrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "加密":
                        child.config(state=tk.DISABLED)
        
        # 显示进度条
        self.message_queue.put(("show_progress",))
        self.message_queue.put(("status", "正在加密..."))
        
        # 启动后台线程执行加密操作
        threading.Thread(target=self._encrypt_text_thread, args=(text, save_path), daemon=True).start()
    
    def _encrypt_text_thread(self, text, save_path, ignore_pixel_limit=False):
        """在后台线程中执行加密操作"""
        try:
            # 确保默认输出目录存在
            if not os.path.exists(self.default_output_dir):
                os.makedirs(self.default_output_dir)
            
            # 如果save_path不是绝对路径，则将其放在默认输出目录中
            if not os.path.isabs(save_path):
                save_path = os.path.join(self.default_output_dir, save_path)
            
            # 创建加密器
            encryptor = TextToImageEncryptor(
                block_width=self.block_width_var.get(),
                block_height=self.block_height_var.get(),
                base=self.base_var.get()
            )
            
            # 加密文本
            binary_string, actual_save_path = encryptor.encrypt_to_image(
                text, 
                save_path, 
                max_width=self.max_width_var.get(),
                ignore_pixel_limit=ignore_pixel_limit
            )
            
            # 保存二进制表示到文本文件
            # 获取图片文件名（不带扩展名）
            image_name = os.path.splitext(os.path.basename(actual_save_path))[0]
            # 创建二进制表示文件路径
            binary_file_path = os.path.join(os.path.dirname(actual_save_path), f"{image_name}_二进制表示.txt")
            # 保存二进制表示到txt文件
            with open(binary_file_path, 'w', encoding='utf-8') as f:
                f.write(binary_string)
            
            # 发送结果到主线程
            self.message_queue.put(("status", "加密完成"))
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("message", "info", "成功", f"文本已加密并保存到: {actual_save_path}\n\n二进制表示已保存到:\n{binary_file_path}"))
            
            # 更新UI
            self.root.after(0, self._update_encrypt_result, binary_string, actual_save_path)
            
        except Exception as e:
            # 检查是否是像素限制错误
            if "像素数量超过限制" in str(e) or "可能存在安全风险" in str(e):
                # 发送像素限制错误到主线程，并提供无视风险继续生成的选项
                self.message_queue.put(("pixel_limit_error", str(e), text, save_path))
            else:
                # 发送其他错误信息到主线程
                self.message_queue.put(("status", "加密失败"))
                self.message_queue.put(("message", "error", "错误", f"加密过程中出错: {str(e)}"))
        finally:
            # 隐藏进度条
            self.message_queue.put(("hide_progress",))
            # 重新启用加密按钮
            self.root.after(0, self._enable_encrypt_button)
    
    def _update_encrypt_result(self, binary_string, image_path):
        """更新加密结果UI"""
        # 不再显示二进制表示，而是保存到文件
        # 清空二进制表示文本框
        self.encrypt_binary_text.delete("1.0", tk.END)
        self.encrypt_binary_text.insert(tk.END, "二进制表示已保存到文本文件")
        
        # 预览加密后的图片
        self.preview_encrypt_image(image_path)
    
    def _enable_encrypt_button(self):
        """重新启用加密按钮"""
        for widget in self.encrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "加密":
                        child.config(state=tk.NORMAL)
    
    def preview_encrypt_image(self, image_path):
        """预览加密后的图片"""
        try:
            image = Image.open(image_path)
            # 调整图片大小以适应预览区域
            image.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(image)
            self.encrypt_preview_label.configure(image=photo)
            self.encrypt_preview_label.image = photo  # 保持引用
        except Exception as e:
            messagebox.showerror("错误", f"无法预览图片: {str(e)}")
    
    def decrypt_image(self):
        """解密图片 - 启动后台线程"""
        image_path = self.decrypt_image_path_var.get()
        if not image_path:
            messagebox.showwarning("警告", "请选择要解密的图片")
            return
        
        # 禁用解密按钮，防止重复点击
        for widget in self.decrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "解密":
                        child.config(state=tk.DISABLED)
        
        # 显示进度条
        self.message_queue.put(("show_progress",))
        self.message_queue.put(("status", "正在解密..."))
        
        # 启动后台线程执行解密操作
        threading.Thread(target=self._decrypt_image_thread, args=(image_path,), daemon=True).start()
    
    def _decrypt_image_thread(self, image_path):
        """在后台线程中执行解密操作"""
        try:
            # 创建解密器
            # 获取选择的进制，如果是"自动识别"则传入None
            base_value = self.decrypt_base_var.get()
            if base_value == "自动识别":
                base_value = None
            else:
                # 将字符串转换为整数
                try:
                    base_value = int(base_value)
                except ValueError:
                    base_value = None
                
            decryptor = ImageToTextDecryptor(
                block_width=self.decrypt_block_width_var.get(),
                block_height=self.decrypt_block_height_var.get(),
                base=base_value
            )
            
            # 解密图片
            decrypted_text, binary_string, base = decryptor.decrypt_from_image_with_binary(image_path)
            
            # 发送结果到主线程
            self.message_queue.put(("status", "解密完成"))
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("message", "info", "成功", "图片解密成功"))
            
            # 更新UI，传递图片路径
            self.root.after(0, self._update_decrypt_result, decrypted_text, binary_string, image_path)
            
        except ValueError as e:
            error_msg = str(e)
            # 检查是否是像素限制错误
            if "可能存在安全风险" in error_msg or "图片尺寸过大" in error_msg:
                # 发送像素限制错误消息，包含图片路径
                self.message_queue.put(("pixel_limit_error_decrypt", error_msg, image_path))
            else:
                # 发送错误信息到主线程
                self.message_queue.put(("status", "解密失败"))
                self.message_queue.put(("message", "error", "错误", f"解密过程中出错: {error_msg}"))
        except Exception as e:
            # 发送错误信息到主线程
            self.message_queue.put(("status", "解密失败"))
            self.message_queue.put(("message", "error", "错误", f"解密过程中出错: {str(e)}"))
        finally:
            # 隐藏进度条
            self.message_queue.put(("hide_progress",))
            # 重新启用解密按钮
            self.root.after(0, self._enable_decrypt_button)
    
    def _decrypt_image_thread_ignore_limit(self, image_path):
        """在后台线程中执行解密操作（忽略像素限制）"""
        try:
            # 创建解密器
            # 获取选择的进制，如果是"自动识别"则传入None
            base_value = self.decrypt_base_var.get()
            if base_value == "自动识别":
                base_value = None
            else:
                # 将字符串转换为整数
                try:
                    base_value = int(base_value)
                except ValueError:
                    base_value = None
                
            decryptor = ImageToTextDecryptor(
                block_width=self.decrypt_block_width_var.get(),
                block_height=self.decrypt_block_height_var.get(),
                base=base_value,
                ignore_pixel_limit=True  # 忽略像素限制
            )
            
            # 解密图片
            decrypted_text, binary_string, base = decryptor.decrypt_from_image_with_binary(image_path)
            
            # 发送结果到主线程
            self.message_queue.put(("status", "解密完成"))
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("message", "info", "成功", "图片解密成功"))
            
            # 更新UI，传递图片路径
            self.root.after(0, self._update_decrypt_result, decrypted_text, binary_string, image_path)
            
        except Exception as e:
            # 发送错误信息到主线程
            self.message_queue.put(("status", "解密失败"))
            self.message_queue.put(("message", "error", "错误", f"解密过程中出错: {str(e)}"))
        finally:
            # 隐藏进度条
            self.message_queue.put(("hide_progress",))
            # 重新启用解密按钮
            self.root.after(0, self._enable_decrypt_button)
    
    def _update_decrypt_result(self, decrypted_text, binary_string, image_path=None):
        """将解密结果和二进制表示保存为txt文件"""
        try:
            # 获取图片路径
            if image_path is None:
                image_path = self.decrypt_image_path_var.get()
            
            if not image_path:
                messagebox.showerror("错误", "无法获取图片路径")
                return
            
            # 获取图片所在目录
            image_dir = os.path.dirname(image_path)
            
            # 获取图片文件名（不带扩展名）
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # 创建解密结果文件路径
            result_file_path = os.path.join(image_dir, f"{image_name}_解密结果.txt")
            
            # 创建二进制表示文件路径
            binary_file_path = os.path.join(image_dir, f"{image_name}_二进制表示.txt")
            
            # 保存解密结果到txt文件
            with open(result_file_path, 'w', encoding='utf-8') as f:
                f.write(decrypted_text)
            
            # 保存二进制表示到txt文件
            with open(binary_file_path, 'w', encoding='utf-8') as f:
                f.write(binary_string)
            
            # 清空界面上的文本框
            self.decrypt_result_text.delete("1.0", tk.END)
            self.decrypt_binary_text.delete("1.0", tk.END)
            
            # 在界面上显示文件保存路径
            self.decrypt_result_text.insert(tk.END, f"解密结果已保存到: {result_file_path}")
            self.decrypt_binary_text.insert(tk.END, f"二进制表示已保存到: {binary_file_path}")
            
            # 显示成功消息
            messagebox.showinfo("成功", f"解密结果已保存到:\n{result_file_path}\n\n二进制表示已保存到:\n{binary_file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存解密结果时出错: {str(e)}")
    
    def _enable_decrypt_button(self):
        """重新启用解密按钮"""
        for widget in self.decrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "解密":
                        child.config(state=tk.NORMAL)

    def select_file_to_encrypt(self):
        """选择要加密的文件"""
        file_path = filedialog.askopenfilename(
            title="选择要加密的文件",
            filetypes=[("All files", "*.*")],
            initialdir=os.getcwd()
        )
        if file_path:
            self.file_to_encrypt_var.set(file_path)
            self.display_file_info(file_path)
    
    def display_file_info(self, file_path):
        """显示文件信息"""
        try:
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1]
            
            # 格式化文件大小
            if file_size < 1024:
                size_str = f"{file_size} 字节"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.2f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            
            # 显示文件信息
            self.file_info_text.delete("1.0", tk.END)
            self.file_info_text.insert(tk.END, f"文件名: {file_name}\n")
            self.file_info_text.insert(tk.END, f"文件类型: {file_ext}\n")
            self.file_info_text.insert(tk.END, f"文件大小: {size_str}\n")
            
            # 判断文件类型
            if is_image_file(file_path):
                self.file_info_text.insert(tk.END, "文件类型: 图片文件")
            elif is_text_file(file_path):
                self.file_info_text.insert(tk.END, "文件类型: 文本文件")
            else:
                self.file_info_text.insert(tk.END, "文件类型: 二进制文件")
                
        except Exception as e:
            self.file_info_text.delete("1.0", tk.END)
            self.file_info_text.insert(tk.END, f"无法获取文件信息: {str(e)}")
    
    def select_file_encrypt_save_path(self):
        """选择文件加密图片保存路径"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialdir=self.default_output_dir
        )
        if file_path:
            self.file_encrypt_save_path_var.set(file_path)
    
    def select_file_decrypt_image(self):
        """选择要解密的文件加密图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")],
            initialdir=self.default_output_dir
        )
        if file_path:
            self.file_decrypt_image_path_var.set(file_path)
            self.preview_file_decrypt_image(file_path)
    
    def preview_file_decrypt_image(self, image_path):
        """预览要解密的文件加密图片"""
        try:
            image = Image.open(image_path)
            # 调整图片大小以适应预览区域
            image.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(image)
            self.file_decrypt_preview_label.configure(image=photo)
            self.file_decrypt_preview_label.image = photo  # 保持引用
        except Exception as e:
            messagebox.showerror("错误", f"无法预览图片: {str(e)}")
    
    def select_file_decrypt_save_path(self):
        """选择文件解密保存路径"""
        dir_path = filedialog.askdirectory(
            title="选择文件解密保存路径",
            initialdir=self.default_output_dir
        )
        if dir_path:
            self.file_decrypt_save_path_var.set(dir_path)
    
    def encrypt_file(self):
        """加密文件 - 启动后台线程"""
        file_path = self.file_to_encrypt_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请选择要加密的文件")
            return
        
        save_path = self.file_encrypt_save_path_var.get()
        if not save_path:
            messagebox.showwarning("警告", "请选择保存路径")
            return
        
        # 禁用加密按钮，防止重复点击
        for widget in self.file_encrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "加密文件":
                        child.config(state=tk.DISABLED)
        
        # 显示进度条
        self.message_queue.put(("show_progress",))
        self.message_queue.put(("status", "正在加密文件..."))
        
        # 启动后台线程执行加密操作
        threading.Thread(target=self._encrypt_file_thread, args=(file_path, save_path), daemon=True).start()
    
    def _encrypt_file_thread(self, file_path, save_path, ignore_pixel_limit=False):
        """在后台线程中执行文件加密操作"""
        try:
            # 确保默认输出目录存在
            if not os.path.exists(self.default_output_dir):
                os.makedirs(self.default_output_dir)
            
            # 如果save_path不是绝对路径，则将其放在默认输出目录中
            if not os.path.isabs(save_path):
                save_path = os.path.join(self.default_output_dir, save_path)
            
            # 创建文件加密器
            encryptor = FileToImageEncryptor(
                block_width=self.file_block_width_var.get(),
                block_height=self.file_block_height_var.get(),
                base=self.file_base_var.get()
            )
            
            # 加密文件
            binary_string, actual_save_path = encryptor.encrypt_file_to_image(
                file_path, 
                save_path, 
                max_width=self.file_max_width_var.get(),
                ignore_pixel_limit=ignore_pixel_limit
            )
            
            # 保存二进制表示到文本文件
            base_name = os.path.splitext(os.path.basename(actual_save_path))[0]
            binary_file_path = os.path.join(os.path.dirname(actual_save_path), f"{base_name}_二进制表示.txt")
            with open(binary_file_path, 'w', encoding='utf-8') as f:
                f.write(binary_string)
            
            # 发送结果到主线程
            self.message_queue.put(("status", "文件加密完成"))
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("message", "info", "成功", f"文件已加密并保存到: {actual_save_path}\n二进制表示已保存到: {binary_file_path}"))
            
            # 更新UI
            self.root.after(0, self._update_file_encrypt_result, binary_string, actual_save_path, binary_file_path)
            
        except ValueError as e:
            # 检查是否是像素限制错误
            if "像素数量超过限制" in str(e) or "可能存在安全风险" in str(e):
                # 发送像素限制错误到主线程
                self.message_queue.put(("pixel_limit_error", str(e), file_path, save_path))
            else:
                # 发送错误信息到主线程
                self.message_queue.put(("status", "文件加密失败"))
                self.message_queue.put(("message", "error", "错误", f"文件加密过程中出错: {str(e)}"))
        except Exception as e:
            # 发送错误信息到主线程
            self.message_queue.put(("status", "文件加密失败"))
            self.message_queue.put(("message", "error", "错误", f"文件加密过程中出错: {str(e)}"))
        finally:
            # 隐藏进度条
            self.message_queue.put(("hide_progress",))
            # 重新启用加密按钮
            self.root.after(0, self._enable_file_encrypt_button)
    
    def _update_file_encrypt_result(self, binary_string, image_path, binary_file_path):
        """更新文件加密结果UI"""
        # 不再显示二进制表示，而是显示保存路径
        self.file_encrypt_binary_text.delete("1.0", tk.END)
        self.file_encrypt_binary_text.insert(tk.END, f"二进制表示已保存到: {binary_file_path}")
        
        # 预览加密后的图片
        self.preview_file_encrypt_image(image_path)
    
    def _enable_file_encrypt_button(self):
        """重新启用文件加密按钮"""
        for widget in self.file_encrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "加密文件":
                        child.config(state=tk.NORMAL)
    
    def preview_file_encrypt_image(self, image_path):
        """预览加密后的文件图片"""
        try:
            image = Image.open(image_path)
            # 调整图片大小以适应预览区域
            image.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(image)
            self.file_encrypt_preview_label.configure(image=photo)
            self.file_encrypt_preview_label.image = photo  # 保持引用
        except Exception as e:
            messagebox.showerror("错误", f"无法预览图片: {str(e)}")
    
    def decrypt_file(self):
        """解密文件 - 启动后台线程"""
        image_path = self.file_decrypt_image_path_var.get()
        if not image_path:
            messagebox.showwarning("警告", "请选择要解密的图片")
            return
        
        save_path = self.file_decrypt_save_path_var.get()
        if not save_path:
            messagebox.showwarning("警告", "请选择保存路径")
            return
        
        # 禁用解密按钮，防止重复点击
        for widget in self.file_decrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "解密文件":
                        child.config(state=tk.DISABLED)
        
        # 显示进度条
        self.message_queue.put(("show_progress",))
        self.message_queue.put(("status", "正在解密文件..."))
        
        # 启动后台线程执行解密操作
        threading.Thread(target=self._decrypt_file_thread, args=(image_path, save_path), daemon=True).start()
    
    def _decrypt_file_thread(self, image_path, save_path):
        """在后台线程中执行文件解密操作"""
        try:
            # 确保默认输出目录存在
            if not os.path.exists(self.default_output_dir):
                os.makedirs(self.default_output_dir)
            
            # 如果save_path不是绝对路径，则将其放在默认输出目录中
            if not os.path.isabs(save_path):
                save_path = os.path.join(self.default_output_dir, save_path)
            
            # 创建解密器
            # 获取选择的进制，如果是"自动识别"则传入None
            base_value = self.file_decrypt_base_var.get()
            if base_value == "自动识别":
                base_value = None
            else:
                # 将字符串转换为整数
                try:
                    base_value = int(base_value)
                except ValueError:
                    base_value = None
            
            # 创建文件解密器
            decryptor = ImageToFileDecryptor(
                block_width=self.file_decrypt_block_width_var.get(),
                block_height=self.file_decrypt_block_height_var.get(),
                base=base_value
            )
            
            # 解密文件
            file_path, file_name, file_ext, decrypted_text, binary_string = decryptor.decrypt_image_to_file(image_path, save_path)
            
            # 发送结果到主线程
            self.message_queue.put(("status", "文件解密完成"))
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("message", "info", "成功", f"文件已解密并保存到: {file_path}"))
            
            # 更新UI
            self.root.after(0, self._update_file_decrypt_result, file_path, file_name, file_ext, decrypted_text, binary_string)
            
        except ValueError as e:
            # 检查是否是像素限制错误
            if "图片尺寸过大" in str(e) and "可能存在安全风险" in str(e):
                # 发送像素限制错误到主线程
                self.message_queue.put(("pixel_limit_error_decrypt", str(e), image_path))
            else:
                # 发送错误信息到主线程
                self.message_queue.put(("status", "解密失败"))
                self.message_queue.put(("message", "error", "错误", f"解密过程中出错: {str(e)}"))
        except Exception as e:
            # 发送错误信息到主线程
            self.message_queue.put(("status", "文件解密失败"))
            self.message_queue.put(("message", "error", "错误", f"文件解密过程中出错: {str(e)}"))
        finally:
            # 隐藏进度条
            self.message_queue.put(("hide_progress",))
            # 重新启用解密按钮
            self.root.after(0, self._enable_file_decrypt_button)
    
    def _decrypt_file_thread_ignore_limit(self, image_path, save_path):
        """在后台线程中执行文件解密操作（忽略像素限制）"""
        try:
            # 确保默认输出目录存在
            if not os.path.exists(self.default_output_dir):
                os.makedirs(self.default_output_dir)
            
            # 如果save_path不是绝对路径，则将其放在默认输出目录中
            if not os.path.isabs(save_path):
                save_path = os.path.join(self.default_output_dir, save_path)
            
            # 创建解密器
            # 获取选择的进制，如果是"自动识别"则传入None
            base_value = self.file_decrypt_base_var.get()
            if base_value == "自动识别":
                base_value = None
            else:
                # 将字符串转换为整数
                try:
                    base_value = int(base_value)
                except ValueError:
                    base_value = None
            
            # 创建文件解密器，设置ignore_pixel_limit=True以忽略像素限制
            decryptor = ImageToFileDecryptor(
                block_width=self.file_decrypt_block_width_var.get(),
                block_height=self.file_decrypt_block_height_var.get(),
                base=base_value,
                ignore_pixel_limit=True
            )
            
            # 解密文件
            file_path, file_name, file_ext, decrypted_text, binary_string = decryptor.decrypt_image_to_file(image_path, save_path)
            
            # 发送结果到主线程
            self.message_queue.put(("status", "文件解密完成"))
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("message", "info", "成功", f"文件已解密并保存到: {file_path}"))
            
            # 更新UI
            self.root.after(0, self._update_file_decrypt_result, file_path, file_name, file_ext, decrypted_text, binary_string)
            
        except Exception as e:
            # 发送错误信息到主线程
            self.message_queue.put(("status", "文件解密失败"))
            self.message_queue.put(("message", "error", "错误", f"文件解密过程中出错: {str(e)}"))
        finally:
            # 隐藏进度条
            self.message_queue.put(("hide_progress",))
            # 重新启用解密按钮
            self.root.after(0, self._enable_file_decrypt_button)
    
    def _update_file_decrypt_result(self, file_path, file_name, file_ext, decrypted_text, binary_string):
        """将文件解密结果和二进制表示保存为txt文件"""
        try:
            # 获取图片路径
            image_path = self.file_decrypt_image_path_var.get()
            if not image_path:
                messagebox.showerror("错误", "无法获取图片路径")
                return
            
            # 获取图片所在目录
            image_dir = os.path.dirname(image_path)
            
            # 获取图片文件名（不带扩展名）
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # 创建解密结果信息文件路径
            result_info_path = os.path.join(image_dir, f"{image_name}_解密信息.txt")
            
            # 创建二进制表示文件路径
            binary_file_path = os.path.join(image_dir, f"{image_name}_二进制表示.txt")
            
            # 保存解密结果信息到txt文件
            with open(result_info_path, 'w', encoding='utf-8') as f:
                f.write(f"文件名: {file_name}\n")
                f.write(f"文件类型: {file_ext}\n")
                f.write(f"保存路径: {file_path}\n")
                f.write(f"解密文本: {decrypted_text}\n")
            
            # 保存二进制表示到txt文件
            with open(binary_file_path, 'w', encoding='utf-8') as f:
                f.write(binary_string)
            
            # 清空界面上的文本框
            self.file_decrypt_result_text.delete("1.0", tk.END)
            self.file_decrypt_binary_text.delete("1.0", tk.END)
            
            # 在界面上显示文件保存路径
            self.file_decrypt_result_text.insert(tk.END, f"文件已解密并保存到: {file_path}")
            self.file_decrypt_binary_text.insert(tk.END, f"解密信息已保存到: {result_info_path}\n二进制表示已保存到: {binary_file_path}")
            
            # 显示成功消息
            messagebox.showinfo("成功", f"文件已解密并保存到:\n{file_path}\n\n解密信息已保存到:\n{result_info_path}\n\n二进制表示已保存到:\n{binary_file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存解密结果时出错: {str(e)}")
    
    def _enable_file_decrypt_button(self):
        """重新启用文件解密按钮"""
        for widget in self.file_decrypt_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget("text") == "解密文件":
                        child.config(state=tk.NORMAL)
    
    def apply_recommended_encrypt_values(self):
        """应用加密选项卡的推荐值"""
        # 获取文本长度
        text_length = len(self.text_input.get("1.0", tk.END).strip())
        
        # 获取进制
        base_value = self.base_var.get()
        
        # 计算推荐的块大小
        # 基础块大小
        base_block_width = 9
        base_block_height = 16
        
        # 根据文本长度调整
        # 文本长度因子：短文本使用较小块，长文本使用较大块
        if text_length < 100:
            length_factor = 0.7  # 短文本使用较小的块
        elif text_length < 1000:
            length_factor = 1.0  # 中等长度文本使用标准块
        else:
            length_factor = 1.3  # 长文本使用较大的块
        
        # 根据进制调整 - 更精确的进制因子计算
        # 不同进制有不同的颜色复杂度和信息密度
        if base_value == 2:
            # 二进制：只有黑白两色，信息密度低，需要较大的块来保证可识别性
            base_factor = 1.4
        elif base_value == 3:
            # 三进制：三种颜色，信息密度较低
            base_factor = 1.2
        elif base_value <= 4:
            # 四进制：四种颜色，信息密度较低
            base_factor = 1.0
        elif base_value <= 8:
            # 八进制及以下：中等信息密度
            base_factor = 0.9
        elif base_value <= 10:
            # 十进制：较高信息密度，可以使用较小的块
            base_factor = 0.8
        elif base_value <= 16:
            # 十六进制：高信息密度，可以使用更小的块
            base_factor = 0.7
        else:
            # 其他进制：默认值
            base_factor = 1.0
        
        # 计算最终推荐的块大小
        recommended_width = max(5, min(20, int(base_block_width * length_factor * base_factor)))
        recommended_height = max(8, min(30, int(base_block_height * length_factor * base_factor)))
        
        # 确保宽高比合理
        aspect_ratio = recommended_width / recommended_height
        if aspect_ratio < 0.4:  # 太窄
            recommended_width = int(recommended_height * 0.5)
        elif aspect_ratio > 1.0:  # 太宽
            recommended_height = int(recommended_width * 1.2)
        
        # 应用推荐值
        self.block_width_var.set(recommended_width)
        self.block_height_var.set(recommended_height)
        
        # 显示进制特点说明
        base_description = ""
        if base_value == 2:
            base_description = "二进制：黑白两色，信息密度低"
        elif base_value == 3:
            base_description = "三进制：三色，信息密度较低"
        elif base_value <= 4:
            base_description = "四进制：四色，信息密度较低"
        elif base_value <= 8:
            base_description = f"{base_value}进制：中等信息密度"
        elif base_value <= 10:
            base_description = f"{base_value}进制：较高信息密度"
        elif base_value <= 16:
            base_description = f"{base_value}进制：高信息密度，支持更多颜色"
        
        messagebox.showinfo("推荐值", f"已应用推荐值：\n块宽度: {recommended_width}\n块高度: {recommended_height}\n\n计算依据：\n文本长度: {text_length} 字符\n{base_description}")
    
    def apply_recommended_decrypt_values(self):
        """应用解密选项卡的推荐值"""
        # 对于解密，使用默认值作为推荐值
        self.decrypt_block_width_var.set(9)
        self.decrypt_block_height_var.set(16)
        
        messagebox.showinfo("推荐值", f"已应用推荐值：\n块宽度: {self.decrypt_block_width_var.get()}\n块高度: {self.decrypt_block_height_var.get()}")
    
    def apply_recommended_file_encrypt_values(self):
        """应用文件加密选项卡的推荐值"""
        # 获取文件路径
        file_path = self.file_to_encrypt_var.get()
        base_value = self.file_base_var.get()
        
        # 默认值
        recommended_width = 9
        recommended_height = 16
        
        if file_path and os.path.exists(file_path):
            # 获取文件大小（字节）
            file_size = os.path.getsize(file_path)
            
            # 计算文件大小因子
            # 使用对数函数，使文件大小的影响更加平滑
            if file_size > 0:
                # 对数函数：log(文件大小/1024 + 1) / 10 + 0.5
                # 这样小文件接近0.5，中等文件接近1.0，大文件接近1.5
                size_factor = math.log10(file_size / 1024 + 1) / 2 + 0.5
                size_factor = max(0.5, min(2.0, size_factor))  # 限制在0.5-2.0之间
            else:
                size_factor = 1.0
            
            # 计算最大像素限制下的最小块大小
            # 假设最大宽度为800像素，最大高度为600像素
            max_width = 800
            max_height = 600
            max_pixels = 50000000  # 50兆像素
            
            # 估算需要的字符数（Base64编码后大约是原文件的1.33倍）
            estimated_chars = int(file_size * 1.33 * 1.5)  # 1.5是安全系数
            
            # 计算最小块大小以确保不超过最大像素
            if estimated_chars > 0:
                # 每行字符数 = max_width / block_width
                # 行数 = estimated_chars / 每行字符数
                # 总像素 = 行数 * block_height * max_width
                # 解这个方程得到最小块大小
                
                # 简化计算：假设块宽高比为1:1.8（默认比例）
                min_block_size = math.sqrt(max_pixels / (estimated_chars * 1.8))
                min_block_size = max(5, min_block_size)  # 最小5像素
                
                # 根据文件大小调整
                recommended_width = max(5, min(15, int(min_block_size * size_factor)))
                recommended_height = max(8, min(25, int(recommended_width * 1.8)))
            else:
                # 如果文件为空，使用默认值
                recommended_width = 9
                recommended_height = 16
        else:
            # 如果没有选择文件，使用默认值
            recommended_width = 9
            recommended_height = 16
        
        # 根据进制调整 - 更精确的进制因子计算
        # 不同进制有不同的颜色复杂度和信息密度
        if base_value == 2:
            # 二进制：只有黑白两色，信息密度低，需要较大的块来保证可识别性
            recommended_width = min(15, int(recommended_width * 1.4))
            recommended_height = min(25, int(recommended_height * 1.4))
        elif base_value == 3:
            # 三进制：三种颜色，信息密度较低
            recommended_width = min(15, int(recommended_width * 1.2))
            recommended_height = min(25, int(recommended_height * 1.2))
        elif base_value <= 4:
            # 四进制：四种颜色，信息密度较低
            recommended_width = min(15, int(recommended_width * 1.0))
            recommended_height = min(25, int(recommended_height * 1.0))
        elif base_value <= 8:
            # 八进制及以下：中等信息密度
            recommended_width = max(5, int(recommended_width * 0.9))
            recommended_height = max(8, int(recommended_height * 0.9))
        elif base_value <= 10:
            # 十进制：较高信息密度，可以使用较小的块
            recommended_width = max(5, int(recommended_width * 0.8))
            recommended_height = max(8, int(recommended_height * 0.8))
        elif base_value <= 16:
            # 十六进制：高信息密度，可以使用更小的块
            recommended_width = max(5, int(recommended_width * 0.7))
            recommended_height = max(8, int(recommended_height * 0.7))
        else:
            # 其他进制：默认值
            pass
        
        # 应用推荐值
        self.file_block_width_var.set(recommended_width)
        self.file_block_height_var.set(recommended_height)
        
        # 显示文件大小信息
        file_size_info = ""
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size < 1024:
                file_size_info = f"文件大小: {file_size} 字节"
            elif file_size < 1024 * 1024:
                file_size_info = f"文件大小: {file_size/1024:.2f} KB"
            else:
                file_size_info = f"文件大小: {file_size/(1024*1024):.2f} MB"
        
        # 显示进制特点说明
        base_description = ""
        if base_value == 2:
            base_description = "二进制：黑白两色，信息密度低"
        elif base_value == 3:
            base_description = "三进制：三色，信息密度较低"
        elif base_value <= 4:
            base_description = "四进制：四色，信息密度较低"
        elif base_value <= 8:
            base_description = f"{base_value}进制：中等信息密度"
        elif base_value <= 10:
            base_description = f"{base_value}进制：较高信息密度"
        elif base_value <= 16:
            base_description = f"{base_value}进制：高信息密度，支持更多颜色"
        
        messagebox.showinfo("推荐值", f"已应用推荐值：\n块宽度: {recommended_width}\n块高度: {recommended_height}\n\n计算依据：\n{file_size_info}\n{base_description}")
    
    def apply_recommended_file_decrypt_values(self):
        """应用文件解密选项卡的推荐值"""
        # 对于文件解密，使用默认值作为推荐值
        self.file_decrypt_block_width_var.set(9)
        self.file_decrypt_block_height_var.set(16)
        
        messagebox.showinfo("推荐值", f"已应用推荐值：\n块宽度: {self.file_decrypt_block_width_var.get()}\n块高度: {self.file_decrypt_block_height_var.get()}")


def main():
    root = tk.Tk()
    app = ImageEncryptorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()