#!/usr/bin/env python3
"""
OpenCode Service Manager
Controls opencode.service on-demand to prevent memory accumulation
"""

import subprocess
import time
import sys
import os
from pathlib import Path

class OpenCodeManager:
    def __init__(self):
        self.service_name = "opencode.service"
        self.max_wait_time = 30  # seconds
        self.log_file = "/home/kent/Assistant/logs/opencode_manager.log"
        
    def ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Write to log file
        self.ensure_log_directory()
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")
    
    def run_command(self, command, check=True):
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=check
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
    
    def is_service_running(self):
        """Check if opencode service is currently running"""
        success, stdout, _ = self.run_command(
            f"systemctl is-active {self.service_name}", 
            check=False
        )
        return success and "active" in stdout
    
    def start_service(self):
        """Start opencode service"""
        if self.is_service_running():
            self.log("OpenCode service already running")
            return True
            
        self.log("Starting OpenCode service...")
        success, stdout, stderr = self.run_command(
            f"sudo systemctl start {self.service_name}"
        )
        
        if success:
            # Wait for service to be fully ready
            self.log("Waiting for service to be ready...")
            time.sleep(3)
            
            # Verify it's actually running
            if self.is_service_running():
                self.log("✅ OpenCode service started successfully")
                return True
            else:
                self.log("❌ Service started but not detected as active")
                return False
        else:
            self.log(f"❌ Failed to start service: {stderr}")
            return False
    
    def stop_service(self):
        """Stop opencode service"""
        if not self.is_service_running():
            self.log("OpenCode service not running")
            return True
            
        self.log("Stopping OpenCode service...")
        success, stdout, stderr = self.run_command(
            f"sudo systemctl stop {self.service_name}"
        )
        
        if success:
            # Wait for graceful shutdown
            time.sleep(2)
            
            # Verify it's actually stopped
            if not self.is_service_running():
                self.log("✅ OpenCode service stopped - memory cleared")
                return True
            else:
                self.log("❌ Service stopped but still detected as active")
                return False
        else:
            self.log(f"❌ Failed to stop service: {stderr}")
            return False
    
    def restart_service(self):
        """Restart opencode service (clears memory)"""
        self.log("Restarting OpenCode service to clear memory...")
        success, stdout, stderr = self.run_command(
            f"sudo systemctl restart {self.service_name}"
        )
        
        if success:
            time.sleep(3)
            if self.is_service_running():
                self.log("✅ OpenCode service restarted - memory cleared")
                return True
            else:
                self.log("❌ Service restarted but not detected as active")
                return False
        else:
            self.log(f"❌ Failed to restart service: {stderr}")
            return False
    
    def get_service_status(self):
        """Get detailed service status"""
        success, stdout, stderr = self.run_command(
            f"systemctl status {self.service_name}", 
            check=False
        )
        return success, stdout, stderr
    
    def consult_opencode(self, task_description, timeout_minutes=10):
        """
        Start OpenCode, perform consultation, stop service
        Returns: (success, result_data)
        """
        self.log(f"🧠 Starting OpenCode consultation: {task_description}")
        
        # Start the service
        if not self.start_service():
            return False, {"error": "Failed to start OpenCode service"}
        
        try:
            # Here we would connect to OpenCode and perform the task
            # For now, this is a placeholder for the actual consultation logic
            self.log(f"🔄 Performing consultation task: {task_description}")
            self.log("⚠️  TODO: Implement actual OpenCode connection and task execution")
            
            # Simulate consultation time
            time.sleep(2)
            
            # Placeholder result
            result = {
                "task": task_description,
                "status": "completed",
                "message": "Consultation completed - TODO: implement actual logic"
            }
            
            self.log("✅ Consultation completed successfully")
            return True, result
            
        except Exception as e:
            self.log(f"❌ Consultation failed: {str(e)}")
            return False, {"error": str(e)}
            
        finally:
            # Always stop the service to clear memory
            self.stop_service()
    
    def cleanup_memory(self):
        """Force memory cleanup by restarting service"""
        return self.restart_service()

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python opencode_manager.py <command> [args]")
        print("Commands:")
        print("  start                    Start OpenCode service")
        print("  stop                     Stop OpenCode service") 
        print("  restart                  Restart OpenCode service")
        print("  status                   Get service status")
        print("  consult <task>           Start, consult, stop")
        print("  cleanup                  Force memory cleanup")
        sys.exit(1)
    
    manager = OpenCodeManager()
    command = sys.argv[1].lower()
    
    if command == "start":
        success = manager.start_service()
        sys.exit(0 if success else 1)
        
    elif command == "stop":
        success = manager.stop_service()
        sys.exit(0 if success else 1)
        
    elif command == "restart":
        success = manager.restart_service()
        sys.exit(0 if success else 1)
        
    elif command == "status":
        success, stdout, stderr = manager.get_service_status()
        print(stdout)
        if stderr:
            print("STDERR:", stderr)
        sys.exit(0 if success else 1)
        
    elif command == "consult":
        if len(sys.argv) < 3:
            print("Usage: python opencode_manager.py consult <task_description>")
            sys.exit(1)
        task = " ".join(sys.argv[2:])
        success, result = manager.consult_opencode(task)
        if success:
            print("✅ Consultation successful:")
            print(result)
        else:
            print("❌ Consultation failed:")
            print(result)
        sys.exit(0 if success else 1)
        
    elif command == "cleanup":
        success = manager.cleanup_memory()
        sys.exit(0 if success else 1)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()