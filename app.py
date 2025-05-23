from flask import Flask, render_template, request, send_file
from xhtml2pdf import pisa
import io
import os
from engine import generate_resume
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret")

# PDF generator helper
def generate_pdf(data):
    html = render_template("resume_template.html", **data)
    result = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=result)
    result.seek(0)
    return result

# Home page route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        data = {
            "name": request.form.get("name", ""),
            "email": request.form.get("email", ""),
            "summary": request.form.get("summary", ""),
            "experience": request.form.get("experience", ""),
            "skills": request.form.get("skills", ""),
            "education": request.form.get("education", "")
        }

        try:
            # Generate AI-enhanced content
            summary, bullets = generate_resume(data)
            data["summary"] = summary
            data["bullet_points"] = bullets

            # Create and return PDF
            pdf = generate_pdf(data)
            return send_file(pdf, download_name="resume.pdf", as_attachment=True)

        except Exception as e:
            print("Resume generation failed:", e)
            return render_template("index.html", error="Generation failed.")

    return render_template("index.html")

if __name__ == "__main__":
  import os
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
