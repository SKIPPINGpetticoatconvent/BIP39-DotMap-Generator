# BIP39 DotMap Generator

[中文版本](README.md) | [English Version](README_EN.md)

一个用于生成BIP39助记词点图的Python工具，专为物理雕刻和手动恢复场景优化。支持加密功能，可选择无加密或基于密码的SHA-256加密模式。

## 项目简介

本项目的主要功能：

- **BIP39 DotMap Generator**: 用于生成 BIP39 助记词点图，专为物理雕刻和手动恢复场景优化。
- **加密支持**: 支持两种模式 - 无加密（明文点图）和基于密码的加密（点图旋转加密）。

## 功能特性

- **点图转换**: 将2048个BIP39英文单词转换为易于识别的点图格式
- **手动恢复优化**: 点位按权重从低到高排列，便于手动计算
- **PDF生成**: 使用ReportLab生成高质量PDF文档
- **字体支持**: 支持自定义字体以完美显示●和○符号
- **分页处理**: 自动处理大量数据并分页显示
- **加密模式**: 支持无加密和SHA-256密码加密两种模式
- **双模式支持**: 支持11位（权重1-1024）和12位（权重1-2048）模式
- **GUI界面**: 提供友好的图形界面，支持密码显示/隐藏

## 工作原理

1. 读取 `english.txt`文件中的2048个BIP39单词
2. 将每个单词的索引号（1-2048）转换为11位或12位二进制
3. 将二进制位反转，使权重从低到高排列（11位: 1-1024, 12位: 1-2048）
4. 使用●（实心点）表示1，○（空心点）表示0
5. 根据加密模式选择是否对每列点图进行随机旋转加密
6. 生成包含单词和对应点图的PDF文档

## 加密原理

- **无加密模式**: 点图直接显示，不进行任何旋转，适合快速手动恢复
- **SHA-256加密模式**: 使用密码生成种子，对每列点图进行可逆的随机循环移位。解密时需要相同的密码才能恢复原始点图顺序。

## 文件说明

- `main.py` - 主程序文件，支持GUI和命令行两种模式
- `english.txt` - BIP39英文单词列表（2048个单词）
- `requirements.txt` - Python依赖包列表
- `DejaVuSans.ttf` - 常规字体文件（用于完美显示点图符号）
- `DejaVuSans-Bold.ttf` - 粗体字体文件
- `msyh.ttc` - 中文字体文件（微软雅黑，可选）
- `bip39_encrypted_dotmap.pdf` - 生成的PDF输出文件（默认名称）

## 系统要求

- Python 3.6+
- ReportLab 3.0+
- 支持UTF-8编码的文本编辑器

## 快速开始

### 环境准备

1. 安装 Python 3.6+
2. 安装 ReportLab 3.0+

### 安装依赖

使用 requirements.txt 安装依赖：

```bash
pip install -r requirements.txt
```

或手动安装 ReportLab：

```bash
pip install reportlab
```

## 使用方法

### GUI模式（推荐）

双击运行 `main.py` 或在命令行中执行：

```bash
python main.py
```

GUI界面功能：
- 选择11位或12位模式
- 设置密码（SHA-256加密模式下必填）
- 选择加密模式（无加密或SHA-256加密）
- 自定义输出PDF文件名
- 实时进度显示

### 命令行模式

```bash
# 11位模式，无加密
python main.py --mode 11 --encrypt none --output my_dotmap.pdf

# 12位模式，SHA-256加密（会提示输入密码）
python main.py --mode 12 --encrypt sha256 --output encrypted_dotmap.pdf

# 使用命令行指定密码
python main.py --password mypassword --encrypt sha256 --output secure_dotmap.pdf
```

**命令行参数说明：**
- `--mode`: 选择模式，11 (权重1-1024) 或 12 (权重1-2048)
- `--password`: 加密密码（SHA-256模式下使用）
- `--output`: 输出PDF文件名
- `--encrypt`: 加密模式，none 或 sha256

### 必需文件

确保以下文件在同一目录下：
- `main.py`
- `english.txt`
- `DejaVuSans.ttf` (推荐)
- `DejaVuSans-Bold.ttf` (推荐)

## 输出格式说明

PDF文档包含以下信息：

- 标题：BIP39 Mnemonic Encrypted DotMap (Manual Recovery)
- 加密模式说明（无加密或需要密码解密）
- 点图含义说明
- 权重顺序说明（11位: 1-1024, 12位: 1-2048）
- 表格包含：索引号、英文单词、三个点图列（Col1, Col2, Col3）
- 每列可能经过随机旋转（加密模式下）

## 点图解读

- **●** (实心点) = 1 = 该权重被选中
- **○** (空心点) = 0 = 该权重未被选中

点图专为手动恢复优化，权重按升序排列便于计算。加密模式下每列点图经过随机旋转，需要使用相同密码才能正确解读。

## 故障排除

### 字体文件未找到

```
错误：字体文件 'DejaVuSans.ttf' 或 'DejaVuSans-Bold.ttf' 未找到！
请确保这些文件和 main.py 在同一个文件夹下。
```

**解决方法**：确保字体文件存在，或程序将自动回退到Helvetica字体。

### 英文单词文件未找到

```
Error: 'english.txt' not found. Please ensure it is in the same directory as the script.
```

**解决方法**：确保 `english.txt`文件存在于程序目录中。

### 单词数量不匹配

```
Error: english.txt has X words (should be 2048).
```

**解决方法**：确保 `english.txt`包含完整的2048个BIP39单词。

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

您可以自由地：

- 使用、复制和修改代码
- 商业使用
- 分发原始或修改版本

使用时只需保留原始版权声明和许可证文件即可。

**重要提醒**：本项目仅供学习和研究使用。在使用BIP39相关功能时，请确保遵守当地法律法规和相关加密货币监管要求。

## 贡献

[中文版本](README.md) | [English Version](README_EN.md)
欢迎提交 Issue 和 Pull Request 来改进这个项目。

如果您有任何问题或建议，请随时提出。

## 离线运行

1. 确保已安装所有依赖。
2. 在没有网络连接的情况下运行程序，以保证程序无后门，100% 离线运行。
3. 程序完全基于本地文件运行，不需要任何网络访问。

程序将生成 `bip39_encrypted_dotmap.pdf` 文件（或您指定的文件名）。

## 安全注意事项

- **密码安全**: 使用强密码进行加密。密码强度直接影响加密的安全性。
- **文件安全**: 生成的PDF文件包含敏感信息，请妥善保管。
- **离线使用**: 建议在离线环境下运行，以避免潜在的安全风险。
- **备份**: 重要信息请多重备份。

## 版本更新

当前版本支持：
- 11位和12位BIP39单词映射
- SHA-256和SHA3-256哈希算法（自动检测）
- 密码保护的点图加密
- 跨平台GUI界面
