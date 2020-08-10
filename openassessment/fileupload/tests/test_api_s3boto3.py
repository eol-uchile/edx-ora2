import ddt

from django.test import TestCase
from django.test.utils import override_settings

import boto3
from moto import mock_s3
from mock import patch
from pytest import raises
from openassessment.fileupload import api, exceptions


@ddt.ddt
@override_settings(
    ORA2_FILEUPLOAD_BACKEND='s3boto3',
)
class TestFileUploadService(TestCase):
    @mock_s3
    @override_settings(
        AWS_ACCESS_KEY_ID="foobar",
        AWS_SECRET_ACCESS_KEY="bizbaz",
        FILE_UPLOAD_STORAGE_BUCKET_NAME="mybucket",
    )
    def test_get_upload_url(self):
        conn = boto3.client("s3")
        conn.create_bucket(Bucket="mybucket")
        uploadUrl = api.get_upload_url("foo", "bar")
        self.assertIn("/submissions_attachments/foo", uploadUrl)

    @mock_s3
    @override_settings(
        AWS_ACCESS_KEY_ID="foobar",
        AWS_SECRET_ACCESS_KEY="bizbaz",
        FILE_UPLOAD_STORAGE_BUCKET_NAME="mybucket",
    )
    def test_get_download_url(self):
        conn = boto3.client("s3")
        conn.create_bucket(Bucket="mybucket")
        conn.put_object(
            Bucket="mybucket",
            Key="submissions_attachments/foo",
            Body=b"How d'ya do?"
        )
        downloadUrl = api.get_download_url("foo")
        self.assertIn("/submissions_attachments/foo", downloadUrl)

    @mock_s3
    @override_settings(
        AWS_ACCESS_KEY_ID="foobar",
        AWS_SECRET_ACCESS_KEY="bizbaz",
        FILE_UPLOAD_STORAGE_BUCKET_NAME="mybucket",
    )
    def test_remove_file(self):
        conn = boto3.client("s3")
        conn.create_bucket(Bucket="mybucket")
        conn.put_object(
            Bucket="mybucket",
            Key="submissions_attachments/foo",
            Body=b"Test"
        )
        result = api.remove_file("foo")
        self.assertTrue(result)
        result = api.remove_file("foo")
        self.assertFalse(result)

    def test_get_upload_url_no_bucket(self):
        with raises(exceptions.FileUploadInternalError):
            api.get_upload_url("foo", "bar")

    def test_get_upload_url_no_key(self):
        with raises(exceptions.FileUploadRequestError):
            api.get_upload_url("", "bar")

    @mock_s3
    @override_settings(
        AWS_ACCESS_KEY_ID="foobar",
        AWS_SECRET_ACCESS_KEY="bizbaz",
        FILE_UPLOAD_STORAGE_BUCKET_NAME="mybucket",
    )
    @patch.object(boto3, "client")
    def test_get_upload_url_error(self, mock_s3):
        with raises(exceptions.FileUploadInternalError):
            mock_s3.side_effect = Exception("Oh noes")
            api.get_upload_url("foo", "bar")

    @mock_s3
    @override_settings(
        AWS_ACCESS_KEY_ID="foobar",
        AWS_SECRET_ACCESS_KEY="bizbaz",
        FILE_UPLOAD_STORAGE_BUCKET_NAME="mybucket",
    )
    @patch.object(boto3, "client")
    def test_get_download_url_error(self, mock_s3):
        with raises(exceptions.FileUploadInternalError):
            mock_s3.side_effect = Exception("Oh noes")
            api.get_download_url("foo")
