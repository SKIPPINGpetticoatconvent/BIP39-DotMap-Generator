# main.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import hashlib
import random
import argparse
import getpass
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# 检查是否支持 SHA3-256
sha3_available = hasattr(hashlib, "sha3_256")

# --- 字体设置 ---
# 使用 DejaVu 字体以完美显示 ● 和 ○ 符号。
FONT_FILE_REGULAR = "DejaVuSans.ttf"
FONT_FILE_BOLD = "DejaVuSans-Bold.ttf"
FONT_NAME = "DejaVuSans"
FONT_NAME_BOLD = "DejaVuSans-Bold"

try:
    if not os.path.exists(FONT_FILE_REGULAR) or not os.path.exists(FONT_FILE_BOLD):
        raise FileNotFoundError()

    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE_REGULAR))
    pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, FONT_FILE_BOLD))
    print(f"成功加载字体文件: {FONT_FILE_REGULAR}, {FONT_FILE_BOLD}")

except FileNotFoundError:
    print(f"错误：字体文件 'DejaVuSans.ttf' 或 'DejaVuSans-Bold.ttf' 未找到！")
    print("请确保这些文件和 main.py 在同一个文件夹下。")
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"
except Exception as e:
    print(f"加载字体时发生未知错误: {e}")
    FONT_NAME = "Helvetica"
    FONT_NAME_BOLD = "Helvetica-Bold"


def load_words():
    """加载 english.txt 并做基本校验（2048 个 BIP39 单词）"""
    try:
        with open("english.txt", "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(
            "Error: 'english.txt' not found. Please ensure it is in the same directory as the script."
        )

    if len(words) != 2048:
        raise ValueError(f"Error: english.txt has {len(words)} words (should be 2048).")

    return words


def encrypt_columns(col1: str, col2: str, col3: str, seed: int, bits: int = 11):
    """对点阵列进行基于种子随机性的加密置换"""
    # 使用独立的随机数生成器，避免污染全局 random 状态
    r = random.Random(seed)

    # 基于种子生成随机移位值
    shift1 = r.randint(0, 3)
    shift2 = r.randint(0, 3)
    shift3 = r.randint(0, 2 if bits == 11 else 3)  # 12位时col3为4位

    # 对每列进行循环移位
    encrypted_col1 = col1[shift1:] + col1[:shift1]
    encrypted_col2 = col2[shift2:] + col2[:shift2]
    encrypted_col3 = col3[shift3:] + col3[:shift3]

    return encrypted_col1, encrypted_col2, encrypted_col3


def decrypt_columns(col1: str, col2: str, col3: str, seed: int, bits: int = 11):
    """对加密的点阵列进行解密恢复原始顺序"""
    # 使用与加密相同的独立 RNG
    r = random.Random(seed)

    # 获取加密时使用的移位值
    shift1 = r.randint(0, 3)
    shift2 = r.randint(0, 3)
    shift3 = r.randint(0, 2 if bits == 11 else 3)  # 12位时col3为4位

    # 逆向移位进行解密
    decrypted_col1 = col1[-shift1:] + col1[:-shift1] if shift1 > 0 else col1
    decrypted_col2 = col2[-shift2:] + col2[:-shift2] if shift2 > 0 else col2
    decrypted_col3 = col3[-shift3:] + col3[:-shift3] if shift3 > 0 else col3

    return decrypted_col1, decrypted_col2, decrypted_col3


def apply_encryption(col1: str, col2: str, col3: str, seed: int, bits: int, encrypt_mode: str):
    """
    根据加密模式决定是否进行旋转加密。
    encrypt_mode:
        - "none"   : 无加密（不旋转）
        - "sha256" : 使用 seed 做随机旋转
    """
    if encrypt_mode == "none":
        # 无加密模式，直接返回
        return col1, col2, col3
    else:
        # 默认使用原有加密逻辑（seed来自密码哈希）
        return encrypt_columns(col1, col2, col3, seed, bits)


def number_to_dotmap(n: int, seed: int, bits: int = 11, encrypt_mode: str = "sha256"):
    """将单词索引号 n 转换为二进制的点图 (为手动解码优化)，并应用（可选）加密"""
    # 1. 生成标准的二进制字符串 (高位在前)
    binary_str = bin(n - 1)[2:].zfill(bits)

    # 2. 将二进制字符串反转，以实现 1 -> 最高权重 的顺序 (低位在前)
    reversed_bits = binary_str[::-1]

    # 3. 根据反转后的字符串生成点图
    dots = ["●" if b == "1" else "○" for b in reversed_bits]

    if bits == 11:
        col1 = "".join(dots[0:4])   # 1,2,4,8
        col2 = "".join(dots[4:8])   # 16,32,64,128
        col3 = "".join(dots[8:11])  # 256,512,1024
    else:  # bits == 12
        col1 = "".join(dots[0:4])   # 1,2,4,8
        col2 = "".join(dots[4:8])   # 16,32,64,128
        col3 = "".join(dots[8:12])  # 256,512,1024,2048

    # 4. 应用加密模式（无加密 / SHA-256）
    col1, col2, col3 = apply_encryption(col1, col2, col3, seed, bits, encrypt_mode)

    return col1, col2, col3


def generate_pdf(words, output_file="bip39_encrypted_dotmap.pdf", seed=None, bits=11, encrypt_mode: str = "sha256"):
    """为物理雕刻和手动恢复场景，生成优化后的 PDF"""
    if seed is None:
        # 默认种子（无密码时用），这里用固定常量即可
        # 对于 encrypt_mode == "none" 实际不会使用
        seed = int(hashlib.sha256(b"default").hexdigest(), 16)

    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    x_margin = 20 * mm
    y_margin = 20 * mm
    line_height = 5 * mm

    y = height - y_margin
    c.setFont(FONT_NAME_BOLD, 16)
    c.drawString(x_margin, y, "BIP39 Mnemonic Encrypted DotMap (Manual Recovery)")
    y -= 12 * mm

    text = c.beginText(x_margin, y)
    text.setFont(FONT_NAME, 10)
    text.setLeading(14)

    text.textLine("The meaning of each dot is as follows:")
    text.textLine("  ● (Solid Dot)   represents a 1 (the weight is selected)")
    text.textLine("  ○ (Hollow Dot)  represents a 0 (the weight is not selected)")
    text.textLine(" ")

    if encrypt_mode == "none":
        text.textLine("ENCRYPTION MODE: None. Dots in each column are NOT rotated.")
        text.textLine("You can directly sum the weights of all ● dots and add 1 to get the word index.")
    else:
        text.textLine("ENCRYPTION NOTE: Dots within each column are randomly rotated using password-derived seed.")
        text.textLine("Use the same password to decrypt and recover original positions.")
    text.textLine(" ")

    # 【关键】说明权重顺序
    weight_description = "1-1024" if bits == 11 else "1-2048"
    text.textLine(
        f"FOR EASY MANUAL CALCULATION, the {bits} dot positions are ordered from LOWEST to HIGHEST weight ({weight_description}):"
    )

    text.setFont(FONT_NAME_BOLD, 9)
    if bits == 11:
        text.textLine("   Weights: 1 | 2 | 4 | 8 || 16 | 32 | 64 | 128 || 256 | 512 | 1024")
    else:
        text.textLine("   Weights: 1 | 2 | 4 | 8 || 16 | 32 | 64 | 128 || 256 | 512 | 1024 | 2048")

    c.drawText(text)
    y = text.getY() - 10 * mm

    font_size = 9
    x_index = x_margin
    x_word = x_margin + 18 * mm
    x_col1 = x_margin + 55 * mm
    x_col2 = x_margin + 85 * mm
    x_col3 = x_margin + (115 if bits == 11 else 125) * mm

    def draw_header(y_pos):
        c.setFont(FONT_NAME_BOLD, font_size)
        c.drawString(x_index, y_pos, "Index")
        c.drawString(x_word, y_pos, "Word")
        # 列标题根据是否加密动态标记
        if encrypt_mode == "none":
            suffix = ""
        else:
            suffix = " (Random)"
        c.drawString(x_col1, y_pos, f"Col1{suffix}")
        c.drawString(x_col2, y_pos, f"Col2{suffix}")
        c.drawString(x_col3, y_pos, f"Col3{suffix}")
        c.line(x_margin, y_pos - 1.5 * mm, width - x_margin, y_pos - 1.5 * mm)

    draw_header(y)
    y -= line_height * 1.5

    c.setFont(FONT_NAME, font_size)
    for i, word in enumerate(words, start=1):
        if y < y_margin:
            c.showPage()
            y = height - y_margin
            draw_header(y)
            y -= line_height * 1.5
            c.setFont(FONT_NAME, font_size)

        col1, col2, col3 = number_to_dotmap(i, seed, bits, encrypt_mode)

        c.drawString(x_index, y, str(i))
        c.drawString(x_word, y, word)
        c.drawString(x_col1, y, col1)
        c.drawString(x_col2, y, col2)
        c.drawString(x_col3, y, col3)

        y -= line_height

    c.save()
    print(f"[Success] PDF generated: {output_file}")


def get_password_seed(password: str) -> int:
    """从密码生成种子，优先使用 SHA3-256（否则回退到 SHA-256）"""
    if sha3_available:
        hash_obj = hashlib.sha3_256(password.encode("utf-8"))
        hash_name = "SHA3-256"
    else:
        hash_obj = hashlib.sha256(password.encode("utf-8"))
        hash_name = "SHA-256"

    print(f"使用哈希算法: {hash_name}")
    # 使用完整哈希值作为大整数种子，避免人为截断熵
    return int(hash_obj.hexdigest(), 16)


class BIP39GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BIP39 Encrypted DotMap Generator")
        self.root.geometry("500x380")
        self.root.resizable(False, False)

        # 模式选择
        ttk.Label(root, text="模式选择:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.mode_var = tk.StringVar(value="11")
        self.mode_frame = ttk.Frame(root)
        self.mode_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ttk.Radiobutton(self.mode_frame, text="11位 (权重1-1024)", variable=self.mode_var, value="11").pack(side=tk.LEFT)
        ttk.Radiobutton(self.mode_frame, text="12位 (权重1-2048)", variable=self.mode_var, value="12").pack(side=tk.LEFT)

        # 密码输入
        ttk.Label(root, text="密码:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(root, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # 显示/隐藏密码
        self.show_password_var = tk.BooleanVar()
        ttk.Checkbutton(
            root,
            text="显示密码",
            variable=self.show_password_var,
            command=self.toggle_password
        ).grid(row=1, column=2, padx=10, pady=10)

        # 加密模式选择
        ttk.Label(root, text="加密模式:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.encrypt_mode_var = tk.StringVar(value="sha256")
        encrypt_frame = ttk.Frame(root)
        encrypt_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        ttk.Radiobutton(encrypt_frame, text="无加密", variable=self.encrypt_mode_var, value="none").pack(side=tk.LEFT)
        ttk.Radiobutton(encrypt_frame, text="SHA-256 加密", variable=self.encrypt_mode_var, value="sha256").pack(side=tk.LEFT)

        # 输出文件选择
        ttk.Label(root, text="输出文件:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.output_var = tk.StringVar(value="bip39_encrypted_dotmap.pdf")
        self.output_entry = ttk.Entry(root, textvariable=self.output_var)
        self.output_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        ttk.Button(root, text="浏览...", command=self.browse_output).grid(row=3, column=2, padx=10, pady=10)

        # 生成按钮
        self.generate_button = ttk.Button(root, text="生成PDF", command=self.generate_pdf)
        self.generate_button.grid(row=4, column=1, pady=20)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_label = ttk.Label(root, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

        # 配置列权重
        root.columnconfigure(1, weight=1)

    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="选择输出文件",
        )
        if filename:
            self.output_var.set(filename)

    def generate_pdf(self):
        mode = self.mode_var.get()
        password = self.password_var.get()
        output_file = self.output_var.get()
        encrypt_mode = self.encrypt_mode_var.get()

        # 无加密模式下可以不输入密码；SHA-256 模式必须输入密码
        if encrypt_mode != "none" and not password:
            messagebox.showerror("错误", "SHA-256 加密模式下必须输入密码！")
            return

        if not output_file:
            messagebox.showerror("错误", "请选择输出文件！")
            return

        # 禁用按钮
        self.generate_button.config(state="disabled")
        self.status_var.set("正在生成PDF...")
        self.progress_var.set(0)

        # 在后台线程中运行PDF生成
        thread = threading.Thread(
            target=self._generate_pdf_thread,
            args=(mode, password, output_file, encrypt_mode),
            daemon=True,
        )
        thread.start()

    def _generate_pdf_thread(self, mode, password, output_file, encrypt_mode):
        try:
            bits = int(mode)
            list_length = 2 ** bits  # 11位=2048, 12位=4096，但我们只有2048个单词

            all_words = load_words()
            words = all_words[:list_length] if list_length <= len(all_words) else all_words

            # 生成种子（无加密模式下种子为0，不会被使用）
            if encrypt_mode == "none":
                seed = 0
            else:
                seed = get_password_seed(password)

            weight_range = "1-1024" if bits == 11 else "1-2048"

            # 以下所有 UI 操作通过 root.after 切回主线程，保证线程安全
            self.root.after(0, lambda: self.status_var.set(
                f"正在生成 {bits}位模式 PDF (权重 {weight_range}, 模式: {encrypt_mode})..."
            ))
            self.root.after(0, lambda: self.progress_var.set(50))

            # 真正执行 PDF 生成（纯计算 + 文件 IO，不触碰 Tk 对象）
            generate_pdf(words, output_file, seed, bits, encrypt_mode)

            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_var.set(f"PDF生成成功: {output_file}"))

            if encrypt_mode == "none":
                msg = "PDF已生成！（无加密模式）"
            else:
                msg = f"PDF已生成!\n种子: {seed}"

            self.root.after(0, lambda: messagebox.showinfo("成功", msg))

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"生成失败: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"生成PDF时出错:\n{str(e)}"))
        finally:
            self.root.after(0, lambda: self.generate_button.config(state="normal"))
            self.root.after(0, lambda: self.progress_var.set(0))


def main():
    import sys

    if len(sys.argv) > 1:
        # 命令行模式
        parser = argparse.ArgumentParser(description="Generate BIP39 encrypted dotmap PDF")
        parser.add_argument(
            "--mode",
            choices=["11", "12"],
            default="11",
            help="Bits mode (11: weights 1-1024, 12: weights 1-2048)",
        )
        parser.add_argument(
            "--password",
            help="Password for encryption (will prompt if not provided in sha256 mode)",
        )
        parser.add_argument(
            "--output",
            default="bip39_encrypted_dotmap.pdf",
            help="Output PDF file path",
        )
        parser.add_argument(
            "--encrypt",
            choices=["none", "sha256"],
            default="sha256",
            help="Encryption mode: 'none' (no rotation) or 'sha256' (password-based rotation)",
        )

        args = parser.parse_args()

        bits = int(args.mode)
        list_length = 2 ** bits

        try:
            all_words = load_words()
            words = all_words[:list_length] if list_length <= len(all_words) else all_words

            encrypt_mode = args.encrypt

            if encrypt_mode == "none":
                seed = 0
                weight_range = "1-1024" if bits == 11 else "1-2048"
                print(
                    f"Generating PDF with {bits}-bit mode (weights {weight_range}) "
                    f"in NO-ENCRYPTION mode..."
                )
            else:
                # 获取密码
                if args.password:
                    password = args.password
                else:
                    password = getpass.getpass("Enter password for encryption: ")

                seed = get_password_seed(password)
                weight_range = "1-1024" if bits == 11 else "1-2048"

                print(
                    f"Generating PDF with {bits}-bit mode (weights {weight_range}) "
                    f"using password-based encryption (SHA-256/SHA3-256)..."
                )

            generate_pdf(words, args.output, seed, bits, encrypt_mode)

            if encrypt_mode != "none":
                print(f"Encryption seed: {seed} (derived from password)")

        except (FileNotFoundError, ValueError) as e:
            print(e)
    else:
        # GUI 模式
        root = tk.Tk()
        app = BIP39GUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
