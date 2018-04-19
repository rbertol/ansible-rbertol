#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.2',
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

options:
    name:
        description:
            - This is the name of username account that will be created in CyberARK Safe
        required: true
    safe:
        description:
            - The safe tha account password will be saved.
        required: true
    plataform:
        description:
            - Plataform Name created in CyberARK, It's a rule that will be applied at this password.
        required: true
    address:
        description:
            - The address that will be used a password genereted.
        required: true
    password:
        description:
            - Password that will be created in username and address saved in Safe.
            - If password variable wasn't set, a random password will be genereted.
        required: false
    description:
        description:
            - A simple description of password.
        required: false
    cyberark_host:
        description:
            - IP Address or Hostname of CyberARK.
        required: true
    cyberark_username:
        description:
            - Username of CyberARK.
        required: true
    cyberark_password:
        description:
            - Password of User.
        required: true

author:
    - Rudnei Bertol Junior <rudneibertol@gmail.com>
'''

EXAMPLES = '''
### Simple example to create account in CyberARK Safe if account doesn't exists
- name: Create account 
  cyberark_password:
    name: 'root'
    safe: 'ACME'
    platform: 'ssh_user_noch'
    address: 'machine.acme.local
    cyberark_username: 'user_cyberark_access'
    cyberark_password: "pass_cyberark_access"
    cyberark_host: "cyberark.acme.com.br'
    description: "Small description of password"

### Example to generate a unique password externaly and use that to create multiples accounts in CyberARK Safe if accounts don't exists.
- name: Generate a new random password.
  set_fact:
    random_password: "{{ lookup('password', '/tmp/null chars=ascii_letters,digits,hexdigits') }}"

- name: Create cyberark password in safe.
  cyberark_password:
    name: "root"
    safe: "ACME"
    platform: "ssh_user_noch"
    address: "{{ item }}"
    password: "{{ random_password }}"
    cyberark_username: 'user_cyberark_access'
    cyberark_password: "pass_cyberark_access"
    cyberark_host: "cyberark.acme.com.br'
    description: "Small description of password"
  register: cyberpass
  with_items:
    - machine1.acme.local
    - machine2.acme.local
    - machine3.acme.local

- name: Create variable with new password.
  set_fact:
    password: "{{ cyberpass.results[0].password }}"

- name: Show Password from CyberARK
  debug: var=password

'''

RETURN = '''
message:
    description: The output message with sucessfully password created or already exists.
password:
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
        password=dict(type='str', required=False),
        description=dict(type='str', required=False),
        cyberark_host=dict(type='str', required=True),
        cyberark_username=dict(type='str', required=True),
        cyberark_password=dict(type='str', required=True)
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

    api='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/PIMServices.svc/Accounts?Keywords='+module.params['name']+'+'+module.params['address']+'+'+module.params['platform']+'&Safe='+module.params['safe']
    headers={'content-type': 'application/json', 'Authorization': auth}
    response=requests.get(api, headers=headers, verify=False)
    account=response.json()
    count_exist=account['Count']

    if count_exist >= 1:
        getid=account['accounts'][0]['AccountID']
        api='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/PIMServices.svc/Accounts/'+getid+'/Credentials'
        headers={'content-type': 'application/json', 'Authorization': auth}
        response=requests.get(api, headers=headers, verify=False)
        response_result=response.status_code
        password=response.text
        message='Account '+module.params['name']+' already exist to address '+module.params['address']+' in plataform '+module.params['platform']+'.'
        changed=False

    if count_exist == 0:
        if module.params['password']:
		password=module.params['password']
	else:
		password=randompassword()
        url='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/PIMServices.svc/Account'
        headers={'content-type': 'application/json', 'Authorization': auth}
        payload={'account' : {'safe':module.params['safe'],'platformID':module.params['platform'],'address':module.params['address'],'password':password,'username':module.params['name'],'disableAutoMgmt':'true','disableAutoMgmtReason':module.params['description']}}
        response=requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        response_result=response.status_code
        changed=True
        message='Account '+module.params['name']+' created successfully to address '+module.params['address']+' in plataform '+module.params['platform']+'.'

    api='https://'+module.params['cyberark_host']+'/PasswordVault/WebServices/auth/Cyberark/CyberArkAuthenticationService.svc/Logoff'
    headers={'content-type': 'application/json', 'Authorization': auth}
    response=requests.post(api, data=json.dumps(payload), headers=headers, verify=False)

    result['changed']=changed
    result['message']=message
    result['password']=password

    if response_result == 400:
        module.fail_json(msg='The request could not be understood by the server due to incorrect syntax.')
    module.exit_json(**result)
	
    if response_result == 401:
        module.fail_json(msg='The request requires user authentication.')
    module.exit_json(**result)
	
    if response_result == 403:
        module.fail_json(msg='The server received and understood the request, but will not fulfill it. Authorization will not help and the request MUST NOT be repeated.')
    module.exit_json(**result)
	
    if response_result == 404:
        module.fail_json(msg='The server did not find anything that matches the Request-URI. No indication is given of whether the condition is temporary or permanent.')
    module.exit_json(**result)
	
    if response_result == 409:
        module.fail_json(msg='The request could not be completed due to a conflict with the current state of the resource.')
    module.exit_json(**result)

    if response_result == 500:
        module.fail_json(msg='The server encountered an unexpected condition which prevented it from fulfilling the request.')
    module.exit_json(**result)
	
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
