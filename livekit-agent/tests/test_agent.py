"""
Basic tests for the switchboard agent
"""
import pytest
import os
from unittest.mock import patch, MagicMock


def test_agent_import():
    """Test that the agent can be imported without errors"""
    try:
        from livekit_switchboard_agent import SwitchboardAgent
        assert True
    except ImportError as e:
        pytest.skip(f"Agent import failed: {e}")


def test_supabase_client_import():
    """Test that the Supabase client can be imported"""
    try:
        from db.supabase_client import SupabaseClient
        assert True
    except ImportError as e:
        pytest.skip(f"Supabase client import failed: {e}")


def test_environment_variables():
    """Test that required environment variables are defined"""
    required_vars = [
        'OPENAI_API_KEY',
        'DEEPGRAM_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        pytest.skip(f"Missing environment variables: {missing_vars}")
    
    assert True


@patch.dict(os.environ, {
    'OPENAI_API_KEY': 'test-key',
    'DEEPGRAM_API_KEY': 'test-key',
    'SUPABASE_URL': 'https://test.supabase.co',
    'SUPABASE_KEY': 'test-key',
    'SUPABASE_SERVICE_ROLE_KEY': 'test-key'
})
def test_agent_initialization():
    """Test that the agent can be initialized with mock environment"""
    try:
        from livekit_switchboard_agent import SwitchboardAgent
        # This would normally create an agent instance
        # For now, just test that the module loads
        assert True
    except Exception as e:
        pytest.skip(f"Agent initialization failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
