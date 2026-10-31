
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from starlette.concurrency import run_in_threadpool

from app.agents.clause_extractor import extract_clauses
from app.agents.clause_analyzer import analyze_clause
from app.agents.batch_clause_analyzer import analyze_clauses_in_batch
from app.agents.cross_clause_analyzer import analyze_cross_clauses
from app.agents.recommendation_agent import generate_recommendations
from app.agents.property_investigator import (
    investigate_property_documents
)

from app.services.ocr_service import extract_text_with_ocr
from app.services.language_detector import detect_language
from app.services.document_classifier import classify_document

router = APIRouter()


# ==========================================================
# CONTRACT INVESTIGATION
# ==========================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    use_ai: bool = Query(default=False)
):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF documents are supported."
        )

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty."
        )

    try:
        # DOCUMENT PROCESSING WITH OCR
        page_results = await run_in_threadpool(
            extract_text_with_ocr,
            pdf_bytes
        )

        total_pages = len(page_results)

        extracted_text = ""

        for page in page_results:
            extracted_text += (
                f"\n--- Page {page['page_number']} ---\n"
            )
            extracted_text += page["text"]

        # EXTRACTION SUMMARY
        pdf_text_pages = sum(
            1 for page in page_results
            if page["extraction_method"] == "PDF_TEXT"
        )

        ocr_pages = sum(
            1 for page in page_results
            if page["extraction_method"] == "OCR"
        )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text found, even after OCR."
            )

        # EXTRACTION QUALITY ASSESSMENT
        quality_status_counts = {
            "ACCEPTABLE": 0,
            "NEEDS_REVIEW": 0,
            "INSUFFICIENT_TEXT": 0
        }

        pages_requiring_review = []
        ocr_attempted_pages = 0
        page_quality_results = []

        for page in page_results:

            quality = page["extraction_quality"]
            quality_status = quality["quality_status"]

            if quality_status in quality_status_counts:
                quality_status_counts[quality_status] += 1

            if page["ocr_attempted"]:
                ocr_attempted_pages += 1

            if quality_status != "ACCEPTABLE":
                pages_requiring_review.append(
                    page["page_number"]
                )

            page_quality_results.append({
                "page_number": page["page_number"],
                "extraction_method": page["extraction_method"],
                "ocr_attempted": page["ocr_attempted"],
                "ocr_error": page["ocr_error"],
                "quality": quality
            })

        extraction_quality_summary = {
            "overall_status": (
                "NEEDS_REVIEW"
                if pages_requiring_review
                else "ACCEPTABLE"
            ),
            "total_pages": total_pages,
            "acceptable_pages": quality_status_counts["ACCEPTABLE"],
            "pages_needing_review": quality_status_counts["NEEDS_REVIEW"],
            "pages_with_insufficient_text": quality_status_counts["INSUFFICIENT_TEXT"],
            "ocr_attempted_pages": ocr_attempted_pages,
            "pages_requiring_review": pages_requiring_review
        }

        # DOCUMENT LANGUAGE DETECTION
        language_result = detect_language(extracted_text)

        # DOCUMENT TYPE CLASSIFICATION
        document_classification = classify_document(extracted_text)

        # AGENT 1: CLAUSE EXTRACTION
        clauses = extract_clauses(page_results)

        if not clauses:
            raise HTTPException(
                status_code=422,
                detail="No identifiable clauses were found in the document."
            )

        # AGENT 2: RULE-BASED CLAUSE ANALYSIS
        analyzed_clauses = []

        for clause in clauses:

            analysis = analyze_clause(clause)

            analysis["clause_number"] = clause["clause_number"]
            analysis["heading_level"] = clause["heading_level"]
            analysis["parent_clause"] = clause["parent_clause"]

            analysis["start_page"] = clause["start_page"]
            analysis["end_page"] = clause["end_page"]
            analysis["page_numbers"] = clause["page_numbers"]

            analyzed_clauses.append(analysis)

        # AGENT 3: BATCH AI CLAUSE ANALYSIS
        ai_analysis_status = "NOT_REQUESTED"
        ai_analysis_error = None

        if use_ai:

            try:
                batch_results = await run_in_threadpool(
                    analyze_clauses_in_batch,
                    clauses
                )

                result_map = {
                    result["clause_number"]: result
                    for result in batch_results
                }

                successful_count = 0

                for clause, analysis in zip(
                    clauses,
                    analyzed_clauses
                ):

                    clause_number = clause["clause_number"]
                    ai_result = result_map.get(clause_number)

                    if ai_result is not None:
                        analysis["ai_analysis"] = ai_result
                        successful_count += 1

                    else:
                        analysis["ai_analysis"] = {
                            "status": "AI analysis failed",
                            "error": "No result returned for this clause."
                        }

                if successful_count == len(clauses):
                    ai_analysis_status = "SUCCESS"

                elif successful_count > 0:
                    ai_analysis_status = "PARTIAL"

                else:
                    ai_analysis_status = "FAILED"

            except Exception as error:

                ai_analysis_status = "FAILED"
                ai_analysis_error = str(error)

                for analysis in analyzed_clauses:
                    analysis["ai_analysis"] = {
                        "status": "AI analysis failed",
                        "error": str(error)
                    }

        # AGENT 4: CROSS-CLAUSE ANALYSIS
        cross_clause_findings = analyze_cross_clauses(
            analyzed_clauses
        )

        # AGENT 5: RECOMMENDATION AGENT
        recommendations = generate_recommendations(
            cross_clause_findings
        )

        # RULE-BASED RISK SUMMARY
        risk_summary = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for clause in analyzed_clauses:
            level = clause["risk_level"]

            if level in risk_summary:
                risk_summary[level] += 1

        # AI RISK SUMMARY
        ai_risk_summary = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        successful_ai_count = 0

        if use_ai:

            for clause in analyzed_clauses:

                ai_result = clause.get("ai_analysis", {})

                if ai_result.get("risk_level") in ai_risk_summary:

                    ai_risk_summary[
                        ai_result["risk_level"]
                    ] += 1

                    successful_ai_count += 1

        # FINAL RESPONSE
        return {
            "filename": file.filename,
            "total_pages": total_pages,
            "total_clauses": len(clauses),

            "extraction_summary": {
                "total_pages": total_pages,
                "pdf_text_pages": pdf_text_pages,
                "ocr_pages": ocr_pages
            },

            "extraction_quality_summary": extraction_quality_summary,
            "page_quality_results": page_quality_results,

            "language_detection": language_result,
            "document_classification": document_classification,

            "ai_analysis_enabled": use_ai,
            "ai_analysis_status": ai_analysis_status,
            "ai_successful_clauses": successful_ai_count,
            "ai_failed_clauses": (
                len(clauses) - successful_ai_count
                if use_ai else 0
            ),
            "ai_analysis_error": ai_analysis_error,

            "risk_summary": risk_summary,
            "ai_risk_summary": (
                ai_risk_summary if use_ai else None
            ),

            "analyzed_clauses": analyzed_clauses,
            "cross_clause_findings": cross_clause_findings,
            "recommendations": recommendations,

            "status": "Document analysis completed"
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to process PDF: {str(error)}"
        )


# ==========================================================
# PROPERTY INVESTIGATION
# ==========================================================

@router.post("/property-investigation")
async def investigate_property(
    sale_deed: UploadFile = File(
        ...,
        description=(
            "Upload a Property Sale Deed OR Property Sale Agreement PDF."
        )
    ),

    encumbrance_certificate: UploadFile = File(
        ...,
        description=(
            "Upload an issued Encumbrance Certificate OR "
            "an Encumbrance Certificate Application / Copy PDF."
        )
    )
):
    """
    Investigate two property documents.

    First document:
        Property Sale Deed or Property Sale Agreement.

    Second document:
        Encumbrance Certificate or EC Application / Copy.

    Both documents are classified before property extraction
    and comparison.
    """

    uploaded_files = {
        "first_property_document": sale_deed,
        "second_property_document": encumbrance_certificate
    }

    pdf_contents = {}

    # 1. VALIDATE AND READ BOTH PDF FILES
    for document_name, uploaded_file in uploaded_files.items():

        if (
            not uploaded_file.filename
            or not uploaded_file.filename.lower().endswith(".pdf")
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{document_name} must be a PDF file."
            )

        pdf_bytes = await uploaded_file.read()

        if not pdf_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"{document_name} PDF is empty."
            )

        pdf_contents[document_name] = pdf_bytes

    try:
        # 2. EXTRACT TEXT FROM BOTH PDFs
        document_texts = {}
        extraction_summaries = {}

        for document_name, pdf_bytes in pdf_contents.items():

            page_results = await run_in_threadpool(
                extract_text_with_ocr,
                pdf_bytes
            )

            if not page_results:
                raise HTTPException(
                    status_code=422,
                    detail=f"No pages found in {document_name}."
                )

            extracted_text = ""

            for page in page_results:
                extracted_text += (
                    f"\n--- Page {page['page_number']} ---\n"
                )
                extracted_text += page["text"]

            if not extracted_text.strip():
                raise HTTPException(
                    status_code=422,
                    detail=f"No readable text found in {document_name}."
                )

            document_texts[document_name] = extracted_text

            extraction_summaries[document_name] = {
                "total_pages": len(page_results),

                "pdf_text_pages": sum(
                    1 for page in page_results
                    if page["extraction_method"] == "PDF_TEXT"
                ),

                "ocr_pages": sum(
                    1 for page in page_results
                    if page["extraction_method"] == "OCR"
                )
            }

        # 3. RUN PROPERTY INVESTIGATION ENGINE
        investigation_result = await run_in_threadpool(
            investigate_property_documents,
            document_texts["first_property_document"],
            document_texts["second_property_document"]
        )

        # 4. RETURN CONSOLIDATED RESULT
        first_document_type = (
            investigation_result["investigation_summary"][
                "first_document_type"
            ]
        )

        second_document_type = (
            investigation_result["investigation_summary"][
                "second_document_type"
            ]
        )

        return {
            "first_property_document": {
                "filename": sale_deed.filename,
                "document_type": first_document_type
            },

            "second_property_document": {
                "filename": encumbrance_certificate.filename,
                "document_type": second_document_type
            },

            "extraction_summaries": extraction_summaries,

            "investigation": investigation_result,

            "status": "Property investigation completed"
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to investigate property documents: "
                f"{str(error)}"
            )
        )
