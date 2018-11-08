## Documentation of this role

How to use this role.

- 1) Go to the customer portal and generate a manifest.

- 2) Store the manifest under the directory "files" in this role. ~/ansible-satellite6-install/files

- 3) Create a playbook as the following instance:

~~~
cat playbook_install_sat.yml

---
## Playbook to deploy Satellite 6.3.3
- name: MAIN | Deploying satellite server
  hosts: all
  vars:
    rhsm_user: 'ROOT_USER'
    rhsm_password: 'MYSUPERPASS'
    satellite_package_version: "satellite-6.3.3*"
    satellite_version: "6.3"
    manifest_name: "my_super_manifest.zip"
  roles:
    - ansible-satellite6-install
~~~

- 4) Configure the satellite into the ansible hosts "/etc/ansible/hosts"

- 5) Run the ansible-playbook command and wait. 

  `ansible-playbook playbook_install_sat.yml -l <satellite_host>`

        Get a coffee and be happy \o/

## Variables
To see the default values please check the `main.yml` file in the `vars` directory in the role.

### rhsm_user
Username to register the machine in the customer portal.

### rhsm_password
Password to the user connect and register the machine to the customer portal.

### satellite_version
Satellite main version, this variable is used to set the right repository
i.e: `satellite_version=6.3` to configure the repositories to Satellite 6.3


### satellite_package_version
Satellite package name 
i.e: To install Satellite 6.3.2 use `satellite_package_version="satellite-6.3.2*"` for the latest z-stream version use `"satellite_package_version=satellite"`

### foreman_admin_password
Satellite default admin password.

### foreman_initial_organization
Satellite default organization

### foreman_initial_location
Satellite default location

### manifest_path
Path where will be copied the manifest into the Satellite.

### manifest_name 
The name of the manifest generated in the customer portal.
Save the manifest in the role files directory `"~/ansible-satellite6-install/files"`.

### cv_name
The content view name that will be created during the configuration process.


# Notes:


### Satellite 6 release version
https://access.redhat.com/articles/1365633


## Examples:

~~~
---
## Playbook to deploy Satellite 6.4 latest
- name: MAIN | Deploying satellite server
  hosts: all
  vars:
    rhsm_user: 'ROOT_USER'
    rhsm_password: 'MYSUPERPASS'
    satellite_version: "6.4"
    manifest_name: "my_super_manifest.zip"
  roles:
    - ansible-satellite6-install
~~~