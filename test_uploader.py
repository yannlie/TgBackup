#!/usr/bin/env python3
"""
单元测试
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tg_to_onedrive import Config, OneDriveUploader, UploadFilter


class TestConfig(unittest.TestCase):
    """测试配置管理"""

    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'test_config.json')

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.test_dir)

    def test_load_config_success(self):
        """测试加载配置成功"""
        config_data = {
            'client_id': 'test_id',
            'client_secret': 'test_secret',
            'refresh_token': 'test_token',
            'base_path': '/test'
        }

        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)

        config = Config(self.config_file)
        self.assertEqual(config.get('client_id'), 'test_id')
        self.assertEqual(config.get('base_path'), '/test')

    def test_load_config_missing_file(self):
        """测试配置文件不存在"""
        with self.assertRaises(FileNotFoundError):
            Config('nonexistent.json')

    def test_load_config_missing_fields(self):
        """测试配置文件缺少必需字段"""
        incomplete_config = {'client_id': 'test_id'}

        with open(self.config_file, 'w') as f:
            json.dump(incomplete_config, f)

        with self.assertRaises(ValueError):
            Config(self.config_file)

    def test_save_config(self):
        """测试保存配置"""
        config_data = {
            'client_id': 'test_id',
            'client_secret': 'test_secret',
            'refresh_token': 'test_token'
        }

        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)

        config = Config(self.config_file)
        config.set('new_field', 'new_value')
        config.save()

        # 重新加载验证
        with open(self.config_file, 'r') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data['new_field'], 'new_value')


class TestUploadFilter(unittest.TestCase):
    """测试上传过滤器"""

    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.config = Mock()

    def tearDown(self):
        """测试后清理"""
        os.rmdir(self.test_dir)

    def test_filter_by_extension(self):
        """测试按扩展名过滤"""
        self.config.get = Mock(side_effect=lambda key, default=None: {
            'excluded_extensions': ['.txt', '.log'],
            'min_file_size': 0,
            'max_file_size': 1024 * 1024
        }.get(key, default))

        upload_filter = UploadFilter(self.config)

        # 创建测试文件
        test_file = Path(self.test_dir) / 'test.txt'
        test_file.write_text('test')

        should_upload, reason = upload_filter.should_upload(test_file)
        self.assertFalse(should_upload)
        self.assertIn('文件类型被排除', reason)

    def test_filter_by_size(self):
        """测试按大小过滤"""
        self.config.get = Mock(side_effect=lambda key, default=None: {
            'excluded_extensions': [],
            'min_file_size': 1024,
            'max_file_size': 1024 * 1024
        }.get(key, default))

        upload_filter = UploadFilter(self.config)

        # 创建小文件
        small_file = Path(self.test_dir) / 'small.dat'
        small_file.write_bytes(b'x' * 100)

        should_upload, reason = upload_filter.should_upload(small_file)
        self.assertFalse(should_upload)
        self.assertIn('文件太小', reason)

    def test_filter_allow_upload(self):
        """测试允许上传"""
        self.config.get = Mock(side_effect=lambda key, default=None: {
            'excluded_extensions': [],
            'min_file_size': 0,
            'max_file_size': 1024 * 1024
        }.get(key, default))

        upload_filter = UploadFilter(self.config)

        # 创建合适的文件
        good_file = Path(self.test_dir) / 'good.mp4'
        good_file.write_bytes(b'x' * 10000)

        should_upload, reason = upload_filter.should_upload(good_file)
        self.assertTrue(should_upload)
        self.assertIsNone(reason)


class TestOneDriveUploader(unittest.TestCase):
    """测试 OneDrive 上传器"""

    def setUp(self):
        """测试前准备"""
        self.config = Mock()
        self.config.get = Mock(side_effect=lambda key, default=None: {
            'client_id': 'test_id',
            'client_secret': 'test_secret',
            'refresh_token': 'test_token',
            'base_path': '/test',
            'chunk_size': 10
        }.get(key, default))

    @patch('tg_to_onedrive.requests.Session')
    def test_uploader_initialization(self, mock_session):
        """测试上传器初始化"""
        uploader = OneDriveUploader(self.config)

        self.assertIsNotNone(uploader.session)
        self.assertEqual(uploader.upload_stats['total'], 0)
        self.assertEqual(uploader.upload_stats['success'], 0)

    @patch('tg_to_onedrive.requests.Session')
    def test_get_access_token(self, mock_session):
        """测试获取 access token"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'new_token',
            'expires_in': 3600
        }
        mock_response.raise_for_status = Mock()

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        uploader = OneDriveUploader(self.config)
        token = uploader._get_access_token()

        self.assertEqual(token, 'new_token')
        self.assertIsNotNone(uploader.access_token)

    def test_get_stats(self):
        """测试获取统计信息"""
        uploader = OneDriveUploader(self.config)
        uploader.upload_stats['total'] = 10
        uploader.upload_stats['success'] = 8
        uploader.upload_stats['failed'] = 2

        stats = uploader.get_stats()

        self.assertEqual(stats['total'], 10)
        self.assertEqual(stats['success'], 8)
        self.assertEqual(stats['failed'], 2)


if __name__ == '__main__':
    unittest.main()
