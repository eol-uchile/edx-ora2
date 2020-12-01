"""
EOL Api Upgrades

"""
from django.contrib.auth.models import User
from submissions import api as sub_api
from .models import AssessmentWorkflow

import logging
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

DEFAULT_STATUS = "empty"

def get_students_status(course_id, item_id):
    """
    Workflow status for each student, for a given item in a course.

    Keyword Arguments:
        course_id (unicode): The ID of the course.
        item_id (unicode): The ID of the item in the course.

    Example usage:
        >>> get_students_status("ora2/1/1", "peer-assessment-problem")
        [
            {"username": "user01", "status": "peer"},
            {"username": "user02", "status": "waiting"},
            {"username": "user03", "status": "done"},
            {"username": "user04", "status": "empty"},
        ]
    """
    # Store the generator results in a data structure on memory or disk which you can iterate over again
    submissions = list(sub_api.get_all_submissions(course_id, item_id, 'openassessment'))

    # Get submissions uuid and assessments related (with learner status)
    assessments_uuid = [ s['uuid'] for s in submissions]
    assessments = AssessmentWorkflow.objects.filter(submission_uuid__in=assessments_uuid).values(
        "submission_uuid",
        "status"
    )

    # Link submission uuid with assessment status
    assessments_status = { a["submission_uuid"] : a["status"] for a in assessments }
    # Link assessment status with student_id (anonymous user id)
    submissions_status = { s["student_id"] : assessments_status[s['uuid']] for s in submissions }

    # Get all users enrolled
    users = get_all_users_enrolled(course_id)
    # Generate dict with learner username and submission status if exists (default: DEFAULT_STATUS)
    return [
        {
            "username"  : u["username"],
            "status"    : (submissions_status[u["anonymoususerid__anonymous_user_id"]] 
                            if u["anonymoususerid__anonymous_user_id"] in submissions_status 
                            else DEFAULT_STATUS)
        }
        for u in users
    ]

def get_all_users_enrolled(course_id):
    return User.objects.filter(
        courseenrollment__course_id=course_id,
        courseenrollment__is_active=1,
        anonymoususerid__course_id=course_id
    ).values(
        "anonymoususerid__anonymous_user_id",
        "username"
    ).order_by("username")