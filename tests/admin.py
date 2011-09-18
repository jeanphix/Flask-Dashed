# -*- coding: utf-8 -*-
import unittest
from flask import Flask
from flaskext.testing import TestCase
from flask_dashed.admin import Admin, AdminModule


class AdminTest(TestCase):
    def create_app(self):
        app = Flask(__name__)
        self.admin = Admin(app)
        return app

    def test_main_dashboard_view(self):
        r = self.client.get(self.admin.navigation[0]['url'])
        self.assertEqual(r.status_code, 200)
        self.assertIn('Hello world', r.data)

    def test_register_admin_module(self):
        self.assertRaises(
            NotImplementedError,
            self.admin.register_module,
            AdminModule, '/my-module', 'my_module', 'my module title'
        )

    def test_register_node(self):
        node = self.admin.register_node('first_node', 'first node')
        self.assertEqual(len(self.admin.registered_nodes), 1)

    def test_register_node_wrong_parent(self):
        self.assertRaises(
            Exception,
            self.admin.register_node,
            'first_node', 'first node', parent='undifined'
        )

    def test_register_node_with_parent(self):
        node = self.admin.register_node('first_node', 'first node')
        node = self.admin.register_node('child_node', 'child node',
            parent='first_node')
        self.assertEqual(len(self.admin.registered_nodes), 2)

    def test_navigation(self):
        node = self.admin.register_node('first_root_node', 'first node')
        node = self.admin.register_node('first_child_node', 'child node',
            parent='first_root_node')
        node = self.admin.register_node('second_root_node', 'second node')

        values = [{
            'url': '/admin/', 'children': [], 'class': 'main-dashboard',
            'short_title': 'dashboard', 'title': 'Go to main dashboard'
        }, {
            'url': None, 'children': [{
                'url': None, 'children': [],
                'class': 'first_root_node.first_child_node',
                'short_title': 'child node', 'title': 'Go to child node'
            }], 'class': 'first_root_node', 'short_title': 'first node',
            'title': 'Go to first node'
        }, {
            'url': None, 'children': [], 'class': 'second_root_node',
            'short_title': 'second node', 'title': 'Go to second node'
        }]

        self.assertEqual(len(self.admin.registered_nodes), 3)
        self.assertEqual(self.admin.navigation, values)


if __name__ == '__main__':
    unittest.main()
