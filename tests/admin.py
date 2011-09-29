# -*- coding: utf-8 -*-
import unittest
from flask import Flask
from flaskext.testing import TestCase
from flask_dashed.admin import Admin, AdminModule


class DashedTestCase(TestCase):

    def create_app(self):
        app = Flask(__name__)
        self.admin = Admin(app)
        return app


class AdminTest(DashedTestCase):

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
        self.admin.register_node('/first-node', 'first_node', 'first node')
        self.assertEqual(len(self.admin.registered_nodes), 1)

    def test_register_node_wrong_parent(self):
        self.assertRaises(
            Exception,
            self.admin.register_node,
            'first_node', 'first node', parent='undifined'
        )

    def test_register_node_with_parent(self):
        parent = self.admin.register_node('/parent', 'first_node',
            'first node')
        child = self.admin.register_node('/child', 'child_node', 'child node',
            parent='first_node')
        self.assertEqual(len(self.admin.registered_nodes), 2)
        self.assertEqual(parent, child.parent)
        self.assertEqual(child.url_path, '/parent/child')

    def test_navigation(self):
        self.admin.register_node('/root', 'first_root_node', 'first node')
        self.admin.register_node('/child', 'first_child_node', 'child node',
            parent='first_root_node')
        self.admin.register_node('/second', 'second_root_node', 'second node')

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

    def test_get_full_path_for_enpoint(self):
        parent = self.admin.register_node('/root', 'first_root_node',
            'first node')
        self.admin.register_node('/child', 'first_child_node', 'child node',
            parent='first_root_node')
        self.assertEqual(
            self.admin.get_parents_for_path(
                'first_root_node.first_child_node'),
            [parent]
        )

    def test_get_full_path_for_enpoint_two_levels(self):
        parent = self.admin.register_node('/root', 'first_root_node',
            'first node')
        child = self.admin.register_node('/child', 'first_child_node',
            'child node', parent='first_root_node')
        self.admin.register_node('/child', 'second_child_node', 'child node',
            parent=child.path)
        self.assertEqual(
            self.admin.get_parents_for_path(
                'first_root_node.first_child_node.second_child_node'),
            [parent, child]
        )


if __name__ == '__main__':
    unittest.main()
