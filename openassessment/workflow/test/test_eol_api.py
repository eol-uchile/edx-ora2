from openassessment.test_utils import CacheResetTest
import openassessment.workflow.eol_api as workflow_eol_api
import openassessment.workflow.api as workflow_api
import submissions.api as sub_api
from openassessment.workflow.models import AssessmentWorkflow

from mock import patch

STUDENTS = [
    {
        "anonymoususerid__anonymous_user_id": "user01",
        "username" : "user01"
    },
    {
        "anonymoususerid__anonymous_user_id": "user02",
        "username" : "user02"
    },
    {
        "anonymoususerid__anonymous_user_id": "user03",
        "username" : "user03"
    }
]

STUDENTS_DEFAULT_STATUS = [
    {
        "status": "empty",
        "username" : "user01"
    },
    {
        "status": "empty",
        "username" : "user02"
    },
    {
        "status": "empty",
        "username" : "user03"
    }
]

class TestEolApi(CacheResetTest):
    """ Tests Eol Api. """

    @patch('openassessment.workflow.eol_api.get_all_users_enrolled')
    def test_get_students_status(self, get_all_users_enrolled):
        # Students should have default status without submissions
        status = STUDENTS_DEFAULT_STATUS
        get_all_users_enrolled.side_effect = [STUDENTS]
        students_status = workflow_eol_api.get_students_status(
            "test/1/1",
            "ora2-problem"
        )
        self.assertEqual(students_status, status)

        # Create assessments with status. Students status should update
        self._create_workflow_with_status("user01", "test/1/1", "ora2-problem", "training")
        self._create_workflow_with_status("user03", "test/1/1", "ora2-problem", "waiting")
        status[0]["status"] = "training"
        status[2]["status"] = "waiting"
        get_all_users_enrolled.side_effect = [STUDENTS]
        students_status = workflow_eol_api.get_students_status(
            "test/1/1",
            "ora2-problem"
        )
        self.assertEqual(students_status, status)

        # Create a workflow in a different course, same user and item
        # Students Status should be the same
        self._create_workflow_with_status("user01", "other_course", "ora2-problem", "peer")
        get_all_users_enrolled.side_effect = [STUDENTS]
        students_status = workflow_eol_api.get_students_status(
            "test/1/1",
            "ora2-problem"
        )
        self.assertEqual(students_status, status)

        # Create a workflow in the same course, different item
        # Students Status should be the same
        self._create_workflow_with_status("user01", "test/1/1", "other-problem", "done")
        get_all_users_enrolled.side_effect = [STUDENTS]
        students_status = workflow_eol_api.get_students_status(
            "test/1/1",
            "ora2-problem"
        )
        self.assertEqual(students_status, status)


    def _create_workflow_with_status(
            self, student_id, course_id, item_id,
            status, answer="answer", steps=None
    ):
        """
        Create a submission and workflow with a given status.

        Args:
            student_id (unicode): Student ID for the submission.
            course_id (unicode): Course ID for the submission.
            item_id (unicode): Item ID for the submission
            status (unicode): One of acceptable status values (e.g. "peer", "self", "waiting", "done")

        Keyword Arguments:
            answer (unicode): Submission answer.
            steps (list): A list of steps to create the workflow with. If not
                specified the default steps are "peer", "self".

        Returns:
            workflow, submission
        """
        if not steps:
            steps = ["peer", "self"]

        submission = sub_api.create_submission({
            "student_id": student_id,
            "course_id": course_id,
            "item_id": item_id,
            "item_type": "openassessment",
        }, answer)

        workflow = workflow_api.create_workflow(submission['uuid'], steps)
        workflow_model = AssessmentWorkflow.objects.get(submission_uuid=workflow['submission_uuid'])
        workflow_model.status = status
        workflow_model.save()
        return workflow, submission