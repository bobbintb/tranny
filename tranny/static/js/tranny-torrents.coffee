fetch_torrents = ->
    jQuery.getJSON("/torrents/list").done((data) ->
        speed_up.innterHTML = data[0]
        speed_dn.innerHTML = data[1]
        console.log "updating"
    )

jQuery ->
    jQuery('#torrent_table').dataTable({
        processing: true,
        serverSize: true,
        ajax: "/torrents/list",
        paginate: false,
        scrollY: 300,
        columns: [
            { data: 'name' },
            { data: 'ratio' },
            { data: 'up_rate' },
            { data: 'dn_rate' },
            { data: 'leechers'},
            { data: 'peers'},
            { data: 'priority'}
        ]
    })
