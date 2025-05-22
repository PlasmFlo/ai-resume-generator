from flask import Flask, render_template, request, send_file
from xhtml2pdf import pisa
import io

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
def index():
    return render_template("index.html")


@app.route('/')
def home():
    data = {
        "name": "Plasm",  # or pull this from a form/session/db later
    }
    return render_template('index.html', data=data)


# === Process Form & Generate PDF ===
@app.route("/generate-resume", methods=["POST"])
def generate_resume():
    name = request.form.get("name", "")
    job_title = request.form.get("job_title", "")
    summary = request.form.get("summary", "")
    experience = request.form.get("experience", "")
    skills = request.form.get("skills", "")
    education = request.form.get("education", "")

    html = render_template(
        "resume_template.html",
        name=name,
        job_title=job_title,
        summary=summary,
        experience=experience,
        skills=skills,
        education=education
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
def health_check():
    return {"status": "ok", "message": "API running"}, 200

if __name__ == "__main__":
    app.run(debug=True)
