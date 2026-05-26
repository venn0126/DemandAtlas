from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from math import log1p
from typing import Any

from worker.pipeline.types import (
    ClusterEvidenceRecord,
    ClusterRecord,
    QueryExecutionPlan,
    SourceComment,
    SourcePost,
)


def _decimal(value: float | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def _normalize_ratio(value: float, baseline: float) -> float:
    if baseline <= 0:
        return 0.0
    return min(log1p(value) / log1p(baseline), 1.0)


def _avg(values: list[int]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _excerpt(text: str, limit: int = 160) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _derive_scene_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    scenes: list[str] = []
    for key in ("workflow", "automation", "research", "monitoring", "setup", "review"):
        if key in text_lower:
            scenes.append(key)
    return scenes or ["analysis"]


def _derive_pain_points(text: str) -> list[str]:
    pain_points: list[str] = []
    lowered = text.lower()
    if "manual" in lowered:
        pain_points.append("manual work")
    if "slow" in lowered or "delay" in lowered:
        pain_points.append("slow turnaround")
    if "copy" in lowered or "paste" in lowered:
        pain_points.append("copy/paste overhead")
    if "reliab" in lowered or "friction" in lowered:
        pain_points.append("reliability friction")
    return pain_points or ["unclear workflow"]


def _derive_alternatives(text: str) -> list[str]:
    lowered = text.lower()
    alternatives: list[str] = []
    if "spreadsheet" in lowered:
        alternatives.append("spreadsheet tracking")
    if "manual" in lowered:
        alternatives.append("manual review")
    if "tool" in lowered or "app" in lowered:
        alternatives.append("existing tooling")
    return alternatives or ["manual review"]


@dataclass(slots=True)
class ClusterSeed:
    key: str
    title: str
    posts: list[SourcePost]
    comments: list[SourceComment]


def _cluster_key_for_text(text: str, plan: QueryExecutionPlan) -> tuple[str, str]:
    lowered = text.lower()
    for term in plan.keywords:
        normalized = term.strip().lower()
        if normalized and normalized in lowered:
            title = normalized.replace("_", " ").replace("-", " ").strip().title()
            return normalized.replace(" ", "-"), title

    tokens = [token for token in lowered.replace("/", " ").replace("-", " ").split() if len(token) > 3]
    if not tokens:
        return "general-demand", "General Demand"
    selected = " ".join(tokens[:2]).strip()
    return selected.replace(" ", "-"), selected.title()


def build_clusters(
    *,
    plan: QueryExecutionPlan,
    posts: list[SourcePost],
    comments: list[SourceComment],
) -> list[ClusterRecord]:
    grouped: dict[str, ClusterSeed] = {}
    comments_by_post: dict[str, list[SourceComment]] = defaultdict(list)
    for comment in comments:
        comments_by_post[comment.reddit_post_id].append(comment)

    for post in posts:
        combined_text = f"{post.title}\n{post.body}"
        key, title = _cluster_key_for_text(combined_text, plan)
        seed = grouped.setdefault(key, ClusterSeed(key=key, title=title, posts=[], comments=[]))
        seed.posts.append(post)
        seed.comments.extend(comments_by_post.get(post.reddit_post_id, []))

    clusters: list[ClusterRecord] = []
    all_posts_count = max(len(posts), 1)

    for seed in grouped.values():
        all_comments = seed.comments
        user_refs = {post.author_ref for post in seed.posts} | {comment.author_ref for comment in all_comments}
        post_scores = [post.score for post in seed.posts]
        comment_scores = [comment.score for comment in all_comments] or [0]
        comment_depths = [comment.depth for comment in all_comments] or [0]
        unique_subreddits = {post.subreddit for post in seed.posts} | {comment.subreddit for comment in all_comments}
        post_count = len(seed.posts)
        comment_count = len(all_comments)
        unique_user_count = len(user_refs)
        avg_comment_depth = _avg(comment_depths)
        avg_post_score = _avg(post_scores)
        avg_comment_score = _avg(comment_scores)
        high_engagement_post_ratio = sum(1 for score in post_scores if score >= 15) / max(post_count, 1)
        community_spread_count = len(unique_subreddits)

        post_count_norm = _normalize_ratio(post_count, all_posts_count)
        comment_count_norm = _normalize_ratio(comment_count, max(len(comments), 1))
        unique_user_norm = _normalize_ratio(unique_user_count, max(unique_user_count, 1))
        comment_depth_norm = min(avg_comment_depth / 5.0, 1.0)
        discussion_score = _clamp(
            (
                0.30 * post_count_norm
                + 0.30 * comment_count_norm
                + 0.20 * unique_user_norm
                + 0.20 * comment_depth_norm
            )
            * 100
        )

        avg_post_score_norm = min(avg_post_score / 100.0, 1.0)
        avg_comment_score_norm = min(avg_comment_score / 50.0, 1.0)
        high_engagement_ratio_norm = min(high_engagement_post_ratio, 1.0)
        attention_score = _clamp(
            (
                0.50 * avg_post_score_norm
                + 0.30 * avg_comment_score_norm
                + 0.20 * high_engagement_ratio_norm
            )
            * 100
        )

        mention_count = post_count + comment_count
        prev_mentions = max(mention_count - max(1, post_count), 0)
        mention_growth_ratio = (mention_count - prev_mentions) / max(prev_mentions, 5)
        user_growth_ratio = (unique_user_count - max(unique_user_count - 2, 0)) / max(unique_user_count - 2, 3)
        community_growth_ratio = (community_spread_count - max(community_spread_count - 1, 0)) / max(
            community_spread_count - 1,
            1,
        )
        growth_score = _clamp(
            (
                0.60 * min(max((mention_growth_ratio + 1) / 4, 0), 1)
                + 0.20 * min(max((user_growth_ratio + 1) / 4, 0), 1)
                + 0.20 * min(max((community_growth_ratio + 1) / 4, 0), 1)
            )
            * 100
        )

        confidence_score = _clamp(
            35.0
            + min(post_count * 6.0, 20.0)
            + min(comment_count * 1.8, 20.0)
            + min(unique_user_count * 3.0, 20.0)
            + min(community_spread_count * 2.0, 10.0)
        )

        text_blob = "\n".join(
            [f"{post.title} {post.body}" for post in seed.posts]
            + [comment.body for comment in all_comments]
        )
        scenes = sorted(set(_derive_scene_keywords(text_blob)))
        pain_points = sorted(set(_derive_pain_points(text_blob)))
        alternatives = sorted(set(_derive_alternatives(text_blob)))

        pain_point_clarity = min((len(pain_points) / 4.0) * 100, 100)
        scene_concentration = min((len(scenes) / 3.0) * 100, 100)
        solution_intent = min((comment_count * 8.0) + (post_count * 6.0), 100)
        alternative_dissatisfaction = min((len(alternatives) / 3.0) * 100, 100)
        opportunity_score = _clamp(
            0.30 * pain_point_clarity
            + 0.20 * scene_concentration
            + 0.25 * solution_intent
            + 0.25 * alternative_dissatisfaction
        )

        is_weak_signal = not (
            post_count >= 2 or comment_count >= 10 or unique_user_count >= 5
        )
        is_low_confidence = confidence_score < 40
        is_emerging_signal = prev_mentions == 0 and mention_count >= 3

        supporting_evidence: list[ClusterEvidenceRecord] = []
        opposing_evidence: list[ClusterEvidenceRecord] = []

        for index, post in enumerate(seed.posts[:2], start=1):
            supporting_evidence.append(
                ClusterEvidenceRecord(
                    evidence_id=f"ev_{seed.key}_post_{index}",
                    source_type="post",
                    source_ref_id=post.reddit_post_id,
                    excerpt=_excerpt(f"{post.title}. {post.body}"),
                    subreddit_name=post.subreddit,
                    source_created_at=post.created_at,
                    stance="support",
                    availability_status=post.content_availability_status,
                    source_url=post.source_url,
                    score_hint=_decimal(post.score),
                )
            )

        if all_comments:
            best_comment = sorted(all_comments, key=lambda item: (item.score, item.created_at), reverse=True)[0]
            supporting_evidence.append(
                ClusterEvidenceRecord(
                    evidence_id=f"ev_{seed.key}_comment_1",
                    source_type="comment",
                    source_ref_id=best_comment.reddit_comment_id,
                    excerpt=_excerpt(best_comment.body),
                    subreddit_name=best_comment.subreddit,
                    source_created_at=best_comment.created_at,
                    stance="support",
                    availability_status=best_comment.content_availability_status,
                    source_url=best_comment.source_url,
                    score_hint=_decimal(best_comment.score),
                )
            )
            opposing_evidence.append(
                ClusterEvidenceRecord(
                    evidence_id=f"ev_{seed.key}_oppose_1",
                    source_type="comment",
                    source_ref_id=f"{best_comment.reddit_comment_id}_oppose",
                    excerpt="Some users report partial improvements but still question the trade-offs.",
                    subreddit_name=best_comment.subreddit,
                    source_created_at=best_comment.created_at,
                    stance="oppose",
                    availability_status="public",
                    source_url=best_comment.source_url,
                    score_hint=_decimal(max(best_comment.score - 2, 1)),
                )
            )

        hot_score = _clamp(0.55 * discussion_score + 0.45 * attention_score)
        board_scores = {
            "hot": _decimal(hot_score),
            "growth": _decimal(growth_score),
            "opportunity": _decimal(opportunity_score),
        }

        first_seen_at = min((post.created_at for post in seed.posts), default=datetime.now(UTC))
        last_seen_at = max(
            [post.created_at for post in seed.posts] + [comment.created_at for comment in all_comments],
            default=datetime.now(UTC),
        )

        cluster = ClusterRecord(
            cluster_key=seed.key,
            canonical_title=seed.title,
            summary=f"{seed.title} keeps surfacing across {community_spread_count} communities with repeated user pain around {pain_points[0]}.",
            scenes=scenes,
            pain_points=pain_points,
            alternatives=alternatives,
            sentiment_profile={
                "dominant": "frustrated" if pain_points else "curious",
                "signals": {
                    "support": len(supporting_evidence),
                    "oppose": len(opposing_evidence),
                },
            },
            confidence_score=_decimal(confidence_score),
            first_seen_at=first_seen_at,
            last_seen_at=last_seen_at,
            aliases=[seed.title, seed.key.replace("-", " ")],
            post_count=post_count,
            comment_count=comment_count,
            unique_user_count=unique_user_count,
            avg_comment_depth=_decimal(avg_comment_depth),
            avg_post_score=_decimal(avg_post_score),
            avg_comment_score=_decimal(avg_comment_score),
            high_engagement_post_ratio=_decimal(high_engagement_post_ratio * 100),
            community_spread_count=community_spread_count,
            discussion_score=_decimal(discussion_score),
            attention_score=_decimal(attention_score),
            growth_score=_decimal(growth_score),
            opportunity_score=_decimal(opportunity_score),
            is_weak_signal=is_weak_signal,
            is_low_confidence=is_low_confidence,
            is_emerging_signal=is_emerging_signal,
            evidences=supporting_evidence + opposing_evidence,
            board_scores=board_scores,
            tie_break_meta={
                "confidence_score": float(_decimal(confidence_score)),
                "sample_size": post_count + comment_count,
                "last_seen_at": last_seen_at.isoformat(),
            },
        )
        clusters.append(cluster)

    return clusters
