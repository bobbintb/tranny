var OK, STATUS_CLIENT_NOT_AVAILABLE, STATUS_FAIL, STATUS_INCOMPLETE_REQUEST, STATUS_INTERNAL_ERROR, STATUS_INVALID_INFO_HASH, STATUS_OK, TorrentTable, action_reannounce, action_recheck, action_remove, action_remove_data, action_start, action_stop, action_torrent_details, action_torrent_peers, action_torrent_speed, add_class, btn_save, bytes_to_iec_size, bytes_to_size, detail_elements, detail_traffic_chart, detail_update_speed, detail_update_timer, endpoint, error_handler, feed_create, feed_delete, feed_reset, feed_save, filter_add, filter_remove, fmt_duration, fmt_timestamp, handle_event_alert, handle_event_speed_overall_response, handle_event_torrent_details_response, handle_event_torrent_files_response, handle_event_torrent_list_response, handle_event_torrent_peers_response, handle_event_torrent_reannounce_response, handle_event_torrent_recheck_response, handle_event_torrent_remove_response, handle_event_torrent_speed_response, handle_event_torrent_stop_response, handle_response, has_class, has_connected, in_url, init_context_menu, init_provider_totals_chart, init_provider_type_totals_chart, init_section_totals_chart, init_traffic_chart, label_formatter, make_pie_chart, msg_cur_id, msg_user, overall_speed_update, overall_speed_update_timer, parse_json, peer_update_timer, rand_int, remove_class, render_peers, render_pie_chart, render_section_totals, render_service_totals, render_service_type_totals, root, row_load_handler, row_remove, selected_class, selected_detail_id, selected_rows, settings_save, show_alert, socket, special_alerts, speed_data, speed_dn, speed_up, speed_update_timer, template, toggle_class, torrent_table, torrent_wrapper, ts, update_speed, user_messages, window_resize_handler, _alert_num, _chart_interval_timer, _iec_sizes, _sizes,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

OK = 0;

label_formatter = function(label, series) {
  var pct;
  pct = Math.round(series.percent);
  return "<div class=\"pie_label\">" + label + "<br/>" + pct + "% (" + series.data[0][1] + ")</div>";
};

parse_json = function(json_string) {
  if (json_string.constructor === String) {
    return jQuery.parseJSON(json_string);
  }
  return json_string;
};

msg_cur_id = 0;


/*
  This function will place a user oriented message at the top of the page

  @param {string} Message text to show
  @param {string} Message type, one of: 'success', 'alert', ''
  @param {number} Message timeout in seconds. Fades message out after N seconds
 */

msg_user = function(msg, msg_type, timeout) {
  var html, icon_class, _ref;
  if (msg_type == null) {
    msg_type = '';
  }
  if (timeout == null) {
    timeout = 5;
  }
  if ((_ref = !msg_type) === 'success' || _ref === 'alert' || _ref === '') {
    msg_type = '';
  }
  if (msg_type === "success") {
    icon_class = "foundicon-checkmark";
  } else if (msg_type === "alert") {
    icon_class = "foundicon-remove";
  } else {
    icon_class = "foundicon-idea";
  }
  html = "<div id=\"msgid_" + msg_cur_id + "\" class=\"rounded alert-box [success " + msg_type + " secondary]\" style=\"display:none;\">\n<i class=\"" + icon_class + "\"></i>" + msg + " <a href=\"\" class=\"close\">&times;</a> </div>";
  user_messages.append(html);
  jQuery("#msgid_" + msg_cur_id).show(500);
  if (timeout && timeout > 0) {
    setTimeout("jQuery('#msgid_" + msg_cur_id + "').fadeOut(500)", timeout * 1000);
  }
  return msg_cur_id++;
};

user_messages = jQuery('#user_messages');


/*
  Parse the AJAX json response and show any messages to the user before returning the
  parsed object
 */

handle_response = function(response, callable) {
  if (callable == null) {
    callable = false;
  }
  response = parse_json(response);
  response.ok = function() {
    return this['status'] === OK;
  };
  if ((response['msg'] != null) && response['msg'] !== "") {
    if (response['status'] === OK) {
      msg_user(response['msg'], "success", 10);
    } else {
      msg_user(response['msg'], "error", 10);
    }
  }
  if (typeof callable === "function") {
    callable(response);
  }
  return response;
};


/*
    Render a pie chart
 */

render_pie_chart = function(dataset, element_id) {
  var options;
  options = {
    series: {
      pie: {
        show: true,
        radius: 1,
        label: {
          show: true,
          radius: 0.65,
          formatter: label_formatter,
          background: {
            opacity: 0
          }
        }
      }
    },
    legend: {
      show: true
    }
  };
  return jQuery.plot(element_id, dataset, options);
};


/*
    Fetch source totals and render in a pie graph
 */

render_service_totals = function() {
  return jQuery.get("/stats/service_totals", function(response) {
    var leader_dataset;
    leader_dataset = parse_json(response);
    return render_pie_chart(leader_dataset, "#service_totals");
  });
};

render_section_totals = function() {
  return jQuery.get("/stats/section_totals", function(response) {
    var section_dataset;
    section_dataset = parse_json(response);
    return render_pie_chart(section_dataset, "#section_totals");
  });
};

render_service_type_totals = function() {
  return jQuery.get("/stats/service_type_totals", function(response) {
    var type_dataset;
    type_dataset = parse_json(response);
    return render_pie_chart(type_dataset, "#service_type_totals");
  });
};

filter_remove = function(evt) {
  var Err, args, element;
  evt.preventDefault();
  element = jQuery(this);
  try {
    args = {
      title: element.data("title"),
      quality: element.data("quality"),
      section: element.data("section")
    };
  } catch (_error) {
    Err = _error;
    return false;
  }
  return jQuery.post("/filters/delete", args, function(response) {
    if (handle_response(response).ok()) {
      return element.parent().fadeOut(500);
    }
  });
};

filter_add = function(evt) {
  var Err, args, element, input_element, quality, section, title;
  evt.preventDefault();
  console.log("got add");
  element = jQuery(this);
  try {
    quality = element.data("quality");
    section = element.data("section");
    input_element = jQuery("#input_" + section + "_" + quality);
    title = input_element.val();
    args = {
      title: title,
      quality: quality,
      section: section
    };
  } catch (_error) {
    Err = _error;
    return false;
  }
  return jQuery.post("/filters/add", args, function(response) {
    if (handle_response(response).ok()) {
      console.log("added ok");
      return input_element.val("");
    }
  });
};

feed_create = function(evt) {
  var data;
  evt.preventDefault();
  data = {
    feed: jQuery("#new_feed_name").val(),
    url: jQuery("#new_url").val(),
    interval: jQuery("#new_interval").val(),
    enabled: jQuery("#new_enabled").val()
  };
  return jQuery.post("/rss/create", data, function(response) {
    jQuery("#rss_add").foundation('reveal', 'close');
    if (handle_response(response).ok()) {
      return location.reload();
    }
  });
};

feed_save = function(evt) {
  var data, feed_name;
  evt.preventDefault();
  feed_name = jQuery(this).data("feed");
  data = {
    feed: feed_name,
    url: jQuery("#" + ("" + feed_name + "_url")).val(),
    interval: jQuery("#" + ("" + feed_name + "_interval")).val(),
    enabled: jQuery("#" + ("" + feed_name + "_enabled")).is(':checked')
  };
  return jQuery.post("/rss/save", data, handle_response);
};

feed_delete = function(evt) {
  var feed_name;
  evt.preventDefault();
  if (!confirm("Are you sure you want to delete this RSS feed? This is a non reversable action.")) {
    return false;
  }
  feed_name = jQuery(this).data("feed");
  return jQuery.post("/rss/delete", {
    feed: feed_name
  }, function(response) {
    if (handle_response(response).ok()) {
      return jQuery("#feed_" + feed_name).fadeOut(500);
    }
  });
};

feed_reset = function(evt) {
  var feed_name;
  evt.preventDefault();
  feed_name = jQuery(this).data("feed");
  return jQuery("#" + feed_name + "_form")[0].reset();
};

btn_save = function(evt) {
  var data;
  evt.preventDefault();
  data = {
    btn_api_token: jQuery("#btn_api_token").val(),
    btn_interval: jQuery("#btn_interval").val(),
    btn_enabled: !jQuery("#btn_enabled").is(":checked"),
    btn_url: jQuery("#btn_url").val()
  };
  return jQuery.post("/services/btn/save", data, handle_response);
};

settings_save = function(evt) {
  var option, settings, _i, _len, _ref;
  evt.preventDefault();
  settings = {};
  _ref = jQuery("#settings_form").serializeArray();
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    option = _ref[_i];
    settings[option['name']] = option['value'];
  }
  return jQuery.post("/settings/save", settings, handle_response);
};

jQuery(function() {
  if (window.location.pathname.indexOf("filters") !== -1) {
    jQuery(".filter_remove").on("click", filter_remove);
    jQuery(".filter_add").on("click", filter_add);
  } else if (window.location.pathname.indexOf("services") !== -1) {
    jQuery(".btn_save").on("click", btn_save);
  } else if (window.location.pathname.indexOf("settings") !== -1) {
    jQuery(".settings_save").on("click", settings_save);
  } else if (window.location.pathname.indexOf("rss") !== -1) {
    jQuery(".feed_save").on("click", feed_save);
    jQuery(".feed_delete").on("click", feed_delete);
    jQuery(".feed_create").on("click", feed_create);
    jQuery(".feed_reset").on("click", feed_reset);
  }
  return jQuery(document).foundation();
});

root = typeof exports !== "undefined" && exports !== null ? exports : this;


/* Contains a list of currently selected row id's (info_hash's) */

selected_rows = [];


/* class defining selected rows in the torrent listing */

selected_class = 'selected';


/* Currently selected torrent that should be used in the detail display */

selected_detail_id = false;


/* Application endpoint prefix */

endpoint = "http://" + document.domain + ":" + location.port + "/ws";


/* Update interval for the traffic graph in ms */

update_speed = 1000;


/* Update interval for the stats/detail tabs */

detail_update_speed = update_speed * 2;


/* Timer to update the selected torrent detail page */

detail_update_timer = null;


/* Timer for the overall speed indicator */

overall_speed_update_timer = null;


/* Timer to update the selected torrent speed graph */

speed_update_timer = null;


/* Timer to update the selected torrent peer list */

peer_update_timer = null;


/* socket.io-client instance */

socket = null;


/* Keep track of if we have connected before or not */

has_connected = false;


/* Element used to show flash message */

user_messages = jQuery("#user_messages");


/* Overall speed indicator elements */

speed_up = jQuery("#speed_up");

speed_dn = jQuery("#speed_dn");


/* Traffic chart instance */

detail_traffic_chart = null;

STATUS_OK = 0;

STATUS_FAIL = 1;

STATUS_INTERNAL_ERROR = 3;

STATUS_CLIENT_NOT_AVAILABLE = 5;

STATUS_INCOMPLETE_REQUEST = 10;

STATUS_INVALID_INFO_HASH = 11;


/* Use mustache/jinja style interpolation  {{ }} */

_.templateSettings.interpolate = /{{([\s\S]+?)}}/g;


/* Compiled _ templates */

template = {
  progress: _.template("<div class=\"progress {{ style }}\">\n    <span class=\"count\">{{ data }} %</span>\n    <span class=\"meter\" style=\"width: {{ data }}\"></span>\n</div>"),
  ratio: _.template("<span class=\"{{ class_name }}\">{{ data }}</span>"),
  peer_info: _.template("{{ num }} ({{ total }})")
};

init_context_menu = function() {
  context.init({
    fadeSpeed: 100,
    above: 'auto',
    preventDoubleContext: true,
    compress: false
  });
  return context.attach('.row', [
    {
      header: 'Options'
    }, {
      text: '<i class="icon-play"></i> Start',
      href: '#',
      action: function() {
        return action_start();
      }
    }, {
      text: '<i class="icon-pause"></i> Stop',
      href: '#',
      action: function() {
        return action_stop();
      }
    }, {
      divider: true
    }, {
      text: '<i class="icon-minus"></i> Remove',
      href: '#',
      action: function() {
        return action_remove();
      }
    }, {
      text: '<i class="icon-minus"></i> Remove Data',
      href: '#',
      action: function() {
        return action_remove_data();
      }
    }, {
      divider: true
    }, {
      text: '<i class="icon-arrows-cw"></i> Recheck Data',
      href: '#',
      action: function() {
        return action_recheck();
      }
    }, {
      text: '<i class="icon-signal"></i> Reannounce',
      href: '#',
      action: function() {
        return action_reannounce();
      }
    }
  ]);
};

has_class = function(elem, className) {
  return new RegExp(' ' + className + ' ').test(' ' + elem.className + ' ');
};

add_class = function(elem, className) {
  if (!has_class(elem, className)) {
    return elem.className += ' ' + className;
  }
};

remove_class = function(elem, className) {
  var newClass;
  newClass = ' ' + elem.className.replace(/[\t\r\n]/g, ' ') + ' ';
  if (has_class(elem, className)) {
    while (newClass.indexOf(' ' + className + ' ') >= 0) {
      newClass = newClass.replace(' ' + className + ' ', ' ');
    }
    return elem.className = newClass.replace(/^\s+|\s+$/g, '');
  }
};

toggle_class = function(elem, className) {
  var newClass;
  newClass = " " + (elem.className.replace(/[\t\r\n]/g, ' ')) + " ";
  if (has_class(elem, className)) {
    while (newClass.indexOf(' ' + className + ' ') >= 0) {
      newClass = newClass.replace(' ' + className + ' ', ' ');
    }
    return elem.className = newClass.replace(/^\s+|\s+$/g, '');
  } else {
    return elem.className += ' ' + className;
  }
};


/*
    Class to handle interactions and rendering of the torrent table.

    This does not use jQuery nor does it use string concatenation to generate
    table rows & cells. This is purposefully done to ensure maximum client
    side performance for users with large numbers of torrents loaded.
 */

TorrentTable = (function() {

  /* Allow self reference when @ doesnt refer to this instance */
  var self, torrents;

  self = {};

  torrents = {};

  function TorrentTable(dom_id) {
    this.dom_id = dom_id;
    self = this;
    this.table_body = document.querySelector(dom_id + " article");
    this.cols = ['name', 'size', 'progress', 'ratio', 'up_rate', 'dn_rate', 'leechers', 'peers', 'priority', 'is_active'];
    this.info_hashes = {};
  }


  /*
  We are using dom elements here over plain strings to keep things performant
   */

  TorrentTable.prototype.insert_row = function(row) {
    var class_name, div_col, div_row, key, key_name, style, _i, _len, _ref, _ref1;
    if (_ref = row['info_hash'], __indexOf.call(this.info_hashes, _ref) >= 0) {
      return;
    }
    div_row = document.createElement("div");
    div_row.setAttribute('id', row['info_hash']);
    div_row.className = "row torrent_context_menu";
    div_row.onclick = this.row_select_handler;
    _ref1 = this.cols;
    for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
      key = _ref1[_i];
      div_col = document.createElement("div");
      key_name = key === 'progress' ? 'completed' : key;
      div_col.setAttribute("class", key_name);
      if (key === "priority" || key === "is_active") {
        break;
      }
      switch (key) {
        case "progress":
          style = Math.floor(row[key] >= 100) ? "success" : "alert";
          div_col.innerHTML = template['progress']({
            'style': style,
            'data': row[key].toFixed(2)
          });
          break;
        case "ratio":
          class_name = row[key] < 1 ? 'alert' : 'success';
          div_col.innerHTML = template['ratio']({
            'class_name': class_name,
            'data': row[key].toFixed(2)
          });
          break;
        case "seeders":
          div_col.appendChild(document.createTextNode(template['peer_info']({
            'num': row[key],
            'total': row['total_seeders']
          })));
          break;
        case "peers":
          div_col.appendChild(document.createTextNode(template['peer_info']({
            'num': row[key],
            'total': row['total_peers']
          })));
          break;
        case "size":
          div_col.appendChild(document.createTextNode(bytes_to_size(row[key])));
          break;
        case "up_rate":
        case "dn_rate":
          div_col.appendChild(document.createTextNode(bytes_to_size(row[key], true)));
          break;
        default:
          div_col.appendChild(document.createTextNode(row[key]));
      }
      torrents[row['info_hash']] = {
        row: div_row.appendChild(div_col)
      };
    }
    return this.table_body.appendChild(div_row);
  };

  TorrentTable.prototype.add_rows = function(rows) {
    var row;
    return rows = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = rows.length; _i < _len; _i++) {
        row = rows[_i];
        _results.push(this.insert_row(row));
      }
      return _results;
    }).call(this);
  };

  TorrentTable.prototype.update = function(data) {};

  TorrentTable.prototype.remove = function(info_hash) {
    return this.table_body.removeChild(this.table_body.getElementById(info_hash));
  };


  /*
      Called when a user selects a row with the cursor. Will update the currently selected rows.
      If the user holds ctrl while clicking the row will be added to the selected_rows array. Otherwise
      the row will be "activated" and show more detailed information for that row in another panel.
   */

  TorrentTable.prototype.row_select_handler = function(e) {
    var index, row_id;
    row_id = this.id;
    if (e.ctrlKey) {
      index = _.indexOf(selected_rows, row_id);
      if (index === -1) {
        selected_rows.push(row_id);
      } else {
        selected_rows.splice(index, 1);
      }
      return toggle_class(this, selected_class);
    } else {
      return self.select_row(row_id);
    }
  };


  /*
      Will select a row outside of an event context so it can be called from
      any context. eg: context menus
   */

  TorrentTable.prototype.select_row = function(row_id) {
    var element, selected_element, _i, _len, _ref;
    _ref = self.table_body.querySelectorAll(".selected");
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      element = _ref[_i];
      remove_class(element, "selected");
    }
    selected_element = document.getElementById(row_id);
    selected_rows = [row_id];
    selected_detail_id = row_id;
    if (detail_update_timer !== null) {
      clearTimeout(detail_update_timer);
    }
    if (speed_update_timer !== null) {
      clearTimeout(speed_update_timer);
    }
    if (peer_update_timer !== null) {
      clearTimeout(peer_update_timer);
    }
    action_torrent_details();
    action_torrent_speed();
    action_torrent_peers();
    init_traffic_chart();
    if (!has_class(selected_element, selected_class)) {
      return add_class(selected_element, selected_class);
    }
  };

  return TorrentTable;

})();

torrent_table = null;

make_pie_chart = function(id, data, series, title) {
  if (title == null) {
    title = "";
  }
  return jQuery(id).highcharts({
    chart: {
      plotBackgroundColor: null,
      plotBorderWidth: 1,
      plotShadow: false
    },
    title: {
      text: title
    },
    tooltip: {
      pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
    },
    plotOptions: {
      pie: {
        allowPointSelect: true,
        cursor: 'pointer',
        dataLabels: {
          enabled: false
        },
        showInLegend: true
      }
    },
    series: series,
    credits: {
      enabled: false
    }
  });
};

init_provider_totals_chart = function() {
  var series_data_obj;
  series_data_obj = [
    {
      type: 'pie',
      name: 'Provider Totals',
      data: provider_totals
    }
  ];
  return make_pie_chart("#provider_totals", null, series_data_obj, null);
};

init_section_totals_chart = function() {
  var series_data_obj;
  series_data_obj = [
    {
      type: 'pie',
      name: 'Section Totals',
      data: section_totals
    }
  ];
  return make_pie_chart("#section_totals", null, series_data_obj, null);
};

init_provider_type_totals_chart = function() {
  var series_data_obj;
  series_data_obj = [
    {
      type: 'pie',
      name: 'Section Totals',
      data: provider_type_totals
    }
  ];
  return make_pie_chart("#provider_type_totals", null, series_data_obj, null);
};

rand_int = function() {
  return Math.floor(Math.random() * 100000000);
};

speed_data = [];

_chart_interval_timer = null;


/*
    (re)Initialize the speed detail graph. This needs to be called each time a new single
    torrent is selected for details.

    This function will clear memory of existing charts and remove the existing interval
    timer used to update it.
 */

init_traffic_chart = function(id, title) {
  if (id == null) {
    id = "#detail-traffic-chart";
  }
  if (title == null) {
    title = null;
  }
  if (detail_traffic_chart) {
    detail_traffic_chart.highcharts().destroy();
  }
  if (_chart_interval_timer) {
    clearInterval(_chart_interval_timer);
  }
  return detail_traffic_chart = jQuery(id).highcharts({
    chart: {
      alignTicks: true,
      reflow: true,
      type: 'areaspline',
      events: {
        load: function() {
          var series_dn, series_up;
          series_up = this.series[0];
          series_dn = this.series[1];
          return _chart_interval_timer = setInterval((function() {
            var speed, x;
            speed = speed_data.pop();
            if (!speed) {
              speed = [0, 0];
            }
            x = (new Date()).getTime();
            if (series_up.data.length >= 100) {
              series_up.data[0].remove();
              series_dn.data[0].remove();
            }
            series_up.addPoint([x, speed[0]], true, false);
            return series_dn.addPoint([x, speed[1]], true, false);
          }), 1000);
        }
      }
    },
    title: {
      text: title
    },
    legend: {
      layout: 'vertical',
      align: 'left',
      verticalAlign: 'top',
      x: 90,
      y: 30,
      floating: true,
      borderWidth: 1,
      backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
    },
    xAxis: {
      type: 'datetime',
      tickPixelInterval: 150
    },
    yAxis: {
      title: {
        text: 'Speed'
      },
      min: 0,
      floor: 0,
      startOnTick: true,
      showEmpty: false
    },
    tooltip: {
      shared: true,
      formatter: (function() {
        var d, formattedTime, hours, minutes, s, seconds;
        d = new Date(this.x);
        hours = d.getHours();
        minutes = d.getMinutes();
        seconds = d.getSeconds();
        formattedTime = hours + ':' + minutes + ':' + seconds;
        s = "<b>" + formattedTime + "</b>";
        jQuery.each(this.points, function() {
          return s += "<br/>" + this.series.name + ": " + (bytes_to_size(this.y, true));
        });
        return s;
      })
    },
    credits: {
      enabled: false
    },
    plotOptions: {
      areaspline: {
        fillOpacity: 0.5
      }
    },
    series: [
      {
        name: 'Upload Speed'
      }, {
        name: 'Download Speed'
      }
    ]
  });
};


/*
    Called for each new row loaded into the data table

    @param {string} DT_RowId defined for the row ( which corresponds to the info_hash )
    @param {object} The rows data object
    @param {number} Index of the row in the table
 */

row_load_handler = function(row, data, displayIndex) {
  if (jQuery.inArray(data.DT_RowId, selected_rows) !== -1) {
    return jQuery(row).addClass(selected_class);
  }
};


/*
Remove a row from the torrent list by its info_hash
 */

row_remove = function(info_hash) {
  return jQuery("#" + info_hash).remove();
};


/* Client actions */

action_recheck = function() {
  if (selected_rows) {
    socket.emit('event_torrent_recheck', {
      info_hash: selected_rows
    });
    return false;
  }
};

action_reannounce = function() {
  if (selected_rows) {
    return socket.emit('event_torrent_announce', {
      info_hash: selected_rows
    });
  }
};

action_remove = function() {
  var info_hash, _i, _len, _results;
  _results = [];
  for (_i = 0, _len = selected_rows.length; _i < _len; _i++) {
    info_hash = selected_rows[_i];
    _results.push(socket.emit('event_torrent_remove', {
      info_hash: info_hash,
      remove_data: false
    }));
  }
  return _results;
};

action_remove_data = function() {
  var info_hash, _i, _len, _results;
  _results = [];
  for (_i = 0, _len = selected_rows.length; _i < _len; _i++) {
    info_hash = selected_rows[_i];
    _results.push(socket.emit('event_torrent_remove', {
      info_hash: info_hash,
      remove_data: true
    }));
  }
  return _results;
};

action_stop = function() {
  if (selected_rows) {
    return socket.emit('event_torrent_stop', {
      info_hash: selected_rows
    });
  }
};

action_start = function() {
  if (selected_rows) {
    return socket.emit('event_torrent_start', {
      info_hash: selected_rows
    });
  }
};

action_torrent_details = function() {
  if (selected_detail_id) {
    return socket.emit('event_torrent_details', {
      info_hash: selected_detail_id
    });
  }
};

action_torrent_speed = function() {
  if (selected_detail_id) {
    socket.emit('event_torrent_speed', {
      info_hash: selected_detail_id
    });
  }
  return speed_update_timer = setTimeout(action_torrent_speed, update_speed);
};

action_torrent_peers = function() {
  if (selected_detail_id) {
    socket.emit('event_torrent_peers', {
      info_hash: selected_detail_id
    });
  }
  return peer_update_timer = setTimeout(action_torrent_peers, update_speed);
};

special_alerts = {};


/*
    Response handlers for sent websocket events
 */

error_handler = function(func, message) {
  if (message['status'] === STATUS_CLIENT_NOT_AVAILABLE) {
    if (!special_alerts[STATUS_CLIENT_NOT_AVAILABLE]) {
      return special_alerts[STATUS_CLIENT_NOT_AVAILABLE] = show_alert("Torrent client not online", 'error', 0);
    }
  } else {
    return func(message);
  }
};

handle_event_torrent_files_response = function(message) {
  return false;
};

handle_event_torrent_reannounce_response = function(message) {
  return show_alert("Got reannounce response");
};

handle_event_torrent_recheck_response = function(message) {
  return show_alert("Got recheck response");
};

handle_event_alert = function(message) {
  return show_alert(message['msg'], message['msg_type']);
};

handle_event_torrent_list_response = function(message) {
  return torrent_table.add_rows(message['data']);
};

handle_event_torrent_stop_response = function(message) {
  return show_alert(message['msg'], message['msg_type']);
};

handle_event_speed_overall_response = function(message) {
  speed_up.text(bytes_to_size(message['data']['up'], true));
  return speed_dn.text(bytes_to_size(message['data']['dn'], true));
};

handle_event_torrent_speed_response = function(message) {
  return speed_data.push([message['data']['upload_payload_rate'], message['data']['download_payload_rate']]);
};

handle_event_torrent_peers_response = function(message) {
  var client, client_chart_data, count, country, peer_chart_data, sort_client, _ref, _ref1;
  sort_client = function(peer) {
    return (peer['client'].split(" ")).slice(0, -1).toString();
  };
  peer_chart_data = [];
  client_chart_data = [];
  _ref = _.countBy(message['data']['peers'], 'country');
  for (country in _ref) {
    count = _ref[country];
    peer_chart_data.push({
      label: country,
      value: count
    });
  }
  _ref1 = _.countBy(message['data']['peers'], sort_client);
  for (client in _ref1) {
    count = _ref1[client];
    client_chart_data.push({
      label: client,
      value: count
    });
  }
  return render_peers(message['data']['peers']);
};

handle_event_torrent_remove_response = function(message) {
  if (message['status'] === 0) {
    return jQuery("#" + message['data']['info_hash']).remove();
  }
};

handle_event_torrent_details_response = function(message) {
  var data, eta, peers, pieces, seeds;
  data = message['data'];
  eta = data['eta'] === 0 ? '∞' : fmt_duration(data['eta']);
  seeds = "" + data['num_seeds'] + " (" + data['total_seeds'] + ")";
  peers = "" + data['num_peers'] + " (" + data['total_peers'] + ")";
  pieces = "" + data['num_pieces'] + " (" + (bytes_to_iec_size(data['piece_length'])) + ")";
  detail_elements.detail_downloaded.text(bytes_to_size(data['total_done']));
  detail_elements.detail_uploaded.text(bytes_to_size(data['total_uploaded']));
  detail_elements.detail_tracker_status.text(data['tracker_status']);
  detail_elements.detail_ratio.text(data['ratio'].toFixed(2));
  detail_elements.detail_next_announce.text(data['next_announce']);
  detail_elements.detail_speed_dl.text(bytes_to_size(data['download_payload_rate'], true));
  detail_elements.detail_speed_ul.text(bytes_to_size(data['upload_payload_rate'], true));
  detail_elements.detail_eta.text(eta);
  detail_elements.detail_pieces.text(pieces);
  detail_elements.detail_seeders.text(seeds);
  detail_elements.detail_peers.text(peers);
  detail_elements.detail_availability.text(data['distributed_copies']);
  detail_elements.detail_active_time.text(fmt_duration(data['active_time']));
  detail_elements.detail_seeding_time.text(fmt_duration(data['seeding_time']));
  detail_elements.detail_added_on.text(fmt_timestamp(data['time_added']));
  detail_elements.detail_name.text(data['name']);
  detail_elements.detail_hash.text(selected_detail_id);
  detail_elements.detail_path.text(data['save_path']);
  detail_elements.detail_total_size.text(data['total_size']);
  detail_elements.detail_num_files.text(data['detail_num_files']);
  detail_elements.detail_status.text(data['detail_status']);
  return detail_elements.detail_tracker.text(data['tracker_host']);
};

_alert_num = 0;


/*
    Show an alert popup message to the user. The message will fade after a few seconds have passed

    @param {string} Message to display
    @param {string} Type of message (css class used)
    @param {number} Time in seconds to show the message
 */

show_alert = function(msg, msg_type, ttl) {
  if (msg_type == null) {
    msg_type = 'info';
  }
  if (ttl == null) {
    ttl = 5;
  }
  _alert_num += 1;
  console.log(ttl, msg, _alert_num);
  user_messages.append("<div id=\"alert_" + _alert_num + "\" data-alert class=\"alert-box radius " + msg_type + "\">" + msg + "<a href=\"#\" class=\"close\">&times;</a></div>");
  if (ttl > 0) {
    setTimeout(((function(_this) {
      return function() {
        return jQuery("#alert_" + _alert_num).fadeOut(function() {
          return this.remove();
        });
      };
    })(this)), ttl * 1000);
  }
  return _alert_num;
};

fmt_timestamp = function(ts) {
  return moment.unix(ts).format('D/M/YYYY hh:mm:s');
};

fmt_duration = function(seconds) {
  if (!seconds) {
    return "n/a";
  }
  return moment.duration(seconds, 'seconds').humanize();
};

overall_speed_update = function() {
  socket.emit('event_speed_overall', {});
  return overall_speed_update_timer = setTimeout(overall_speed_update, update_speed);
};

_sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

bytes_to_size = function(bytes, per_sec) {
  var human_size, i, k;
  if (per_sec == null) {
    per_sec = false;
  }
  if (bytes <= 1000) {
    if (per_sec) {
      return "" + bytes + " B/s";
    } else {
      return "" + bytes + " B";
    }
  }
  k = 1000;
  i = Math.floor(Math.log(bytes) / Math.log(k));
  human_size = (bytes / Math.pow(k, i)).toFixed(2) + ' ' + _sizes[i];
  if (per_sec) {
    human_size = "" + human_size + "/s";
  }
  return human_size;
};

_iec_sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];

bytes_to_iec_size = function(bytes, per_sec) {
  var human_size, i, k;
  if (per_sec == null) {
    per_sec = false;
  }
  if (bytes <= 1024) {
    if (per_sec) {
      return "" + bytes + " B/s";
    } else {
      return "" + bytes + " B";
    }
  }
  k = 1024;
  i = Math.floor(Math.log(bytes) / Math.log(k));
  human_size = (bytes / Math.pow(k, i)).toFixed(2) + ' ' + _sizes[i];
  if (per_sec) {
    human_size = "" + human_size + "/s";
  }
  return human_size;
};

render_peers = function(peer_list) {
  var output_html, peer, _i, _len;
  output_html = [];
  for (_i = 0, _len = peer_list.length; _i < _len; _i++) {
    peer = peer_list[_i];
    output_html.push("<tr>\n    <td><img src=\"/static/img/country/" + (peer['country'].toLowerCase()) + ".png\"></td>\n    <td>" + peer['ip'] + "</td>\n    <td>" + peer['client'] + "</td>\n    <td><div class=\"progress\"><span class=\"meter\" style=\"" + (peer['progress'] * 100) + "\"></span></div></td>\n    <td>" + (bytes_to_size(peer['down_speed'], true)) + "</td>\n    <td>" + (bytes_to_size(peer['up_speed'], true)) + "</td>\n</tr>");
  }
  return jQuery("#peer_list tbody").html(output_html.join(""));
};


/* Return the current unix timestamp in seconds */

ts = function() {
  return Math.round(new Date().getTime() / 1000) | 0;
};


/* Cache all the detail element nodes */

detail_elements = {
  detail_downloaded: jQuery("#detail_downloaded"),
  detail_uploaded: jQuery("#detail_uploaded"),
  detail_ratio: jQuery("#detail_ratio"),
  detail_next_announce: jQuery("#detail_next_announce"),
  detail_tracker_status: jQuery("#detail_tracker_status"),
  detail_speed_dl: jQuery("#detail_speed_dl"),
  detail_speed_ul: jQuery("#detail_speed_ul"),
  detail_eta: jQuery("#detail_eta"),
  detail_pieces: jQuery("#detail_pieces"),
  detail_seeders: jQuery("#detail_seeders"),
  detail_peers: jQuery("#detail_peers"),
  detail_availability: jQuery("#detail_availability"),
  detail_active_time: jQuery("#detail_active_time"),
  detail_seeding_time: jQuery("#detail_seeding_time"),
  detail_added_on: jQuery("#detail_added_on"),
  detail_name: jQuery("#detail_name"),
  detail_hash: jQuery("#detail_hash"),
  detail_path: jQuery("#detail_path"),
  detail_total_size: jQuery("#detail_total_size"),
  detail_num_files: jQuery("#detail_num_files"),
  detail_comment: jQuery("#detail_comment"),
  detail_status: jQuery("#detail_status"),
  detail_tracker: jQuery("#detail_tracker")
};


/* Check for the existence of a string in the URL */

in_url = function(text) {
  return window.location.pathname.indexOf(text) !== -1;
};

torrent_wrapper = document.querySelector("#torrents article");

window_resize_handler = function() {
  return torrent_wrapper.style.height = "" + (window.innerHeight - 465) + "px";
};

jQuery(function() {
  if (in_url("/torrents/")) {
    init_context_menu();
    torrent_table = new TorrentTable("#torrents");
    root.t = torrent_table;
    detail_traffic_chart = init_traffic_chart("#detail-traffic-chart");
    jQuery('#torrents article').perfectScrollbar({
      suppressScrollX: true
    });
  }
  socket = io.connect(endpoint);
  socket.on('connect', function() {
    var e;
    if (has_connected) {
      show_alert("Reconnected to backend successfully", null, 5);
    }
    if (in_url("/torrents/")) {
      try {
        torrent_table.fnClearTable();
      } catch (_error) {
        e = _error;
        null;
      }
      socket.emit('event_torrent_list');
    }
    overall_speed_update();
    return has_connected = true;
  });
  socket.on('event_speed_overall_response', (function(_this) {
    return function(message) {
      return error_handler(handle_event_speed_overall_response, message);
    };
  })(this));
  if (in_url("/torrents/")) {
    socket.on('event_torrent_recheck', (function(_this) {
      return function(message) {
        return error_handler(handle_event_torrent_recheck_response, message);
      };
    })(this));
    socket.on('event_torrent_peers_response', handle_event_torrent_peers_response);
    socket.on('event_torrent_speed_response', handle_event_torrent_speed_response);
    socket.on('event_torrent_details_response', handle_event_torrent_details_response);
    socket.on('event_torrent_files', handle_event_torrent_files_response);
    socket.on('event_torrent_list_response', (function(_this) {
      return function(message) {
        return error_handler(handle_event_torrent_list_response, message);
      };
    })(this));
    socket.on('event_torrent_remove_response', handle_event_torrent_remove_response);
    socket.on('event_alert', handle_event_alert);
    socket.on('event_torrent_reannounce_response', handle_event_torrent_reannounce_response);
    socket.on('event_torrent_stop_response', handle_event_torrent_stop_response);
    jQuery('#action_stop').on('click', action_stop);
    jQuery('#action_start').on('click', action_start);
    jQuery('#action_recheck').on('click', action_recheck);
    jQuery('#action_reannounce').on('click', action_reannounce);
    jQuery('#action_remove').on('click', action_remove);
    jQuery('#action_remove_data').on('click', action_remove_data);
    window_resize_handler();
    jQuery(window).on('resize', window_resize_handler);
  }
  if (in_url("/home")) {
    init_provider_totals_chart();
    init_section_totals_chart();
    return init_provider_type_totals_chart();
  }
});

Highcharts.theme = {
  colors: ["#2b908f", "#90ee7e", "#f45b5b", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee", "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
  chart: {
    backgroundColor: null,
    style: {
      fontFamily: '"Helvetica Neue", Helvetica, Roboto, Arial, sans-serif'
    },
    plotBorderColor: null
  },
  title: {
    title: {
      style: {
        color: '#E0E0E3',
        textTransform: 'uppercase',
        fontSize: '20px'
      }
    },
    subtitle: {
      style: {
        color: '#E0E0E3',
        textTransform: 'uppercase'
      }
    },
    xAxis: {
      gridLineColor: '#707073',
      labels: {
        style: {
          color: '#E0E0E3'
        }
      },
      lineColor: '#707073',
      minorGridLineColor: '#505053',
      tickColor: '#707073',
      title: {
        style: {
          color: '#A0A0A3'
        }
      }
    },
    yAxis: {
      gridLineColor: '#707073',
      labels: {
        style: {
          color: '#E0E0E3'
        }
      },
      lineColor: '#707073',
      minorGridLineColor: '#505053',
      tickColor: '#707073',
      tickWidth: 1,
      title: {
        style: {
          color: '#A0A0A3'
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      style: {
        color: '#F0F0F0'
      }
    },
    plotOptions: {
      pie: {
        borderColor: "#666"
      },
      series: {
        dataLabels: {
          color: '#B0B0B3'
        },
        marker: {
          lineColor: '#333'
        }
      },
      'boxplot': {
        fillColor: '#505053'
      },
      candlestick: {
        lineColor: 'white'
      },
      errorbar: {
        color: 'white'
      }
    },
    legend: {
      itemStyle: {
        color: '#E0E0E3'
      },
      itemHoverStyle: {
        color: '#FFF'
      },
      itemHiddenStyle: {
        color: '#606063'
      }
    },
    credits: {
      style: {
        color: '#666'
      }
    },
    labels: {
      style: {
        color: '#707073'
      }
    },
    drilldown: {
      activeAxisLabelStyle: {
        color: '#F0F0F3'
      },
      activeDataLabelStyle: {
        color: '#F0F0F3'
      }
    },
    navigation: {
      buttonOptions: {
        symbolStroke: '#DDDDDD',
        theme: {
          fill: '#505053'
        }
      }
    },
    rangeSelector: {
      buttonTheme: {
        fill: '#505053',
        stroke: '#000000',
        style: {
          color: '#CCC'
        },
        states: {
          hover: {
            fill: '#707073',
            stroke: '#000000',
            style: {
              color: 'white'
            }
          },
          select: {
            fill: '#000003',
            stroke: '#000000',
            style: {
              color: 'white'
            }
          }
        }
      },
      inputBoxBorderColor: '#505053',
      inputStyle: {
        backgroundColor: '#333',
        color: 'silver'
      },
      labelStyle: {
        color: 'silver'
      }
    },
    navigator: {
      handles: {
        backgroundColor: '#666',
        borderColor: '#AAA'
      },
      outlineColor: '#CCC',
      maskFill: 'rgba(255,255,255,0.1)',
      series: {
        color: '#7798BF',
        lineColor: '#A6C7ED'
      },
      xAxis: {
        gridLineColor: '#505053'
      }
    },
    scrollbar: {
      barBackgroundColor: '#808083',
      barBorderColor: '#808083',
      buttonArrowColor: '#CCC',
      buttonBackgroundColor: '#606063',
      buttonBorderColor: '#606063',
      rifleColor: '#FFF',
      trackBackgroundColor: '#404043',
      trackBorderColor: '#404043'
    },
    legendBackgroundColor: 'rgba(0, 0, 0, 0.5)',
    background2: '#505053',
    dataLabelsColor: '#B0B0B3',
    textColor: '#C0C0C0',
    contrastTextColor: '#F0F0F3',
    maskColor: 'rgba(255,255,255,0.3)'
  }
};

Highcharts.setOptions(Highcharts.theme);

//# sourceMappingURL=app.js.map
