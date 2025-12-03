# Resources
## Tutorials
- https://spacelift.io/blog/ansible-tutorial
## Inventory
- https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html
## Config
- https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html
## Task
### Collections
- https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/apt_module.html

# Requirements
- Vagrant
- Virtual Box

# Deployment steps
- Have a VM ready (NUC, or rent on cloud, etc.)
- Set up Ansible on the master host machine
  - `inventory.ini` is configured
  - `ansible.cfg` is configured
- Apply the playbook
  - Use [setup-playbook-tagged.yaml](playbooks/setup-playbook-tagged.yaml)

# Commands
```bash
# List inventory
ansible-inventory --list

# Test ssh and echo
ansible all --limit vagrant_host1 -a "/bin/echo hello"

# SSH into the guest VM
vagrant ssh vagrant_host1
ssh -p 2222 -i .vagrant/machines/vagrant_host1/virtualbox/private_key vagrant@127.0.0.1

# Save local VM state (to restore back to clean state)
vagrant snapshot save clean-state
vagrant snapshot restore clean-state

# Destroy the VM forcibly
vagrant destroy --force

# Show port info
vagrant port

# Apply playbook
ansible-playbook setup-playbook.yaml

# Check the playbook (not actually applying any changes)
ansible-playbook setup-playbook.yaml --check

# Skip all the tasks related to a component
ansible-playbook playbooks/setup-playbook-tagged.yaml --skip-tags uv

# Disable the installation of a certain component
ansible-playbook playbooks/setup-playbook-tagged.yaml -e "install_k3s=false"

# Start at a specific task
ansible-playbook playbooks/setup-playbook-tagged.yaml --start-at-task="DOCKER | Install Docker packages"
```
