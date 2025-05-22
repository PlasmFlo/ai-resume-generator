import pdfkit

config = pdfkit.configuration(wkhtmltopdf=r'"C:\Users\Isaiah Davis\Downloads\wkhtmltox-0.12.6-1.mxe-cross-win64\wkhtmltox\bin\wkhtmltopdf.exe"')

html = "<h1>✅ PDF Export Works!</h1><p>This is a test resume.</p>"

pdfkit.from_string(html, "test_resume.pdf", configuration=config)
