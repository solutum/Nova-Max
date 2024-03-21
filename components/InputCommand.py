from components.EventHandler import EventHandler
from components.Logger import Logger

class InputCommand:
    def __init__(self):
        pass

    def cmd_update_charts(self, new_data):
        Logger.get_instance().log_message(f"InputCommand.cmd_update_charts.")      
        pass

    def cmd_connection_success(self, data):
        Logger.get_instance().log_message(f"InputCommand.cmd_connection_success.")
        EventHandler.trigger_event(EventHandler.EVENT_ON_CONNECTION_SUCCESS, data)

    def cmd_error(self, data):
        Logger.get_instance().log_message(f"InputCommand.cmd_error.")
        EventHandler.trigger_event(EventHandler.EVENT_ON_GET_ERROR, data)

    def cmd_get_configs(self, data):
        Logger.get_instance().log_message(f"InputCommand.cmd_get_configs.")
        EventHandler.trigger_event(EventHandler.EVENT_ON_GET_CONFIGS, data)

    # def cmd_dummy(self, data):
        Logger.get_instance().log_message(f"InputCommand.cmd_dummy.")
        #EventHandler.trigger_event(EventHandler.EVENT_ON_SCAN_RAGE_DATA, 'data_from InputCommand.cmd_dummy.')

    def cmd_scan_range(self, data):
        Logger.get_instance().log_message(f"InputCommand.cmd_scan_range.")
        EventHandler.trigger_event(EventHandler.EVENT_ON_SCAN_RANGE_DATA, data)

    def parse_input_command(self, data):
        switch_dict  = {
            'error': self.cmd_error,
            'connection_success': self.cmd_connection_success,
            'scan_data': self.cmd_update_charts,
            'scan_range_data': self.cmd_scan_range,
            'configs': self.cmd_get_configs,

        }
        
        chosen_case = switch_dict.get(data['cmd'])
        result = chosen_case(data['data'])