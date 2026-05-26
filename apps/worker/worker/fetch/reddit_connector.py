from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from worker.core.config import settings
from worker.pipeline.types import FetchWarning, QueryExecutionPlan


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _slugify(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")


def _match_terms(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    matched: list[str] = []
    for term in terms:
        normalized = term.strip().lower()
        if normalized and normalized in lowered:
            matched.append(term)
    return matched


def _fixture_posts_for_scope(scope: str, plan: QueryExecutionPlan) -> list[dict[str, Any]]:
    now = _utc_now()
    base_terms = plan.keywords[:2] or ["workflow", "automation"]
    posts: list[dict[str, Any]] = []
    for index, term in enumerate(base_terms, start=1):
        title = f"{term.title()} friction keeps showing up in {scope}"
        body = (
            f"People in r/{scope} keep discussing {term} setup friction, reliability issues, "
            "and repetitive manual steps."
        )
        posts.append(
            {
                "source_scope": scope,
                "id": f"fixture_{_slugify(scope)}_{index}",
                "subreddit": scope,
                "title": title,
                "selftext": body,
                "author": f"user_{index}",
                "score": 20 + index * 7,
                "num_comments": 8 + index * 4,
                "created_utc": int((now - timedelta(days=index)).timestamp()),
                "permalink": f"/r/{scope}/comments/fixture_{_slugify(scope)}_{index}",
                "stickied": False,
                "over_18": False,
                "is_self": True,
                "matched_keywords": _match_terms(f"{title} {body}", plan.keywords + plan.region_hints),
            }
        )
    return posts


def _fixture_comments_for_post(post: dict[str, Any], plan: QueryExecutionPlan) -> list[dict[str, Any]]:
    now = _utc_now()
    comments: list[dict[str, Any]] = []
    seed_terms = post.get("matched_keywords") or plan.keywords[:1] or ["workflow"]
    for index, term in enumerate(seed_terms[: max(1, settings.reddit_comment_limit_per_post // 4)], start=1):
        body = (
            f"I keep running into {term} problems here. The current tools still require "
            "manual review and too much copy/paste."
        )
        comments.append(
            {
                "id": f"{post['id']}_c{index}",
                "link_id": f"t3_{post['id']}",
                "parent_id": f"t3_{post['id']}",
                "subreddit": post["subreddit"],
                "body": body,
                "author": f"commenter_{index}",
                "score": 5 + index * 3,
                "depth": min(index, 3),
                "created_utc": int((now - timedelta(hours=index)).timestamp()),
                "permalink": f"{post['permalink']}?comment={post['id']}_c{index}",
                "matched_keywords": _match_terms(body, plan.keywords + plan.region_hints),
            }
        )
    return comments


class RedditConnector:
    def __init__(self) -> None:
        self._token: str | None = None
        self._token_expires_at: datetime | None = None

    @property
    def oauth_enabled(self) -> bool:
        return bool(
            settings.reddit_client_id
            and settings.reddit_client_secret
            and settings.reddit_user_agent
        )

    def fetch(self, plan: QueryExecutionPlan) -> dict[str, Any]:
        if self.oauth_enabled:
            try:
                return self._fetch_via_oauth(plan)
            except Exception as exc:
                fixture_payload = self._build_fixture_payload(plan)
                fixture_payload["warnings"].append(
                    FetchWarning(
                        code="REDDIT_OAUTH_FALLBACK",
                        message=f"oauth fetch failed, fallback to fixture payload: {exc}",
                    )
                )
                return fixture_payload
        return self._build_fixture_payload(plan)

    def _build_fixture_payload(self, plan: QueryExecutionPlan) -> dict[str, Any]:
        posts: list[dict[str, Any]] = []
        comments: list[dict[str, Any]] = []
        warnings: list[FetchWarning] = []

        for index, scope in enumerate(plan.source_scope):
            if plan.query_type == "directed" and len(plan.source_scope) >= 3 and index == len(plan.source_scope) - 1:
                warnings.append(
                    FetchWarning(
                        code="SOURCE_FETCH_PARTIAL",
                        message=f"source scope {scope} unavailable during fetch",
                        source=scope,
                    )
                )
                continue

            scope_posts = _fixture_posts_for_scope(scope, plan)
            posts.extend(scope_posts)
            for post in scope_posts:
                comments.extend(_fixture_comments_for_post(post, plan))

        return {
            "posts": posts,
            "comments": comments,
            "warnings": warnings,
            "sync_freshness_note": f"latest source sync at {_utc_now().isoformat()}",
            "execution_mode": "fixture_pipeline",
        }

    def _fetch_via_oauth(self, plan: QueryExecutionPlan) -> dict[str, Any]:
        token = self._get_token()
        headers = {
            "Authorization": f"bearer {token}",
            "User-Agent": settings.reddit_user_agent,
        }
        posts: list[dict[str, Any]] = []
        comments: list[dict[str, Any]] = []
        warnings: list[FetchWarning] = []

        with httpx.Client(timeout=20.0, headers=headers) as client:
            for scope in plan.source_scope:
                try:
                    scope_posts = self._fetch_scope_posts(client, scope, plan)
                except Exception as exc:
                    warnings.append(
                        FetchWarning(
                            code="SOURCE_FETCH_PARTIAL",
                            message=f"source scope {scope} unavailable during fetch: {exc}",
                            source=scope,
                        )
                    )
                    continue

                posts.extend(scope_posts)
                for post in scope_posts[: settings.reddit_fetch_limit_per_source]:
                    comments.extend(self._fetch_post_comments(client, post, plan))

        return {
            "posts": posts,
            "comments": comments,
            "warnings": warnings,
            "sync_freshness_note": f"latest source sync at {_utc_now().isoformat()}",
            "execution_mode": "reddit_oauth_pipeline",
        }

    def _get_token(self) -> str:
        now = _utc_now()
        if self._token and self._token_expires_at and now < self._token_expires_at:
            return self._token

        response = httpx.post(
            settings.reddit_token_url,
            auth=(settings.reddit_client_id, settings.reddit_client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": settings.reddit_user_agent},
            timeout=20.0,
        )
        response.raise_for_status()
        payload = response.json()
        access_token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 3600))
        self._token = access_token
        self._token_expires_at = now + timedelta(seconds=max(60, expires_in - 60))
        return access_token

    def _fetch_scope_posts(
        self,
        client: httpx.Client,
        scope: str,
        plan: QueryExecutionPlan,
    ) -> list[dict[str, Any]]:
        if plan.query_type == "directed" and plan.keywords:
            query = " OR ".join(plan.keywords[:3])
            url = f"{settings.reddit_base_url}/r/{scope}/search"
            params = {
                "q": query,
                "sort": "new" if plan.view_type == "new" else "relevance",
                "limit": settings.reddit_fetch_limit_per_source,
                "restrict_sr": "on",
                "type": "link",
            }
        else:
            listing = "new" if plan.view_type == "new" else "hot"
            url = f"{settings.reddit_base_url}/r/{scope}/{listing}"
            params = {"limit": settings.reddit_fetch_limit_per_source}

        response = client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()
        items = payload.get("data", {}).get("children", [])
        posts: list[dict[str, Any]] = []
        for item in items:
            data = item.get("data") or {}
            text = f"{data.get('title', '')}\n{data.get('selftext', '')}"
            posts.append(
                {
                    "source_scope": scope,
                    "id": data.get("id") or f"missing_{scope}",
                    "subreddit": data.get("subreddit") or scope,
                    "title": data.get("title") or "",
                    "selftext": data.get("selftext") or "",
                    "author": data.get("author") or "[deleted]",
                    "score": int(data.get("score") or 0),
                    "num_comments": int(data.get("num_comments") or 0),
                    "created_utc": int(data.get("created_utc") or 0),
                    "permalink": data.get("permalink") or "",
                    "stickied": bool(data.get("stickied") or False),
                    "over_18": bool(data.get("over_18") or False),
                    "is_self": bool(data.get("is_self") or False),
                    "matched_keywords": _match_terms(text, plan.keywords + plan.region_hints),
                }
            )
        return posts

    def _fetch_post_comments(
        self,
        client: httpx.Client,
        post: dict[str, Any],
        plan: QueryExecutionPlan,
    ) -> list[dict[str, Any]]:
        permalink = post.get("permalink") or ""
        if not permalink:
            return []

        response = client.get(
            f"{settings.reddit_base_url}{permalink}",
            params={"limit": settings.reddit_comment_limit_per_post, "depth": 2},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2:
            return []

        listing = payload[1].get("data", {}).get("children", [])
        comments: list[dict[str, Any]] = []
        for item in listing:
            data = item.get("data") or {}
            body = data.get("body") or ""
            comments.append(
                {
                    "id": data.get("id") or f"{post['id']}_comment",
                    "link_id": data.get("link_id") or f"t3_{post['id']}",
                    "parent_id": data.get("parent_id"),
                    "subreddit": data.get("subreddit") or post["subreddit"],
                    "body": body,
                    "author": data.get("author") or "[deleted]",
                    "score": int(data.get("score") or 0),
                    "depth": int(data.get("depth") or 0),
                    "created_utc": int(data.get("created_utc") or 0),
                    "permalink": data.get("permalink") or permalink,
                    "matched_keywords": _match_terms(body, plan.keywords + plan.region_hints),
                }
            )
        return comments
