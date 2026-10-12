"""Historical WP:GAN nominations; all naive timestamps represent UTC."""
from django.db import models


class Snapshot(models.Model):
    """One revision of Wikipedia:Good article nominations."""

    revision_id = models.BigIntegerField(unique=True)
    revision_timestamp = models.DateTimeField(db_index=True)
    imported_at = models.DateTimeField(auto_now_add=True)
    page_title = models.CharField(
        max_length=255, default="Wikipedia:Good article nominations"
    )
    # Deliberately no full-page raw wikitext; fetch it again by revision_id.

    class Meta:
        ordering = ("-revision_timestamp",)

    def __str__(self):
        return f"{self.page_title} (oldid={self.revision_id})"


class Nomination(models.Model):
    """Stable nomination identity across snapshots (linked after matching)."""

    title = models.CharField(max_length=512)
    nominator = models.CharField(max_length=255, blank=True)
    nominated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=("title", "nominator"))]

    def __str__(self):
        return f"{self.title} ({self.nominator})"


class NominationRecord(models.Model):
    """One nomination's observed state in a source revision."""

    class Status(models.TextChoices):
        UNREVIEWED = "U", "Unreviewed"
        UNDER_REVIEW = "R", "Under review"
        ON_HOLD = "H", "On hold"
        SECOND_OPINION = "2", "Second opinion"

    snapshot = models.ForeignKey(
        Snapshot, on_delete=models.CASCADE, related_name="nominations"
    )
    # Nullable until a cross-revision matching process establishes identity.
    nomination = models.ForeignKey(
        Nomination,
        on_delete=models.PROTECT,
        related_name="observations",
        null=True,
        blank=True,
    )
    position = models.PositiveIntegerField()
    title = models.CharField(max_length=512, null=True, blank=True)
    nominator = models.CharField(max_length=255, null=True, blank=True)
    nomination_number = models.CharField(max_length=20, default="1")
    nomination_timestamp = models.DateTimeField(null=True, blank=True)
    section = models.CharField(max_length=255)
    subsection = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.UNREVIEWED
    )
    review_timestamp = models.DateTimeField(null=True, blank=True)
    malformed = models.BooleanField(default=False)
    malformed_review = models.BooleanField(default=False)
    # Individual GANentry line; small and useful for debugging parser changes.
    raw_text = models.TextField()

    class Meta:
        ordering = ("snapshot", "position")
        constraints = [
            models.UniqueConstraint(
                fields=("snapshot", "position"),
                name="unique_snapshot_position",
            ),
            models.UniqueConstraint(
                fields=("snapshot", "nomination"),
                name="unique_snapshot_nomination",
            ),
        ]
        indexes = [
            models.Index(fields=("title",)),
            models.Index(fields=("nominator",)),
            models.Index(fields=("status",)),
            models.Index(fields=("nomination_timestamp",)),
            models.Index(fields=("snapshot", "status")),
        ]

    def __str__(self):
        return self.title or f"Malformed nomination in {self.snapshot.revision_id}"
