#!/usr/bin/env python3

import unittest
from selenium import webdriver
from testpack_helper_library.unittests.dockertests import Test1and1Common


class Test1and1ApacheImage(Test1and1Common):
    container_ip = None

    @classmethod
    def setUpClass(cls):
        Test1and1Common.setUpClass()
        Test1and1Common.copy_test_files("testpack/files", "html", "/var/www")

    # <tests to run>

    def test_apache2_installed(self):
        self.assertPackageIsInstalled("apache2")

    def test_apache2_running(self):
        self.assertTrue(
            self.execRun("ps -ef").find('apache2') > -1,
            msg="apache2 not running"
        )

    def test_apache2_ports(self):
        self.assertFalse(
            self.execRun("ls /etc/apache2/ports.conf").find("No such file or directory") > -1,
            msg="/etc/apache2/ports.conf is missing"
        )
        self.assertTrue(
            self.execRun("cat /etc/apache2/ports.conf").find("Listen 8080") > -1,
            msg="ports.conf misconfigured"
        )

    def test_apache2_lock(self):
        result = self.execRun("ls -ld /var/lock/apache2")
        self.assertFalse(
            result.find("No such file or directory") > -1,
            msg="/var/lock/apache2 is missing"
        )
        self.assertEqual(result[0], 'd', msg="/var/lock/apache2 is not a directory")
        self.assertEqual(result[8], 'w', msg="/var/lock/apache2 is not a writable by others")

    def test_apache2_run(self):
        result = self.execRun("ls -ld /var/run/apache2")
        self.assertFalse(
            result.find("No such file or directory") > -1,
            msg="/var/run/apache2 is missing"
        )
        self.assertEqual(result[0], 'd', msg="/var/run/apache2 is not a directory")
        self.assertEqual(result[8], 'w', msg="/var/run/apache2 is not a writable by others")

    def test_apache2_mods_enabled(self):
        result = self.execRun("ls -l /etc/apache2/mods-enabled/rewrite.load")
        self.assertFalse(
            result.find("No such file or directory") > -1,
            msg="/etc/apache2/mods-enabled/rewrite.load is missing"
        )
        self.assertEqual(result[0], 'l', msg="rewrite module not enabled")

    def test_apache2_default_site(self):
        result = self.execRun("cat /etc/apache2/sites-available/000-default.conf")
        self.assertFalse(
            result.find("No such file or directory") > -1,
            msg="/etc/apache2/sites-available/000-default.conf is missing"
        )
        self.assertTrue(
            result.find("VirtualHost *:8080") > -1,
            msg="Missing or incorrect VirtualHost entry"
        )
        self.assertTrue(
            result.find("AllowOverride All") > -1,
            msg="Missing AllowOverride All"
        )

    def test_docker_logs(self):
        expected_log_lines = [
            "Executing hook /hooks/entrypoint-pre.d/19_doc_root_setup",
            "Executing hook /hooks/entrypoint-pre.d/20_ssl_setup",
            "Checking if /var/www/html is empty",
            "Log directory exists"
        ]
        container_logs = self.container.logs().decode('utf-8')
        for expected_log_line in expected_log_lines:
            self.assertTrue(
                container_logs.find(expected_log_line) > -1,
                msg="Docker log line missing: %s from (%s)" % (expected_log_line, container_logs)
            )

    def test_apache2_get(self):
        driver = self.getChromeDriver()
        driver.get("http://%s:8080/test.html" % Test1and1Common.container_ip)
        self.assertEqual('Success', driver.title)
        #self.screenshot("open")

        # </tests to run>

if __name__ == '__main__':
    unittest.main(verbosity=1)
