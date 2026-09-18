import json
from datetime import datetime
from pathlib import Path


class ExperienceMemory:
    """
    Stores lightweight contextual experiences that help Saphira
    maintain continuity across conversations and sessions.

    This is intentionally separate from long-term personal memories.
    """

    def __init__(self, path):
        self.path = Path(path)

        self.data = {
            "activities": [],
            "game_facts": [],
            "observations": [],
        }

        self.load()

    def load(self):
        if not self.path.exists():
            self.save()
            return

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                self.data["activities"] = data.get(
                    "activities", []
                )
                self.data["game_facts"] = data.get(
                    "game_facts", []
                )
                self.data["observations"] = data.get(
                    "observations", []
                )

        except (json.JSONDecodeError, OSError):
            self.data = {
                "activities": [],
                "game_facts": [],
                "observations": [],
            }

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=2,
                ensure_ascii=False,
            )

    @staticmethod
    def _now():
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _relative_time(timestamp):
        """
        Converts an ISO timestamp into a simple human-readable
        relative description for Saphira's context.
        """

        if not timestamp:
            return "unknown time"

        try:
            then = datetime.fromisoformat(timestamp)
            now = datetime.now()

            seconds = max(
                0,
                (now - then).total_seconds()
            )

            if seconds < 60:
                return "just now"

            minutes = int(seconds // 60)

            if minutes < 60:
                return f"{minutes} minute(s) ago"

            hours = int(minutes // 60)

            if hours < 24:
                return f"{hours} hour(s) ago"

            days = int(hours // 24)

            if days == 1:
                return "yesterday"

            if days < 7:
                return f"{days} days ago"

            return then.strftime("%Y-%m-%d")

        except (TypeError, ValueError):
            return "unknown time"

    def add_activity(self, activity, details=""):
        activity = str(activity).strip()
        details = str(details).strip()

        if not activity:
            return False

        timestamp = self._now()

        for existing in self.data["activities"]:
            if (
                existing.get("activity", "").casefold()
                == activity.casefold()
            ):
                existing["last_seen"] = timestamp
                existing["count"] = (
                    int(existing.get("count", 0)) + 1
                )

                if details:
                    existing["details"] = details

                self.save()
                return False

        self.data["activities"].append({
            "activity": activity,
            "details": details,
            "first_seen": timestamp,
            "last_seen": timestamp,
            "count": 1,
        })

        self.data["activities"] = (
            self.data["activities"][-50:]
        )

        self.save()
        return True

    def add_game_fact(
        self,
        game,
        fact,
        subject="",
    ):
        game = str(game).strip()
        fact = str(fact).strip()
        subject = str(subject).strip()

        if not game or not fact:
            return False

        normalized_game = game.casefold()
        normalized_fact = fact.casefold()
        normalized_subject = subject.casefold()

        timestamp = self._now()

        for existing in self.data["game_facts"]:
            if (
                existing.get("game", "").casefold()
                == normalized_game
                and existing.get("fact", "").casefold()
                == normalized_fact
                and existing.get("subject", "").casefold()
                == normalized_subject
            ):
                existing["last_seen"] = timestamp
                self.save()
                return False

        self.data["game_facts"].append({
            "game": game,
            "subject": subject,
            "fact": fact,
            "first_seen": timestamp,
            "last_seen": timestamp,
        })

        self.data["game_facts"] = (
            self.data["game_facts"][-150:]
        )

        self.save()
        return True

    def add_observation(self, observation):
        observation = str(observation).strip()

        if not observation:
            return False

        self.data["observations"].append({
            "observation": observation,
            "timestamp": self._now(),
        })

        self.data["observations"] = (
            self.data["observations"][-50:]
        )

        self.save()
        return True

    def recent_activities(self, limit=10):
        return list(
            reversed(self.data["activities"][-limit:])
        )

    def game_facts_for(self, game, limit=15):
        game = str(game).strip().casefold()

        matches = [
            item
            for item in self.data["game_facts"]
            if item.get("game", "").casefold() == game
        ]

        return list(
            reversed(matches[-limit:])
        )

    def recent_game_facts(self, limit=15):
        return list(
            reversed(self.data["game_facts"][-limit:])
        )

    def context_for(self, game=None):
        """
        Build compact context for Saphira's brain.

        When a specific game is supplied, prioritize its facts.

        When no game is supplied, include recent game facts too.
        This allows idle conversation to maintain continuity even
        when the current screen does not clearly identify the game.
        """

        lines = []

        activities = self.recent_activities(10)

        if activities:
            lines.append("RECENT ACTIVITIES:")

            for item in activities:
                activity = item.get(
                    "activity", ""
                ).strip()

                details = item.get(
                    "details", ""
                ).strip()

                last_seen = self._relative_time(
                    item.get("last_seen", "")
                )

                count = int(
                    item.get("count", 1)
                )

                line = (
                    f"- {activity} "
                    f"({last_seen}, seen {count} time(s))"
                )

                if details:
                    line += f": {details}"

                lines.append(line)

        if game:
            facts = self.game_facts_for(
                game,
                15,
            )
        else:
            facts = self.recent_game_facts(15)

        if facts:
            lines.append("")

            if game:
                lines.append(
                    f"KNOWN FACTS ABOUT {game.upper()}:"
                )
            else:
                lines.append(
                    "RECENT GAME-SPECIFIC FACTS:"
                )

            for item in facts:
                game_name = item.get(
                    "game", ""
                ).strip()

                subject = item.get(
                    "subject", ""
                ).strip()

                fact = item.get(
                    "fact", ""
                ).strip()

                last_seen = self._relative_time(
                    item.get("last_seen", "")
                )

                if game:
                    prefix = ""
                else:
                    prefix = f"{game_name}: "

                if subject:
                    lines.append(
                        f"- {prefix}{subject}: "
                        f"{fact} ({last_seen})"
                    )
                else:
                    lines.append(
                        f"- {prefix}{fact} "
                        f"({last_seen})"
                    )

        return "\n".join(lines)