### Contains a list of currently selected DT_RowId (info_hash's) ###
selected_rows = []
selected_class = 'selected'

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
        console.log "Selected #{selected_rows.length} rows!"
    else
        for existing_row_id in selected_rows
            jQuery("##{existing_row_id}").removeClass selected_class
        selected_rows = [row_id]
        jQuery("##{row_id}").addClass selected_class
        console.log "Selected single row!"


action_stop = ->
    jQuery.ajax '/torrents/stop', {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

action_start = ->
    jQuery.ajax '/torrents/start', {
        data: JSON.stringify(selected_rows),
        contentType: 'application/json',
        type: 'POST'
    }

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
            { data: 'priority'},
            { data: 'is_active'}
        ],
        rowCallback: row_load_cb
    })

    jQuery('#torrent_table tbody').on 'click', 'tr', row_select_cb
    jQuery('#action_stop').on 'click', action_stop
    jQuery('#action_start').on 'click', action_start
