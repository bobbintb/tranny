OK = 0

label_formatter = (label, series) ->
    pct = Math.round(series.percent)
    "<div class=\"pie_label\">#{label}<br/>#{pct}% (#{series.data[0][1]})</div>";

parse_json = (json_string) ->
    JSON and JSON.parse json_string or jQuery.parseJSON json_string

msg_cur_id = 0

###
  This function will place a user oriented message at the top of the page

  @param {string} Message text to show
  @param {string} Message type, one of: 'success', 'alert', ''
  @param {number} Message timeout in seconds. Fades message out after N seconds
###
msg_user = (msg, msg_type = '', timeout = 5) ->
    if not msg_type in ['success', 'alert', '']
        msg_type = ''
    if msg_type == "success"
        icon_class = "foundicon-checkmark"
    else if msg_type == "alert"
        icon_class = "foundicon-remove"
    else
        icon_class = "foundicon-idea"
    html = """<div id="msgid_#{msg_cur_id}" class="rounded alert-box [success #{msg_type} secondary]" style="display:none;">
           <i class="#{icon_class}"></i>#{msg} <a href="" class="close">&times;</a> </div>"""
    user_messages.append html
    jQuery("#msgid_#{msg_cur_id}").show 500
    if timeout and timeout > 0
        setTimeout "jQuery('#msgid_#{msg_cur_id}').fadeOut(500)", timeout * 1000
    msg_cur_id++

user_messages = jQuery '#user_messages'

###
  Parse the AJAX json response and show any messages to the user before returning the
  parsed object
###
handle_response = (response, callable = false) ->
    response = parse_json(response)
    response.ok = () ->
        @['status'] is OK
    if response['msg']? and response['msg'] isnt ""
        if response['status'] is OK
            msg_user response['msg'], "success", 10
        else
            msg_user response['msg'], "error", 10
    callable?(response)
    return response

###
    Render a pie chart
###
render_pie_chart = (dataset, element_id) ->
    options = {
        series: {
            pie: {
                show: true
                radius: 1
                label: {
                    show: true
                    radius: 0.65
                    formatter: label_formatter
                    background: {
                        opacity: 0
                    }
                }
            }
        }
        legend: {
            show: true
        }
    }
    jQuery.plot element_id, dataset, options

###
    Fetch source totals and render in a pie graph
###
render_service_totals = ->
    jQuery.get "/stats/service_totals", (response) ->
        leader_dataset = parse_json response
        render_pie_chart leader_dataset, "#service_totals"

render_section_totals = ->
    jQuery.get "/stats/section_totals", (response) ->
        section_dataset = parse_json response
        render_pie_chart section_dataset, "#section_totals"

render_service_type_totals = ->
    jQuery.get "/stats/service_type_totals", (response) ->
        type_dataset = parse_json response
        render_pie_chart type_dataset, "#service_type_totals"


filter_remove = (evt) ->
    evt.preventDefault()
    element = jQuery @
    try
        args =
            title: element.data "title"
            quality: element.data "quality"
            section: element.data "section"
    catch Err
        return false
    jQuery.post "/filters/delete", args, (response) ->
        if handle_response(response).ok()
            element.parent().fadeOut 500

filter_add = (evt) ->
    evt.preventDefault()
    console.log "got add"
    element = jQuery @

    try
        quality = element.data "quality"
        section = element.data "section"
        input_element = jQuery("#input_#{section}_#{quality}")
        title = input_element.val()
        args =
            title: title
            quality: quality
            section: section
    catch Err
        return false
    jQuery.post "/filters/add", args, (response) ->
        if handle_response(response).ok()
            console.log "added ok"
            input_element.val ""


feed_save = (evt) ->
    evt.preventDefault()
    feed_name = jQuery(@).data "feed"
    data =
        feed: feed_name
        url: jQuery("##{feed_name}_url").val()
        interval: jQuery("##{feed_name}_interval").val()
        enabled: not jQuery("##{feed_name}_enabled").is(':checked')
    jQuery.post "/rss/save", data, handle_response


feed_delete = (evt) ->
    evt.preventDefault()
    if not confirm "Are you sure you want to delete this RSS feed? This is a non reversable action."
        return false
    feed_name = jQuery(@).data "feed"
    jQuery.post "/rss/delete", {feed: feed_name}, (response) ->
        if handle_response(response).ok()
            jQuery("#feed_#{feed_name}").fadeOut 500

btn_save = (evt) ->
    evt.preventDefault()
    data =
        btn_api_token: jQuery("#btn_api_token").val()
        btn_interval: jQuery("#btn_interval").val()
        btn_enabled: not jQuery("#btn_enabled").is(":checked")
        btn_url: jQuery("#btn_url").val()
    jQuery.post "/services/btn/save", data, handle_response


settings_save = (evt) ->
    evt.preventDefault()
    settings = {}
    for option in jQuery("#settings_form").serializeArray()
        settings[option['name']] = option['value']
    jQuery.post "/settings/save", settings, handle_response


jQuery ->
    if window.location.pathname == "/"
        render_service_totals()
        render_section_totals()
        render_service_type_totals()
    else if window.location.pathname.indexOf("filters") != -1
        jQuery(".filter_remove").on "click", filter_remove
        jQuery(".filter_add").on "click", filter_add
    else if window.location.pathname.indexOf("services") != -1
        jQuery(".btn_save").on "click", btn_save
    else if window.location.pathname.indexOf("settings") != -1
        jQuery(".settings_save").on "click", settings_save
    else if window.location.pathname.indexOf("rss") != -1
        jQuery(".feed_save").on "click", feed_save
        jQuery(".feed_delete").on "click", feed_delete

    jQuery(document).foundation()
