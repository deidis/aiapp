import os
import re
import json

from decouple import Config, AutoConfig
from openai import OpenAI
from IPython.display import display, Markdown

from find_env import env_path

_clients = {}

# Should be a relative path to the current working directory
# Must not end with '/'
results_path_prefix = './answers'


def ai(name=None):
    config = AutoConfig(env_path())
    api_key = config('OPENAI_API_KEY')
    if f"{api_key}_{name}" not in _clients:
        _clients[f"{api_key}_{name}"] = AIApp(name, api_key)
    return _clients[f"{api_key}_{name}"]


def remove_html_comments(content):
    pattern = r'<!--.*?-->\s*'
    clean_content = re.sub(pattern, '', content, flags=re.DOTALL)
    return clean_content


class AIApp:

    def __init__(self, name, api_key):
        self.api_key = api_key
        self.openai = OpenAI(api_key=api_key)

        self.name = name
        self.messages = {}
        self.vars = {}
        self.example_json_object = False
        self.json_schema_object = False
        self.response = ''
        self.compiled_system_prompt = ''

        for role in ['system', 'user', 'assistant', '']:
            file = f"{os.getcwd()}/{self.name + ('_' + role if role != '' else '')}.md"
            if os.path.exists(file):
                with open(file, "r") as f:
                    role = role if role != '' else 'system'
                    self.messages[role] = {"role": role, "content": f.read()}
        # Resolve path
        path = os.path.abspath(f"{os.getcwd()}/{results_path_prefix}")
        file = f"/{path}/{self.name + '_result_latest'}.md"
        if os.path.exists(file):
            with open(file, "r") as f:
                self.response = f.read()

    def __set_message(self, role, message_or_file_name):
        if message_or_file_name is None:
            return
        if len(message_or_file_name) < 50:
            file = message_or_file_name

            possible_files = [
                # More specific first
                f"{message_or_file_name}_{role}", f"{os.getcwd()}/{message_or_file_name}_{role}",
                f"{message_or_file_name}_{role}.md", f"{os.getcwd()}/{message_or_file_name}_{role}.md",
                # More general last
                message_or_file_name, f"{os.getcwd()}/{message_or_file_name}",
                f"{message_or_file_name}.md", f"{os.getcwd()}/{message_or_file_name}.md",
            ]

            for try_file in possible_files:
                if os.path.exists(try_file):
                    file = try_file
                    break

            if not os.path.exists(file):
                message = message_or_file_name
            else:
                with open(file, "r") as f:
                    message = f.read()
        else:
            message = message_or_file_name

        self.messages[role] = {"role": role, "content": message}

    def __get_message(self, role):
        if role in self.messages:
            return self.messages[role]["content"].strip()
        else:
            return ""

    def __prompt(self, model, user_message=None, temperature=0.5, top_p=0.5, frequency_penalty=0, presence_penalty=0):
        self.__set_message("user", user_message)

        chat_messages = list(self.messages.values()).copy()
        for m in chat_messages:
            m['content'] = remove_html_comments(m['content']).strip()

        self.__include_vars(chat_messages, "system")
        if self.example_json_object:
            self.__include_json_example(chat_messages, "system")
        if self.json_schema_object:
            self.__include_json_schema(chat_messages, "system")

        params = {
            "model": model,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "messages": chat_messages,
            "temperature": temperature,
            "top_p": top_p,
        }

        # Only for turbo models, force to respond as json
        if (self.example_json_object or self.json_schema_object) and model.endswith("preview"):
            params["response_format"] = {"type": "json_object"}

        if 'system' in self.messages:
            self.compiled_system_prompt = self.messages['system']['content']

        for item in chat_messages:
            if item['role'] == 'system':
                self.compiled_system_prompt = item['content']

        completion = self.openai.chat.completions.create(**params)
        self.response = completion.choices[0].message.content

        basename = os.path.basename(f"{self.name}".strip('.md'))
        os.makedirs(f"{os.getcwd()}/{results_path_prefix}", exist_ok=True)
        with open(f"{os.getcwd()}/{results_path_prefix}/{basename}_result_latest.md", "w") as f:
            f.write(self.response)

        return self

    def __include_vars(self, messages, role, prepend=True):
        if len(self.vars) > 0:
            if role in self.messages:
                for m in messages:
                    if m['role'] == role:
                        appendix = (
                            """
======================================================================
START OF VARIABLE DECLARATION SECTION
Below are the texts with headlines. Use the headline as a variable name and the text underneath it as the value.
======================================================================
"""
                        )
                        for k, v in self.vars.items():
                            appendix += f"# {k}\n{v}\n"
                        appendix += (
                            """
======================================================================
END OF VARIABLE DECLARATION SECTION
======================================================================
"""
                        )
                        if prepend:
                            m['content'] = appendix + "\n\n" + m['content']
                        else:
                            m['content'] += "\n\n" + appendix

    def __include_json_example(self, messages, role="system", prepend=False):
        appendix = (
            """
======================================================================
START OF FORMATTING RULES SECTION
Below is the example json format that must be used for the assistant response.
======================================================================
"""
        )
        appendix += f"{json.dumps(self.example_json_object)}"
        appendix += (
            """
======================================================================
END OF FORMATTING RULES SECTION
======================================================================
"""
        )

        if len(self.example_json_object):
            if role in self.messages:
                for m in messages:
                    if m['role'] == role:
                        if prepend:
                            m['content'] = appendix + "\n\n" + m['content']
                        else:
                            m['content'] += "\n\n" + appendix
            else:
                messages.append({"role": role, "content": appendix})

    def __include_json_schema(self, messages, role="system", prepend=False):
        appendix = (
            """
======================================================================
START OF FORMATTING RULES SECTION
Below is the json schema that must be used for formatting assistant response.
======================================================================
"""
        )
        appendix += f"{json.dumps(self.json_schema_object)}"
        appendix += (
            """
======================================================================
END OF FORMATTING RULES SECTION
======================================================================
"""
        )

        if len(self.json_schema_object):
            if role in self.messages:
                for m in messages:
                    if m['role'] == role:
                        if prepend:
                            m['content'] = appendix + "\n\n" + m['content']
                        else:
                            m['content'] += "\n\n" + appendix
            else:
                messages.append({"role": role, "content": appendix})

    def user(self, message=None):
        if message is not None:
            self.__set_message("user", message)
            return self
        else:
            return self.__get_message("user")

    def assistant(self, message=None):
        if message is not None:
            self.__set_message("assistant", message)
            return self
        else:
            return self.__get_message("assistant")

    def system(self, message=None):
        if message is not None:
            self.__set_message("system", message)
            return self
        else:
            return self.__get_message("system")

    def system_compiled(self):
        return self.compiled_system_prompt

    def var(self, name, value):
        self.vars[name] = value
        return self

    def example_json(self, value):
        self.example_json_object = value
        self.json_schema_object = False
        return self

    def json_schema(self, value):
        self.json_schema_object = value
        self.example_json_object = False
        return self

    # Updated GPT-3.5 Turbo, gpt-3.5-turbo-1106. 16,385 tokens
    def gpt35turbo(self, user_message=None, temperature=0.5, top_p=0.5, frequency_penalty=0, presence_penalty=0):
        return self.__prompt(
            "gpt-3.5-turbo-1106",
            user_message,
            temperature,
            top_p,
            frequency_penalty,
            presence_penalty
        )

    def gpt35(self, user_message=None, temperature=0.5, top_p=0.5, frequency_penalty=0, presence_penalty=0):
        return self.__prompt(
            "gpt-3.5",
            user_message,
            temperature,
            top_p,
            frequency_penalty,
            presence_penalty
        )

    # Latest and greatest GPT-4 Turbo, gpt-4-1106-preview. 128,000 tokens
    def gpt4turbo(self, user_message=None, temperature=0.5, top_p=0.5, frequency_penalty=0, presence_penalty=0):
        return self.__prompt(
            "gpt-4-1106-preview",
            user_message,
            temperature,
            top_p,
            frequency_penalty,
            presence_penalty
        )

    # GPT-4, gpt-4. 8,000 tokens
    def gpt4(self, user_message=None, temperature=0.5, top_p=0.5, frequency_penalty=0, presence_penalty=0):
        return self.__prompt(
            "gpt-4",
            user_message,
            temperature,
            top_p,
            frequency_penalty,
            presence_penalty
        )

    def clear(self):
        self.messages.clear()
        return self

    def result(self):
        return self.response

    def result_show(self):
        return display(Markdown(self.response))

    def result_print(self):
        print(self.response)
