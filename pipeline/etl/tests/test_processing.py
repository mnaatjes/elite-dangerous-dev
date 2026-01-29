import pytest
import os
import requests
from pipeline.etl import process_data

# Define download data function
def test_download_data_uses_correct_url(mocker):
        """
        This is a test to ensure that `download_data` function attempts to download from URL specific to EDSM_DUMP_URL const
        """
        # Spy on requests.get
        mock_get = mocker.patch('requests.get')
        
        # Set os.path.exists to always return false
        mocker.patch('os.path.exists', return_value=False)

        # Call function we are testing
        process_data.download_data()
        
        # Assert requests.get called
        mock_get.assert_called_once_with(process_data.EDSM_DUMP_URL, stream=True)