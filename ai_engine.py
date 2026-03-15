from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import PyPDF2
import io

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>AI Contract Risk Analyzer</title>
    </head>
    <body>
        <h2>Upload Contract PDF</h2>
        <form action="/upload-pdf" enctype="multipart/form-data" method="post">
            <input name="file" type="file">
            <input type="submit">
        </form>
    </body>
    </html>
    """

app = FastAPI()

# Input model
class ClauseInput(BaseModel):
    clause: str

# Policy-based risk analyzer
def analyze_clause(clause):
    clause_lower = clause.lower()

    if "terminate without notice" in clause_lower:
        return {
            "risk_level": "HIGH",
            "reason": "Clause allows termination without prior notice"
        }

    elif "unlimited liability" in clause_lower:
        return {
            "risk_level": "CRITICAL",
            "reason": "Clause contains unlimited liability"
        }

    elif "confidential" in clause_lower:
        return {
            "risk_level": "MEDIUM",
            "reason": "Confidential clause present, requires review"
        }

    else:
        return {
            "risk_level": "LOW",
            "reason": "No major risk detected"
        }

@app.get("/")
def home():
    return {"message": "Contract AI Engine Running"}

# Analyze text input
@app.post("/analyze")
def analyze(input_data: ClauseInput):

    clauses = input_data.clause.split(".")

    results = []

    for clause in clauses:
        clause = clause.strip()
        if clause:
            analysis = analyze_clause(clause)
            results.append({
                "clause": clause,
                "risk_level": analysis["risk_level"],
                "reason": analysis["reason"]
            })

    return {
        "total_clauses": len(results),
        "analysis_results": results
    }

# Upload and analyze PDF
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    contents = await file.read()

    pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))

    text = ""

    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    clauses = text.split(".")

    results = []

    for clause in clauses:
        clause = clause.strip()
        if clause:
            analysis = analyze_clause(clause)
            results.append({
                "clause": clause,
                "risk_level": analysis["risk_level"],
                "reason": analysis["reason"]
            })

    return {
        "total_clauses": len(results),
        "analysis_results": results
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
