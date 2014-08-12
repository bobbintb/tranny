### Contains a list of currently selected DT_RowId (info_hash's) ###
selected_rows = []

### class defining selected rows in the torrent listing ###
selected_class = 'selected'

### Currently selected torrent that should be used in the detail display ###
selected_detail_id = false


### Application endpoint prefix ###
endpoint = '/torrents'

### Update interval for the traffic graph in ms ###
chart_update_speed = 1000



###
    Called for each new row loaded into the data table

    @param {string} DT_RowId defined for the row ( which corresponds to the info_hash )
    @param {object} The rows data object
    @param {number} Index of the row in the table
###
row_load_cb = (row, data, displayIndex) ->
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
        jQuery("#" + row_id).addClass selected_class

action_recheck = ->
    jQuery.ajax "#{endpoint}/recheck", {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

action_reannounce = ->
    jQuery.ajax "#{endpoint}/reannounce", {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

action_remove = ->
    jQuery.ajax "#{endpoint}/remove", {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

action_remove_data = ->
    jQuery.ajax "#{endpoint}/remove/data", {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

action_stop = ->
    jQuery.ajax "#{endpoint}/stop", {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

action_start = ->
    jQuery.ajax "#{endpoint}/start", {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

_rand = -> Math.floor((Math.random() * 1000) + 1)

chart_update = ->
    update_data = [
        {time: ts(), y: _rand()},
        {time: ts(), y: _rand()}
    ]
    detail_traffic_chart.push update_data
    setTimeout chart_update, chart_update_speed

### Return the current unix timestamp in seconds ###
ts = -> Math.round(new Date().getTime() / 1000)|0

detail_traffic_chart = null

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
        type: 'time.line',
        data: [{label: "upload", values: []}, {label: "download", values: []}],
        axes: ['left', 'right']
    }

    setTimeout chart_update, chart_update_speed
