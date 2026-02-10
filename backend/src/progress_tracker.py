import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class ProgressTracker:
    """
    Tracks progress of long-running qualification creation tasks.
    Writes progress to an external log file to enable resumption after failures.
    """

    def __init__(self, log_file: str = "qualification_progress.log"):
        self.log_file = Path(log_file)
        self.progress_file = Path("qualification_progress.json")
        self.last_processed_team_id: Optional[int] = None
        self.last_processed_index: int = -1
        self.total_teams: int = 0
        self.start_time: Optional[datetime] = None
        self.processed_count: int = 0

    def initialize(self, total_teams: int, resume: bool = True) -> int:
        """
        Initialize the progress tracker.

        Args:
            total_teams: Total number of teams to process
            resume: Whether to attempt resuming from last checkpoint

        Returns:
            Index to start processing from (0 for new run, last index + 1 for resume)
        """
        self.total_teams = total_teams
        self.start_time = datetime.now()

        if resume and self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as f:
                    data = json.load(f)
                    self.last_processed_index = data.get("last_processed_index", -1)
                    self.last_processed_team_id = data.get("last_processed_team_id")
                    self.processed_count = data.get("processed_count", 0)

                    start_index = self.last_processed_index + 1
                    self._log(
                        f"RESUMING from index {start_index} "
                        f"(team_id: {self.last_processed_team_id}). "
                        f"Already processed: {self.processed_count}/{total_teams} teams"
                    )
                    return start_index
            except Exception as e:
                self._log(f"Failed to load progress file, starting fresh: {e}")
                self._clear_progress()
                return 0
        else:
            self._log(
                f"STARTING new qualification creation run for {total_teams} teams"
            )
            self._clear_progress()
            return 0

    def update_progress(
        self,
        current_index: int,
        team_id: int,
        qualification_status: str,
        force_save: bool = False,
    ):
        """
        Update progress after processing a team.

        Args:
            current_index: Current index in the teams list
            team_id: ID of the team just processed
            qualification_status: Qualification status assigned
            force_save: Force save progress to file (default: only logs without saving)
        """
        self.last_processed_index = current_index
        self.last_processed_team_id = team_id
        self.processed_count = current_index + 1

        # Log every 10 teams or if forced
        if self.processed_count % 10 == 0 or force_save:
            elapsed = (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time
                else 0
            )
            remaining_teams = self.total_teams - self.processed_count
            avg_time_per_team = (
                elapsed / self.processed_count if self.processed_count > 0 else 0
            )
            estimated_remaining = avg_time_per_team * remaining_teams

            progress_pct = (
                (self.processed_count / self.total_teams * 100)
                if self.total_teams > 0
                else 0
            )

            self._log(
                f"Progress: {self.processed_count}/{self.total_teams} ({progress_pct:.1f}%) | "
                f"Current team_id: {team_id} | Status: {qualification_status} | "
                f"Elapsed: {elapsed:.0f}s | Avg: {avg_time_per_team:.2f}s/team | "
                f"Est. remaining: {estimated_remaining:.0f}s ({estimated_remaining / 60:.1f}m)"
            )

        # ONLY save checkpoint to file if force_save is True
        if force_save:
            self._save_progress()

    def complete(self):
        """Mark the qualification creation as complete and clean up progress file."""
        elapsed = (
            (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        )
        self._log(
            f"COMPLETED qualification creation for {self.processed_count} teams "
            f"in {elapsed:.0f}s ({elapsed / 60:.1f}m)"
        )
        self._clear_progress()

    def _save_progress(self):
        """Save current progress to JSON file for resumption."""
        try:
            data = {
                "last_processed_index": self.last_processed_index,
                "last_processed_team_id": self.last_processed_team_id,
                "processed_count": self.processed_count,
                "total_teams": self.total_teams,
                "timestamp": datetime.now().isoformat(),
            }
            with open(self.progress_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self._log(f"ERROR: Failed to save progress file: {e}")

    def _clear_progress(self):
        """Clear the progress checkpoint file."""
        if self.progress_file.exists():
            try:
                self.progress_file.unlink()
            except Exception as e:
                self._log(f"WARNING: Failed to delete progress file: {e}")

    def _log(self, message: str):
        """Write a log message to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        try:
            with open(self.log_file, "a") as f:
                f.write(log_message)
            # Also print to console
            print(log_message.strip())
        except Exception as e:
            print(f"ERROR: Failed to write to log file: {e}")
