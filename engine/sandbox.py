import subprocess
import shlex

class VerificationSandbox:
    """Safely executes diagnostic commands within strict whitelist boundaries."""
    
    ALLOWED_COMMANDS = {"nginx", "systemctl", "ss", "netstat", "ip", "cat", "tail"}

    def execute_verification(self, command_str: str) -> dict:
        try:
            tokens = shlex.split(command_str)
            if not tokens:
                return {"success": False, "error": "Empty command provided."}

            # Check binary against safety whitelist (handle optional sudo prefix)
            binary = tokens[1] if tokens[0] == "sudo" else tokens[0]

            if binary not in self.ALLOWED_COMMANDS:
                return {
                    "success": False,
                    "error": f"Command '{binary}' blocked by safety policy."
                }

            # Run with a 10-second timeout to prevent hangs
            result = subprocess.run(
                tokens,
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Verification command timed out (10s limit)."}
        except Exception as e:
            return {"success": False, "error": f"Execution error: {str(e)}"}