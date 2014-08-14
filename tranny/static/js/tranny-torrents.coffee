### Contains a list of currently selected DT_RowId (info_hash's) ###
selected_rows = []

### class defining selected rows in the torrent listing ###
selected_class = 'selected'

### Currently selected torrent that should be used in the detail display ###
selected_detail_id = false

### Application endpoint prefix ###
endpoint = '/torrents'

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

### Timer to update the selected torrent speed graph ###
speed_update_timer = null


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
        selected_detail_id = [row_id]
        if detail_update_timer != null
            clearTimeout detail_update_timer
        if speed_update_timer != null
            clearTimeout speed_update_timer
        detail_update()
        speed_update()
        jQuery("#" + row_id).addClass selected_class

action_recheck = ->
    if selected_rows
        jQuery.ajax "#{endpoint}/recheck", {
            data: JSON.stringify(selected_rows),
            contentType: 'application/json',
            type: 'POST'
        }

action_reannounce = ->
    if selected_rows
        jQuery.ajax "#{endpoint}/reannounce", {
            data: JSON.stringify(selected_rows),
            contentType: 'application/json',
            type: 'POST'
        }

action_remove = ->
    if selected_rows
        jQuery.ajax "#{endpoint}/remove", {
            data: JSON.stringify(selected_rows),
            contentType: 'application/json',
            type: 'POST'
        }

action_remove_data = ->
    if selected_rows
        jQuery.ajax "#{endpoint}/remove/data", {
            data: JSON.stringify(selected_rows),
            contentType: 'application/json',
            type: 'POST'
        }

action_stop = ->
    if selected_rows
        jQuery.ajax "#{endpoint}/stop", {
            data: JSON.stringify(selected_rows),
            contentType: 'application/json',
            type: 'POST'
        }

action_start = ->
    if selected_rows
        jQuery.ajax "#{endpoint}/start", {
            data: JSON.stringify(selected_rows),
            contentType: 'application/json',
            type: 'POST'
        }

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
        jQuery.getJSON "#{endpoint}/detail/#{selected_detail_id}/speed", (data) ->
            chart_update data['download_payload_rate'], data['upload_payload_rate']
    speed_update_timer = setTimeout speed_update, update_speed

bytes_to_size = (bytes, per_sec=false) ->
    if bytes == 0
        return '0 B'
    k = 1000;
    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    i = Math.floor(Math.log(bytes) / Math.log(k))
    human_size = (bytes / Math.pow(k, i)).toPrecision(2) + ' ' + sizes[i]
    if per_sec
        human_size = "#{human_size}/s"
    return human_size


detail_update = ->
    if selected_detail_id
        jQuery.getJSON "#{endpoint}/detail/#{selected_detail_id}", (data) ->
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

    detail_update_timer = setTimeout detail_update, detail_update_speed

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

jQuery ->
    jQuery('#torrent_table').dataTable {
        processing: true,
        serverSize: true,
        ajax: "#{endpoint}/list",
        paginate: false,
        searching: false,
        scrollY: 300,
        columns: [
            { data: 'name' },
            { data: 'size' },
            { data: 'ratio' },
            { data: 'up_rate' },
            { data: 'dn_rate' },
            { data: 'leechers'},
            { data: 'peers'},
            { data: 'priority'},
            { data: 'is_active'}
        ],
        rowCallback: row_load_cb
    }

    jQuery('#torrent_table tbody').on 'click', 'tr', row_select_cb
    jQuery('#action_stop').on 'click', action_stop
    jQuery('#action_start').on 'click', action_start
    jQuery('#action_recheck').on 'click', action_recheck
    jQuery('#action_reannounce').on 'click', action_reannounce

    ### Initialize epoch chart on the traffic tab ###
    detail_traffic_chart = jQuery('#detail-traffic-chart').epoch {
        type: graph_type,
        data: [{label: "upload", values: []}, {label: "download", values: []}],
        axes: ['left', 'right'],
        fps: graph_fps,
        windowSize: graph_window_size,
        queueSize: queue_size
    }
