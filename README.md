# websockify-client

这东西能将 websockify 转成 websocket 的数据再转回 TCP

## How to use

### On server

See [https://github.com/novnc/websockify/blob/master/README.md](https://github.com/novnc/websockify/blob/master/README.md)

### On client

```
usage: websockify-client.py [-h] -r REMOTE_ADDRESS [-l BIND_ADDRESS]
                            [-p BIND_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -r REMOTE_ADDRESS, --remote-address REMOTE_ADDRESS
                        Remote address, like
                        "ws://your.site.example.org/some/path"
  -l BIND_ADDRESS, --listen-address BIND_ADDRESS
                        Listen address, default value is "127.0.0.1"
  -p BIND_PORT, --bind-port BIND_PORT
                        Bind port, default value is "3124"
```

Examples:

```
./websockify-client.py --remote-address ws://your.site.example.org/some/path
```

```
./websockify-client.py \
--remote-address ws://your.site.example.org/some/path \
--listen-address 127.0.0.1 \
--bind-port 10086
```