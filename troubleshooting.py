# This section provides two codes, one using function calling to fix the issue customer is facing and other using prompt engineering:

# Code 1: Fiixng the issue via Function calling

import os
import time
import openai
import pandas as pd

# Initialize the OpenAI client
client = openai.OpenAI()

# Step 1: Upload the file (already done earlier)
file_id = 'file-UyWuOXh1i3IxcbMXqZMJflFp'  # You uploaded this earlier

# Step 2: Load the CSV data into a DataFrame
file_path = 'tse_takehome_dataset.csv'
data = pd.read_csv(file_path)

# Step 3: Define a function to extract 'favourite_city_and_why' for a specific person
def get_favourite_city_details(data, name):
    # Filter the row for the person's name and get the 'favourite_city_and_why' column
    person_data = data[data['name'] == name]
    if not person_data.empty:
        return person_data['favourite_city_and_why'].values[0]
    else:
        return f"No data available for {name}"

# Step 4: Define a function that the assistant will call to provide the full city details
def process_request_for_city(client, thread_id, assistant_id, person_name, data):
    # Get the favourite city details for the person
    favourite_city_info = get_favourite_city_details(data, person_name)
    
    # Step 5: Create a new message in the thread, passing the full city information
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=(
            f"{person_name}'s favorite city and why: {favourite_city_info}."
        )
    )
    
    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Wait for the run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == 'completed':
            break
        time.sleep(1)

    # Retrieve and print the Assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages.data:
        if msg.role == 'assistant':
            print(f"Assistant: {msg.content[0].text.value}")
            break

# Step 6: Create an Assistant
assistant = client.beta.assistants.create(
    name="City Information Assistant",
    instructions=(
        "You are an assistant that provides information about people's favorite cities "
        "based on the provided CSV data. When asked about a person's favorite city, call the function "
        "to read the provided file and give the full information, including any additional facts."
    ),
    model="gpt-4",
    tools=[{"type": "code_interpreter"}]  # Using code interpreter to process data
)

# Step 7: Create a Thread
thread = client.beta.threads.create()

# Step 8: Process request for Tina Escobar
process_request_for_city(client, thread.id, assistant.id, 'Tina Escobar', data)

# Step 9: Test with another person, James Padilla
process_request_for_city(client, thread.id, assistant.id, 'James Padilla', data)

# Step 10: Clean up: Delete the assistant and file after use
client.beta.assistants.delete(assistant_id=assistant.id)
client.files.delete(file_id=file_id)


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
