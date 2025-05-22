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





load_dotenv()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')



# Function for creating resume output

app = Flask(__name__) # create the app

app.secret_key = 'plasm-secret-key'

@app.route('/', methods=['GET', 'POST']) # homepage route
def home():
    if request.method == 'POST':
      # Get form data from user input
      name = request.form.get('name') 
      experience = request.form.get('experience')
      email = request.form.get("email")
      education = request.form.get('education')
      print(request.form)
      
      # Prepare the data for resume engine 
      data = {
        "name": request.form.get('name', ''),
        "experience": request.form.get('experience', ''),
        "skilss": request.form.get('skills', ''),
        "education": request.form.get('education', '')
      }
      
      print("Final data sent to engine:", data) # Add this debug
      
      # Call your resume generation function
      print("Received form data:", request.form)
      summary, bullets_points = generate_resume(data)
      
      rendered = render_template('resume_template.html', name=name, email=email, experience=experience)
      
      pdf = pdfkit.from_string(rendered, False, configuration=config)
      
      response = make_response(pdf)
      response.headers['Content-Type'] = 'application/pdf'
      response.headers['Content-Disponsition'] = 'attachment; filename=resume.pdf'
      
      return response
    
      return send_file(io.BytesIO(pdf), download_name="resume.pdf", as_attachment=True)
    
    
    
    
      # Render the HTML with the results
      return render_template('index.html', summary=summary, bullets_points=bullets_points, data=data)
    
    # First time loading page
    return render_template('index.html')
  
@app.route('/generate', methods=['POST'])
def generate_resume():
    name = request.form['name']
    email = request.form['email']
    summary = request.form['summary']

    rendered_html = render_template('resume_template.html', name=name, email=email, summary=summary)

    result = BytesIO()
    pisa.CreatePDF(rendered_html, dest=result)

    result.seek(0)
    return send_file(result, as_attachment=True, download_name="resume.pdf", mimetype='application/pdf')

  
  
@app.route("/", methods=["GET", "POST"])
def index():
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
def create_checkout_session():
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
def pro():
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
    
    
if __name__ == '__main__':
    app.run(debug=True)

