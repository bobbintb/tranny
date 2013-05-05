label_formatter = (label, series) ->
    pct = Math.round(series.percent)
    "<div class=\"pie_label\">#{label}<br/>#{pct}% (#{series.data[0][1]})</div>";

parse_json = (json_string) ->
    JSON and JSON.parse json_string or jQuery.parseJSON json_string

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
render_rankings = ->
    jQuery.get "/webui/stats/source_leaders", (response) ->
        dataset = parse_json response
        render_pie_chart dataset, "#leader_board"

render_section_totals = ->
    jQuery.get "/webui/stats/section_totals", (response) ->
        dataset = parse_json response
        render_pie_chart dataset, "#section_totals"

init = ->
    render_rankings()
    render_section_totals()

@Tranny =
    render_rankings: render_rankings

jQuery ->
    init()
    console.log "started!"
