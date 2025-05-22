import os 
import sys
from dotenv import load_dotenv  
import openai
from openai import OpenAI
from parser import parse_json 

sys.stdout.reconfigure(encoding='utf-8')

# Load enviornment variables
load_dotenv() 

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai

def generate_experience_bullet(exp_entry):
  """ 
  Takes ono work-experience dict and returns a single GPT-generated bullet point. 
  """
  
  system = "You are an expert career coach. Generate one concise, achievement-focused bullet point."
  user = (
    f"Company: {exp_entry['Company']}\n"
    f"Title: {exp_entry['Title']}\n"
    f"Duration: {exp_entry['Start Date']}-{exp_entry.get('End Date', 'Present')}\n"
    f"Responsibilities: {exp_entry['Responsibilities']}\n"
    f"Metrics: {exp_entry['Metrics']}"
  )
  resp = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role":"system","content":system},
             {"role":"user","content":user}]
  )
  return resp.choices[0].message.content.strip()

def generate_summary(data):
  """ 
  Takes the full resume dict and returns a 3-4 sentence summary.
  """
  system = "You are a resume writer. Craft a 3-4 sentence professional summary."
  user = (
    f"Name: {data['Contact Information']['Name']}\n"
    f"Field: {data.get('Industry','N/A')}\n"
    f"Experience: {len(data['Work Experience'])} years\n"
    f"Top Skills: {', '.join(data['Skills'])}\n"
    f"Goal: Seeking a role where I can..."
  )
  resp = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role":"system","content":system},
              {"role":"user","content":user}]
  )
  return resp.choices[0].message.content.strip()


def generate_resume(data):
  prompt = f"""
  You are an expert resume writer. Create a professional resume summary and 3-5 bullet points for the following canidate: 
  
  Name: {data.get('name')}
  Work Experience: {data.get('experience')}
  Skills: {data.get('skills')}
  Education: {data.get('education')}
  
  Format it like this:
  
  Summary:
  [Write a professinal summary here]
  
  Bullet Points:
  - Point 1 
  - Point 2
  - ...
  """
  
  try: 
    response = client.chat.completions.create(
      model="gpt-4", # or gpt-3.5-turbo if using cheaper option
      messages=[{"role": "user", "content": prompt}],
      temperature=0.7
    )
    
    result = response.choices[0].message.content
    
    # Seperate summary, bullets
    summary = result.split("Bullet Points:")[0].replace("Summary:", "").strip()
    bullet_section = result.split("bullet Points:")[-1].strip()
    bullets = [line.strip("- ").strip() for line in bullet_section.split("\n") if line.startswith("-") or line.strip()]
               
    return summary, bullets
    
  except Exception as e: 
    return f"Error generating resume: {e}",[]
  

  


if __name__ == "__main__":
  if __name__ == "__main__":
    json_path = os.path.join(SCRIPT_DIR, "sample_resume.json")
  data = parse_json(json_path)

  name = data['Contact Information']['Name']
  summary = generate_summary(data)
  bullets = []
  
  print("=== Summary ===")
  print(summary)

  print("\n=== Bullets ===")
  for exp in data["Work Experience"]:
    bullet = generate_experience_bullet(exp)
    bullets.append(bullet)
    print("-", bullet)

  # PDF EXPORT
  import pdfkit
  config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')


  html_template = f"""
  <!DOCTYPE html>
  <html>
  <head>
      <style>
          body {{
              font-family: Arial, sans-serif;
              margin: 30px;
              line-height: 1.6;
          }}
          h1 {{ font-size: 28px; color: #333; }}
          h2 {{ margin-top: 20px; font-size: 20px; color: #444; }}
          p {{ font-size: 16px; color: #222; }}
          ul {{ list-style-type: disc; padding-left: 20px; }}
          li {{ margin-bottom: 8px; }}
      </style>
  </head>
  <body>
      <h1>{name}</h1>
      <h2>Summary</h2>
      <p>{summary}</p>
      <h2>Experience Highlights</h2>
      <ul>
          {''.join([f'<li>{b}</li>' for b in bullets])}
      </ul>
  </body>
  </html>
  """

  # Export to PDF
  pdfkit.from_string(html_template, "final_resume.pdf", configuration=config)
  print("\n✅ PDF successfully generated: final_resume.pdf")
