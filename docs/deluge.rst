Deluge Configuration (Direct)
-----------------------------

If you wish to use the deluge direct client (NOT OVER JSON-RPC) there are some caveats to making it
work properly alongside tranny.

- If you are using a virtualenv to run tranny, select one of the following:

    - Install deluge into your virtualenv directly. This can be a non-trivial task, especially if you are not familiar with python packaging. Its not recommended unless you know what you are doing.

    - Install deluge system wide using your package manager and then install the virtualenv using the `--system-site-packages` flag. This will make it so you inherit the global python packages.

- Install everything globally and don't use virtualenv at all. This is highly unrecommended.

