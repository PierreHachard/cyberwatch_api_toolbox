"""Test file for cbw_api.py"""

import vcr  # pylint: disable=import-error
import pytest  # pylint: disable=import-error
from cbw_api_toolbox.cbw_api import CBWApi

# To generate a new vcr cassette:
# - DO NOT CHANGE THE API_URL
# - Add your local credentials API_KEY and SECRET_KEY
# - Execute the test a first time, it should generate the cassette
# - Remove your credentials
# - relaunch the test. everything should work.

API_KEY = ''
SECRET_KEY = ''
API_URL = 'https://localhost'


class TestCBWApi:

    """Test for class CBWApi"""

    def test_ping(self):  # pylint: disable=no-self-use
        """Tests for method ping"""

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/ping_ok.yaml'):
            response = CBWApi(API_URL, API_KEY, SECRET_KEY).ping()
            assert response is True

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/ping_without_secret_key.yaml'):
            response = CBWApi(API_URL, API_KEY, '').ping()
            assert response is False

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/ping_without_api_key.yaml'):
            response = CBWApi(API_URL, '', SECRET_KEY).ping()
            assert response is False

        with pytest.raises(SystemExit) as exc:
            CBWApi('', API_KEY, SECRET_KEY).ping()
        assert exc.value.code == -1

    @staticmethod
    def test_servers():
        """Tests for servers method"""

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/servers_ok.yaml'):

            validate_server = "cbw_object(id=2, hostname='cyberwatch-esxi.localdomain', description=None, \
last_communication='2020-07-28T15:02:08.000+02:00', reboot_required=None, updates_count=0, boot_at=None, category='hypervisor', \
created_at='2020-07-28T15:02:05.000+02:00', cve_announcements_count=0, prioritized_cve_announcements_count=0, \
status='server_update_comm_fail', os=cbw_object(key='vmware_esxi_7_0', name='VMware ESXi 7.0', arch='x86_64', \
eol='2025-04-02T02:00:00.000+02:00', short_name='ESXi 7.0', type='Os::Vmware'), environment=cbw_object(id=2, name='Medium', \
confidentiality_requirement='confidentiality_requirement_medium', integrity_requirement='integrity_requirement_medium', \
availability_requirement='availability_requirement_medium'), groups=[], compliance_groups=[])"

            params = {'page': '1'}
            response = CBWApi(API_URL, API_KEY, SECRET_KEY).servers(params)
            assert isinstance(response, list) is True
            assert str(response[0]) == validate_server

    @staticmethod
    def test_server():
        """Tests for server method"""

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/server_ok.yaml'):
            response = CBWApi(API_URL, API_KEY, SECRET_KEY).server('3')
            assert response.category == 'server'
            assert response.cve_announcements[0].cve_code == 'CVE-2019-14869'

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/server_failed.yaml'):
            response = CBWApi(API_URL, API_KEY, SECRET_KEY).server('wrong_id')
            assert response is None

    @staticmethod
    def test_delete_server():
        """Tests for method delete_server"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        response = client.delete_server(None)
        assert response is False

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_server_without_server_id.yaml'):
            response = client.delete_server('wrong id')
            assert response is False

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_server_with_server_id.yaml'):
            response = client.delete_server('6')
            assert response is True

    @staticmethod
    def test_update_server():
        """Tests for server method"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        info = {'groups': [13, 12]}
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_server.yaml'):
            response = client.update_server('6', info)
            assert response is True

            response = client.update_server('', info)
            assert response is False

            response = client.update_server(None, info)
            assert response is False

            info = {'groups': [None], 'compliance_groups': [None]}
            with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_server_with_group_none.yaml'):
                response = client.update_server('6', info)
                assert response is True

    @staticmethod
    def test_agents():
        """Tests for method agents"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/agents.yaml'):
            params = {'page': '1'}

            servers_validate = [
                'cbw_object(id=4, server_id=3, node_id=1, version=None, \
remote_ip=None, last_communication=None)',
                "cbw_object(id=5, server_id=10, node_id=2, version='9', \
remote_ip='12.34.56.78', last_communication=None)",
                "cbw_object(id=6, server_id=30, node_id=2, version='9', \
remote_ip='12.34.56.78', last_communication=None)",
                "cbw_object(id=7, server_id=3, node_id=2, version='7', \
remote_ip='12.34.56.78', last_communication=None)"]

            response = client.agents(params)
            assert isinstance(response, list) is True
            assert str(response[0]) == servers_validate[0]
            assert str(response[1]) == servers_validate[1]
            assert str(response[2]) == servers_validate[2]
            assert str(response[3]) == servers_validate[3]

    @staticmethod
    def test_agent():
        """Tests for method agent"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/agent.yaml'):
            response = client.agent('4')

            assert str(response) == "cbw_object(id=4, server_id=3, node_id=1, \
version=None, remote_ip=None, last_communication=None)"

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/agent_wrong_id.yaml'):
            response = client.agent('wrong_id')

            assert response is None

    @staticmethod
    def test_delete_agent():
        """Tests for method delete_agent"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_agent.yaml'):
            response = client.delete_agent('5')

            assert response is True

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_agent_wrong_id.yaml'):
            response = client.delete_agent('wrong_id')

            assert response is False

    @staticmethod
    def test_remote_accesses():
        """Tests for method remote_accesses"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        remote_accesses_validate = [
            "cbw_object(id=22, type='CbwRam::RemoteAccess::Ssh::WithPassword', address='10.0.2.15', \
port=22, is_valid=False, last_error='Connection refused - connect(2) for 10.0.2.15:22', server_id=None, node_id=1)",
            "cbw_object(id=23, type='CbwRam::RemoteAccess::Ssh::WithPassword', address='server02.example.com', \
port=22, is_valid=False, last_error='getaddrinfo: Name or service not known', server_id=None, node_id=1)",
            "cbw_object(id=25, type='CbwRam::RemoteAccess::Ssh::WithPassword', address='10.0.2.16', \
port=22, is_valid=False, last_error='No route to host - connect(2) for 10.0.2.16:22', server_id=None, node_id=1)"]

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/remote_accesses.yaml'):
            params = {'page': '1'}
            response = client.remote_accesses(params)

            assert isinstance(response, list) is True
            assert str(response[0]) == remote_accesses_validate[0], str(response[1]) == remote_accesses_validate[2]
            assert response[2].type == 'CbwRam::RemoteAccess::Ssh::WithPassword'

    @staticmethod
    def test_create_remote_access():
        """Tests for method remote_access"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        info = {
            'type': 'CbwRam::RemoteAccess::Ssh::WithPassword',
            'address': 'X.X.X.X',
            'port': '22',
            'login': 'loginssh',
            'password': 'passwordssh',
            'key': '',
            'node_id': '1',
            'server_groups': 'test, production',
            'priv_password': '',
            'auth_password': '',
        }

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/create_remote_access.yaml'):
            response = client.create_remote_access(info)

            assert response.address == 'X.X.X.X', response.server_groups == ['test', 'production']
            assert response.type == 'CbwRam::RemoteAccess::Ssh::WithPassword', response.login == 'loginssh'

        info['address'] = ''

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/create_remote_access_failed_without_address.yaml'):
            response = client.create_remote_access(info)

            assert response is False

    @staticmethod
    def test_remote_access():
        """Tests for method remote_access"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/remote_access.yaml'):
            response = client.remote_access('15')

            assert response.address == 'X.X.X.X', response.server_groups == ['test', 'production']
            assert response.type == 'CbwRam::RemoteAccess::Ssh::WithPassword', response.login == 'loginssh'

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/remote_access_wrong_id.yaml'):
            response = client.remote_access('wrong_id')

            assert response is None

    @staticmethod
    def test_delete_remote_access():
        """Tests for method delete_remote_access"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_remote_access.yaml'):
            response = client.delete_remote_access('15')

            assert response is True

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_remote_access_wrong_id.yaml'):
            response = client.delete_remote_access('wrong_id')

            assert response is False

    @staticmethod
    def test_update_remote_access():
        """Tests for update remote method"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        info = {
            'type': 'CbwRam::RemoteAccess::Ssh::WithPassword',
            'address': '10.10.10.228',
            'port': '22',
            'login': 'loginssh',
            'password': 'passwordssh',
            'key': '',
            'node': 'master',
        }

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_remote_access.yaml'):
            response = client.update_remote_access('15', info)

            assert response.address == '10.10.10.228', response.type == 'CbwRam::RemoteAccess::Ssh::WithPassword'

        info['address'] = '10.10.11.228'

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_remote_access_id_none.yaml'):
            response = client.update_remote_access(None, info)

            assert response is False

        info['type'] = ''

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_remote_access_without_type.yaml'):
            response = client.update_remote_access('15', info)

            assert response.type == 'CbwRam::RemoteAccess::Ssh::WithPassword'

    @staticmethod
    def test_cve_announcement():
        """Tests for method cve_announcement"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/cve_announcement.yaml'):
            response = client.cve_announcement('CVE-2017-0146')
            assert response.cve_code == "CVE-2017-0146"

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/cve_announcement_failed.yaml'):
            response = client.cve_announcement('wrong_id')

            assert response is None

    @staticmethod
    def test_group():
        """Tests for method groups"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        groups_validate = [
            "cbw_object(id=12, name='production', description=None, color='#12AFCB')",
            "cbw_object(id=13, name='Development', description=None, color='#12AFCB)"]

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/groups.yaml'):
            response = client.groups()

            assert str(response[0]) == groups_validate[0], str(response[1]) == groups_validate[1]

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/group.yaml'):
            response = client.group('12')

            assert str(response) == groups_validate[0]

        params = {
            "name": "test",
            "description": "test description",
        }

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/create_group.yaml'):
            response = client.create_group(params)

            assert response.name == "test", response.description == "test description"

        params["name"] = "test_change"

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_group.yaml'):
            response = client.update_group('12', params)

            assert response.name == "test_change"

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_group.yaml'):
            response = client.delete_group('12')

            assert response.name == "test_change"

    @staticmethod
    def test_deploy():
        """Tests for method test_deploy_remote_access"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/test_deploy.yaml'):
            response = client.test_deploy_remote_access('15')

            assert str(response) == "cbw_object(id=15, type='CbwRam::RemoteAccess::Ssh::WithPassword', \
address='10.10.11.228', port=22, is_valid=None, last_error='Net::SSH::ConnectionTimeout', server_id=None, node_id=1)"

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/test_deploy_failed.yaml'):
            response = client.test_deploy_remote_access('wrong_id')

            assert response is None

    @staticmethod
    def test_users():
        """Tests for method users"""

        params = {'auth_provider': 'local_password'}
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/users.yaml'):
            response = CBWApi(API_URL, API_KEY, SECRET_KEY).users(params)

            assert str(response[0]) == "cbw_object(id=1, login='daniel@cyberwatch.fr', email='daniel@cyberwatch.fr', \
name='', firstname='', locale='fr', auth_provider='local_password', description='', server_groups=[])"

    @staticmethod
    def test_user():
        """Tests for method user"""

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/user.yaml'):
            response = CBWApi(API_URL, API_KEY, SECRET_KEY).user('1')

            assert str(response) == "cbw_object(id=1, login='daniel@cyberwatch.fr', email='daniel@cyberwatch.fr', \
name='', firstname='', locale='fr', auth_provider='local_password', description='', server_groups=[])"

    @staticmethod
    def test_cve_announcements():
        """Tests for method cve_announcements()"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)
        params = {
            'page': '1'
        }
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/cve_announcements.yaml'):
            response = client.cve_announcements(params)

        assert response[0].cve_code == 'CVE-2015-8158', response[10].cve_code == 'CVE-2015-8139'

    @staticmethod
    def test_update_cve_announcement():
        """Tests for method update_cve_announcement()"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)
        cve_code = 'CVE-2019-16768'
        params = {
            'score_custom': '7',
            'access_complexity': 'access_complexity_low',
            'access_vector': 'access_vector_adjacent_network',
            'availability_impact': 'availability_impact_none',
            'confidentiality_impact': 'confidentiality_impact_low',
            'integrity_impact': 'integrity_impact_low',
            'privilege_required': 'privilege_required_none',
            'scope': 'scope_changed',
            'user_interaction': 'user_interaction_required',
        }
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_cve_announcement.yaml'):
            response = client.update_cve_announcement(cve_code, params)

        assert response.score_custom == 7.0, response.cvss_custom.scope == 'scope_changed'

    @staticmethod
    def test_delete_cve_announcement():
        """Tests for method delete_cve_announcement()"""

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)
        cve_code = 'CVE-2019-16768'
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_cve_announcement.yaml'):
            response = client.delete_cve_announcement(cve_code)

        assert response.cve_code == 'CVE-2019-16768'

    @staticmethod
    def test_nodes():
        """Tests for method nodes()"""

        node_validate = [
            "cbw_object(id=1, name='master', created_at='2019-11-08T15:06:11.000+01:00', \
updated_at='2019-12-18T14:34:09.000+01:00')",
            "cbw_object(id=1, name='master', created_at='2019-11-08T15:06:11.000+01:00', \
updated_at='2019-12-16T14:17:29.000+01:00')"]

        client = CBWApi(API_URL, API_KEY, SECRET_KEY)
        params = {'page': '1'}
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/nodes.yaml'):
            response = client.nodes(params)

        assert str(response[0]) == node_validate[0]

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/node.yaml'):
            response = client.node('1')

            assert str(response) == node_validate[1]

        params = {'new_id': '1'}
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_node.yaml'):

            response = client.delete_node('2', params)

            assert response.id == 2

    @staticmethod
    def test_host():
        """Tests for method hosts"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        hosts_validate = [
            "cbw_object(id=8, target='172.18.0.13', category='linux', \
hostname='bb79e64ccd6e.dev_default', cve_announcements_count=0, created_at='2019-11-14T11:58:50.000+01:00', \
updated_at='2019-12-16T16:45:42.000+01:00', node_id=1, server_id=5, status='server_update_init', \
technologies=[], security_issues=[], cve_announcements=[], scans=[])",
            "cbw_object(id=12, target='5.5.5.5', category='linux', hostname=None, cve_announcements_count=0, \
created_at='2019-12-17T14:28:00.000+01:00', updated_at='2019-12-17T14:28:00.000+01:00', node_id=1, \
server_id=7, status='server_update_init', technologies=[], security_issues=[], cve_announcements=[], scans=[])"]

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/hosts.yaml'):
            response = client.hosts()

        assert len(response) == 4, str(response[0]) == hosts_validate[0]

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/host.yaml'):
            response = client.host('12')

            assert str(response) == hosts_validate[1]

        params = {
            "target": "192.168.1.2",
            "node_id": "1"
        }
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/create_host.yaml'):
            response = client.create_host(params)

            assert response.target == "192.168.1.2", response.node_id == 1

        params["category"] = "other"
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_host.yaml'):
            response = client.update_host('1', params)

        assert response.category == "other", response.node_id == 1

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_host.yaml'):
            response = client.delete_host('1')

            assert response.target == '10.10.1.186'

    @staticmethod
    def test_update_server_cve():
        """Tests for server method"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        info = {
            "comment": "test"
        }
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_server_cve.yaml'):
            response = client.update_server_cve('9', "CVE-2019-3028", info)
            assert response.cve_announcements[36].comment == 'test'

        info = {
            "ignored": "true",
            "comment": "test-ignore"
        }
        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_server_cve_ignored.yaml'):
            response = client.update_server_cve('8', "CVE-2020-3962", info)
            assert len(response.cve_announcements) == 12

    @staticmethod
    def test_security_issues():
        """Tests for method security_issues"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        security_issues_validate = [
            "cbw_object(id=1, type=None, sid='', level='level_info', title=None, description=None)",
            "cbw_object(id=2, type=None, sid='', level='level_info', title=None, description=None)",
            "cbw_object(id=3, type=None, sid='', level='level_info', title=None, description=None)"]

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/security_issues.yaml'):
            params = {
                'page': '1'
            }
            response = client.security_issues(params)
            assert isinstance(response, list) is True
            assert str(response[0]) == security_issues_validate[0], str(response[1]) == security_issues_validate[1]

    @staticmethod
    def test_create_security_issue():
        """Tests for method security_issue"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        info = {
            "description": "Test",
            "level": "level_critical",
            "score": "5",
        }

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/create_security_issue.yaml'):
            response = client.create_security_issue(info)

            assert response.level == "level_critical", response.description == "Test"

    @staticmethod
    def test_update_security_issue():
        """Tests for update remote method"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        info = {
            "description": "Test update",
            "level": "level_critical",
            "score": "5",
        }

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_security_issue.yaml'):
            response = client.update_security_issue('2', info)

            assert response.description == "Test update"

        info["level"] = "level_test"

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/update_security_issue_wrong_level.yaml'):
            response = client.update_security_issue("2", info)

            assert response is None

    @staticmethod
    def test_delete_security_issue():
        """Tests for method delete_security_issue"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_security_issue.yaml'):
            response = client.delete_security_issue('1')
            assert str(response) == "cbw_object(id=1, type=None, sid='', level='level_info', \
title=None, description=None, servers=[], cve_announcements=[])"

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/delete_security_issue_wrong_id.yaml'):
            response = client.delete_security_issue('wrong_id')
            assert response is None

    @staticmethod
    def test_fetch_importer_scripts():
        """Tests for method importer"""
        client = CBWApi(API_URL, API_KEY, SECRET_KEY)

        with vcr.use_cassette('spec/fixtures/vcr_cassettes/fetch_importer_script.yaml'):
            response = client.fetch_importer_script('1')
            assert response.version == '47c8367e1c92d50fad8894362f5c09e9bfe65e712aab2d23ffbb61e354e270dd'
