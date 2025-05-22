from flask import Flask, render_template, request, send_file
from xhtml2pdf import pisa
import io
from engine import generate_resume

app = Flask(__name__)

# === Convert HTML to PDF ===
def convert_html_to_pdf(source_html):
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.StringIO(source_html), result)
    if not pdf.err:
        return result.getvalue()
    return None

# === Home Page: Input Form ===
@app.route("/", methods=["GET"])
def index(data):
    return render_template("index.html")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name', '') 
        experience = request.form.get('experience', '')
        email = request.form.get("email", '')
        education = request.form.get('education', '')
        skills = request.form.get('skills', '')

        data = {
            "name": name,
            "experience": experience,
            "skills": skills,
            "education": education
        }

        try:
            summary, bullet_points = generate_resume(data)
        except Exception as e:
            print(f"Resume generation failed: {e}")
            return render_template("index.html", error="Resume generation failed.")

        return render_template("index.html", summary=summary, bullet_points=bullet_points, data=data)

    # Handle GET requests
    return render_template("index.html")


# === Process Form & Generate PDF ===
@app.route("/generate-resume", methods=["POST"])
def generate_pdf(data):
    data = {
        "name": request.form.get("name", ""),
        "job_title": request.form.get("job_title", ""),
        "summary": request.form.get("summary", ""),
        "experience": request.form.get("experience", ""),
        "skills": request.form.get("skills", ""),
        "education": request.form.get("education", "")
    }
    
    summary = data.get("summary", "")
    experience = data.get("experience", "")
    skills = data.get("skills", "")

    bullet_points = [
        f"Demonstrated {skill.strip()} in professional settings"
        for skill in skills.split(",") if skill.strip()
    ]

    return summary, bullet_points

     

    html = render_template(
        "resume_template.html",
        name=data["name"],
        job_title=data["job_title"],
        summary=summary,
        experience=data["experience"],
        skills=data["skills"],
        education=data["education"],
        bullet_points=bullet_points  # If you're using it
    )

    pdf = convert_html_to_pdf(html)

    if pdf:
        return send_file(
            io.BytesIO(pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name="resume.pdf"
        )
    else:
        return "PDF generation failed", 500


# === Health Check or API Ping ===
@app.route("/health", methods=["GET"])
def health_check(data):
    return {"status": "ok", "message": "API running"}, 200




   



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT env var or fallback to 5000
    app.run(debug=True, host='0.0.0.0', port=port)
