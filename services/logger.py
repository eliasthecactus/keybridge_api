import logging
import json
import socket
from logging.handlers import SysLogHandler
from models import db, Logs, SyslogServer

class Loggie:
    def __init__(self):
        """Initialize the logging system."""
        self.logger = logging.getLogger("keybridge")
        self.logger.setLevel(logging.INFO)

        # Standard log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Console logging (prints logs to the terminal)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _log(self, level, message, title=None, data=None, do_syslog=True, do_db=True):
        """
        Internal method to handle logging.

        Args:
            level (str): Log level (INFO, ERROR, WARNING, DEBUG).
            message (str): Log message.
            title (str): Optional log title.
            data (dict): Additional log data.
            do_syslog (bool): Whether to send to a syslog server.
        """
        log_level = getattr(logging, level.upper(), logging.INFO)

        log_data = {
            "level": level.upper(),
            "message": message,
            "title": title,
            "data": data or {}
            }

        # Log to console
        self.logger.log(log_level, f"{message} | Data: {json.dumps(data, indent=2)}")


        # Log to the database
        if do_db:
            try:
                log_entry = Logs(
                    level=level.upper(),
                    title=title,
                    message=message,
                    data=json.dumps(data) if data else None
                )
                db.session.add(log_entry)
                db.session.commit()
            except Exception as e:
                self.logger.error(f"Failed to log to DB: {message}. Error: {str(e)}")

            # Log to syslog if enabled
            if do_syslog:
                self._send_to_syslog(log_level, message, data)

    def _send_to_syslog(self, level, message, data):
        """Send logs to an external syslog server if configured."""
        try:
            syslog_server = SyslogServer.query.filter_by(disabled=False).first()
            if syslog_server:
                handler = SysLogHandler(
                    address=(syslog_server.host, syslog_server.port),
                    socktype=socket.SOCK_DGRAM if syslog_server.protocol.lower() == 'udp' else socket.SOCK_STREAM
                )

                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)

                syslog_logger = logging.getLogger('syslog_logger')
                syslog_logger.setLevel(level)
                syslog_logger.addHandler(handler)

                syslog_message = f"{message} | Data: {json.dumps(data, indent=2)}"
                syslog_logger.log(level, syslog_message)

                # Remove handler after sending log (prevents duplicate logs)
                syslog_logger.removeHandler(handler)
        except Exception as e:
            self.logger.error(f"Failed to log to Syslog: {message}. Error: {str(e)}")

    # Public methods for different log levels
    def info(self, message, title=None, data=None, do_syslog=True, do_db=True):
        self._log("INFO", message, title, data, do_syslog, do_db)

    def error(self, message, title=None, data=None, do_syslog=True, do_db=True):
        self._log("ERROR", message, title, data, do_syslog, do_db)

    def warning(self, message, title=None, data=None, do_syslog=True, do_db=True):
        self._log("WARNING", message, title, data, do_syslog, do_db)

    def debug(self, message, title=None, data=None, do_syslog=True, do_db=True):
        self._log("DEBUG", message, title, data, do_syslog, do_db)


# Create a global instance of Loggie
loggie = Loggie()