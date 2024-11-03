import pytest
from unittest.mock import AsyncMock, MagicMock
from src.functionality.create_event_type import create_event_type

@pytest.mark.asyncio
async def test_create_event_type():
    # Mock context and client
    mock_ctx = MagicMock()
    mock_ctx.author.id = "test_user_id"  # mock user ID
    mock_ctx.author.create_dm = AsyncMock()  # Use AsyncMock for create_dm
    mock_channel = AsyncMock()  # mock DM channel as async
    mock_ctx.author.create_dm.return_value = mock_channel
    
    mock_client = MagicMock()

    # Mock the channel's send method to check what messages are sent
    mock_channel.send = AsyncMock()

    # Mock `wait_for` to return a response to the time range prompt
    mock_client.wait_for = AsyncMock(return_value=MagicMock(content="12:00 pm 2:00 pm"))
    
    # Run the function with a sample event message
    await create_event_type(mock_ctx, mock_client, "Meeting")
        
    # Verify the prompt for the time range was sent
    mock_channel.send.assert_any_call(
        "Now give me your perefered time range this event type.\n"
        + "Make sure you include 'am' or 'pm' so I know what is the range of your event, \n"
        + "Here is the format you should follow (Start is first, end is second):\n"
        + "hh:mm am/pm hh:mm am/pm"
    )
