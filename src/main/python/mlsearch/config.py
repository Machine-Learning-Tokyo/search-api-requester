import os

class Config(object):
    """Class for API Request configuration."""

    # Paper with code configuration
    PWC_USER_NAME = os.environ.get('PWC_USER_NAME') or ''
    PWC_PASSWORD = os.environ.get('PWC_PASSWORD') or ''
    PWC_URL = os.environ.get('PWC_URL') or "https://paperswithcode.com/api/v0/search/?q="

    # Github configuration
    GITHUB_ACC_TOKEN = os.environ.get('GITHUB_ACC_TOKEN') or None
    GITHUB_URL = os.environ.get('GITHUB_URL') or "in:readme+in:description"

    # AIP Source
    VALID_API_SOURCE = ['paperwithcode', 'github', 'coursera', 'youtube']

    # Youtube configuration
    YOUTUBE_SERVICE_NAME = os.environ.get('YOUTUBE_SERVICE_NAME') or "youtube"
    YOUTUBE_API_VERSION = os.environ.get('YOUTUBE_API_VERSION') or "v3"
    YOUTUBE_DEVELOPER_KEY = os.environ.get('YOUTUBE_DEVELOPER_KEY') or None
    YOUTUBE_ORDER = os.environ.get('YOUTUBE_ORDER') or "relevance"
    YOUTUBE_SAFESEARCH = os.environ.get('YOUTUBE_SAFESEARCH') or "strict"
    YOUTUBE_PART = os.environ.get('YOUTUBE_PART') or "snippet"