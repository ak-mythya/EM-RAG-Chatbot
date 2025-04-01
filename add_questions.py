import os
import json
import csv

input_folder = "extracted_docs_byjus"
output_csv = "class12_physics_qa.csv"

existing_questions = set()
csv_data = []

# Step 1: Read existing questions from CSV (if the file exists)
if os.path.exists(output_csv):
    with open(output_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_questions.add(row["Question"])

# Step 2: Load JSON files and add only new questions
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(input_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data.get("questions", []):
                question_text = item["question"] + "\n" + "\n".join(item["options"])
                solution_text = item["solution"]
                if question_text not in existing_questions:
                    csv_data.append([question_text, solution_text])
                    existing_questions.add(question_text)  # So we don't duplicate in this session too

# Step 3: Append new data to CSV
with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    if os.stat(output_csv).st_size == 0:
        writer.writerow(["Question", "Solution"])  # Add header if file is empty
    writer.writerows(csv_data)

print(f"Added {len(csv_data)} new question(s) to '{output_csv}'.")
