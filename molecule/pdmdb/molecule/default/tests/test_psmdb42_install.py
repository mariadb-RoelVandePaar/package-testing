import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEB_PACKAGES = ['percona-server-mongodb', 'percona-server-mongodb-server', 'percona-server-mongodb-mongos',
                'percona-server-mongodb-shell', 'percona-server-mongodb-tools', 'percona-server-mongodb-dbg']
RPM_PACKAGES = ['percona-server-mongodb', 'percona-server-mongodb-server', 'percona-server-mongodb-mongos',
                'percona-server-mongodb-shell', 'percona-server-mongodb-tools', 'percona-server-mongodb-debuginfo']
RPM_NEW_CENTOS_PACKAGES = ['percona-server-mongodb', 'percona-server-mongodb-mongos-debuginfo',
                           'percona-server-mongodb-server-debuginfo', 'percona-server-mongodb-shell-debuginfo',
                           'percona-server-mongodb-tools-debuginfo', 'percona-server-mongodb-debugsource']

BINARIES = ['mongo', 'mongod', 'mongos', 'bsondump', 'mongoexport',
            'mongofiles', 'mongoimport', 'mongorestore', 'mongotop', 'mongostat']

PSMDB42_VER = "4.2.2"


def test_mongod_service(host):
    mongod = host.service("mongod")
    assert mongod.is_running


def test_package_script(host):
    with host.sudo():
        result = host.run("/package-testing/package_check.sh psmdb42")
    assert result.rc == 0, result.stderr


def test_version_script(host):
    with host.sudo():
        result = host.run("/package-testing/version_check.sh psmdb42")
    assert result.rc == 0, result.stderr


@pytest.mark.parametrize("package", DEB_PACKAGES)
def test_deb_packages(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB42_VER in pkg.version


# TODO add check that minor version is correct
@pytest.mark.parametrize("package", RPM_PACKAGES)
def test_rpm_packages(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    if float(host.system_info.release) >= 8.0:
        pytest.skip("Only for centos7 tests")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB42_VER in pkg.version


@pytest.mark.parametrize("package", RPM_NEW_CENTOS_PACKAGES)
def test_rpm8_packages(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    if float(host.system_info.release) < 8.0:
        pytest.skip("Only for centos7 tests")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB42_VER in pkg.version


@pytest.mark.parametrize("binary", BINARIES)
def test_binary_version(host, binary):
    cmd = '{} --version|head -n1|grep -c "{}"'.format(binary, PSMDB42_VER)
    result = host.run(cmd)
    assert result.rc == 0, result.stdout
