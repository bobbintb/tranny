Deluge API Methods
==================

A list of the methods exported for use by Deluges WebUI module.

Pre Authentication
~~~~~~~~~~~~~~~~~~

Before auth.login -> web.connect sequence the following methods are available

| auth.change_password
| auth.check_session
| auth.delete_session
| auth.login
| web.add_host
| web.add_torrents
| web.connect
| web.connected
| web.deregister_event_listener
| web.disconnect
| web.download_torrent_from_url
| web.get_config
| web.get_events
| web.get_host_status
| web.get_hosts
| web.get_magnet_info
| web.get_plugin_info
| web.get_plugin_resources
| web.get_plugins
| web.get_torrent_files
| web.get_torrent_info
| web.get_torrent_status
| web.register_event_listener
| web.remove_host
| web.set_config
| web.start_daemon
| web.stop_daemon
| web.update_ui
| web.upload_plugin


Post Authentication
~~~~~~~~~~~~~~~~~~~

| auth.change_password
| auth.check_session
| auth.delete_session
| auth.login
| core.add_torrent_file
| core.add_torrent_magnet
| core.add_torrent_url
| core.connect_peer
| core.create_torrent
| core.disable_plugin
| core.enable_plugin
| core.force_reannounce
| core.force_recheck
| core.get_available_plugins
| core.get_cache_status
| core.get_config
| core.get_config_value
| core.get_config_values
| core.get_enabled_plugins
| core.get_filter_tree
| core.get_free_space
| core.get_libtorrent_version
| core.get_listen_port
| core.get_num_connections
| core.get_path_size
| core.get_session_state
| core.get_session_status
| core.get_torrent_status
| core.get_torrents_status
| core.glob
| core.move_storage
| core.pause_all_torrents
| core.pause_torrent
| core.queue_bottom
| core.queue_down
| core.queue_top
| core.queue_up
| core.remove_torrent
| core.rename_files
| core.rename_folder
| core.rescan_plugins
| core.resume_all_torrents
| core.resume_torrent
| core.set_config
| core.set_torrent_auto_managed
| core.set_torrent_file_priorities
| core.set_torrent_max_connections
| core.set_torrent_max_download_speed
| core.set_torrent_max_upload_slots
| core.set_torrent_max_upload_speed
| core.set_torrent_move_completed
| core.set_torrent_move_completed_path
| core.set_torrent_options
| core.set_torrent_prioritize_first_last
| core.set_torrent_remove_at_ratio
| core.set_torrent_stop_at_ratio
| core.set_torrent_stop_ratio
| core.set_torrent_trackers
| core.test_listen_port
| core.upload_plugin
| daemon.get_method_list
| daemon.info
| daemon.shutdown
| web.add_host
| web.add_torrents
| web.connect
| web.connected
| web.deregister_event_listener
| web.disconnect
| web.download_torrent_from_url
| web.get_config
| web.get_events
| web.get_host_status
| web.get_hosts
| web.get_magnet_info
| web.get_plugin_info
| web.get_plugin_resources
| web.get_plugins
| web.get_torrent_files
| web.get_torrent_info
| web.get_torrent_status
| web.register_event_listener
| web.remove_host
| web.set_config
| web.start_daemon
| web.stop_daemon
| web.update_ui
| web.upload_plugin
| webui.get_config
| webui.got_deluge_web
| webui.set_config
| webui.start
| webui.stop
