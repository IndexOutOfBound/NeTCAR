
chmod 700 ~/.ssh
#Disable Strict Host key Checking in SSH Config
echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_conifg

#generate a ssh key
ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -C "Open MPI"

#copy the key into authorized key and make it work
#this aollowed other node to login with public key
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys