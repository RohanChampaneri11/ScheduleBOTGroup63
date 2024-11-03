import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys
from pathlib import Path

# Adjust the import path for your actual module structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.functionality.export_file import export_file

@pytest.mark.asyncio
async def test_export_file():
    # Mock context and DM channel
    mock_ctx = MagicMock()
    mock_ctx.author.id = 12345
    mock_dm_channel = AsyncMock()
    mock_ctx.author.create_dm = AsyncMock(return_value=mock_dm_channel)

    # File path for testing
    user_id = str(mock_ctx.author.id)
    test_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv")

    # Mock the necessary functions and Discord file behavior
    with patch("src.functionality.export_file.os.path.exists", return_value=True), \
         patch("src.functionality.export_file.create_event_directory") as mock_create_dir, \
         patch("src.functionality.export_file.create_event_file") as mock_create_file, \
         patch("src.functionality.export_file.load_key", return_value=b"fake_key") as mock_load_key, \
         patch("src.functionality.export_file.decrypt_file") as mock_decrypt_file, \
         patch("src.functionality.export_file.encrypt_file") as mock_encrypt_file, \
         patch("src.functionality.export_file.discord.File") as mock_discord_file:
        
        # Mock return value for discord.File to match expected behavior
        mock_discord_file.return_value = MagicMock()

        # Run the export_file function
        await export_file(mock_ctx)
        
        # Basic assertions to confirm functions were called
        mock_create_dir.assert_not_called()  # Since the file is mocked as existing
        mock_create_file.assert_not_called()  # Same reason as above
        mock_load_key.assert_called_once_with(user_id)
        mock_decrypt_file.assert_called_once_with(b"fake_key", test_file_path)
        mock_encrypt_file.assert_called_once_with(b"fake_key", test_file_path)
        mock_discord_file.assert_called_once_with(test_file_path)
        
        # Check that send was called with the correct file mock
        mock_dm_channel.send.assert_called_once_with(file=mock_discord_file.return_value)
