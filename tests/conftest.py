# -*- coding: utf-8 -*-
def pytest_addoption(parser):
    parser.addoption("--username", action="store", help="rackspace username for integration tests")
    parser.addoption("--apikey", action="store", help="rackspace apikey for integration tests")