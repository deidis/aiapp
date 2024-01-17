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

The parameter `name` serves these purposes:

1. It's the name of the so called "AI app" which we can later get by the same name
2. If the name is something like "blabla" then it will try to find the `blabla.md`, blabla_system.md` or `blabla_user.md` and use the contents of the file as the respective prompt message (system or user message - system by default)
3. Just in case the name coincides with a file name (if a file found) it will be used as a system message

#### Examples

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

### gpt35(...) gpt35turbo(...), gpt4(...), gpt4turbo(...)

Full list of parameters: user_message=None, temperature=0.5, top_p=0.5, frequency_penalty=0, presence_penalty=0. Please refer to the OpenAI API documentation, but the defaults are quite balanced.

These methods simply call the API with the user prompt and other parameters.



#### Examples

```python
# Assume there's a file prompt_user.md with the message to OpenAI
# The user message (prompt) will be resolved from prompt_user.md therefore we don't need to pass it into the gpt4() method
ai("prompt").gpt4().result_print()
```

```python
ai("myapp").gpt4turbo("Say hi!").result_print()
```

### result_print()

Simply print the result using Python's `print()` function, returns void.

### result_show()

Will return the IPython.display with Markdown object inside. Which is mostly useful for Jupyter.

### result()

Will return the raw unformatted result from the API (only single/first result, not the list of results).

#### Examples

```python
ai("myapp").gpt4("Say hi!").result_print()
# Equivalent to:
print(ai("myapp").gpt4("Say hi!").result())
```

### system(message), user(message), assistant(message)

These are used to set the messages that will go to the API.

The parameter `message` serves these purposes:

1. If the message is something like "blabla" then it will try to find the `blabla_system.md`, `blabla_user.md` or `blabla_assitant.md` and use the contents of the file as the respective role message
2. In case you pass the filename to the function, the contents will be used as the message
3. If no file is found, the `message` will be used as is
4. If message isn't provided it will return the message that was set before

#### Examples

```python
ai("myapp").system("Act as a polyglot").user("Say 'hi'!").gpt4().result_print()
```

```python
# Let's say we also have a translate_system.md with a system message
ai("myapp").system("translate").user(ai("myapp").user()).gpt4().result_print()
```

### var(name, value)

This will prepend a section to the system prompt about a variable named `name` which we can reference in the system prompt as we write it. To see how the whole system prompt looks like, print the result of `system_compiled()` function.

#### Examples

```python
ai("step1").system("Act as a polyglot").user("Say 'hi' in Lithuanian").gpt4()
step2 = ai("step2").system("Use the RESULT1 and translate it to French").var("RESULT1", ai("step1").result()).gpt4turbo()

# Now let's see what we were actually doing in step2
print(step2.system_compiled())

# And finally print the result
step2.result_print()
```

### example_json(value), json_schema(value)

We can hint the model to respond in JSON. OpenAPI will surely return JSON response with `gpt4turbo()` with others it's not guaranteed, but works most of the time.

As the methods indicate `value` should be either a json how we want the response to look like or a json schema, where we would normally say in the description of every field what it means.

Internally this function simply appends a section about formatting to the system prompt. To see how the whole system prompt looks like, print the result of `system_compiled()` function.

#### Examples

```python
ai("myapp").system("Act as a polyglot").user("Say 'hi' in Lithuanian").gpt4turbo().example_json({
    "language": "lt",
    "translation": "The translated result"
})

# Now let's se what we were actually doing
print(ai("myapp").system_compiled())

# And finally print the result
ai("myapp").result_print()
```