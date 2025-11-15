# BIP39 DotMap Generator

A Python tool for generating BIP39 mnemonic dot maps, optimized for physical engraving and manual recovery scenarios. Supports encryption with optional password-based SHA-256 encryption mode.

[中文版本](README.md) | [English Version](README_EN.md)

## Project Overview

This project includes the main features:

- **BIP39 DotMap Generator**: Generates BIP39 mnemonic dot maps optimized for physical engraving and manual recovery
- **Encryption Support**: Two modes - plain dot maps or password-based SHA-256 encrypted rotation

## Features

- **Dot Map Conversion**: Converts 2048 BIP39 English words into easily recognizable dot map format
- **Manual Recovery Optimization**: Dots arranged from lowest to highest weight for easy manual calculation
- **PDF Generation**: Uses ReportLab to generate high-quality PDF documents
- **Font Support**: Supports custom fonts for perfect display of ● and ○ symbols
- **Pagination**: Automatically handles large datasets with page breaks
- **Encryption Modes**: Supports plain and SHA-256 password-encrypted modes
- **Dual Mode Support**: 11-bit (weights 1-1024) and 12-bit (weights 1-2048) modes
- **GUI Interface**: User-friendly graphical interface with password show/hide functionality

## How It Works

1. Reads 2048 BIP39 words from `english.txt` file
2. Converts each word's index number (1-2048) to 11-bit or 12-bit binary
3. Reverses binary bits so weights are ordered from low to high (11-bit: 1-1024, 12-bit: 1-2048)
4. Uses ● (solid dot) for 1 and ○ (hollow dot) for 0
5. Optionally applies random rotation encryption to each column based on encryption mode
6. Generates a PDF document containing words and their corresponding dot maps

## Encryption Mechanism

- **Plain Mode**: Dot maps are displayed directly without any rotation, suitable for quick manual recovery
- **SHA-256 Encryption Mode**: Uses password to generate seed for reversible random cyclic shifts of each column. Same password required for decryption to restore original dot map order.

## File Structure

- `main.py` - Main program file
- `english.txt` - BIP39 English word list (2048 words)
- `requirements.txt` - Python dependencies list
- `DejaVuSans.ttf` - Regular font file
- `DejaVuSans-Bold.ttf` - Bold font file
- `msyh.ttc` - Chinese font file (Microsoft YaHei)
- `bip39_dotmap_for_engraving.pdf` - Generated PDF output file

## System Requirements

- Python 3.6+
- ReportLab 3.0+
- Text editor with UTF-8 encoding support

## Quick Start

### Environment Preparation

1.  Install Python 3.6+
2.  Install ReportLab 3.0+

### Installation

Install dependencies using requirements.txt:

```bash
pip install -r requirements.txt
```

Or install ReportLab manually:

```bash
pip install reportlab
```

## Usage

### GUI Mode (Recommended)

Double-click `main.py` or run from command line:

```bash
python main.py
```

GUI Features:
- Select 11-bit or 12-bit mode
- Set password (required for SHA-256 encryption mode)
- Choose encryption mode (plain or SHA-256 encrypted)
- Custom output PDF filename
- Real-time progress display

### Command Line Mode

```bash
# 11-bit mode, plain text
python main.py --mode 11 --encrypt none --output my_dotmap.pdf

# 12-bit mode, SHA-256 encryption (will prompt for password)
python main.py --mode 12 --encrypt sha256 --output encrypted_dotmap.pdf

# Specify password via command line
python main.py --password mypassword --encrypt sha256 --output secure_dotmap.pdf
```

**Command Line Arguments:**
- `--mode`: Mode selection, 11 (weights 1-1024) or 12 (weights 1-2048)
- `--password`: Encryption password (used in SHA-256 mode)
- `--output`: Output PDF filename
- `--encrypt`: Encryption mode, none or sha256

### Required Files

Ensure these files are in the same directory:
- `main.py`
- `english.txt`
- `DejaVuSans.ttf` (recommended)
- `DejaVuSans-Bold.ttf` (recommended)

## Output Format

The PDF document includes:
- Title: BIP39 Mnemonic DotMap (Manual Recovery Optimized)
- Dot meaning explanation
- Weight order explanation (1 | 2 | 4 | 8 || 16 | 32 | 64 | 128 || 256 | 512 | 1024)
- Table with: Index number, English word, three dot map columns (corresponding to different weight ranges)

## Dot Map Interpretation

- **●** (Solid Dot) = 1 = Weight is selected
- **○** (Hollow Dot) = 0 = Weight is not selected

Dot maps are optimized for manual recovery with weights arranged in ascending order for easy calculation. In encrypted mode, each column is randomly rotated and requires the same password for proper interpretation.

## Troubleshooting

### Font Files Not Found
```
Error: Font files 'DejaVuSans.ttf' or 'DejaVuSans-Bold.ttf' not found!
Please ensure these files are in the same directory as the script.
```
**Solution**: Ensure font files exist, or the program will automatically fall back to Helvetica font.

### English Word File Not Found
```
Error: 'english.txt' not found. Please ensure it is in the same directory as the script.
```
**Solution**: Ensure `english.txt` exists in the program directory.

### Word Count Mismatch
```
Error: english.txt has X words (should be 2048).
```
**Solution**: Ensure `english.txt` contains the complete set of 2048 BIP39 words.

## License

This project is licensed under the [MIT License](LICENSE).

You are free to:
- Use, copy, and modify the code
- Use commercially
- Distribute original or modified versions

Simply retain the original copyright notice and license file when using.

**Important Notice**: This project is for educational and research purposes only. Please ensure compliance with local laws and cryptocurrency regulations when using BIP39-related features.

## Contributing

Issues and Pull Requests are welcome to improve this project.

If you have any questions or suggestions, please feel free to submit them.

## Running Offline

1. Ensure all dependencies are installed.
2. Run the program without an internet connection to guarantee the program has no backdoors and runs 100% offline.
3. The program runs completely based on local files with no network access required.

The program will generate `bip39_encrypted_dotmap.pdf` (or your specified filename).

## Security Notes

- **Password Security**: Use strong passwords for encryption. Password strength directly affects encryption security.
- **File Security**: Generated PDF files contain sensitive information, store them securely.
- **Offline Usage**: Recommended to run in offline environments to avoid potential security risks.
- **Backup**: Create multiple backups of important information.

## Version Features

Current version supports:
- 11-bit and 12-bit BIP39 word mapping
- SHA-256 and SHA3-256 hash algorithms (auto-detected)
- Password-protected dot map encryption
- Cross-platform GUI interface

---

[中文版本](README.md) | [English Version](README_EN.md)