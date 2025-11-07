#!/usr/bin/env python3
"""
Session Manager for OpenCode
Handles session persistence and context restoration
"""

import os
import json
from datetime import datetime
from pathlib import Path

class SessionManager:
    def __init__(self):
        self.sessions_dir = Path("/home/kent/Assistant/sessions")
        self.current_session_file = self.sessions_dir / "current_session.json"
        self.cumulative_recap_file = self.sessions_dir / "cumulative_recap.json"
        self.env_file = Path("/home/kent/Assistant/.env")
        
        # Ensure sessions directory exists
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def get_current_session_info(self):
        """Get current session information"""
        return {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "working_directory": os.getcwd(),
            "git_status": self._get_git_status(),
            "opencode_service_status": self._get_opencode_status()
        }
    
    def _get_git_status(self):
        """Get git repository status"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd="/home/kent/Assistant"
            )
            return {
                "has_changes": bool(result.stdout.strip()),
                "status_output": result.stdout.strip()
            }
        except:
            return {"has_changes": False, "status_output": "Git not available"}
    
    def _get_opencode_status(self):
        """Get OpenCode service status"""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "/home/kent/Assistant/scripts/opencode_manager.py", "status"],
                capture_output=True,
                text=True
            )
            return {
                "running": "active (running)" in result.stdout,
                "status_output": result.stdout.strip()
            }
        except:
            return {"running": False, "status_output": "Status check failed"}
    
    def save_session_finish(self, accomplishments, current_state, next_steps, notes=""):
        """Save session completion data and update cumulative recap"""
        session_info = self.get_current_session_info()
        session_info.update({
            "end_time": datetime.now().isoformat(),
            "accomplishments": accomplishments,
            "current_state": current_state,
            "next_steps": next_steps,
            "notes": notes,
            "session_type": "finish"
        })
        
        # Save to current session file
        with open(self.current_session_file, 'w') as f:
            json.dump(session_info, f, indent=2)
        
        # Update cumulative recap
        self._update_cumulative_recap(session_info)
        
        return session_info["session_id"]
    
    def load_latest_session(self):
        """Load the most recent session for context restoration"""
        if not self.current_session_file.exists():
            return None
        
        try:
            with open(self.current_session_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _update_cumulative_recap(self, session_info):
        """Update rolling cumulative recap with new session data"""
        # Load existing cumulative recap
        existing_recap = self._load_cumulative_recap()
        
        # Extract key information from new session
        session_key_points = self._extract_session_key_points(session_info)
        
        # Merge and condense
        updated_recap = self._merge_session_data(existing_recap, session_key_points)
        
        # Save updated cumulative recap
        with open(self.cumulative_recap_file, 'w') as f:
            json.dump(updated_recap, f, indent=2)
        
        # Trigger automatic GitHub backup
        self._auto_github_backup(session_info)
        
        # Trigger automatic GitHub backup
        self._auto_github_backup(session_info)
    
    def _load_cumulative_recap(self):
        """Load existing cumulative recap"""
        if self.cumulative_recap_file.exists():
            try:
                with open(self.cumulative_recap_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Return empty recap structure if none exists
        return {
            "project_start_time": datetime.now().isoformat(),
            "last_updated": None,
            "total_sessions": 0,
            "technical_decisions": [],
            "architecture_changes": [],
            "critical_discoveries": [],
            "current_state": {},
            "next_steps": [],
            "security_constraints": [],
            "blocked_items": [],
            "completed_phases": []
        }
    
    def _extract_session_key_points(self, session_info):
        """Extract and condense key information from session"""
        return {
            "session_id": session_info["session_id"],
            "session_time": session_info["end_time"],
            "accomplishments": self._condense_text(session_info["accomplishments"]),
            "technical_decisions": self._extract_technical_decisions(session_info),
            "architecture_changes": self._extract_architecture_changes(session_info),
            "current_state_update": self._condense_text(session_info["current_state"]),
            "next_steps": self._extract_next_steps(session_info["next_steps"]),
            "critical_notes": self._extract_critical_notes(session_info["notes"])
        }
    
    def _condense_text(self, text):
        """Condense text to key points"""
        if not text or len(text) < 100:
            return text
        
        # Simple condensation - split by lines and keep key ones
        lines = text.split('\n')
        key_lines = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('✅') or line.startswith('🔧') or 
                       line.startswith('🚀') or line.startswith('💡') or
                       line.startswith('🔒') or len(line) > 20):
                key_lines.append(line)
        
        return '\n'.join(key_lines[:10])  # Limit to 10 key points
    
    def _extract_technical_decisions(self, session_info):
        """Extract technical decisions from session"""
        decisions = []
        text = session_info.get("accomplishments", "") + " " + session_info.get("notes", "")
        
        # Look for decision keywords
        decision_keywords = ["decided", "chose", "selected", "implemented", "created", "built", "designed", "developed", "established", "fixed", "updated", "improved"]
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Direct keyword matches
            if any(keyword in line.lower() for keyword in decision_keywords):
                decisions.append(line)
            # Past tense technical achievements
            elif any(tech_word in line.lower() for tech_word in ["system", "architecture", "framework", "solution", "approach", "method", "logic", "extraction"]):
                if any(past_tense in line.lower() for past_tense in ["ed", "created", "built", "designed", "implemented", "fixed", "updated", "improved"]):
                    decisions.append(line)
            # If it contains technical terms and past tense, it's likely a decision
            elif any(tech_term in line.lower() for tech_term in ["session", "manager", "extraction", "logic", "plain", "text", "inputs", "unstructured"]):
                if any(past_tense in line.lower() for past_tense in ["fixed", "improved", "updated", "created", "built"]):
                    decisions.append(line)
        
        return decisions[:5]  # Limit to 5 decisions per session
    
    def _extract_architecture_changes(self, session_info):
        """Extract architecture changes from session"""
        changes = []
        text = session_info.get("accomplishments", "") + " " + session_info.get("current_state", "")
        
        # Look for architecture keywords
        arch_keywords = ["architecture", "system", "structure", "design", "framework", "pattern", "approach"]
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in arch_keywords):
                changes.append(line)
            # Look for major structural changes
            elif any(change_word in line.lower() for change_word in ["redesigned", "restructured", "reorganized", "refactored", "overhauled"]):
                changes.append(line)
        
        return changes[:3]  # Limit to 3 architecture changes per session
    
    def _extract_next_steps(self, next_steps_text):
        """Extract and prioritize next steps"""
        if not next_steps_text:
            return []
        
        lines = next_steps_text.split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for formatted lists
            if (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or
                line.startswith('-') or line.startswith('*') or '🚀' in line):
                steps.append(line)
            # Check for action-oriented sentences
            elif any(action_word in line.lower() for action_word in ['test', 'implement', 'create', 'fix', 'update', 'build', 'design', 'complete', 'verify', 'run']):
                steps.append(line)
            # Check for sentences with "should" or "need to"
            elif 'should' in line.lower() or 'need to' in line.lower() or 'will' in line.lower():
                steps.append(line)
        
        # If no structured steps found, treat the whole text as one step
        if not steps and next_steps_text.strip():
            steps = [next_steps_text.strip()]
        
        return steps[:5]  # Limit to 5 next steps
    
    def _extract_critical_notes(self, notes):
        """Extract critical notes and security constraints"""
        if not notes:
            return {"security": [], "critical": []}
        
        critical = {"security": [], "critical": []}
        lines = notes.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'security' in line.lower() or '🔒' in line:
                critical["security"].append(line)
            elif 'critical' in line.lower() or 'important' in line.lower() or '💡' in line:
                critical["critical"].append(line)
        
        return critical
    
    def _merge_session_data(self, existing_recap, session_key_points):
        """Merge new session data into cumulative recap"""
        # Update metadata
        existing_recap["last_updated"] = session_key_points["session_time"]
        existing_recap["total_sessions"] += 1
        
        # Merge technical decisions (keep recent 20)
        existing_recap["technical_decisions"].extend(session_key_points["technical_decisions"])
        existing_recap["technical_decisions"] = existing_recap["technical_decisions"][-20:]
        
        # Merge architecture changes (keep recent 15)
        existing_recap["architecture_changes"].extend(session_key_points["architecture_changes"])
        existing_recap["architecture_changes"] = existing_recap["architecture_changes"][-15:]
        
        # Merge critical discoveries (keep recent 25)
        discoveries = session_key_points["critical_notes"]["critical"]
        existing_recap["critical_discoveries"].extend(discoveries)
        existing_recap["critical_discoveries"] = existing_recap["critical_discoveries"][-25:]
        
        # Update current state (replace with latest)
        existing_recap["current_state"] = {
            "session_id": session_key_points["session_id"],
            "state_summary": session_key_points["current_state_update"],
            "last_updated": session_key_points["session_time"]
        }
        
        # Update next steps (replace with latest)
        existing_recap["next_steps"] = session_key_points["next_steps"]
        
        # Merge security constraints (keep all)
        security_items = session_key_points["critical_notes"]["security"]
        existing_recap["security_constraints"].extend(security_items)
        # Remove duplicates
        existing_recap["security_constraints"] = list(set(existing_recap["security_constraints"]))
        
        return existing_recap
    
    def _auto_github_backup(self, session_info):
        """Trigger automatic GitHub backup after session save"""
        try:
            import subprocess
            import sys
            
            # Path to GitHub backup script
            backup_script = Path("/home/kent/Assistant/scripts/github_backup.py")
            
            if backup_script.exists():
                # Use accomplishments for commit message
                accomplishments = session_info.get("accomplishments", "session completed")
                result = subprocess.run(
                    [sys.executable, str(backup_script), "session", accomplishments[:50]],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Log result but don't fail session save if backup fails
                if result.returncode == 0:
                    print(f"🔒 GitHub backup successful: {result.stdout.strip()}")
                else:
                    print(f"⚠️  GitHub backup failed: {result.stderr.strip()}")
        except Exception as e:
            print(f"⚠️  GitHub backup error: {e}")
    
    def start_new_session(self):
        """Start a new session and restore context from cumulative recap"""
        cumulative_recap = self._load_cumulative_recap()
        
        if cumulative_recap["total_sessions"] > 0:
            return self._create_session_start_context(cumulative_recap)
        else:
            return "# No previous session found\n\nStarting fresh session."
    
    def _create_session_start_context(self, cumulative_recap):
        """Create optimized context for starting new session"""
        content = f"""# AI Memory Context Restored

**Project Timeline:** {cumulative_recap["project_start_time"]} to {cumulative_recap["last_updated"]}
**Total Sessions:** {cumulative_recap["total_sessions"]}

## 🧠 Memory Injection: Complete Project Context

### 🏗️ Current Architecture & State
{cumulative_recap["current_state"].get("state_summary", "No current state recorded")}

### 🎯 Immediate Next Steps (Priority Order)
"""
        
        # Add numbered next steps
        for i, step in enumerate(cumulative_recap["next_steps"][:5], 1):
            content += f"{i}. {step}\n"
        
        content += f"""
### 🔧 Recent Technical Decisions (Last 5)
"""
        # Add recent technical decisions
        for decision in cumulative_recap["technical_decisions"][-5:]:
            content += f"- {decision}\n"
        
        content += f"""
### 🏛️ Architecture Evolution (Recent Changes)
"""
        # Add recent architecture changes
        for change in cumulative_recap["architecture_changes"][-3:]:
            content += f"- {change}\n"
        
        if cumulative_recap["security_constraints"]:
            content += f"""
### 🔒 Security Constraints (CRITICAL)
"""
            for constraint in cumulative_recap["security_constraints"]:
                content += f"- {constraint}\n"
        
        if cumulative_recap["critical_discoveries"]:
            content += f"""
### 💡 Key Insights & Discoveries
"""
            for discovery in cumulative_recap["critical_discoveries"][-5:]:
                content += f"- {discovery}\n"
        
        content += f"""
---
*Memory injected by SessionManager | Total context: {cumulative_recap["total_sessions"]} sessions*
"""
        return content

def main():
    """Command line interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python session_manager.py <command>")
        print("Commands:")
        print("  start                    Load and display previous session context")
        print("  finish                   Interactive session finish")
        print("  quick-finish <args>     Quick finish with command line args")
        sys.exit(1)
    
    manager = SessionManager()
    command = sys.argv[1].lower()
    
    if command == "start":
        context = manager.start_new_session()
        print(context)
        
    elif command == "finish":
        print("Session Finish - Interactive Mode")
        print("Enter details for session completion:")
        
        accomplishments = input("🎯 What did we accomplish? ")
        current_state = input("📊 What's the current state? ")
        next_steps = input("🚀 What are the next steps? ")
        notes = input("📝 Any additional notes? ")
        
        session_id = manager.save_session_finish(
            accomplishments, current_state, next_steps, notes
        )
        
        print(f"\n✅ Session {session_id} saved successfully!")
        print("📁 Session files created in /Assistant/sessions/")
        
    elif command == "quick-finish":
        if len(sys.argv) < 5:
            print("Usage: python session_manager.py quick-finish <accomplishments> <current_state> <next_steps> [notes]")
            sys.exit(1)
        
        accomplishments = sys.argv[2]
        current_state = sys.argv[3]
        next_steps = sys.argv[4]
        notes = sys.argv[5] if len(sys.argv) > 5 else ""
        
        session_id = manager.save_session_finish(
            accomplishments, current_state, next_steps, notes
        )
        
        print(f"✅ Session {session_id} saved!")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()