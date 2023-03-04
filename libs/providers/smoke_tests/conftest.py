import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True, scope="session")
def load_env_from_dotenv():
    load_dotenv()
