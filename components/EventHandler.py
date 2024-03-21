
class EventHandler:

    EVENT_ON_SCAN_RANGE_DATA = 'on_scan_range_data'
    EVENT_ON_GET_CONFIGS = 'on_get_configs'
    EVENT_ON_GET_ERROR = 'on_get_error'
    EVENT_ON_CONNECTION_SUCCESS = 'on_connection_success'

    _events_list = {}

    @staticmethod
    def add_event(event_key, event_callback):
        if event_key not in EventHandler._events_list:
            EventHandler._events_list[event_key] = []

        EventHandler._events_list[event_key].append(event_callback)

    @staticmethod
    def trigger_event(event_key, event_data):
        if event_key not in EventHandler._events_list:
            return
        
        for event_callback in EventHandler._events_list[event_key]:
            event_callback(event_data)

