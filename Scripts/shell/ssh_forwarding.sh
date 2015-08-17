## SSH forwarding configurations

# local port 8080 forwarding to remote 80
ssh -N -f -L 8080:localhost:80 guest@joes-pc

# remote port 5900 forwarding to local 5900
ssh -N -f -R 5900:localhost:5900 guest@joes-pc

# multihop port forwarding
host1=username@login_node.com
host2=username@dest.ination.com
ssh -L 7777:localhost:7777 $host1 ssh -L 7777:localhost:7777 -N $host2

# dynamic port forwarding
ssh -C -D 7777 guest@joes-pc
