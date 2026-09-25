from app.schemas import ProcessResponse


def test_process_response():

    response = ProcessResponse(

        status="SUCCESS",

        message="OK",

        processing_time_seconds=4.52,

        total_incidents=5000,

        total_clusters=43,

        total_problem_candidates=8

    )

    assert response.total_incidents == 5000

    assert response.total_clusters == 43