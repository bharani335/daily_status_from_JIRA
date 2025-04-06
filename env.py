
def load_env():
    """
    Load environment variables from a .env file.
    """
    from dotenv import load_dotenv
    import os

    # Load environment variables from .env file
    load_dotenv()

    # Get the environment variables
    env_vars = {
        'JIRA_EMAIL': os.getenv('JIRA_EMAIL'),
        'JIRA_API_TOKEN': os.getenv('JIRA_API_TOKEN'),
        'JIRA_SERVER': os.getenv('JIRA_SERVER'),
        'XL_CREDS_FILE_PATH': os.getenv('XL_CREDS_FILE_PATH')
    }

    return env_vars