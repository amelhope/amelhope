import ollama

reponse = ollama.chat(model="mistral:7b-instruct-q4_0", messages=[
    {"role": "user", "content": "Dis bonjour en une phrase, en français."}
])

print(reponse["message"]["content"])
