# remote service via login host
host1=username@login_node.com
host2=username@dest.ination.com
ssh -L 7777:localhost:7777 $host1 ssh -L 7777:localhost:7777 -N $host2
