"""Daily scheduled tasks for parsing skills and updating qualifications."""

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session
import db
from robotevents import RobotEvents
from progress_tracker import ProgressTracker
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DailyTaskScheduler:
    """Manages daily scheduled tasks for skills parsing and qualification updates."""

    def __init__(self, robotevents: RobotEvents, engine):
        self.robotevents = robotevents
        self.engine = engine
        self.scheduler = BackgroundScheduler()
        self.progress_tracker = ProgressTracker(log_file="scheduled_tasks.log")

    def parse_skills_task(self):
        """Daily task to parse skills for both High School and Middle School."""
        logger.info("Starting daily skills parsing task...")

        try:
            with Session(self.engine) as session:
                # Parse High School skills
                logger.info("Parsing High School skills...")
                hs_updated, hs_created = self.robotevents.parse_skills(
                    session, ms=False
                )
                logger.info(
                    f"High School: Updated {hs_updated} teams, Created {hs_created} new teams"
                )

                # Parse Middle School skills
                logger.info("Parsing Middle School skills...")
                ms_updated, ms_created = self.robotevents.parse_skills(session, ms=True)
                logger.info(
                    f"Middle School: Updated {ms_updated} teams, Created {ms_created} new teams"
                )

                # Update timestamp
                db.set_update_time(session, update_type="skills")

                logger.info(
                    f"Skills parsing completed successfully! Total: {hs_updated + hs_created + ms_updated + ms_created} teams processed"
                )

        except Exception as e:
            logger.error(f"Error during skills parsing: {e}", exc_info=True)

    def update_signature_qualifications_task(self):
        """Daily task to update signature event qualifications."""
        logger.info("Starting signature qualifications update task...")

        try:
            with Session(self.engine) as session:
                # Get signature qualifications
                qualifications = self.robotevents.create_qualifications_sig()

                if qualifications:
                    logger.info(
                        f"Processing {len(qualifications)} signature event qualifications..."
                    )

                    # Upsert qualifications to database
                    for q in qualifications:
                        db.upsert_quals(session, q)

                    session.commit()

                    # Update timestamp
                    db.set_update_time(session, update_type="signature")

                    logger.info(
                        f"Signature qualifications completed! Processed {len(qualifications)} teams"
                    )
                else:
                    logger.warning("No signature qualifications found")

        except Exception as e:
            logger.error(
                f"Error during signature qualifications update: {e}", exc_info=True
            )

    def update_worlds_qualifications_task(self):
        """Daily task to update World Championship qualifications from registered teams."""
        logger.info("Starting worlds qualifications update task...")

        try:
            with Session(self.engine) as session:
                # Get teams registered for Worlds and build qualifications
                qualifications = self.robotevents.create_qualifications_worlds(
                    session=session
                )

                if qualifications:
                    logger.info(
                        f"Processing {len(qualifications)} worlds qualifications..."
                    )

                    # Upsert qualifications to database
                    for q in qualifications:
                        db.upsert_quals(session, q)

                    session.commit()

                    # Update timestamp
                    db.set_update_time(session, update_type="worlds")

                    logger.info(
                        f"Worlds qualifications completed! Processed {len(qualifications)} teams"
                    )
                else:
                    logger.warning("No worlds qualifications found")

        except Exception as e:
            logger.error(
                f"Error during worlds qualifications update: {e}", exc_info=True
            )

    def start(self):
        """Start the scheduler with daily tasks."""
        # Schedule skills parsing every day at 2:00 AM
        self.scheduler.add_job(
            self.parse_skills_task,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_skills_parsing",
            name="Daily Skills Parsing (HS + MS)",
            replace_existing=True,
        )
        logger.info("Scheduled: Skills parsing - Daily at 2:00 AM")

        # Schedule signature qualifications update every day at 3:00 AM
        self.scheduler.add_job(
            self.update_signature_qualifications_task,
            trigger=CronTrigger(hour=3, minute=0),
            id="daily_signature_quals",
            name="Daily Signature Qualifications Update",
            replace_existing=True,
        )
        logger.info("Scheduled: Signature qualifications - Daily at 3:00 AM")

        # Schedule worlds qualifications update every day at 4:00 AM
        self.scheduler.add_job(
            self.update_worlds_qualifications_task,
            trigger=CronTrigger(hour=4, minute=0),
            id="daily_worlds_quals",
            name="Daily Worlds Qualifications Update",
            replace_existing=True,
        )
        logger.info("Scheduled: Worlds qualifications - Daily at 4:00 AM")

        # Start the scheduler
        self.scheduler.start()
        logger.info("Scheduler started successfully!")

        # Log next run times
        for job in self.scheduler.get_jobs():
            logger.info(f"Next run for '{job.name}': {job.next_run_time}")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def run_now(self, task: str = "all"):
        """Manually trigger tasks immediately (useful for testing).

        Args:
            task: Which task to run - "skills", "signature", "worlds", or "all"
        """
        if task in ["skills", "all"]:
            logger.info("Manually triggering skills parsing...")
            self.parse_skills_task()

        if task in ["signature", "all"]:
            logger.info("Manually triggering signature qualifications...")
            self.update_signature_qualifications_task()

        if task in ["worlds", "all"]:
            logger.info("Manually triggering worlds qualifications...")
            self.update_worlds_qualifications_task()
