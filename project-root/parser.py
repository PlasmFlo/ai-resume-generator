import json 
import csv             
import os      

# Define the sectiions our AI resume generator must handle 
REQUIRED_SECTIONS = [
  "Contact Information", 
  "Professional Summary",
  "Work Experience", 
  "Skills",
  "Education"
]

def parse_json(filepath):
  """Load and validate resume data from a JSON file."""
  if not os.path.isfile(filepath):
    raise FileNotFoundError(f"File not found: {filepath}")
  with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f) 
    
  # Check for missing sections
  missing = [sec for sec in REQUIRED_SECTIONS if sec not in data]
  if missing: 
    raise ValueError(f"Missing required sections: {missing}")
  
  return data


def parse_csv(filepath):
  """Load and collect resume entries from a CSV file."""
  if not os.path.isfile(filepath):
    raise FileNotFoundError(f"File not found: {filepath}")
  entries = []
  with open(filepath, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader: 
      entries.append(row)
      
  return entries 

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description="Parse resume input file.")
  parser.add_argument("input_file", help="Path to JSON or CSV file")
  args = parser.parse_args()
  
  ext = os.path.splitext(args.input_file)[1].lower()
  if ext == ".json":
    data = parse_json(args.input_file)
    print("Parsed JSON data:", data)
  elif ext == ".csv":
    data = parse_csv(args.input_file)
    print("Parsed CSV data:", data)
  else:
    print("Unsupported file type. Use .json or .csv")