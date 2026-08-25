from datetime import (
    datetime,
    timedelta,
    timezone,
)


def checkRecency(
    releaseDate: str | None,
    days: int = 30,
) -> bool:

    if not releaseDate:
        return False

    try:
        modelDate = datetime.strptime(
            releaseDate,
            "%Y-%m-%d",
        ).replace(tzinfo=timezone.utc)

    except ValueError:
        return False

    currentDate = datetime.now(timezone.utc)

    cutoffDate = currentDate - timedelta(days=days)

    return cutoffDate <= modelDate <= currentDate
