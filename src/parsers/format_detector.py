"""
Format detector for NABU data files.

This module provides functions to detect file format, encoding, and extract metadata
from filenames. It performs NO semantic interpretation - just format detection.
"""

import re
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import chardet
from loguru import logger


# ============================================================================
# ENUMS
# ============================================================================

class FileFormat(str, Enum):
    """Supported file formats."""
    JSON = "json"
    XML = "xml"
    HTML = "html"
    EXCEL = "excel"
    CSV = "csv"
    TEXT = "text"
    UNKNOWN = "unknown"


# ============================================================================
# FORMAT DETECTION
# ============================================================================

def detect_format(file_path: str | Path) -> FileFormat:
    """
    Detect file format by extension and content.

    Args:
        file_path: Path to the file

    Returns:
        FileFormat enum value

    Note:
        This performs NO semantic understanding - just format detection!
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return FileFormat.UNKNOWN

    if not file_path.is_file():
        logger.error(f"Not a file: {file_path}")
        return FileFormat.UNKNOWN

    # First, try detection by extension
    extension = file_path.suffix.lower()

    extension_map = {
        '.json': FileFormat.JSON,
        '.xml': FileFormat.XML,
        '.html': FileFormat.HTML,
        '.htm': FileFormat.HTML,
        '.xlsx': FileFormat.EXCEL,
        '.xls': FileFormat.EXCEL,
        '.csv': FileFormat.CSV,
        '.txt': FileFormat.TEXT,
    }

    if extension in extension_map:
        logger.debug(f"Detected format by extension: {extension_map[extension].value} ({file_path.name})")
        return extension_map[extension]

    # If no extension match, try content-based detection
    try:
        # Read first few bytes to detect format
        with open(file_path, 'rb') as f:
            header = f.read(1024)

        # Try to decode as UTF-8 for text-based format detection
        try:
            content_preview = header.decode('utf-8', errors='ignore')
        except Exception:
            # Try with detected encoding
            encoding = detect_encoding(file_path)
            try:
                content_preview = header.decode(encoding, errors='ignore')
            except Exception:
                content_preview = ""

        # Detect by content patterns
        content_lower = content_preview.strip().lower()

        # XML/SOAP detection (including files without .xml extension)
        if content_lower.startswith('<?xml') or '<s:envelope' in content_lower or '<soap:envelope' in content_lower:
            logger.debug(f"Detected XML by content: {file_path.name}")
            return FileFormat.XML

        # JSON detection
        if content_lower.startswith('{') or content_lower.startswith('['):
            logger.debug(f"Detected JSON by content: {file_path.name}")
            return FileFormat.JSON

        # HTML detection
        if content_lower.startswith('<!doctype html') or content_lower.startswith('<html'):
            logger.debug(f"Detected HTML by content: {file_path.name}")
            return FileFormat.HTML

        # Excel binary format detection
        if header.startswith(b'PK\x03\x04'):  # ZIP signature (XLSX)
            logger.debug(f"Detected XLSX by content: {file_path.name}")
            return FileFormat.EXCEL

        if header.startswith(b'\xD0\xCF\x11\xE0'):  # OLE signature (XLS)
            logger.debug(f"Detected XLS by content: {file_path.name}")
            return FileFormat.EXCEL

        # CSV detection (look for comma/semicolon separated values)
        lines = content_preview.split('\n')[:5]
        if lines:
            # Check if lines have consistent delimiters
            for delimiter in [',', ';', '\t']:
                delimiter_counts = [line.count(delimiter) for line in lines if line.strip()]
                if delimiter_counts and len(set(delimiter_counts)) == 1 and delimiter_counts[0] > 0:
                    logger.debug(f"Detected CSV by content: {file_path.name}")
                    return FileFormat.CSV

        # Default to text if nothing else matches and it's readable text
        if content_preview and len(content_preview.strip()) > 0:
            logger.debug(f"Detected TEXT by default: {file_path.name}")
            return FileFormat.TEXT

    except Exception as e:
        logger.error(f"Error during format detection for {file_path}: {e}")

    logger.warning(f"Could not detect format for: {file_path.name}")
    return FileFormat.UNKNOWN


# ============================================================================
# ENCODING DETECTION
# ============================================================================

def detect_encoding(file_path: str | Path) -> str:
    """
    Detect file encoding using chardet.

    Args:
        file_path: Path to the file

    Returns:
        Encoding name (e.g., 'utf-8', 'windows-1251', 'koi8-u')

    Note:
        Defaults to 'utf-8' if detection fails.
    """
    file_path = Path(file_path)

    try:
        # Read a sample of the file for encoding detection
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB

        if not raw_data:
            logger.warning(f"Empty file for encoding detection: {file_path.name}")
            return 'utf-8'

        # Detect encoding
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0.0)

        if encoding:
            logger.debug(f"Detected encoding: {encoding} (confidence: {confidence:.2f}) for {file_path.name}")

            # Normalize encoding names
            encoding_lower = encoding.lower()

            # Map common variations to standard names
            if 'utf-8' in encoding_lower or 'utf8' in encoding_lower:
                return 'utf-8'
            elif 'windows-1251' in encoding_lower or 'cp1251' in encoding_lower:
                return 'windows-1251'
            elif 'koi8' in encoding_lower:
                return 'koi8-u'
            elif 'ascii' in encoding_lower:
                return 'utf-8'  # ASCII is compatible with UTF-8

            return encoding

    except Exception as e:
        logger.error(f"Error detecting encoding for {file_path}: {e}")

    logger.debug(f"Defaulting to utf-8 encoding for: {file_path.name}")
    return 'utf-8'


# ============================================================================
# METADATA EXTRACTION
# ============================================================================

def extract_metadata(file_path: str | Path) -> Dict[str, Optional[str]]:
    """
    Extract metadata from filename.

    Extracts:
    - case_number: e.g., "890-ТМ-Д", "891-ТМ-Д", "995-ІБ-Д"
    - request_code: e.g., "В-2025-1898-062-kye", "З-2025-1615-011-fL5"
    - file_type: "request" or "answer" based on filename

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with extracted metadata

    Example path structure:
        nabu_data/890-ТМ-Д/В-2025-1898-062-kye/request.json
        nabu_data/890-ТМ-Д/В-2025-1898-062-kye/answer.xml
        nabu_data/995-ІБ-Д/З-2025-1615-011-fL5/answer.json
    """
    file_path = Path(file_path)

    metadata = {
        'case_number': None,
        'request_code': None,
        'file_type': None,
        'filename': file_path.name,
        'parent_dir': file_path.parent.name if file_path.parent else None,
    }

    try:
        # Extract file type from filename
        stem = file_path.stem.lower()
        if 'request' in stem:
            metadata['file_type'] = 'request'
        elif 'answer' in stem or 'response' in stem:
            metadata['file_type'] = 'answer'

        # Extract case number from parent directories
        # Pattern: 890-ТМ-Д, 891-ТМ-Д, 995-ІБ-Д
        parts = file_path.parts
        for part in reversed(parts):
            # Match case number pattern: NNN-XX-X (Cyrillic letters)
            if re.match(r'^\d{3}-[А-ЯІЇЄҐ]{1,3}-[А-ЯІЇЄҐ]$', part):
                metadata['case_number'] = part
                break

        # Extract request code from parent directory
        # Pattern: В-2025-1898-062-kye or З-2025-1615-011-fL5
        parent_name = file_path.parent.name
        if re.match(r'^[А-ЯІЇЄҐ]-\d{4}-\d{4}-\d{3}-[a-zA-Z0-9]+$', parent_name):
            metadata['request_code'] = parent_name

        logger.debug(f"Extracted metadata from {file_path.name}: {metadata}")

    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}")

    return metadata


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_binary_file(file_path: str | Path) -> bool:
    """
    Check if file is binary (not text-based).

    Args:
        file_path: Path to the file

    Returns:
        True if file is binary, False otherwise
    """
    file_path = Path(file_path)

    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)

        # Check for null bytes (common in binary files)
        if b'\x00' in chunk:
            return True

        # Try to decode as text
        try:
            chunk.decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True

    except Exception as e:
        logger.error(f"Error checking if file is binary: {file_path}: {e}")
        return False


def get_file_info(file_path: str | Path) -> Dict[str, any]:
    """
    Get comprehensive file information including format, encoding, and metadata.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with all file information
    """
    file_path = Path(file_path)

    info = {
        'path': str(file_path),
        'name': file_path.name,
        'size': file_path.stat().st_size if file_path.exists() else 0,
        'format': detect_format(file_path),
        'encoding': None,
        'is_binary': is_binary_file(file_path),
        'metadata': extract_metadata(file_path),
    }

    # Only detect encoding for text-based formats
    if info['format'] in [FileFormat.JSON, FileFormat.XML, FileFormat.HTML, FileFormat.CSV, FileFormat.TEXT]:
        info['encoding'] = detect_encoding(file_path)

    return info


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    import sys

    # Configure logger for testing
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"\n=== Analyzing: {test_file} ===\n")

        info = get_file_info(test_file)

        print(f"Format: {info['format'].value}")
        print(f"Encoding: {info['encoding']}")
        print(f"Is Binary: {info['is_binary']}")
        print(f"Size: {info['size']} bytes")
        print(f"\nMetadata:")
        for key, value in info['metadata'].items():
            print(f"  {key}: {value}")
    else:
        print("Usage: python format_detector.py <file_path>")
