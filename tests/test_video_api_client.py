"""
Light test file for video_api_client functions.
Run with: pytest tests/test_video_api_client.py -v
"""

from unittest.mock import MagicMock, patch

import pytest

from app.api.video_api_client import call_video_task_status_api, create_video_record


class TestVideoTaskStatusAPI:
    """Test cases for call_video_task_status_api function"""

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.put")
    def test_call_video_task_status_api_success(self, mock_put, mock_get_token):
        """Test successful video task status API call"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_put.return_value = mock_response

        # Execute
        result = call_video_task_status_api(
            task_id="task-123",
            status="active",
            render_status="PROCESSING",
            progress=50.0,
            message="Processing video"
        )

        # Assert
        assert result is True
        mock_get_token.assert_called_once()
        mock_put.assert_called_once()

        # Verify headers include Bearer token
        call_kwargs = mock_put.call_args[1]
        assert call_kwargs["headers"]["Authorization"] == "Bearer test-m2m-token"

    @patch("app.api.video_api_client.get_m2m_token")
    def test_call_video_task_status_api_no_token(self, mock_get_token):
        """Test API call when M2M token retrieval fails"""
        # Setup
        mock_get_token.return_value = None

        # Execute
        result = call_video_task_status_api(task_id="task-123")

        # Assert
        assert result is False
        mock_get_token.assert_called_once()

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.put")
    def test_call_video_task_status_api_failure(self, mock_put, mock_get_token):
        """Test API call when server returns success=False"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False, "error": "Invalid task ID"}
        mock_put.return_value = mock_response

        # Execute
        result = call_video_task_status_api(task_id="invalid-task")

        # Assert
        assert result is False

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.put")
    def test_call_video_task_status_api_request_error(self, mock_put, mock_get_token):
        """Test API call when network request fails"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_put.side_effect = Exception("Connection timeout")

        # Execute
        result = call_video_task_status_api(task_id="task-123")

        # Assert
        assert result is False

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.put")
    def test_call_video_task_status_api_with_extra_metadata(self, mock_put, mock_get_token):
        """Test API call with extra metadata"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_put.return_value = mock_response

        extra_data = {"custom_field": "value", "timestamp": "2025-01-01"}

        # Execute
        result = call_video_task_status_api(
            task_id="task-123",
            render_status="COMPLETED",
            progress=100.0,
            extra=extra_data
        )

        # Assert
        assert result is True
        call_kwargs = mock_put.call_args[1]
        assert call_kwargs["json"]["extra"] == extra_data


class TestCreateVideoRecord:
    """Test cases for create_video_record function"""

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.post")
    def test_create_video_record_success(self, mock_post, mock_get_token):
        """Test successful video record creation"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "video_id": "vid-123"}
        mock_post.return_value = mock_response

        # Execute
        result = create_video_record(
            task_id="task-123",
            oss_url="https://example.com/video.mp4",
            video_name="Test Video",
            resolution="1920x1080",
            framerate="30fps",
            duration=120.5,
            file_size=1024000,
            thumbnail_url="https://example.com/thumb.jpg"
        )

        # Assert
        assert result is True
        mock_get_token.assert_called_once()
        mock_post.assert_called_once()

        # Verify headers include Bearer token
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["headers"]["Authorization"] == "Bearer test-m2m-token"

        # Verify payload
        payload = call_kwargs["json"]
        assert payload["task_id"] == "task-123"
        assert payload["oss_url"] == "https://example.com/video.mp4"
        assert payload["video_name"] == "Test Video"

    @patch("app.api.video_api_client.get_m2m_token")
    def test_create_video_record_no_token(self, mock_get_token):
        """Test video record creation when M2M token retrieval fails"""
        # Setup
        mock_get_token.return_value = None

        # Execute
        result = create_video_record(
            task_id="task-123",
            oss_url="https://example.com/video.mp4"
        )

        # Assert
        assert result is False

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.post")
    def test_create_video_record_failure(self, mock_post, mock_get_token):
        """Test video record creation when server returns success=False"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False, "error": "Invalid OSS URL"}
        mock_post.return_value = mock_response

        # Execute
        result = create_video_record(
            task_id="task-123",
            oss_url="invalid-url"
        )

        # Assert
        assert result is False

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.post")
    def test_create_video_record_request_error(self, mock_post, mock_get_token):
        """Test video record creation when network request fails"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_post.side_effect = Exception("Connection refused")

        # Execute
        result = create_video_record(
            task_id="task-123",
            oss_url="https://example.com/video.mp4"
        )

        # Assert
        assert result is False

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.post")
    def test_create_video_record_minimal_fields(self, mock_post, mock_get_token):
        """Test video record creation with only required fields"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # Execute
        result = create_video_record(
            task_id="task-123",
            oss_url="https://example.com/video.mp4"
        )

        # Assert
        assert result is True
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        assert "task_id" in payload
        assert "oss_url" in payload

    @patch("app.api.video_api_client.get_m2m_token")
    @patch("app.api.video_api_client.requests.post")
    def test_create_video_record_with_extra_metadata(self, mock_post, mock_get_token):
        """Test video record creation with extra metadata"""
        # Setup
        mock_get_token.return_value = "test-m2m-token"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        extra_data = {"source": "sdk", "quality": "high"}

        # Execute
        result = create_video_record(
            task_id="task-123",
            oss_url="https://example.com/video.mp4",
            extra=extra_data
        )

        # Assert
        assert result is True
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["extra"] == extra_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
