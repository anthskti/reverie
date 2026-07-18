import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def setup_vertex_credentials():
    """
    Reads the raw Service Account JSON from Render's environment variables,
    writes it to a secure temporary file, and points the Google SDK to it.
    """
    json_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    
    if json_creds:
        # Create a secure temporary file
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, 'w') as f:
            f.write(json_creds)
        
        # Tell the Google Auth library where to find the JSON file
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
        logger.info("Successfully bootstrapped Vertex AI credentials from environment.")
    else:
        logger.warning("GOOGLE_CREDENTIALS_JSON not found. Assuming local ADC is configured.")
