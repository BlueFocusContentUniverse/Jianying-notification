"""
Manual test script for video_api_client functions.
This script tests the actual functions with real API calls in local environment.

Usage:
    python tests/manual_test_video_api_client.py
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.video_api_client import call_video_task_status_api, create_video_record
from app.auth import get_m2m_token, get_cached_token, clear_token_cache

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_m2m_token_retrieval():
    """Test M2M token retrieval and caching"""
    print("\n" + "=" * 60)
    print("TEST 1: M2M Token Retrieval")
    print("=" * 60)

    try:
        # Clear cache first
        clear_token_cache()
        print("✓ Cache cleared")

        # Get token (should make API call)
        print("\nAttempting to get M2M token...")
        token1 = get_m2m_token()

        if token1:
            print(f"✓ Token obtained: {token1[:20]}...")
            print(f"  Token length: {len(token1)}")

            # Get token again (should use cache)
            print("\nAttempting to get M2M token again (should use cache)...")
            token2 = get_m2m_token()

            if token2 == token1:
                print("✓ Cached token returned (same as first call)")
            else:
                print("✗ Different token returned")

            # Check cached token directly
            cached = get_cached_token()
            if cached:
                print(f"✓ Cached token available: {cached[:20]}...")
            else:
                print("✗ No cached token")

        else:
            print("✗ Failed to obtain M2M token")
            print("  Check Cognito configuration in .env file:")
            print("  - COGNITO_DOMAIN")
            print("  - COGNITO_CLIENT_ID")
            print("  - COGNITO_CLIENT_SECRET")
            return False

    except Exception as e:
        print(f"✗ Error during token retrieval: {e}")
        return False

    return True


def test_call_video_task_status_api():
    """Test calling video task status API"""
    print("\n" + "=" * 60)
    print("TEST 2: Call Video Task Status API")
    print("=" * 60)

    try:
        # Test with minimal parameters
        print("\nCalling video task status API...")
        result = call_video_task_status_api(
            task_id="test-task-001",
            render_status="PROCESSING",
            progress=25.0,
            message="Test update from local script"
        )

        if result:
            print("✓ API call succeeded")
        else:
            print("✗ API call failed")
            print("  Check that VIDEO_API_BASE_URL is correct and API is accessible")

        return result

    except Exception as e:
        print(f"✗ Error during API call: {e}")
        return False


def test_create_video_record():
    """Test creating video record via API"""
    print("\n" + "=" * 60)
    print("TEST 3: Create Video Record")
    print("=" * 60)

    try:
        print("\nCreating video record via API...")
        result = create_video_record(
            task_id="test-task-002",
            oss_url="https://example.com/test-video.mp4",
            video_name="Local Test Video",
            resolution="1920x1080",
            framerate="30fps",
            duration=120.0,
            file_size=5242880,
            thumbnail_url="https://example.com/thumb.jpg"
        )

        if result:
            print("✓ Video record created successfully")
        else:
            print("✗ Failed to create video record")
            print("  Check that VIDEO_API_BASE_URL is correct and API is accessible")

        return result

    except Exception as e:
        print(f"✗ Error during video creation: {e}")
        return False


def test_call_video_task_status_api_with_extra():
    """Test calling video task status API with extra metadata"""
    print("\n" + "=" * 60)
    print("TEST 4: Video Task Status API with Extra Metadata")
    print("=" * 60)

    try:
        print("\nCalling video task status API with extra metadata...")
        extra_data = {
            "source": "local-test",
            "test_timestamp": "2025-01-01T12:00:00Z",
            "custom_field": "custom_value"
        }

        result = call_video_task_status_api(
            task_id="test-task-003",
            status="active",
            render_status="COMPLETED",
            progress=100.0,
            message="Test completed",
            video_id="vid-123",
            extra=extra_data
        )

        if result:
            print("✓ API call with extra metadata succeeded")
        else:
            print("✗ API call failed")

        return result

    except Exception as e:
        print(f"✗ Error during API call: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    tests = [
        "M2M Token Retrieval",
        "Video Task Status API",
        "Create Video Record",
        "Video Task Status API with Extra"
    ]

    for i, (test_name, passed) in enumerate(zip(tests, results), 1):
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{i}. {test_name}: {status}")

    total = len(results)
    passed = sum(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    return all(results)


def main():
    """Run all manual tests"""
    print("\n" + "=" * 60)
    print("VIDEO API CLIENT - MANUAL TEST SCRIPT")
    print("=" * 60)
    print("\nThis script tests real API calls. Make sure:")
    print("1. You have configured .env file with required settings")
    print("2. Your Cognito credentials are valid")
    print("3. Your Video API server is accessible")
    print("4. Network connectivity is available")

    results = []

    # Run tests
    results.append(test_m2m_token_retrieval())
    results.append(test_call_video_task_status_api())
    results.append(test_create_video_record())
    results.append(test_call_video_task_status_api_with_extra())

    # Print summary
    success = print_summary(results)

    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Check logs above for details.")
    print("=" * 60 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
