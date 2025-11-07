#!/usr/bin/env python3
"""
Automatic GitHub Backup System
Secures project work by automatically committing and pushing changes
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

class GitHubBackup:
    def __init__(self, repo_path="/home/kent/Assistant"):
        self.repo_path = Path(repo_path)
        self.session_file = self.repo_path / "sessions" / "current_session.json"
        
    def run_git_command(self, cmd, capture_output=True):
        """Run git command and return result"""
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def has_changes(self):
        """Check if there are uncommitted changes"""
        success, stdout, _ = self.run_git_command(["status", "--porcelain"])
        if not success:
            return False
        return len(stdout.strip()) > 0
    
    def get_session_context(self):
        """Get current session context for commit message"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session = json.load(f)
                    return session.get('accomplishments', ''), session.get('session_id', '')
        except:
            pass
        return "", ""
    
    def create_backup(self, reason="auto-backup"):
        """Create automatic backup commit and push"""
        if not self.has_changes():
            return True, "No changes to backup"
        
        # Get context for commit message
        accomplishments, session_id = self.get_session_context()
        
        # Create commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if accomplishments:
            commit_msg = f"Auto-backup: {accomplishments[:100]} [{timestamp}]"
        else:
            commit_msg = f"Auto-backup: {reason} [{timestamp}]"
        
        if session_id:
            commit_msg += f" (session: {session_id})"
        
        # Stage all changes
        success, _, error = self.run_git_command(["add", "."])
        if not success:
            return False, f"Failed to stage changes: {error}"
        
        # Commit changes
        success, _, error = self.run_git_command(["commit", "-m", commit_msg])
        if not success:
            return False, f"Failed to commit: {error}"
        
        # Push to GitHub
        success, _, error = self.run_git_command(["push", "origin", "main"])
        if not success:
            return False, f"Failed to push: {error}"
        
        return True, f"Backup successful: {commit_msg}"
    
    def backup_after_accomplishment(self, accomplishments):
        """Backup after completing major work"""
        if not accomplishments:
            return self.create_backup("routine backup")
        
        # Extract key accomplishments for commit message
        if isinstance(accomplishments, str):
            if len(accomplishments) > 80:
                accomplishments = accomplishments[:77] + "..."
        
        return self.create_backup(f"completed: {accomplishments}")
    
    def emergency_backup(self):
        """Emergency backup - save everything immediately"""
        return self.create_backup("EMERGENCY_BACKUP")

def main():
    """Command line interface for GitHub backup"""
    import sys
    
    backup = GitHubBackup()
    
    if len(sys.argv) > 1:
        reason = " ".join(sys.argv[1:])
        success, message = backup.create_backup(reason)
    else:
        success, message = backup.create_backup()
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()