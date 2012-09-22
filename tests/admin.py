# -*- coding: utf-8 -*-
import unittest
from flask import Flask
from flask.ext.testing import TestCase
from flask_dashed.admin import Admin, AdminModule


class DashedTestCase(TestCase):

    def create_app(self):
        app = Flask(__name__)
        self.admin = Admin(app)
        return app


class AdminTest(DashedTestCase):

    def test_main_dashboard_view(self):
        r = self.client.get(self.admin.root_nodes[0].url)
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
        self.assertEqual(len(self.admin.root_nodes), 2)

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
            parent=parent)
        self.assertEqual(len(self.admin.root_nodes), 2)
        self.assertEqual(parent, child.parent)
        self.assertEqual(child.url_path, '/parent/child')
        self.assertEqual(
            child.parents,
            [parent]
        )

    def test_children_two_levels(self):
        parent = self.admin.register_node('/root', 'first_root_node',
            'first node')
        child = self.admin.register_node('/child', 'first_child_node',
            'child node', parent=parent)
        second_child = self.admin.register_node('/child', 'second_child_node',
            'child node', parent=child)
        self.assertEqual(
            parent.children, [child]
        )
        self.assertEqual(
            child.children, [second_child]
        )
        self.assertEqual(
            child.parent, parent
        )
        self.assertEqual(
            second_child.parent, child
        )


if __name__ == '__main__':
    unittest.main()
