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

# Commands
```bash
# List inventory
ansible-inventory --list

# Test ssh and echo
ansible all --limit vagrant_host1 -a "/bin/echo hello"

# SSH into the guest VM
vagrant ssh vagrant_host1
```
