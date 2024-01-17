# AI App

It's made to be handy.
 
## Basics

1. Make sure to have `.env` file in the root directory of your project.
```
# .env
OPENAI_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

2. Use `xyz.md` files (simple text files with md extension) to write your prompts.
```markdown
<!--
    You can use HTML style comments to describe your prompts,
    these will be stripped before passing to the API.
-->
Say "hi" in Lithuanian
```

3. Get ready to rock:
```python
ai("polyglot").gpt4("xyz").result_print()
```

## API

The entry point is ```ai()``` function. It returns an instance of ```AIApp``` class. Most of the public methods you'll call on that instance will return `self`, so you can chain them.

### ai(name)

The parameter `name` serves two purposes:

1. It's the name of the so called "AI app" which we can later get by the same name
2. If the name is something like "blabla_<system|user>" then it will try to find the `blabla_system.md` and `blabla_user.md` and use the contents of the file as the respective prompt message (system or user message)
3. Just in case the name coincides with a file name (if a file found) it will be used as a system message

### Examples

```python
ai("myapp").gpt4("My awesome prompt").result_print()

# and somewhere later we can reference to the same AI app
ai("myapp").result_print()
```

```python
myapp = ai("system.md").gpt4("My awesome prompt").result_print()

# and somewhere later we can reference to the same AI app using the name
ai("system.md").result_print()

# and somewhere later we can reference to the same AI app using the variable
myapp.result_print()
```

```python
# Assume there's a file prompt_user.md with the message to OpenAI
# The user message (prompt) will be resolved from prompt_user.md therefore we don't need to pass it into the gpt4() method
ai("prompt").gpt4().result_print()
```

