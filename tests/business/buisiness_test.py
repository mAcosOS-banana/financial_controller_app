import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from server.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token
