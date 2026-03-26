"""Media browser for the Demo Integration.

Provides browse and search support for the demo media player, using the
TV_SHOWS list from const.py as a simple in-memory media library.

Browse hierarchy:
  ROOT  →  TV Shows directory (can_browse=True)
  └─ <show title>  (media_class=TV_SHOW, can_play=True)

Search returns any TV show whose title contains the query string
(case-insensitive).

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging

from ucapi.api_definitions import (
    BrowseMediaItem,
    BrowseOptions,
    BrowseResults,
    MediaClass,
    MediaContentType,
    Pagination,
    SearchOptions,
    SearchResults,
)

from const import TV_SHOWS

_LOG = logging.getLogger(__name__)

# Well-known media IDs used in the browse tree
_ROOT_ID = "root"
_TV_SHOWS_ID = "tv_shows"

# Page size when no limit is specified by the client
_DEFAULT_LIMIT = 100


def _make_item(
    media_id: str,
    title: str,
    *,
    media_class: str,
    media_type: str,
    can_browse: bool = False,
    can_play: bool = False,
    can_search: bool = False,
    subtitle: str | None = None,
    items: list[BrowseMediaItem] | None = None,
) -> BrowseMediaItem:
    """Create a :class:`BrowseMediaItem` with sensible defaults."""
    return BrowseMediaItem(
        media_id=media_id,
        title=title,
        media_class=media_class,
        media_type=media_type,
        can_browse=can_browse or False,
        can_play=can_play or False,
        can_search=can_search or False,
        subtitle=subtitle,
        items=items,
    )


def _paginate(items: list, options: BrowseOptions) -> tuple[list, Pagination]:
    """Slice *items* according to the paging options and return the slice + metadata."""
    paging = options.paging
    page = (paging.page or 1) if paging else 1
    limit = (paging.limit or _DEFAULT_LIMIT) if paging else _DEFAULT_LIMIT
    limit = min(max(limit, 1), _DEFAULT_LIMIT)

    start = (page - 1) * limit
    end = start + limit
    sliced = items[start:end]

    pagination = Pagination(page=page, limit=len(sliced), count=len(items))
    return sliced, pagination


def _show_item(title: str) -> BrowseMediaItem:
    """Return a browsable/playable media item for a single TV show."""
    return _make_item(
        media_id=title,
        title=title,
        media_class=MediaClass.TV_SHOW,
        media_type=MediaContentType.TV_SHOW,
        can_play=True,
    )


def _tv_shows_directory(shows: list[str]) -> BrowseMediaItem:
    """Return the *TV Shows* directory item with embedded children."""
    return _make_item(
        media_id=_TV_SHOWS_ID,
        title="TV Shows",
        media_class=MediaClass.DIRECTORY,
        media_type=MediaContentType.TV_SHOW,
        can_browse=True,
        can_search=True,
        items=[_show_item(t) for t in shows],
    )


def _browse_root(options: BrowseOptions) -> BrowseResults:
    """Return the top-level browse root — a single TV Shows directory."""
    root = _make_item(
        media_id=_ROOT_ID,
        title="Demo Library",
        media_class=MediaClass.DIRECTORY,
        media_type=MediaContentType.TV_SHOW,
        can_browse=True,
        items=[_tv_shows_directory(TV_SHOWS)],
    )
    _, pagination = _paginate([root], options)
    return BrowseResults(media=root, pagination=pagination)


def _browse_tv_shows(options: BrowseOptions) -> BrowseResults:
    """Return a paginated list of all TV shows."""
    sliced, pagination = _paginate(TV_SHOWS, options)
    directory = _make_item(
        media_id=_TV_SHOWS_ID,
        title="TV Shows",
        media_class=MediaClass.DIRECTORY,
        media_type=MediaContentType.TV_SHOW,
        can_browse=True,
        can_search=True,
        items=[_show_item(t) for t in sliced],
    )
    return BrowseResults(media=directory, pagination=pagination)


def browse(options: BrowseOptions) -> BrowseResults:
    """
    Return browse results for the given *options*.

    - No ``media_id`` (or ``media_id == "root"``): return the library root.
    - ``media_id == "tv_shows"``: return the paginated list of TV shows.
    - Any other ``media_id``: treat as an individual show — return it as a
      leaf item so the remote can play it directly.
    """
    media_id = options.media_id or _ROOT_ID

    if media_id == _ROOT_ID:
        _LOG.debug("Browsing root")
        return _browse_root(options)

    if media_id == _TV_SHOWS_ID:
        _LOG.debug("Browsing TV shows directory")
        return _browse_tv_shows(options)

    # Individual show — return as a single playable leaf
    if media_id in TV_SHOWS:
        _LOG.debug("Browsing single show: %s", media_id)
        item = _show_item(media_id)
        pagination = Pagination(page=1, limit=1, count=1)
        return BrowseResults(media=item, pagination=pagination)

    _LOG.warning("Unknown media_id for browse: %s", media_id)
    pagination = Pagination(page=1, limit=0, count=0)
    return BrowseResults(media=None, pagination=pagination)


def search(options: SearchOptions) -> SearchResults:
    """
    Search TV shows by free-text *query* (case-insensitive substring match).

    An empty query returns all shows.
    """
    query = (options.query or "").strip().lower()

    if query:
        matches = [t for t in TV_SHOWS if query in t.lower()]
    else:
        matches = list(TV_SHOWS)

    _LOG.debug("Search '%s' → %d result(s)", query, len(matches))

    sliced, pagination = _paginate(matches, options)
    return SearchResults(
        media=[_show_item(t) for t in sliced],
        pagination=pagination,
    )
