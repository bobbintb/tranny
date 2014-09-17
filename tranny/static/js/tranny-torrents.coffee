root = exports ? this

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

### Keep track of if we have connected before or not ###
has_connected = false

### Element used to show flash message ###
user_messages = jQuery("#user_messages")

### Overall speed indicator elements ###
speed_up = jQuery("#speed_up")
speed_dn = jQuery("#speed_dn")

STATUS_OK = 0
STATUS_FAIL = 1
STATUS_INTERNAL_ERROR = 3
STATUS_CLIENT_NOT_AVAILABLE = 5
STATUS_INCOMPLETE_REQUEST = 10
STATUS_INVALID_INFO_HASH = 11

### Use mustache/jinja style interpolation  {{ }} ###
_.templateSettings.interpolate = /{{([\s\S]+?)}}/g;

### Compiled _ templates ###
template =
    progress: _.template """<div class="progress {{ style }}">
                            <span class="count">{{ data }} %</span>
                            <span class="meter" style="width: {{ data }}"></span>
                        </div>"""
    ratio: _.template """<span class="{{ class_name }}">{{ data }}</span>"""
    peer_info: _.template "{{ num }} ({{ total }})"



###
    Class to handle interactions and rendering of the torrent table.

    This does not use jQuery nor does it use string concatenation to generate
    table rows & cells. This is purposefully done to ensure maximum client
    side performance for users with large numbers of torrents loaded.
###
class TorrentTable
    ### Allow self reference when @ doesnt refer to this instance ###
    self = {}
    torrents = {}
    constructor: (@dom_id) ->
        self = @
        @table = document.getElementById dom_id
        @table_body = document.querySelector dom_id + "> tbody"
        @cols = ['name', 'size', 'progress', 'ratio', 'up_rate',
                 'dn_rate', 'leechers', 'peers', 'priority', 'is_active']
        @info_hashes = {}

    ###
    We are using dom elements here over plain strings to keep things performant
    ###
    insert_row: (row) ->
        if row['info_hash'] in @info_hashes
            # Don't re-add known data
            return
        tr = document.createElement "tr"
        tr.setAttribute 'id', row['info_hash']
        tr.onclick = @row_select_handler
        for key in @cols
            td = document.createElement "td"
            key_name = if key == 'progress' then 'completed' else key
            td.setAttribute "class", key_name
            switch key
                when "progress"
                    style = if Math.floor row[key] >= 100 then "success" else "alert"
                    td.innerHTML = template['progress'] {'style': style, 'data': row[key]}
                when "ratio"
                    class_name = if row[key] < 1 then 'alert' else 'success'
                    td.innerHTML = template['ratio'] {'class_name': class_name, 'data': row[key]}
                when "leechers"
                    td.appendChild document.createTextNode template['peer_info'] {
                        'num': row[key], 'total': row['total_leechers']
                    }
                when "peers"
                    td.appendChild document.createTextNode template['peer_info'] {
                        'num': row[key], 'total': row['total_peers']
                    }
                else
                    td.appendChild document.createTextNode row[key]

            torrents[row['info_hash']] = {
                row: tr.appendChild td
            }
        @table_body.appendChild tr

    add_rows: (rows) ->
        rows = (@insert_row row for row in rows)

    update: (data) ->


    remove: (info_hash) ->
        @table_body.removeChild @table_body.getElementById info_hash

    ###
        Called when a user selects a row with the cursor. Will update the currently selected rows.
        If the user holds ctrl while clicking the row will be added to the selected_rows array. Otherwise
        the row will be "activated" and show more detailed information for that row in another panel.
    ###
    row_select_handler: (e) ->
        row_id = @id
        if e.ctrlKey
            index = _.indexOf selected_rows, row_id
            if index == -1
                selected_rows.push row_id
            else
                selected_rows.splice index, 1
            attr = @getAttribute "class"
            if attr != "selected"
                @setAttribute "class", selected_class
            else
                @removeAttribute "class"
        else
            for element in self.table_body.querySelectorAll(".selected")
                element.removeAttribute "class"
            selected_rows = [row_id]
            selected_detail_id = row_id
            if detail_update_timer != null
                clearTimeout detail_update_timer
            if speed_update_timer != null
                clearTimeout speed_update_timer
            if peer_update_timer != null
                clearTimeout peer_update_timer
            action_torrent_details()
            action_torrent_speed()
            action_torrent_peers()
            @setAttribute "class", selected_class

torrent_table = null

init_traffic_chart = ->
    $('#detail-traffic-chart').highcharts {
        chart: {
            type: 'areaspline'
        },
        title: {
            text: 'Average fruit consumption during one week'
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: 150,
            y: 100,
            floating: true,
            borderWidth: 1,
            backgroundColor: (Highcharts.theme and Highcharts.theme.legendBackgroundColor) or '#FFFFFF'
        },
        xAxis: {
            categories: [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday'
            ],
            plotBands: [{
                from: 4.5,
                to: 6.5,
                color: 'rgba(68, 170, 213, .2)'
            }]
        },
        yAxis: {
            title: {
                text: 'Fruit units'
            }
        },
        tooltip: {
            shared: true,
            valueSuffix: ' units'
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            areaspline: {
                fillOpacity: 0.5
            }
        },
        series: [{
            name: 'John',
            data: [3, 4, 3, 5, 4, 10, 12]
        }, {
            name: 'Jane',
            data: [1, 3, 4, 3, 3, 5, 4]
        }]
    }


### Initialize epoch chart on the traffic tab ###
#detail_traffic_chart = jQuery('#detail-traffic-chart').epoch {
#    type: graph_type,
#    data: [{label: "upload", values: []}, {label: "download", values: []}],
#    axes: ['left', 'right'],
#    fps: graph_fps,
#    windowSize: graph_window_size,
#    queueSize: queue_size
#}

### Initialize peer chart on the peers tab ###
peer_chart = jQuery("#peer_chart").epoch {
    type: 'pie',
    inner: 50
}

client_chart = jQuery("#client_chart").epoch {
    type: 'pie',
    inner: 50
}


###
    Called for each new row loaded into the data table

    @param {string} DT_RowId defined for the row ( which corresponds to the info_hash )
    @param {object} The rows data object
    @param {number} Index of the row in the table
###
row_load_handler = (row, data, displayIndex) ->
    #noinspection JSUnresolvedVariable
    if jQuery.inArray(data.DT_RowId, selected_rows) != -1
        jQuery(row).addClass selected_class


###
Remove a row from the torrent list by its info_hash
###
row_remove = (info_hash) ->
    jQuery("#" + info_hash).remove()


### Client actions ###
action_recheck = ->
    if selected_rows
        socket.emit 'event_torrent_recheck', {info_hash: selected_rows}
        return false


action_reannounce = ->
    if selected_rows
        socket.emit 'event_torrent_announce', {info_hash: selected_rows}


action_remove = ->
    for info_hash in selected_rows
        socket.emit 'event_torrent_remove', {info_hash: info_hash, remove_data: false}


action_remove_data = ->
    for info_hash in selected_rows
        socket.emit 'event_torrent_remove', {info_hash: info_hash, remove_data: true}


action_stop = ->
    if selected_rows
        socket.emit 'event_torrent_stop', {info_hash: selected_rows}


action_start = ->
    if selected_rows
        socket.emit 'event_torrent_start', {info_hash: selected_rows}


action_torrent_details = ->
    if selected_detail_id
        socket.emit 'event_torrent_details', {info_hash: selected_detail_id}


action_torrent_speed = ->
    if selected_detail_id
        socket.emit 'event_torrent_speed', {info_hash: selected_detail_id}
    speed_update_timer = setTimeout action_torrent_speed, update_speed


action_torrent_peers= ->
    if selected_detail_id
        socket.emit 'event_torrent_peers', {info_hash: selected_detail_id}
    peer_update_timer = setTimeout action_torrent_peers, update_speed

special_alerts = {}

###
    Response handlers for sent websocket events
###
error_handler = (func, message) ->
    if message['status'] == STATUS_CLIENT_NOT_AVAILABLE
        if not special_alerts[STATUS_CLIENT_NOT_AVAILABLE]
            special_alerts[STATUS_CLIENT_NOT_AVAILABLE] = show_alert "Torrent client not online", 'error', 0
    else
        func message


handle_event_torrent_files_response = (message) ->
    false


handle_event_torrent_reannounce_response = (message) ->
    show_alert "Got reannounce response"


handle_event_torrent_recheck_response = (message) ->
    show_alert "Got recheck response"


handle_event_alert = (message) ->
    show_alert message['msg'], message['msg_type']


handle_event_torrent_list_response = (message) ->
    torrent_table.add_rows message['data']
    #for row in message['data']
    #    torrent_table.fnAddData(row)


handle_event_torrent_stop_response = (message) ->
    show_alert message['msg'], message['msg_type']


handle_event_speed_overall_response = (message) ->
    speed_up.text bytes_to_size message['data']['up'], true
    speed_dn.text bytes_to_size message['data']['dn'], true


handle_event_torrent_speed_response = (message) ->
    chart_update message['data']['download_payload_rate'], message['data']['upload_payload_rate']


handle_event_torrent_peers_response = (message) ->
    sort_client = (peer) -> return (peer['client'].split " ")[0..-2].toString()
    peer_chart_data = []
    client_chart_data = []
    for country, count of _.countBy message['data']['peers'], 'country'
        peer_chart_data.push {label: country, value: count}
    for client, count of _.countBy message['data']['peers'], sort_client
        client_chart_data.push {label: client, value: count}
    peer_chart.update peer_chart_data
    client_chart.update client_chart_data
    render_peers message['data']['peers']

handle_event_torrent_remove_response = (message) ->
    if message['status'] == 0
        jQuery("#" + message['data']['info_hash']).remove()

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

_alert_num = 0
###
    Show an alert popup message to the user. The message will fade after a few seconds have passed

    @param {string} Message to display
    @param {string} Type of message (css class used)
    @param {number} Time in seconds to show the message
###
show_alert = (msg, msg_type='info', ttl=5) ->
    _alert_num += 1
    console.log ttl, msg, _alert_num
    user_messages.append("""<div id="alert_#{_alert_num}" data-alert class="alert-box radius #{msg_type}">#{msg}<a href="#" class="close">&times;</a></div>""")
    if ttl > 0
        setTimeout((=> jQuery("#alert_#{_alert_num}").fadeOut(-> @remove())), ttl * 1000)
    return _alert_num


### Update the chart values with the latest speed values ###
chart_update = (upload, download) ->
    update_data = [
        {time: ts(), y: upload},
        {time: ts(), y: download}
    ]
    detail_traffic_chart.push update_data


fmt_timestamp = (ts) ->
    moment.unix(ts).format 'D/M/YYYY hh:mm:s'


fmt_duration = (seconds) ->
    moment.duration(seconds, 'seconds').humanize()


overall_speed_update = ->
    socket.emit 'event_speed_overall', {}
    overall_speed_update_timer = setTimeout overall_speed_update, update_speed


_sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
bytes_to_size = (bytes, per_sec=false) ->
    if bytes <= 1000
        return if per_sec then "#{bytes} B/s" else "#{bytes} B"
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
                <td>#{bytes_to_size peer['down_speed'], true}</td>
                <td>#{bytes_to_size peer['up_speed'], true}</td>
            </tr>
            """
    jQuery("#peer_list tbody").html output_html.join("")


### Return the current unix timestamp in seconds ###
ts = -> Math.round(new Date().getTime() / 1000)|0

#detail_traffic_chart = null

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

torrent_wrapper = document.querySelector "#table_wrap"
window_resize_handler = ->
    torrent_wrapper.style.height = "#{window.innerHeight - 395}px";


jQuery ->
    if in_url "/torrents/"
        torrent_table = new TorrentTable "#torrent_table"
        root.t = torrent_table
    socket = io.connect endpoint
    socket.on 'connect', ->
        if has_connected
            show_alert "Reconnected to backend successfully", null, 5
        # For some reason this doesnt work on load...???
        #else
        #    show_alert "Connected to backend successfully", null, 5

        if in_url "/torrents/"
            # Make sure not to load duplicate data on each connect if the server goes away by just clearing
            # existing data from the table
            try
                torrent_table.fnClearTable()
            catch e
                null
            socket.emit 'event_torrent_list'
        overall_speed_update()
        has_connected = true

    socket.on 'event_speed_overall_response', (message) =>
        error_handler handle_event_speed_overall_response, message

    if in_url "/torrents/"
        socket.on 'event_torrent_recheck', (message) =>
            error_handler handle_event_torrent_recheck_response, message
        socket.on 'event_torrent_peers_response', handle_event_torrent_peers_response
        socket.on 'event_torrent_speed_response', handle_event_torrent_speed_response
        socket.on 'event_torrent_details_response', handle_event_torrent_details_response
        socket.on 'event_torrent_files', handle_event_torrent_files_response
        socket.on 'event_torrent_list_response', (message) =>
            error_handler handle_event_torrent_list_response, message
        socket.on 'event_torrent_remove_response', handle_event_torrent_remove_response
        socket.on 'event_alert', handle_event_alert
        socket.on 'event_torrent_reannounce_response', handle_event_torrent_reannounce_response
        socket.on 'event_torrent_stop_response', handle_event_torrent_stop_response

        jQuery('#action_stop').on 'click', action_stop
        jQuery('#action_start').on 'click', action_start
        jQuery('#action_recheck').on 'click', action_recheck
        jQuery('#action_reannounce').on 'click', action_reannounce
        jQuery('#action_remove').on 'click', action_remove
        jQuery('#action_remove_data').on 'click', action_remove_data
        jQuery('#resize_columns').on 'click', ->
            torrent_table.fnAdjustColumnSizing true
        window_resize_handler()
        jQuery(window).on 'resize', window_resize_handler
