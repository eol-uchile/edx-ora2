import json

from xblock.core import XBlock
from webob import Response

from openassessment.workflow import eol_api as workflow_api_eol
from .staff_area_mixin import require_course_staff

class EolStaffMixin:
    """
    Eol Upgrades on Staff View
    """
    @XBlock.handler
    @require_course_staff("STAFF_AREA")
    def download_csv(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Retrieve the students status.

        Returns:
            a list that contains dicts with keys
            "student" and "status"
            [
                {"username": "user01", "status": "peer"},
                {"username": "user02", "status": "waiting"},
                {"username": "user03", "status": "done"},
                {"username": "user04", "status": "empty"},
            ]
        """
        student_item = self.get_student_item_dict()
        student_status = workflow_api_eol.get_students_status(
            course_id=student_item['course_id'],
            item_id=student_item['item_id']
        )
        return Response(json.dumps(student_status), content_type='application/json', charset='UTF-8')