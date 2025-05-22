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


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Extract form data safely
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        summary = request.form.get("summary", "")
        experience = request.form.get("experience", "")
        skills = request.form.get("skills", "")
        education = request.form.get("education", "")

        # Pack into data dictionary
        data = {
            "name": name,
            "email": email,
            "summary": summary,
            "experience": experience,
            "skills": skills,
            "education": education
        }

        try:
            # Call your AI resume generation engine (imported from engine.py)
            summary, bullet_points = generate_resume(data)

            # Optionally attach summary/bullets to data
            data["summary"] = summary
            data["bullet_points"] = bullet_points

            # Generate PDF from data
            pdf = generate_pdf(data)

            return send_file(
                pdf,
                mimetype='application/pdf',
                as_attachment=True,
                download_name="resume.pdf"
            )

        except Exception as e:
            print(f"Error generating resume: {e}")
            return render_template("index.html", error="Resume generation failed.")

    # Handle GET
    return render_template("index.html")



# === Process Form & Generate PDF ===
@app.route("/generate-resume", methods=["POST"])
def generate_pdf():
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

    from xhtml2pdf import pisa
    import io

    def convert_html_to_pdf(source_html):
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.StringIO(source_html), result)
        if not pdf.err:
            return result.getvalue()
        return None

    data = {
    "name": request.form.get("name", ""),
    "email": request.form.get("email", ""),
    "summary": request.form.get("summary", ""),
    "experience": request.form.get("experience", ""),
    "skills": request.form.get("skills", ""),
    "education": request.form.get("education", "")
}

    pdf = generate_pdf(data)

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
