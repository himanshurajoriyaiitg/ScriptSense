import json


def build_sample_rubric():
    return {
        "title": "Algorithms Midterm Q1",
        "exam_name": "Algorithms Midterm",
        "description": "Grade the explanation of binary search.",
        "instructions": "Award partial credit when the search strategy is correct.",
        "total_marks": "10",
        "criteria": [
            {
                "title": "Core idea",
                "description": "Recognizes divide and conquer and midpoint logic.",
                "max_marks": 6,
                "expected_points": [
                    "Binary search divides the range",
                    "Checks the middle element",
                ],
                "strict_keywords": ["binary", "middle", "sorted"],
                "partial_credit_rules": ["Give some credit for divide-and-conquer explanation"],
                "notes": "Strictly require sorted-array context.",
            },
            {
                "title": "Complexity",
                "description": "Mentions logarithmic time complexity.",
                "max_marks": 4,
                "expected_points": ["Time complexity is O(log n)"],
                "strict_keywords": ["log", "complexity"],
                "partial_credit_rules": [],
                "notes": None,
            },
        ],
    }


def test_rubric_creation_and_direct_grading(client, instructor_headers):
    rubric_response = client.post(
        "/rubrics",
        headers=instructor_headers,
        json=build_sample_rubric(),
    )

    assert rubric_response.status_code == 201
    rubric_body = rubric_response.json()
    assert rubric_body["title"] == "Algorithms Midterm Q1"
    assert len(rubric_body["criteria"]) == 2

    grade_response = client.post(
        "/grade",
        headers=instructor_headers,
        json={
            "answer": (
                "Binary search works on a sorted array. It checks the middle element "
                "and halves the search space, so the complexity is logarithmic."
            ),
            "rubric": rubric_body,
        },
    )

    assert grade_response.status_code == 200
    grading_result = grade_response.json()["grading_result"]
    assert grading_result["status"] == "heuristic_review_required"
    assert grading_result["score_breakdown"]
    assert grading_result["confidence"] > 0


def test_bulk_upload_review_queue_and_plagiarism_flags(
    client,
    instructor_headers,
    ta_headers,
    monkeypatch,
    sample_pdf_bytes,
):
    rubric_response = client.post(
        "/rubrics",
        headers=instructor_headers,
        json=build_sample_rubric(),
    )
    rubric_id = rubric_response.json()["id"]

    extracted_answers = iter(
        [
            {
                "text": (
                    "Binary search on a sorted array checks the middle element and "
                    "keeps halving the remaining range. The complexity is O(log n)."
                ),
                "page_count": 2,
            },
            {
                "text": (
                    "Binary search on a sorted array checks the middle element and "
                    "keeps halving the remaining range. The complexity is O(log n)."
                ),
                "page_count": 2,
            },
        ]
    )

    def fake_extract_submission_content(_path):
        return next(extracted_answers)

    def fake_grade_answer(answer_text, _rubric):
        return {
            "status": "graded",
            "score_breakdown": [
                {
                    "criterion": "Core idea",
                    "awarded_marks": 6,
                    "max_marks": 6,
                    "reason": "Student explained the divide-and-conquer approach well.",
                },
                {
                    "criterion": "Complexity",
                    "awarded_marks": 4,
                    "max_marks": 4,
                    "reason": "Student included O(log n).",
                },
            ],
            "total_marks": 10,
            "feedback": "Strong answer.",
            "missing_points": [],
            "summary": answer_text[:40],
            "confidence": 0.86,
        }

    monkeypatch.setattr(
        "app.services.pdf_service.extract_submission_content",
        fake_extract_submission_content,
    )
    monkeypatch.setattr(
        "app.services.pdf_service.grade_answer",
        fake_grade_answer,
    )

    manifest = {
        "student-a.pdf": {
            "student_identifier": "A-001",
            "exam_name": "Algorithms Midterm",
            "cohort_name": "CSE-2026",
        },
        "student-b.pdf": {
            "student_identifier": "B-001",
            "exam_name": "Algorithms Midterm",
            "cohort_name": "CSE-2026",
        },
    }

    upload_response = client.post(
        "/upload/bulk",
        headers=instructor_headers,
        data={
            "rubric_id": str(rubric_id),
            "manifest_json": json.dumps(manifest),
            "auto_grade": "true",
        },
        files=[
            ("files", ("student-a.pdf", sample_pdf_bytes, "application/pdf")),
            ("files", ("student-b.pdf", sample_pdf_bytes, "application/pdf")),
        ],
    )

    assert upload_response.status_code == 201
    upload_body = upload_response.json()
    assert upload_body["processed_count"] == 2
    assert upload_body["job"]["status"] == "completed"
    assert all(file["status"] == "graded" for file in upload_body["files"])
    assert all(file["processing_job_id"] == upload_body["job"]["id"] for file in upload_body["files"])

    queue_response = client.get("/review-queue", headers=ta_headers)
    assert queue_response.status_code == 200
    queue_body = queue_response.json()
    assert queue_body["count"] == 2
    assert queue_body["files"][0]["review_priority"] >= queue_body["files"][1]["review_priority"]
    assert queue_body["files"][0]["artifacts"]

    next_review_response = client.get("/review-queue/next", headers=ta_headers)
    assert next_review_response.status_code == 200
    next_review_body = next_review_response.json()
    assert next_review_body["review_status"] == "pending"
    assert next_review_body["pipeline_trace"]

    artifact_list_response = client.get(
        f"/files/{next_review_body['id']}/artifacts",
        headers=ta_headers,
    )
    assert artifact_list_response.status_code == 200
    artifact_list_body = artifact_list_response.json()
    assert artifact_list_body["count"] >= 1

    first_artifact_id = artifact_list_body["artifacts"][0]["id"]
    artifact_file_response = client.get(
        f"/artifacts/{first_artifact_id}",
        headers=ta_headers,
    )
    assert artifact_file_response.status_code == 200
    assert artifact_file_response.headers["content-type"] == "image/png"

    pipeline_response = client.get(
        f"/files/{next_review_body['id']}/pipeline",
        headers=ta_headers,
    )
    assert pipeline_response.status_code == 200
    stages = [event["stage"] for event in pipeline_response.json()["pipeline_trace"]]
    assert "ocr" in stages
    assert "artifacts" in stages
    assert "grading" in stages

    plagiarism_response = client.get(
        "/plagiarism/flags?threshold=0.6",
        headers=ta_headers,
    )
    assert plagiarism_response.status_code == 200
    plagiarism_body = plagiarism_response.json()
    assert plagiarism_body["count"] == 2
    assert all(file["plagiarism_score"] >= 0.6 for file in plagiarism_body["files"])

    first_file_id = upload_body["files"][0]["id"]
    review_response = client.patch(
        f"/files/{first_file_id}/review",
        headers=ta_headers,
        json={
            "review_status": "approved",
            "review_notes": "Looks good after TA review.",
        },
    )
    assert review_response.status_code == 200
    assert review_response.json()["file"]["review_status"] == "approved"

    rubric_files_response = client.get(
        f"/rubrics/{rubric_id}/files",
        headers=ta_headers,
    )
    assert rubric_files_response.status_code == 200
    assert len(rubric_files_response.json()) == 2

    jobs_response = client.get("/jobs", headers=ta_headers)
    assert jobs_response.status_code == 200
    assert jobs_response.json()[0]["id"] == upload_body["job"]["id"]

    job_detail_response = client.get(
        f"/jobs/{upload_body['job']['id']}",
        headers=ta_headers,
    )
    assert job_detail_response.status_code == 200
    assert job_detail_response.json()["processed_files"] == 2

    stats_response = client.get("/stats", headers=ta_headers)
    assert stats_response.status_code == 200
    stats_body = stats_response.json()
    assert stats_body["total_uploaded_files"] == 2
    assert stats_body["plagiarism_flagged_files"] == 2
    assert stats_body["rubric_count"] == 1
