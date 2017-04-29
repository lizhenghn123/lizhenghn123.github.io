counter=$(ps -C httpd --no-heading|wc -l)
if [ "${counter}" = "0" ]; then
    service httpd start
    sleep 2
    counter=$(ps -C httpd --no-heading|wc -l)
    if [ "${counter}" = "0" ]; then
        /etc/rc.d/init.d/keepalived stop
    fi
fi
