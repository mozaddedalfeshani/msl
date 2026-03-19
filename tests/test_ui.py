from unittest.mock import patch
from msl.ui import ask_project_type
from msl.models import ProjectType
from msl.scanner import ProjectScan

def test_ask_project_type_default_match():
    # Mock ProjectScan with a confident detection
    scan = ProjectScan(
        name="test",
        languages=["TypeScript"],
        detected_type=ProjectType.NODEJS_SERVER,
        confidence=0.9,
        frameworks=["Express"]
    )
    
    # We want to verify that questionary.select is called with the correct default
    # The fix was ensuring 'default=ProjectType.NODEJS_SERVER' instead of a string
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = ProjectType.NODEJS_SERVER
        
        result = ask_project_type(scan)
        
        # Verify the call to select
        args, kwargs = mock_select.call_args
        assert kwargs["default"] == ProjectType.NODEJS_SERVER
        assert result == ProjectType.NODEJS_SERVER

def test_ask_project_type_no_confident_detection():
    scan = ProjectScan(
        name="test",
        languages=[],
        detected_type=ProjectType.NODEJS_SERVER,
        confidence=0.3, # Too low
        frameworks=[]
    )
    
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = ProjectType.PYTHON
        
        result = ask_project_type(scan)
        
        args, kwargs = mock_select.call_args
        assert kwargs["default"] is None
        assert result == ProjectType.PYTHON
