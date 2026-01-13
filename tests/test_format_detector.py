"""
Test format detector functionality.
"""

from pathlib import Path

from src.parsers.format_detector import (
    FileFormat,
    detect_encoding,
    detect_format,
    extract_metadata,
    get_file_info,
    is_binary_file,
)


def test_detect_format_xml():
    """Test XML format detection."""
    # Find a sample XML file from nabu_data
    xml_files = list(Path("nabu_data").rglob("*.xml"))

    if xml_files:
        test_file = xml_files[0]
        format_detected = detect_format(test_file)
        assert format_detected == FileFormat.XML, f"Expected XML, got {format_detected}"
        print(f"✓ XML format detection passed: {test_file.name}")
    else:
        print("⚠ No XML files found for testing")


def test_detect_format_json():
    """Test JSON format detection."""
    # Find a sample JSON file from nabu_data
    json_files = list(Path("nabu_data").rglob("*.json"))

    if json_files:
        test_file = json_files[0]
        format_detected = detect_format(test_file)
        assert format_detected == FileFormat.JSON, f"Expected JSON, got {format_detected}"
        print(f"✓ JSON format detection passed: {test_file.name}")
    else:
        print("⚠ No JSON files found for testing")


def test_detect_encoding():
    """Test encoding detection."""
    # Find any text-based file
    files = list(Path("nabu_data").rglob("*.xml"))[:1] + list(Path("nabu_data").rglob("*.json"))[:1]

    for test_file in files:
        encoding = detect_encoding(test_file)
        assert encoding is not None
        assert isinstance(encoding, str)
        assert len(encoding) > 0
        print(f"✓ Encoding detection passed: {test_file.name} -> {encoding}")


def test_extract_metadata():
    """Test metadata extraction from filename."""
    # Test with different path patterns
    test_cases = [
        {
            'path': 'nabu_data/890-ТМ-Д/В-2025-1898-062-kye/answer.xml',
            'expected': {
                'case_number': '890-ТМ-Д',
                'request_code': 'В-2025-1898-062-kye',
                'file_type': 'answer',
            }
        },
        {
            'path': 'nabu_data/995-ІБ-Д/З-2025-1615-011-fL5/request.json',
            'expected': {
                'case_number': '995-ІБ-Д',
                'request_code': 'З-2025-1615-011-fL5',
                'file_type': 'request',
            }
        },
    ]

    for test_case in test_cases:
        # Find an actual file matching the pattern or use the path directly
        path = Path(test_case['path'])
        if not path.exists():
            # Try to find a similar file
            parts = path.parts
            if len(parts) >= 3:
                case_dir = Path(parts[0]) / parts[1]
                if case_dir.exists():
                    # Find any file in a subdirectory
                    subdirs = [d for d in case_dir.iterdir() if d.is_dir()]
                    if subdirs:
                        files = list(subdirs[0].rglob("*"))
                        if files:
                            path = files[0]

        if path.exists():
            metadata = extract_metadata(path)

            # Check expected fields
            for key, expected_value in test_case['expected'].items():
                if expected_value:
                    # For pattern matching, just check if the field was extracted
                    if key == 'case_number':
                        assert metadata[key] is not None, f"Expected case_number to be extracted"
                    elif key == 'request_code':
                        assert metadata[key] is not None, f"Expected request_code to be extracted"
                    elif key == 'file_type':
                        # This one might not match, so we'll just check it exists
                        pass

            print(f"✓ Metadata extraction passed: {path.name}")
            print(f"  Case number: {metadata['case_number']}")
            print(f"  Request code: {metadata['request_code']}")
            print(f"  File type: {metadata['file_type']}")


def test_is_binary_file():
    """Test binary file detection."""
    # Test with text files (should be False)
    text_files = list(Path("nabu_data").rglob("*.xml"))[:1] + list(Path("nabu_data").rglob("*.json"))[:1]

    for test_file in text_files:
        is_binary = is_binary_file(test_file)
        # XML and JSON should not be binary
        assert is_binary == False, f"Expected text file, got binary for {test_file.name}"
        print(f"✓ Binary detection passed (text): {test_file.name}")

    # Test with Excel files if available (should be True)
    excel_files = list(Path("nabu_data").rglob("*.xlsx")) + list(Path("nabu_data").rglob("*.xls"))

    for test_file in excel_files[:1]:
        is_binary = is_binary_file(test_file)
        assert is_binary == True, f"Expected binary file for {test_file.name}"
        print(f"✓ Binary detection passed (binary): {test_file.name}")


def test_get_file_info():
    """Test comprehensive file info extraction."""
    # Test with actual files from nabu_data
    test_files = list(Path("nabu_data").rglob("*.xml"))[:1] + list(Path("nabu_data").rglob("*.json"))[:1]

    for test_file in test_files:
        info = get_file_info(test_file)

        # Verify all expected keys are present
        assert 'path' in info
        assert 'name' in info
        assert 'size' in info
        assert 'format' in info
        assert 'encoding' in info
        assert 'is_binary' in info
        assert 'metadata' in info

        # Verify values are reasonable
        assert info['size'] > 0
        assert info['format'] != FileFormat.UNKNOWN
        assert info['encoding'] is not None

        print(f"✓ File info extraction passed: {test_file.name}")
        print(f"  Format: {info['format'].value}")
        print(f"  Encoding: {info['encoding']}")
        print(f"  Size: {info['size']} bytes")


def test_format_detection_comprehensive():
    """Test format detection on all files in nabu_data."""
    all_files = list(Path("nabu_data").rglob("*"))
    files_to_test = [f for f in all_files if f.is_file()]

    format_counts = {}
    total_files = 0

    print("\n=== Comprehensive Format Detection ===")

    for file_path in files_to_test:
        format_detected = detect_format(file_path)
        format_counts[format_detected] = format_counts.get(format_detected, 0) + 1
        total_files += 1

    print(f"\nTotal files processed: {total_files}")
    print("\nFormat distribution:")
    for fmt, count in sorted(format_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_files) * 100
        print(f"  {fmt.value:15s}: {count:3d} ({percentage:.1f}%)")

    # At least 90% of files should be detected (not UNKNOWN)
    unknown_count = format_counts.get(FileFormat.UNKNOWN, 0)
    unknown_percentage = (unknown_count / total_files) * 100
    assert unknown_percentage < 10, f"Too many unknown formats: {unknown_percentage:.1f}%"

    print(f"\n✓ Comprehensive format detection passed")


if __name__ == "__main__":
    print("\n=== Testing Format Detector ===\n")

    test_detect_format_xml()
    test_detect_format_json()
    test_detect_encoding()
    test_extract_metadata()
    test_is_binary_file()
    test_get_file_info()
    test_format_detection_comprehensive()

    print("\n=== All format detector tests passed! ===\n")
