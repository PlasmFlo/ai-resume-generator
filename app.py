from flask import Flask, render_template, request, make_response, session, send_file, redirect, url_for
from engine import generate_resume
import os, platform
import stripe
from weasyprint import HTML
from dotenv import load_dotenv
import json
from xhtml2pdf import pisa              
from io import BytesIO
import io
import openai
from engine import generate_resume



load_dotenv()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')



# Function for creating resume output

app = Flask(__name__) # create the app

app.secret_key = 'plasm-secret-key'

@app.route('/', methods=['GET', 'POST']) # homepage route
def home():
     if request.method == 'POST':
        name = request.form.get('name') 
        experience = request.form.get('experience')
        email = request.form.get("email")
        education = request.form.get('education')
        skills = request.form.get('skills')

        data = {
            "name": name,
            "experience": experience,
            "skills": skills,
            "education": education
        }

        print("Final data sent to engine:", data)
        summary, bullets_points = generate_resume(data)

        return render_template(
            'resume_template.html',
            name=name,
            email=email,
            experience=experience,
            summary=summary,
            bullets=bullets_points
        )

        return render_template('index.html')
  
@app.route('/generate', methods=['POST'])
def generate_pdf(data):
    name = data.get("name", "")
    experience = data.get("experience", "")
    skills = data.get("skills", "")
    education = data.get("education", "")

    prompt = f"""
You are an expert resume writer. Based on the following information, create:

1. A concise professional summary (2-4 sentences).
2. 3-5 strong bullet points highlighting the person's experience and skills.

Name: {name}
Experience: {experience}
Skills: {skills}
Education: {education}

Output in this format:
SUMMARY:
[Summary]

BULLETS:
- [Point 1]
- [Point 2]
- [Point 3]
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )

    content = response['choices'][0]['message']['content']

    # Split the result into summary and bullet points
    summary_section = content.split("BULLETS:")[0].replace("SUMMARY:", "").strip()
    bullets_section = content.split("BULLETS:")[1].strip().split("\n")

    bullets = [point.strip("- ").strip() for point in bullets_section if point.strip()]

    return summary_section, bullets


  
  
@app.route("/", methods=["GET", "POST"])
def index(data):
  # Initialize resume_count for new users
  if 'resume_count' not in session:
    session['resume_count'] = 0
    
  if session['resume_count'] >= 1:
    return render_template("limit_reached.html") # We'll create this next
  
  if request.method == "POST":
    uploaded_file = request.files["resume"]
    if uploaded_file.filename != "":
      data = json.load(uploaded_file)
      summary = generate_summary(data)
      bullets = [generat_experience_bullet(exp) for exp in data["Work Experience"]]
      
      html_template = build_resume_html(name, summary, bullets)
      output_path = os.path.join("resume_ouput.pdf")
      pdfkit.from_string(html_template, output_path, configuration=config)
      
      session['resume_count'] += 1
      return send_file(output_path, as_attachment=True)
    
  return render_template("index.html")
  
  
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session(data):
  session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    line_items=[{
      "price_data": {
        "currency": "usd",
        "product_data": {
          "name": "AI Resume Generator",
        },
        "unit_amount": 999,
      },
    }],
    mode="payment",
    success_url="http://127.0.0.1:5000/success",
    cancel_url="http://127.0.0.1:5000/cancel",
  )
  return {"id": session.id}


@app.route("/pro", methods=["GET", "POST"])
def pro(data):
  if request.method == "POST":
    uploaded_file = request.files["resume"]
    if uploaded_file.filename != "":
      data = json.load(uploaded_file)
      name = data['Contact Information']['Name']
      summary = generate_summary(data)
      bullets = [generat_experience_bullet(exp) for exp in data["Work Experience"]]
      
      html_template = build_pro_resume_html(name, summary, bullets)
      output_path = os.path.join("pro_resume_output.pdf")
      pdfkit.from_string(html_template, output_path, configuration=PDF_CONFIG)
      
      return send_file(output_path, as_attachment=True)
    
  return render_template("pro.html")
      

def build_resume_html(name, summary, bullets):
  return f"""
<html><head><style>body{{font-family:Arial;margin:30px}}</style?<head><body>
<h1>{name}</h1>
<h2>Summary<h2><p>{summary}</p>
<h2>Experience Highlights</h2><ul>
{''.join([f"<li>{b}</li>" for b in bullets])}
</ul>
</body></html>
"""

def build_pro_resume_html(name, summary, bullets):
  return f"""
  <html>
    <head>
        <style>
            body {{
                font-family: 'Georgia', serif;
                background-color: #f9f9f9;
                padding: 40px;
                color: #222;
            }}
            h1 {{
                font-size: 28px;
                border-bottom: 2px solid #222;
            }}
            h2 {{
                color: #444;
                margin-top: 30px;
            }}
            li {{
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>{name}</h1>
        <h2>Professional Summary</h2>
        <p>{summary}</p>
        <h2>Key Experience Highlights</h2>
        <ul>
            {''.join([f'<li>{b}</li>' for b in bullets])}
        </ul>
    </body>
    </html>
    """
    
def generate_pdf(html_string):
  result = BytesIO()
  pisa.CreatePDF(html, dest=result)
  with open("output.pdf", "wb") as f:
    f.write(result.getvalue())
    
  ''  
    
def convert_html_to_pdf(source_html):
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.StringIO(source_html), result)
    if not pdf.err:
        return result.getvalue()
    return None 
    
    
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT env var or fallback to 5000
    app.run(debug=True, host='0.0.0.0', port=port)



