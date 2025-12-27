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
## Testing
- Vagrant
- Virtual Box

# Deployment steps
- Have a VM ready (NUC, or rent on cloud, etc.)
- Install Tailscale
  - See https://tailscale.com/download/linux
  - Ensure Tailscale is up with `--accept-dns=false`
- Set up Ansible on the master host machine
  - Ensure `inventory.ini` is configured
  - Ensure `ansible.cfg` is configured
- Apply the playbook(s)
  - Harden security:
    - Change SSH port: 
      - [change-ssh-port.yaml](playbooks/change-ssh-port.yaml)
      - After changing port:
        - Test SSH: `ssh root@VM_IP -i ~/.ssh/... -p NEW_PORT`
        - Update port in inventory.ini and test ansible ping: `ansible all -m ping -v`
        - `sed -i '/# BEGIN ANSIBLE MANAGED - TEMPORARY DUAL PORT/,/# END ANSIBLE MANAGED - TEMPORARY DUAL PORT/d' /etc/ssh/sshd_config` (or manually delete those lines)
        - 
        ```
        systemctl daemon-reload
        systemctl restart ssh.socket
        systemctl restart ssh.service
        ```
        - `ufw delete allow 22/tcp`
  - Infra setup: [infra-setup-tagged.yaml](playbooks/infra-setup-tagged.yaml)

# Commands
```bash
# List inventory
ansible-inventory --list

# Test ssh, ping and echo
ansible all -m ping -v
ansible all --limit vagrant_host1 -a "/bin/echo hello"

# SSH into the guest VM
vagrant ssh vagrant_host1
ssh vagrant@127.0.0.1 -p 2222 -i .vagrant/machines/vagrant_host1/virtualbox/private_key

# Save local VM state (to restore back to clean state)
vagrant snapshot save clean-state
vagrant snapshot restore clean-state

# Destroy the VM forcibly
vagrant destroy --force

# Show port info
vagrant port

# Apply playbook
ansible-playbook infra-setup.yaml

# Check the playbook (not actually applying any changes)
ansible-playbook infra-setup.yaml --check

# Skip all the tasks related to a component
ansible-playbook playbooks/infra-setup-tagged.yaml --skip-tags uv

# Disable the installation of a certain component
ansible-playbook playbooks/infra-setup-tagged.yaml -e "install_k3s=false"

# Start at a specific task
ansible-playbook playbooks/infra-setup-tagged.yaml --start-at-task="DOCKER | Install Docker packages"
```
