"""
Quick test for error classifier integration
"""
from error_classifier import classify_user_error, format_error_response

def test_error_patterns():
    """Test common error patterns"""
    test_cases = [
        ("HTTP Error 403: Forbidden", "Access forbidden"),
        ("private video", "This video is private or restricted"),
        ("Video unavailable", "This video is no longer available"),
        ("timed out", "Request timed out"),
        ("HTTP Error 429", "Rate limit reached"),
        ("No video found at this URL", "We couldn't find a video at this URL"),
        ("Audio too large (26.5MB, max 25MB)", "File too large"),
        ("region locked", "This video is region-locked"),
        ("age-restricted", "This video is age-restricted"),
    ]

    print("Testing error classifier...")
    for raw_error, expected_message in test_cases:
        result = classify_user_error(raw_error)
        assert expected_message in result["message"], f"Failed for: {raw_error}"
        assert "action" in result
        assert "help_url" in result
        print(f"✓ {raw_error[:40]:40} -> {result['message']}")

    print("\nTesting format_error_response...")
    response = format_error_response("HTTP Error 429", "download")
    assert response["status"] == "error"
    assert "retry_after" in response
    print(f"✓ Structured response includes: {', '.join(response.keys())}")

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_error_patterns()
