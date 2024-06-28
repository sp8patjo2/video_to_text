import os
import re
import sys
import autogen
import time
import logging

class AIAutogenUtils:
    def __init__(self):
        """Initializes the AI utilities class with basic configurations."""
        self._api_key = None          # Holds the key for this session
        self._api_organization = None # Also requires an "organization key" to send with OpenAI/Autogen requests
        
        self.init_logging()
        self._user_proxy = None       # Keep it simple for now, might not belong in this class
        self._assistant = None



    def init_logging(self) -> None:
        """Sets up logging configuration to output to stdout."""
        logging.basicConfig(stream=sys.stdout,
                            level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")



    def get_run_config(self, run_desc: int = 1) -> str:
        """Returns a description of this run, to be added to run description tables."""
        return f"AI:{self._config_list[0]['model']}_run:{run_desc}"



    def set_config(self, model: str = 'gpt-4-0125-preview', cache_seed: int = 42,
                   api_key_env: str = 'OPENAI_API_KEY', api_org_env: str = 'OPENAI_ORGID') -> None:
        """Sets up model and configuration."""
        if self._api_key is None:
            self._api_key = self.get_api_key(api_key_env)

        if self._api_organization is None:
            self._api_organization = self.get_api_org(api_org_env)
        
        self._config_list = [{
            'model': model,
            'api_key': self._api_key,
            'organization': self._api_organization
        }]

        self._llm_config = {
            "timeout": 180,
            "cache_seed": cache_seed,
            "config_list": self._config_list,
            "temperature": 1.0
        }



    def get_config_list(self) -> list:
        """Returns the configuration list."""
        if self._config_list is None:
            raise ValueError("_config_list is not initialized")
        return self._config_list



    def get_active_api_key(self) -> str:
        """Retrieves the active API key from the configuration."""
        tmp_config_list = self.get_config_list()
        if tmp_config_list:
            return tmp_config_list[0]["api_key"]
        else:
            raise ValueError("Configuration list is empty")


    def get_active_organization_key(self) -> str:
        """Retrieves the active organization key from the configuration."""
        tmp_config_list = self.get_config_list()
        if tmp_config_list:
            return tmp_config_list[0]["organization"]
        else:
            raise ValueError("Configuration list is empty")



    def get_llm_config(self) -> dict:
        """Retrieves the LLM configuration."""
        if self._llm_config is None:
            raise ValueError("llm_config is not initialized")
        return self._llm_config




    def set_agents(self, user_proxy, assistant, overwrite: bool = False) -> None:
        """Sets user_proxy and assistant agents, ensuring proper instances and handling overwrites."""
        if user_proxy is None or assistant is None:
            raise ValueError("Neither user_proxy nor assistant can be None.")
        
        if not isinstance(assistant, autogen.AssistantAgent):
            raise TypeError("assistant must be an instance of autogen.AssistantAgent.")
        
        if not isinstance(user_proxy, autogen.UserProxyAgent):
            raise TypeError("user_proxy must be an instance of autogen.UserProxyAgent.")
        
        if not overwrite and self._user_proxy is not None:
            raise Exception("Attempting to overwrite user_proxy without permission. Set overwrite=True to allow.")
        
        if not overwrite and self._assistant is not None:
            raise Exception("Attempting to overwrite assistant without permission. Set overwrite=True to allow.")
        
        self._user_proxy = user_proxy
        self._assistant = assistant




    def query_AI(self, task: str) -> str:
        """Queries the AI to perform a task and returns the response."""
        if not self._user_proxy:
            raise AttributeError("User proxy is not initialized")
        
        self._user_proxy.initiate_chat(self._assistant, message=task)
        last_msg = self._user_proxy.last_message(None)
        return last_msg



    def get_last_assistant_message(self) -> None:
        """Retrieves the last message from the assistant."""
        self._assistant.last_message(None)




    def get_api_org(self, env_var_name: str = None) -> str:
        """Retrieves the organization API key from an environment variable."""
        org_api_key = os.environ.get(env_var_name)
        if org_api_key is None:
            raise ValueError(f"The environment variable '{env_var_name}' is not set.")

        pattern = r'^org-[a-zA-Z0-9]{24}$'
        if not re.match(pattern, org_api_key):
            raise ValueError(f"The key in '{env_var_name}' - is {org_api_key} is incorrect. It should start with 'org-' followed by 24 characters.")

        return org_api_key




    def get_api_key(self, env_var_name: str = None) -> str:
        """Retrieves the API key from an environment variable, ensuring its correct format."""
        api_key = os.environ.get(env_var_name)
        if api_key is None:
            raise ValueError(f"The environment variable '{env_var_name}' is not set.")

        pattern = r'^sk-[a-zA-Z0-9]{48}$'
        if not re.match(pattern, api_key):
            raise ValueError(f"The environment variable '{env_var_name}' is invalid. It should start with 'sk-' followed by 48 alphanumeric characters.")

        return api_key
