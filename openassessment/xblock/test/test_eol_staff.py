from openassessment.xblock.test.base import XBlockHandlerTestCase, scenario
import json
import six.moves.urllib.request  # pylint: disable=import-error
from mock import Mock, patch

STUDENTS_MOCK_STATUS = [
    {
        "status": "empty",
        "username" : "user01"
    },
    {
        "status": "done",
        "username" : "user02"
    },
    {
        "status": "waiting",
        "username" : "user03"
    }
]

class TestEolStaff(XBlockHandlerTestCase):

    @patch('openassessment.workflow.eol_api.get_students_status')
    @scenario('data/staff_grade_scenario.xml', user_id='Bob')
    def test_download_csv(self, xblock, get_students_status):
        get_students_status.side_effect = [ STUDENTS_MOCK_STATUS ]
        # If we're not course staff, we shouldn't see the staff area
        xblock.xmodule_runtime = self._create_mock_runtime(
            xblock.scope_ids.usage_id, False, False, "Bob"
        )
        resp = self.request(xblock, 'download_csv', json.dumps({}))
        self.assertIn("you do not have permission to access the ora staff area", resp.decode('utf-8').lower())

        # # If we ARE course staff, then we should see the debug info
        xblock.xmodule_runtime.user_is_staff = True
        resp = self.request(xblock, 'download_csv', json.dumps({}))
        content = json.loads(resp.decode("utf-8"))
        self.assertEqual(STUDENTS_MOCK_STATUS, content)

    @staticmethod
    def _create_mock_runtime(
            item_id,
            is_staff,
            is_admin,
            anonymous_user_id,
            user_is_beta=False,
            days_early_for_beta=0
    ):
        """
        Internal helper to define a mock runtime.
        """
        mock_runtime = Mock(
            course_id='test_course',
            item_id=item_id,
            anonymous_student_id='Bob',
            user_is_staff=is_staff,
            user_is_admin=is_admin,
            user_is_beta=user_is_beta,
            days_early_for_beta=days_early_for_beta,
            service=lambda self, service: Mock(
                get_anonymous_student_id=lambda user_id, course_id: anonymous_user_id
            )
        )
        return mock_runtime