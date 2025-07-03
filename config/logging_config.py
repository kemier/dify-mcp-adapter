"""
Logging Configuration for MCP Adapter Plugin
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class MCPLoggerConfig:
    """Configure logging for the MCP adapter plugin."""
    
    def __init__(self, 
                 log_level: str = None,
                 log_dir: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True):
        """
        Initialize logging configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory to store log files
            max_file_size: Maximum size of each log file in bytes
            backup_count: Number of backup log files to keep
            enable_console: Whether to enable console logging
        """
        self.log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up the logging configuration."""
        # Remove all existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set the root logger level
        numeric_level = getattr(logging, self.log_level.upper(), logging.INFO)
        root_logger.setLevel(numeric_level)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set up file handlers
        self._setup_file_handlers(detailed_formatter)
        
        # Set up console handler if enabled
        if self.enable_console:
            self._setup_console_handler(simple_formatter)
        
        # Log the initialization
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized - Level: {self.log_level}, Directory: {self.log_dir}")
    
    def _setup_file_handlers(self, formatter: logging.Formatter):
        """Set up rotating file handlers for different log levels."""
        
        # General application log (all levels)
        general_log_file = self.log_dir / "mcp_adapter.log"
        general_handler = logging.handlers.RotatingFileHandler(
            filename=general_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        general_handler.setFormatter(formatter)
        general_handler.setLevel(logging.DEBUG)
        
        # Error log (ERROR and CRITICAL only)
        error_log_file = self.log_dir / "mcp_adapter_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            filename=error_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Tool execution log (for tracking tool usage)
        tool_log_file = self.log_dir / "mcp_tool_executions.log"
        tool_handler = logging.handlers.RotatingFileHandler(
            filename=tool_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        tool_handler.setFormatter(formatter)
        tool_handler.addFilter(self._create_tool_filter())
        
        # Add handlers to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(general_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(tool_handler)
    
    def _setup_console_handler(self, formatter: logging.Formatter):
        """Set up console handler for stdout logging."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Console shows INFO and above by default
        console_level = os.getenv("CONSOLE_LOG_LEVEL", "INFO")
        numeric_level = getattr(logging, console_level.upper(), logging.INFO)
        console_handler.setLevel(numeric_level)
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
    
    def _create_tool_filter(self) -> logging.Filter:
        """Create a filter for tool execution logs."""
        class ToolExecutionFilter(logging.Filter):
            def filter(self, record):
                # Only log records from tool modules or containing 'tool_execution'
                return (
                    'tools.' in record.name or 
                    'tool_execution' in getattr(record, 'extra_tags', []) or
                    'TOOL_EXEC' in record.getMessage()
                )
        
        return ToolExecutionFilter()
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)


class MCPLogger:
    """Convenience wrapper for MCP-specific logging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(f"[{self._session_id}] {message}", extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(f"[{self._session_id}] {message}", extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(f"[{self._session_id}] {message}", extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(f"[{self._session_id}] {message}", extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(f"[{self._session_id}] {message}", extra=kwargs)
    
    def tool_execution(self, tool_name: str, server_name: str, user_id: str, 
                      parameters: dict, success: bool, execution_time: float = None,
                      error: str = None):
        """Log tool execution details."""
        status = "SUCCESS" if success else "FAILED"
        exec_time = f" in {execution_time:.3f}s" if execution_time else ""
        
        message = (f"TOOL_EXEC | {status} | Tool: {tool_name} | Server: {server_name} | "
                  f"User: {user_id}{exec_time}")
        
        if error:
            message += f" | Error: {error}"
        
        extra = {
            'extra_tags': ['tool_execution'],
            'tool_name': tool_name,
            'server_name': server_name,
            'user_id': user_id,
            'parameters': parameters,
            'success': success,
            'execution_time': execution_time,
            'error': error
        }
        
        if success:
            self.logger.info(message, extra=extra)
        else:
            self.logger.error(message, extra=extra)
    
    def server_operation(self, operation: str, server_name: str, success: bool, 
                        details: str = None):
        """Log server operations (enable/disable/refresh)."""
        status = "SUCCESS" if success else "FAILED"
        message = f"SERVER_OP | {status} | Operation: {operation} | Server: {server_name}"
        
        if details:
            message += f" | Details: {details}"
        
        extra = {
            'extra_tags': ['server_operation'],
            'operation': operation,
            'server_name': server_name,
            'success': success,
            'details': details
        }
        
        if success:
            self.logger.info(message, extra=extra)
        else:
            self.logger.error(message, extra=extra)
    
    def registry_operation(self, operation: str, servers_count: int = None, 
                          success: bool = True, error: str = None):
        """Log registry operations."""
        status = "SUCCESS" if success else "FAILED"
        message = f"REGISTRY_OP | {status} | Operation: {operation}"
        
        if servers_count is not None:
            message += f" | Servers: {servers_count}"
        
        if error:
            message += f" | Error: {error}"
        
        extra = {
            'extra_tags': ['registry_operation'],
            'operation': operation,
            'servers_count': servers_count,
            'success': success,
            'error': error
        }
        
        if success:
            self.logger.info(message, extra=extra)
        else:
            self.logger.error(message, extra=extra)


def initialize_logging(log_level: str = None, 
                      log_dir: str = "logs",
                      enable_console: bool = True) -> MCPLoggerConfig:
    """
    Initialize the logging system for the MCP adapter plugin.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Whether to enable console logging
    
    Returns:
        MCPLoggerConfig instance
    """
    return MCPLoggerConfig(
        log_level=log_level,
        log_dir=log_dir,
        enable_console=enable_console
    )


def get_logger(name: str) -> MCPLogger:
    """Get an MCP logger instance."""
    return MCPLogger(name) 