# ###############################################################################
# 
# Copyright (c) 2024, Septentrio
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from time import sleep
import sys
import signal
from ..StreamConfig.App import App

from flask import Flask, app
from flask import Flask, jsonify 
import threading
import src.UserInterfaces.NmeaMsgShare as NmeaMsgShare

web_app = Flask(__name__) 
@web_app.route('/status') 
def status():
    return jsonify({"Status": NmeaMsgShare.last_nmea_message_sent_to_caster})

def start_web_server(): 
    web_app.run(host='0.0.0.0', port=5000)

class HeadlessUserInterface :

    def __init__(self ,app : App ) -> None:
        self.app : App = app
        signal.signal(signal.SIGTERM, self.shutdown_handler)
        signal.signal(signal.SIGINT, self.shutdown_handler)  # Optional: for Ctrl+C
 
 # Main menu
    def main_menu(self) :
        """Main menu of TUI
        """
        flask_thread = threading.Thread(target=start_web_server, daemon=True) 
        flask_thread.start()
        
        while True:
            # We want to try to connect periodically in case of failure at startup or losing cellular connection or
            # moving to different wifi network, etc. Say every 10 seconds
            sleep(10)
            for port_id, value  in enumerate(self.app.preferences.connect):
                if self.app.stream_list[port_id] is not None and not self.app.stream_list[port_id].is_connected() and value:
                    if port_id < self.app.preferences.max_streams:  
                        try :
                            self.app.stream_list[port_id].connect(self.app.stream_list[port_id].stream_type)
                        except Exception as e:
                            self.app.stream_list[port_id].startup_error =f"Stream couldn't start properly : \n {e}"
                            if self.app.log_file is not None :
                                self.app.log_file.info("Retried Stream %s : Could not start properly. " , self.app.stream_list[port_id].stream_id)
            pass  # Replace with your actual logic

    def shutdown_handler(self, signum, frame):
        print(f"Received shutdown signal ({signum}). Cleaning up...")
        self.app.close_all()
        sys.exit(0)
