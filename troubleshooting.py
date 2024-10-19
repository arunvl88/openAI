# Note: Please vavigate back to openAI directory to find another solution (via function calling):

#Code 2 fixing the issue via prompt tuning (instructions)

import os
import time
import openai

# Initialize the OpenAI client
client = openai.OpenAI()

# Step 1: Provide the uploaded file_id directly (Replace this with your actual file ID)
file_id = "your-file-id-here"  # Provide your existing file ID
print(f"Using file ID: {file_id}")

# Step 2: Create an Assistant
assistant = client.beta.assistants.create(
    name="City Information Assistant",
    instructions=(
        "You are an assistant that provides information about people's favorite cities "
        "based on the provided CSV data. When asked about a person's favorite city, use the data "
        "to provide the full explanation without truncating any details."
    ),
    model="gpt-4",
    tools=[{"type": "code_interpreter"}]
)

# Step 3: Create a Thread
thread = client.beta.threads.create()

# Step 4: Prompt tuning for Tina Escobar
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=(
        "What is Tina Escobar's favorite city and why? Please provide the full information from the 'favourite_city_and_why' column, "
        "including all details, and do not truncate at any punctuation. Use the file with ID: {file_id}."
    )
)

# Step 5: Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Step 6: Wait for the Run to complete
while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run_status.status == 'completed':
        break
    time.sleep(1)

# Step 7: Retrieve and print the Assistant's response for Tina Escobar
messages = client.beta.threads.messages.list(thread_id=thread.id)
for msg in messages.data:
    if msg.role == 'assistant':
        print(f"Assistant: {msg.content[0].text.value}")
        break

# Step 8: Test with another person, James Padilla
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=(
        "What is James Padilla's favorite city and why? Please provide the full information from the 'favourite_city_and_why' column, "
        "including all details, and do not truncate at any punctuation. Use the file with ID: {file_id}."
    )
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Step 9: Wait for the second run to complete
while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run_status.status == 'completed':
        break
    time.sleep(1)

# Step 10: Retrieve and print the Assistant's second response for James Padilla
messages = client.beta.threads.messages.list(thread_id=thread.id)
for msg in messages.data:
    if msg.role == 'assistant':
        print(f"Assistant: {msg.content[0].text.value}")
        break

# Step 11: Clean up: Delete the assistant after use (File will not be deleted)
client.beta.assistants.delete(assistant_id=assistant.id)
