import os 
import sys
from dotenv import load_dotenv  
from openai import OpenAI
from parser import parse_json 

sys.stdout.reconfigure(encoding='utf-8')

# Load enviornment variables
load_dotenv() 

# Set API key directly
api_key = "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"

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def generate_experience_bullet(exp_entry):
  """ 
  Takes ono work-experience dict and returns a single GPT-generated bullet point. 
  """
  
  system = "You are an expert career coach. Generate one concise, achievement-focused bullet point."
  user = (
    f"Company: {exp_entry['Company']}\\n"
    f"Title: {exp_entry['TItle']}\\n"
    f"Duration: {exp_entry['Start Date']}-{exp_entry['End Datte']}\\n"
    f"Responsibilites: {exp_entry['Responsibiites']}\\n"
    f"Metrics: {exp_entry['Metrics']}"
  )
  resp = client.chat.completions.create(
    model="gpt-4o",
    messaes=[{"role":"system","content":system},
             {"role":"user","content":user}]
  )
  return resp.choices[0].message.content.strip()

def generate_summary(data):
  """ 
  Takes the full resume dict and returns a 3-4 sentence summary.
  """
  system = "You are a resume writer.  Creft a 3-4 sentence professinal summary."
  user = (
    f"Name: {data['Contact Information']['Name']}\\n"
    f"Field: {data.get('Industry','N/A')}\\n"
    f"Experience: {len(data['Work Experience'])} years\\n"
    f"Top Skills: {', '.join(data['Skills'])}\\n"
    f"Goal: Seeking a role where I can..."
  )
  resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"system","content":system},
              {"role":"user","content":user}]
  )
  return resp.choices[0].message.content.strip()

def generate_resume(data):
    name = data.get("name", "")
    experience = data.get("experience", "")
    skills = data.get("skills", "")
    education = data.get("education", "")

    summary = f"{name} is experienced in {experience}."
    bullets = [
        f"Skilled in {skills}",
        f"Educated at {education}"
    ]
    return summary, bullets

if __name__ == "__main__":
  data = parse_json("sample_resume.json")
  print("=== Summary ===")
  print(generate_summary(data))
  print("\n=== Bullets ===")
  for exp in data["Work Experience"]:
    print("-", generate_experience_bullet(exp))