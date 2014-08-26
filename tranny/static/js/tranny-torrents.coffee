### Contains a list of currently selected DT_RowId (info_hash's) ###
selected_rows = []

### class defining selected rows in the torrent listing ###
selected_class = 'selected'

### Currently selected torrent that should be used in the detail display ###
selected_detail_id = false

### Application endpoint prefix ###
endpoint = "http://#{document.domain}:#{location.port}/ws"

### Update interval for the traffic graph in ms ###
update_speed = 1000

### Type of graph to draw. time.area is an alternate ###
graph_type = 'time.line'

### Number of frames per second that transitions animations should use. ###
graph_fps = 60

### Number of entries to keep in working memory while the chart is not animating transitions. ###
queue_size = 240

### Number of entries to display in the graph. ###
graph_window_size = 60

### Update interval for the stats/detail tabs ###
detail_update_speed = update_speed * 2

### Timer to update the selected torrent detail page ###
detail_update_timer = null

### Timer for the overall speed indicator ###
overall_speed_update_timer = null

### Timer to update the selected torrent speed graph ###
speed_update_timer = null

### Timer to update the selected torrent peer list ###
peer_update_timer = null

### socket.io-client instance ###
socket = null

### Element used to show flash message ###
user_messages = jQuery("#user_messages")

torrent_table = jQuery('#torrent_table').dataTable {
        processing: true,
        serverSize: true,
        paginate: false,
        searching: false,
        autoWidth: true,
        # Column reordering support
        sDom: 'Rlfrtip',
        scrollY: 300,
        columns: [
            { data: 'name' },
            { data: 'size' },
            { data: 'progress' },
            { data: 'ratio' },
            { data: 'up_rate' },
            { data: 'dn_rate' },
            { data: 'leechers'},
            { data: 'peers'},
            { data: 'priority'},
            { data: 'is_active'}
        ],
        rowCallback: row_load_cb,
        columnDefs: [
            {
                render: (data, type, row) ->
                    pct = Math.floor(data)
                    style = if pct >= 100 then "success" else "alert"
                    """<div class="progress #{style}">
                        <span style="float: left">#{data}%</span>
                        <span class="meter" style="width: #{data}"></span>
                    </div>"""
                targets: 2
            },
            {
                render: (data, type, row) ->
                    class_name = if data < 1 then 'alert' else 'success'
                    """<span class="#{class_name}">#{data}</span>"""
                targets: 3
            }
        ]
    }
#new jQuery.fn.dataTable.ColReorder torrent_table

###
    Called for each new row loaded into the data table

    @param {string} DT_RowId defined for the row ( which corresponds to the info_hash )
    @param {object} The rows data object
    @param {number} Index of the row in the table
###
row_load_cb = (row, data, displayIndex) ->
    #noinspection JSUnresolvedVariable
    if jQuery.inArray(data.DT_RowId, selected_rows) != -1
        jQuery(row).addClass selected_class

###
    Called when a user selects a row with the cursor. Will update the currently selected rows.
    If the user holds ctrl while clicking the row will be added to the selected_rows array. Otherwise
    the row will be "activated" and show more detailed information for that row in another panel.
###
row_select_cb = (e) ->
    row_id = @id
    if e.ctrlKey
        index = _.indexOf selected_rows, row_id
        if index == -1
            selected_rows.push row_id
        else
            selected_rows.splice index, 1
        jQuery(@).toggleClass selected_class
    else
        for existing_row_id in selected_rows
            jQuery("#" + existing_row_id).removeClass selected_class
        selected_rows = [row_id]
        selected_detail_id = row_id
        if detail_update_timer != null
            clearTimeout detail_update_timer
        if speed_update_timer != null
            clearTimeout speed_update_timer
        if peer_update_timer != null
            clearTimeout peer_update_timer
        detail_update()
        speed_update()
        peer_update()
        jQuery("#" + row_id).addClass selected_class

###
Remove a row from the torrent list by its info_hash
###
row_remove = (info_hash) -> jQuery("#" + info_hash).remove()

action_recheck = ->
    if selected_rows
        socket.emit 'event_torrent_recheck', {info_hash: selected_rows}
        return false

action_reannounce = ->
    if selected_rows
        socket.emit 'event_torrent_announce', {info_hash: selected_rows}

action_remove = ->
    for info_hash in selected_rows
        jQuery.ajax "#{endpoint}/#{info_hash}/files", {
            type: 'DELETE'
        }, status_code: {
            204: -> row_remove info_hash
            404: -> console.log "info_hash not found: #{info_hash}"
        }

action_remove_data = ->
    for info_hash in selected_rows
        jQuery.ajax "#{endpoint}/#{info_hash}", {
            type: 'DELETE'
        }, status_code: {
            204: -> row_remove info_hash
            404: -> console.log "info_hash not found: #{info_hash}"
        }

action_stop = ->
    if selected_rows
        socket.emit 'event_torrent_stop', {info_hash: selected_rows}


action_start = ->
    if selected_rows
        socket.emit 'event_torrent_start', {info_hash: selected_rows}


_alert_num = 0

###
    Show an alert popup message to the user. The message will fade after a few seconds have passed
###
show_alert = (msg, msg_type='info') ->
    alert += 1
    """<div id="alert_#{_alert_num}" class="#{msg_type}" data-alert class="alert-box" tabindex="0" aria-live="assertive" role="dialogalert">
  #{msg}
  <button href="#" tabindex="0" class="close" aria-label="Close Alert">&times;</button>
</div>"""


### WS Event handlers ###


event_alert_cb = (message) ->
    show_alert message['message']


event_torrent_list_response_cb = (message) ->
    for row in message['data']
        torrent_table.fnAddData(row)


event_torrent_stop_response_cb = (message) ->
    show_alert message['msg'], message['msg_type']


_rand = -> Math.floor((Math.random() * 1000) + 1)

### Update the chart values with the latest speed values ###
chart_update = (upload, download) ->
    update_data = [
        {time: ts(), y: upload},
        {time: ts(), y: download}
    ]
    detail_traffic_chart.push update_data


fmt_timestamp = (ts) ->
    moment.unix(ts).format 'D/M/YYYY hh:mm:s'

fmt_duration = (seconds) -> moment.duration(seconds, 'seconds').humanize()

speed_update = ->
    if selected_detail_id
        socket.emit 'event_torrent_speed', {info_hash: selected_detail_id}
    speed_update_timer = setTimeout speed_update, update_speed

handle_event_torrent_speed_response = (message) ->
    chart_update message['data']['download_payload_rate'], message['data']['upload_payload_rate']

speed_up = jQuery("#speed_up")
speed_dn = jQuery("#speed_dn")

overall_speed_update = ->
    socket.emit 'event_speed_overall', {}
    overall_speed_update_timer = setTimeout overall_speed_update, update_speed

handle_event_speed_overall_response = (message) ->
    speeds = message['data']
    speed_up.text bytes_to_size speeds['up'], true
    speed_dn.text bytes_to_size speeds['dn'], true

_sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
bytes_to_size = (bytes, per_sec=false) ->
    if bytes == 0
        return '0 B'
    k = 1000
    i = Math.floor(Math.log(bytes) / Math.log(k))
    human_size = (bytes / Math.pow(k, i)).toPrecision(2) + ' ' + _sizes[i]
    if per_sec
        human_size = "#{human_size}/s"
    return human_size

render_peers = (peer_list) ->
    output_html = []
    for peer in peer_list
        output_html.push """
            <tr>
                <td><img src="/static/img/country/#{peer['country'].toLowerCase()}.png"></td>
                <td>#{peer['ip']}</td>
                <td>#{peer['client']}</td>
                <td><div class="progress"><span class="meter" style="#{peer['progress'] * 100}"></span></div></td>
                <td>#{peer['down_speed']}</td>
                <td>#{peer['up_speed']}</td>
            </tr>
            """
    jQuery("#peer_list tbody").html output_html.join("")

peer_update= ->
    if selected_detail_id
        socket.emit 'event_torrent_peers', {info_hash: selected_detail_id}
    peer_update_timer = setTimeout peer_update, update_speed


handle_event_torrent_peers_response = (message) ->
    render_peers message['data']['peers']

detail_update = ->
    if selected_detail_id
        socket.emit('event_torrent_details', {info_hash: selected_detail_id})
    detail_update_timer = setTimeout detail_update, detail_update_speed

handle_event_torrent_details_response = (message) ->
    data = message['data']
    eta = if data['eta'] == 0 then '∞' else fmt_duration data['eta']
    seeds = "#{data['num_seeds']} (#{data['total_seeds']})"
    peers = "#{data['num_peers']} (#{data['total_peers']})"
    pieces = "#{data['num_pieces']} (#{data['piece_length']})"
    detail_elements.detail_downloaded.text bytes_to_size data['total_done']
    detail_elements.detail_uploaded.text bytes_to_size data['total_uploaded']
    detail_elements.detail_tracker_status.text data['tracker_status']
    detail_elements.detail_ratio.text data['ratio'].toFixed(2)
    detail_elements.detail_next_announce.text data['next_announce']
    detail_elements.detail_speed_dl.text bytes_to_size data['download_payload_rate'], true
    detail_elements.detail_speed_ul.text bytes_to_size data['upload_payload_rate'], true
    detail_elements.detail_eta.text eta
    detail_elements.detail_pieces.text pieces
    detail_elements.detail_seeders.text seeds
    detail_elements.detail_peers.text peers
    detail_elements.detail_availability.text data['distributed_copies']
    detail_elements.detail_active_time.text fmt_duration data['active_time']
    detail_elements.detail_seeding_time.text fmt_duration data['seeding_time']
    detail_elements.detail_added_on.text fmt_timestamp data['time_added']
    detail_elements.detail_name.text data['name']
    detail_elements.detail_hash.text selected_detail_id
    detail_elements.detail_path.text data['save_path']
    detail_elements.detail_total_size.text data['total_size']
    detail_elements.detail_num_files.text data['detail_num_files']
    #detail_elements.detail_comment.text data['detail_comment']
    detail_elements.detail_status.text data['detail_status']
    detail_elements.detail_tracker.text data['tracker_host']

### Return the current unix timestamp in seconds ###
ts = -> Math.round(new Date().getTime() / 1000)|0

detail_traffic_chart = null

### Cache all the detail element nodes ###
detail_elements =
    detail_downloaded: jQuery("#detail_downloaded")
    detail_uploaded: jQuery("#detail_uploaded")
    detail_ratio: jQuery("#detail_ratio")
    detail_next_announce: jQuery("#detail_next_announce")
    detail_tracker_status: jQuery("#detail_tracker_status")
    detail_speed_dl: jQuery("#detail_speed_dl")
    detail_speed_ul: jQuery("#detail_speed_ul")
    detail_eta: jQuery("#detail_eta")
    detail_pieces: jQuery("#detail_pieces")
    detail_seeders: jQuery("#detail_seeders")
    detail_peers: jQuery("#detail_peers")
    detail_availability: jQuery("#detail_availability")
    detail_active_time: jQuery("#detail_active_time")
    detail_seeding_time: jQuery("#detail_seeding_time")
    detail_added_on: jQuery("#detail_added_on")
    detail_name: jQuery("#detail_name")
    detail_hash: jQuery("#detail_hash")
    detail_path: jQuery("#detail_path")
    detail_total_size: jQuery("#detail_total_size")
    detail_num_files: jQuery("#detail_num_files")
    detail_comment: jQuery("#detail_comment")
    detail_status: jQuery("#detail_status")
    detail_tracker: jQuery("#detail_tracker")

### Check for the existence of a string in the URL ###
in_url = (text) ->
    window.location.pathname.indexOf(text) != -1

jQuery ->
    socket = io.connect endpoint
    socket.on 'connect', ->
        if in_url "/torrents/"
            # Make sure not to load duplicate data on each connect if the server goes away
            try
                torrent_table.clear().draw()
            catch e
                null
            socket.emit 'event_torrent_list'
        overall_speed_update()

    socket.on 'event_speed_overall_response', handle_event_speed_overall_response

    if in_url "/torrents/"
        socket.on 'event_torrent_recheck', (data) -> console.log data
        socket.on 'event_torrent_peers_response', handle_event_torrent_peers_response
        socket.on 'event_torrent_speed', (data) -> console.log data
        socket.on 'event_torrent_details_response', handle_event_torrent_details_response
        socket.on 'event_torrent_files', (data) -> console.log data
        socket.on 'event_torrent_list_response', event_torrent_list_response_cb
        socket.on 'event_alert', event_alert_cb

        jQuery('#torrent_table tbody').on 'click', 'tr', row_select_cb
        jQuery('#action_stop').on 'click', action_stop
        jQuery('#action_start').on 'click', action_start
        jQuery('#action_recheck').on 'click', action_recheck
        jQuery('#action_reannounce').on 'click', action_reannounce
        jQuery('#action_remove').on 'click', action_remove
        jQuery('#action_remove_data').on 'click', action_remove_data

        ### Initialize epoch chart on the traffic tab ###
        detail_traffic_chart = jQuery('#detail-traffic-chart').epoch {
            type: graph_type,
            data: [{label: "upload", values: []}, {label: "download", values: []}],
            axes: ['left', 'right'],
            fps: graph_fps,
            windowSize: graph_window_size,
            queueSize: queue_size
        }
