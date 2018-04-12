#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: cyberark_password

short_description: This is a sample module to create password in CyberARK Vault or get if already exits.

version_added: "2.4"

description:
    - "This module get a password in CyberARK Vault, this module was created to get integration with CyberARK, some adjust can be required"

author:
    - Rudnei Bertol Junior (@rbertol) <rudneibertol@gmail.com>
'''

EXAMPLES = '''
- name: create account in cyberark if this account not exists.
  cyberark_password:
    name: 'pass_acme_root'
    safe: 'ACME'
    platform: 'ssh_user_noch'
    address: 'acme.local
    cyberark_username: 'user_cyberark_access'
    cyberark_password: "pass_cyberark_access"
    cyberark_host: "cyberark.acme.com.br'
    description: "small description of password"
'''

RETURN = '''
message:
    description: The output message with sucessfully password created or already exists.
user_password:
    description: Password saved in CyberARK..
'''

import json, requests, sys
import string
import random
from ansible.module_utils.basic import *

def randompassword():
    chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
    size= 1
    return ''.join(random.choice(chars) for x in range(size,18))

def run_module():

    module_args = dict(
        name=dict(type='str', required=True),
        safe=dict(type='str', required=True),
        platform=dict(type='str', required=True),
        address=dict(type='str', required=True),
        cyberark_host=dict(type='str', required=True),
        cyberark_username=dict(type='str', required=True),
        cyberark_password=dict(type='str', required=True),
        description=dict(type='str', required=False)
    )

    result = dict(
        changed='False',
        message='',
        password='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        return result

    api='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/auth/Cyberark/CyberArkAuthenticationService.svc/Logon'
    headers={'content-type': 'application/json'}
    payload={'username':module.params['cyberark_username'],'password':module.params['cyberark_password'],'useRadiusAuthentication':'false','connectionNumber':'1'}
    response=requests.post(api, data=json.dumps(payload), headers=headers, verify=False)
    token=response.json()
    auth=token['CyberArkLogonResult']

    api='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/PIMServices.svc/Accounts?Keywords='+module.params['name']+'&Safe='+module.params['safe']
    headers={'content-type': 'application/json', 'Authorization': auth}
    response=requests.get(api, headers=headers, verify=False)
    account=response.json()
    count_exist=account['Count']

    if count_exist >= 1:
        getid=account['accounts'][0]['AccountID']
        api='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/PIMServices.svc/Accounts/'+getid+'/Credentials'
        headers={'content-type': 'application/json', 'Authorization': auth}
        response=requests.get(api, headers=headers, verify=False)
        criamaquina=response.status_code
        password=response.text
        message='Account '+module.params['name']+' already exist.'
        changed=False

    if count_exist == 0:
        password=randompassword()
        url='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/PIMServices.svc/Account'
        headers={'content-type': 'application/json', 'Authorization': auth}
        payload={'account' : {'safe':module.params['safe'],'platformID':module.params['platform'],'address':module.params['address'],'accountName':module.params['name'],'password':password,'username':module.params['name'],'disableAutoMgmt':'true','disableAutoMgmtReason':module.params['description']}}
        response=requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        criamaquina=response.status_code
        changed=True
        message='Account '+module.params['name']+' created successfully.'

    api='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/auth/Cyberark/CyberArkAuthenticationService.svc/Logoff'
    headers={'content-type': 'application/json', 'Authorization': auth}
    response=requests.post(api, data=json.dumps(payload), headers=headers, verify=False)

    result['changed']=changed
    result['message']=message
    result['password']=password

    if criamaquina == 400:
        module.fail_json(msg='The request could not be understood by the server due to incorrect syntax.')
    module.exit_json(**result)
	
    if criamaquina == 401:
        module.fail_json(msg='The request requires user authentication.')
    module.exit_json(**result)
	
    if criamaquina == 403:
        module.fail_json(msg='The server received and understood the request, but will not fulfill it. Authorization will not help and the request MUST NOT be repeated.')
    module.exit_json(**result)
	
    if criamaquina == 404:
        module.fail_json(msg='The server did not find anything that matches the Request-URI. No indication is given of whether the condition is temporary or permanent.')
    module.exit_json(**result)
	
    if criamaquina == 409:
        module.fail_json(msg='The request could not be completed due to a conflict with the current state of the resource.')
    module.exit_json(**result)

    if criamaquina == 500:
        module.fail_json(msg='The server encountered an unexpected condition which prevented it from fulfilling the request.')
    module.exit_json(**result)
	
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
