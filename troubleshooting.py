import os
import time
import openai

# Initialize the OpenAI client
client = openai.OpenAI()

# Step 1: Upload the file
file = client.files.create(
    file=open("tse_takehome_dataset.csv", "rb"),
    purpose='assistants'  # Using 'fine-tune' as the purpose for uploading
)

# Step 2: Create an Assistant
assistant = client.beta.assistants.create(
    name="City Information Assistant",
    instructions="""
You are an assistant that provides comprehensive information about people's favorite cities. When asked about a person's favorite city, follow these steps:

1. Read the CSV file and locate the row for the specified person.
2. Extract the full content of the 'favourite_city_and_why' column for that person.
3. Display the raw content of the cell, treating it as a single string and preserving all information, including any commas or additional facts within the cell.
4. After showing the raw data, provide a detailed explanation of the information, including all aspects mentioned in the cell.

    """,
    model="gpt-4",
    tools=[{"type": "code_interpreter"}]
)


# Step 3: Create a Thread
thread = client.beta.threads.create()

# Step 4: Add a Message to the Thread, referring to the file by its ID in the prompt
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=(
        "What is Tina Escobar's favorite city and why? "
        f"including any additional facts, using the data from the file with ID: {file.id}."
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

# Step 7: Retrieve and print the Assistant's response
messages = client.beta.threads.messages.list(thread_id=thread.id)
for msg in messages.data:
    if msg.role == 'assistant':
        print(f"Assistant: {msg.content[0].text.value}")
        break

# Step 8: Test with another person
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=(
        "What is James Padilla's favorite city and why?"
        f"including any additional facts, using the data from the file with ID: {file.id}."
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

# Step 10: Retrieve and print the Assistant's second response
messages = client.beta.threads.messages.list(thread_id=thread.id)
for msg in messages.data:
    if msg.role == 'assistant':
        print(f"Assistant: {msg.content[0].text.value}")
        break

# Step 11: Clean up: Delete the assistant and file after use
client.beta.assistants.delete(assistant_id=assistant.id)
client.files.delete(file_id=file.id)
