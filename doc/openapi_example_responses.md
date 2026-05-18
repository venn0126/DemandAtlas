# Demand Atlas｜需见 OpenAPI Example Responses

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 OpenAPI Example Responses
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：前后端联调 / Mock 数据准备 / OpenAPI 示例补充 / 验收口径对齐
- 上游输入：
  - `doc/api_contract_draft.md`
  - `doc/openapi_v1_outline.md`
  - `doc/information_architecture_and_state_flow.md`

---

## 2. 文档目标

本文档提供 V1 阶段关键接口的示例响应，用于：

1. 前端 mock 数据生成
2. 后端接口联调参考
3. OpenAPI examples 字段补充
4. 页面状态验收对齐

### 2.1 说明

- 示例中的 ID、时间、URL 均为演示用途
- 字段以 `doc/api_contract_draft.md` 为准
- 若正式实现与示例冲突，以最终 API Contract 为准

---

## 3. Topic Templates

## 3.1 `GET /api/v1/topic-templates`

### 200 成功

```json
{
  "request_id": "req_tpl_list_001",
  "data": {
    "items": [
      {
        "template_id": "tpl_ai_tools",
        "template_version_id": "tplv_ai_tools_003",
        "name": "AI Tools",
        "description": "AI productivity, automation, and creator tooling",
        "default_language": "en",
        "default_view_type": "active"
      },
      {
        "template_id": "tpl_consumer_audio",
        "template_version_id": "tplv_consumer_audio_002",
        "name": "Consumer Audio",
        "description": "Headphones, earbuds, audio accessories, and listening scenarios",
        "default_language": "en",
        "default_view_type": "active"
      }
    ]
  },
  "meta": {},
  "error": null
}
```

## 3.2 `GET /api/v1/topic-templates/{template_id}`

### 200 成功

```json
{
  "request_id": "req_tpl_detail_001",
  "data": {
    "template_id": "tpl_ai_tools",
    "template_version_id": "tplv_ai_tools_003",
    "name": "AI Tools",
    "description": "AI productivity, automation, and creator tooling",
    "default_language": "en",
    "default_view_type": "active",
    "candidate_subreddit_count": 12
  },
  "meta": {},
  "error": null
}
```

### 404 模板不存在

```json
{
  "request_id": "req_tpl_detail_404",
  "data": null,
  "meta": {},
  "error": {
    "code": "TEMPLATE_NOT_FOUND",
    "message": "topic template not found",
    "details": {
      "template_id": "tpl_unknown"
    }
  }
}
```

---

## 4. Query Tasks

## 4.1 `POST /api/v1/query-tasks`

## 场景 A：一键发现命中缓存

### 200 成功

```json
{
  "request_id": "req_qt_create_cache_hit_001",
  "data": {
    "execution_mode": "cache_hit",
    "query_task_id": "qt_01JVA1HBM4YF2T2M6Q5M5M2F0A",
    "status": "success",
    "result_snapshot_id": "rs_01JVA1JD7YQCKRZVMD0W2X5P4M",
    "cached": true
  },
  "meta": {
    "response_source": "database",
    "cache_source": "query_task_result_snapshot",
    "cache_hit_query_task_id": "11111111-1111-1111-1111-111111111111",
    "cache_hit_result_snapshot_id": "22222222-2222-2222-2222-222222222222",
    "cache_hit_status": "success",
    "cache_freshness_seconds": 42
  },
  "error": null
}
```

## 场景 B：定向发现进入异步任务

### 202 已受理

```json
{
  "request_id": "req_qt_create_async_001",
  "data": {
    "execution_mode": "async",
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "status": "pending",
    "poll_url": "/api/v1/query-tasks/qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "anonymous_query_access_token": "anon_tok_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo"
  },
  "meta": {
    "response_source": "database",
    "cache_source": "cache_miss",
    "retry_after_ms": 1500
  },
  "error": null
}
```

## 场景 C：输入范围过大

### 422 语义不可执行

```json
{
  "request_id": "req_qt_create_422_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "QUERY_TOO_BROAD",
    "message": "query scope is too broad for V1 execution limits",
    "details": {
      "max_keywords": 5,
      "max_subreddits": 20
    }
  }
}
```

## 场景 D：模板不可用

### 422 模板不可执行

```json
{
  "request_id": "req_qt_create_422_002",
  "data": null,
  "meta": {},
  "error": {
    "code": "TEMPLATE_NOT_ACTIVE",
    "message": "topic template is not active",
    "details": {
      "template_id": "tpl_archived_audio"
    }
  }
}
```

---

## 4.2 `GET /api/v1/query-tasks/{query_task_id}`

## 场景 A：pending

### 200 成功

```json
{
  "request_id": "req_qt_status_pending_001",
  "data": {
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "status": "pending",
    "current_stage": null,
    "progress": {
      "current_step": 0,
      "total_steps": 8,
      "percent": 0
    },
    "result_snapshot_id": null,
    "coverage_note": null,
    "warnings": []
  },
  "meta": {
    "response_source": "database",
    "pipeline_metadata": null,
    "warning_count": 0,
    "coverage_status": null,
    "requested_source_count": null,
    "completed_source_count": null,
    "source_scope_count": null,
    "result_cluster_count": null
  },
  "error": null
}
```

## 场景 B：running

### 200 成功

```json
{
  "request_id": "req_qt_status_running_001",
  "data": {
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "status": "running",
    "current_stage": "cluster",
    "progress": {
      "current_step": 6,
      "total_steps": 8,
      "percent": 72
    },
    "result_snapshot_id": null,
    "coverage_note": null,
    "warnings": []
  },
  "meta": {},
  "error": null
}
```

## 场景 C：partial_success

### 200 成功

```json
{
  "request_id": "req_qt_status_partial_001",
  "data": {
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "status": "partial_success",
    "current_stage": "snapshot",
    "progress": {
      "current_step": 8,
      "total_steps": 8,
      "percent": 100
    },
    "result_snapshot_id": "rs_01JVA1PAB2Y9PGKQ7NH1AK6R9M",
    "coverage_note": "2 candidate subreddits failed during fetch; results were generated from available sources",
    "warnings": [
      {
        "code": "PARTIAL_COVERAGE",
        "message": "partial coverage: 1 requested subreddit unavailable during fetch"
      },
      {
        "code": "PIPELINE_FETCH_PARTIAL_SUCCESS",
        "message": "fetched placeholder source documents from 2/3 scopes"
      },
      {
        "code": "PIPELINE_FINALIZE_PARTIAL_SUCCESS",
        "message": "pipeline finalized in placeholder mode"
      }
    ]
  },
  "meta": {
    "response_source": "database",
    "pipeline_metadata": {
      "query_type": "directed",
      "execution_mode": "placeholder_worker_pipeline",
      "source_scope": {
        "keywords": ["meta-partial"],
        "subreddits": ["a", "b", "c"],
        "source_count": 3
      },
      "coverage": {
        "status": "partial_success",
        "requested_source_count": 3,
        "completed_source_count": 2
      },
      "result_profile": {
        "cluster_count": 6,
        "post_count": 24,
        "comment_count": 120
      }
    },
    "warning_count": 3,
    "coverage_status": "partial_success",
    "requested_source_count": 3,
    "completed_source_count": 2,
    "source_scope_count": 3,
    "result_cluster_count": 6
  },
  "error": null
}
```

## 场景 D：success

### 200 成功

```json
{
  "request_id": "req_qt_status_success_001",
  "data": {
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "status": "success",
    "current_stage": "snapshot",
    "progress": {
      "current_step": 8,
      "total_steps": 8,
      "percent": 100
    },
    "result_snapshot_id": "rs_01JVA1T4WM4B3PG5N8W1HEP7QA",
    "coverage_note": "full coverage on candidate sources",
    "warnings": []
  },
  "meta": {
    "response_source": "database",
    "pipeline_metadata": {
      "query_type": "directed",
      "execution_mode": "placeholder_worker_pipeline",
      "source_scope": {
        "keywords": ["meta-check"],
        "subreddits": [],
        "source_count": 1
      },
      "coverage": {
        "status": "success",
        "requested_source_count": 1,
        "completed_source_count": 1
      },
      "result_profile": {
        "cluster_count": 4,
        "post_count": 16,
        "comment_count": 80
      }
    },
    "warning_count": 0,
    "coverage_status": "success",
    "requested_source_count": 1,
    "completed_source_count": 1,
    "source_scope_count": 1,
    "result_cluster_count": 4
  },
  "error": null
}
```

## 场景 E：failed

### 200 失败状态返回

```json
{
  "request_id": "req_qt_status_failed_001",
  "data": {
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "status": "failed",
    "current_stage": "fetch",
    "progress": {
      "current_step": 3,
      "total_steps": 8,
      "percent": 25
    },
    "result_snapshot_id": null,
    "coverage_note": null,
    "warnings": []
  },
  "meta": {},
  "error": {
    "code": "NO_FETCHABLE_SOURCE",
    "message": "unable to fetch any valid source data",
    "details": {}
  }
}
```

## 场景 F：匿名 token 无效

### 403 拒绝访问

```json
{
  "request_id": "req_qt_status_403_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "ACCESS_DENIED",
    "message": "invalid anonymous query access token",
    "details": {}
  }
}
```

---

## 5. Result Snapshots

## 5.1 `GET /api/v1/result-snapshots/{result_snapshot_id}`

## 场景 A：正常结果摘要

### 200 成功

```json
{
  "request_id": "req_rs_summary_001",
  "data": {
    "result_snapshot_id": "rs_01JVA1T4WM4B3PG5N8W1HEP7QA",
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "query_type": "directed",
    "view_type": "active",
    "time_window": {
      "start_at": "2026-04-01T00:00:00Z",
      "end_at": "2026-05-01T00:00:00Z"
    },
    "generated_at": "2026-05-12T09:12:00Z",
    "coverage_note": "full coverage on candidate sources",
    "sync_freshness_note": "latest source sync at 2026-05-12T08:47:00Z",
    "summary_stats": {
      "cluster_count": 18,
      "post_count": 236,
      "comment_count": 1943
    },
    "available_boards": ["hot", "growth", "opportunity"]
  },
  "meta": {
    "response_source": "database",
    "pipeline_metadata": {
      "query_type": "directed",
      "execution_mode": "placeholder_worker_pipeline",
      "source_scope": {
        "keywords": ["snapshot-meta-success"],
        "subreddits": [],
        "source_count": 1
      },
      "coverage": {
        "status": "success",
        "requested_source_count": 1,
        "completed_source_count": 1
      },
      "result_profile": {
        "cluster_count": 4,
        "post_count": 16,
        "comment_count": 80
      }
    },
    "warning_count": 0
  },
  "error": null
}
```

## 场景 B：无结果

### 200 成功

```json
{
  "request_id": "req_rs_summary_empty_001",
  "data": {
    "result_snapshot_id": "rs_01JVA2120R3D39SY1CMN18R8QW",
    "query_task_id": "qt_01JVA20F4A1B31ANJVVKQJ0ZJ4",
    "query_type": "directed",
    "view_type": "active",
    "time_window": {
      "start_at": "2026-04-01T00:00:00Z",
      "end_at": "2026-05-01T00:00:00Z"
    },
    "generated_at": "2026-05-12T09:28:00Z",
    "coverage_note": "no valid clusters were formed from available sources",
    "sync_freshness_note": "latest source sync at 2026-05-12T09:20:00Z",
    "summary_stats": {
      "cluster_count": 0,
      "post_count": 8,
      "comment_count": 17
    },
    "available_boards": ["hot"]
  },
  "meta": {},
  "error": null
}
```

## 场景 C：部分成功摘要

### 200 成功

```json
{
  "request_id": "req_rs_summary_partial_001",
  "data": {
    "result_snapshot_id": "rs_01JVA1PAB2Y9PGKQ7NH1AK6R9M",
    "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
    "query_type": "directed",
    "view_type": "active",
    "time_window": {
      "start_at": "2026-04-18T00:00:00+00:00",
      "end_at": "2026-05-18T00:00:00+00:00"
    },
    "generated_at": "2026-05-18T10:11:04.238775+00:00",
    "coverage_note": "partial coverage: 1 requested subreddit unavailable during fetch",
    "sync_freshness_note": "latest source sync at 2026-05-18T10:11:04.217814+00:00",
    "summary_stats": {
      "cluster_count": 6,
      "post_count": 24,
      "comment_count": 120
    },
    "available_boards": ["hot", "growth", "opportunity"]
  },
  "meta": {
    "response_source": "database",
    "pipeline_metadata": {
      "query_type": "directed",
      "execution_mode": "placeholder_worker_pipeline",
      "source_scope": {
        "keywords": ["snapshot-meta-partial"],
        "subreddits": ["a", "b", "c"],
        "source_count": 3
      },
      "coverage": {
        "status": "partial_success",
        "requested_source_count": 3,
        "completed_source_count": 2
      },
      "result_profile": {
        "cluster_count": 6,
        "post_count": 24,
        "comment_count": 120
      }
    },
    "warning_count": 1
  },
  "error": null
}
```

---

## 5.2 `GET /api/v1/result-snapshots/{result_snapshot_id}/boards/{board_type}`

## 场景 A：热门榜正常返回

### 200 成功

```json
{
  "request_id": "req_board_hot_001",
  "data": {
    "board_type": "hot",
    "items": [
      {
        "rank": 1,
        "cluster_id": "clu_01JVA2G0X9W4N9V6W2JQ1H4A4C",
        "title": "Users still prefer wired earbuds for reliability",
        "summary": "Users repeatedly mention reliability, no charging anxiety, and lower latency.",
        "board_score": 87.2,
        "discussion_score": 82.0,
        "attention_score": 79.5,
        "growth_score": 41.0,
        "opportunity_score": 73.0,
        "confidence_score": 88.0,
        "post_count": 12,
        "comment_count": 143,
        "unique_user_count": 56,
        "is_weak_signal": false,
        "is_low_confidence": false,
        "is_emerging_signal": false,
        "top_subreddits": ["Earbuds", "HeadphoneAdvice"],
        "highlight_evidence": [
          {
            "evidence_id": "ev_01JVA2M3N2X6JYV0T2SR2Y8GF7",
            "excerpt": "Wired just works.",
            "subreddit": "Earbuds",
            "created_at": "2026-04-22T09:00:00Z",
            "availability_status": "public",
            "source_url": "https://reddit.com/r/Earbuds/comments/demo1"
          }
        ]
      },
      {
        "rank": 2,
        "cluster_id": "clu_01JVA2HFQYEXN30A94M4EN2HNB",
        "title": "AI note-taking tools still fail on action-item extraction",
        "summary": "Users discuss missing follow-up actions, bad summaries, and poor meeting context retention.",
        "board_score": 84.3,
        "discussion_score": 76.5,
        "attention_score": 81.8,
        "growth_score": 52.7,
        "opportunity_score": 78.9,
        "confidence_score": 82.0,
        "post_count": 9,
        "comment_count": 121,
        "unique_user_count": 43,
        "is_weak_signal": false,
        "is_low_confidence": false,
        "is_emerging_signal": false,
        "top_subreddits": ["productivity", "artificial"],
        "highlight_evidence": [
          {
            "evidence_id": "ev_01JVA2N9KTMT4E6V5H0B7DZT7M",
            "excerpt": "The summary is fine, but it never captures my next steps properly.",
            "subreddit": "productivity",
            "created_at": "2026-04-19T06:30:00Z",
            "availability_status": "public",
            "source_url": "https://reddit.com/r/productivity/comments/demo2"
          }
        ]
      }
    ]
  },
  "meta": {
    "next_page_token": "board_hot_pg_2_demo",
    "response_source": "database",
    "warning_count": 0
  },
  "error": null
}
```

## 场景 B：增长榜中包含新兴信号

### 200 成功

```json
{
  "request_id": "req_board_growth_001",
  "data": {
    "board_type": "growth",
    "items": [
      {
        "rank": 1,
        "cluster_id": "clu_01JVA2Q5XQWQAPBK5B0C7WQ9YP",
        "title": "Users are suddenly discussing offline AI transcription on laptops",
        "summary": "The demand rose quickly around privacy, offline access, and slow cloud upload workflows.",
        "board_score": 91.0,
        "discussion_score": 48.0,
        "attention_score": 55.0,
        "growth_score": 91.0,
        "opportunity_score": 76.0,
        "confidence_score": 66.0,
        "post_count": 3,
        "comment_count": 27,
        "unique_user_count": 14,
        "is_weak_signal": false,
        "is_low_confidence": false,
        "is_emerging_signal": true,
        "top_subreddits": ["LocalLLaMA", "productivity"],
        "highlight_evidence": [
          {
            "evidence_id": "ev_01JVA2S7TZM5XDV0AF0P2SH80C",
            "excerpt": "I just want transcription without sending every meeting to the cloud.",
            "subreddit": "LocalLLaMA",
            "created_at": "2026-04-28T15:00:00Z",
            "availability_status": "public",
            "source_url": "https://reddit.com/r/LocalLLaMA/comments/demo3"
          }
        ]
      }
    ]
  },
  "meta": {
    "next_page_token": null,
    "response_source": "database",
    "warning_count": 0
  },
  "error": null
}
```

## 场景 C：机会榜存在低置信度条目

### 200 成功

```json
{
  "request_id": "req_board_opportunity_001",
  "data": {
    "board_type": "opportunity",
    "items": [
      {
        "rank": 1,
        "cluster_id": "clu_01JVA2W5A7R6T2KRK0Q4N0D4Y7",
        "title": "People want simpler ADHD-friendly daily planning systems",
        "summary": "The need is repeatedly framed around low-friction planning, fewer steps, and visible progress cues.",
        "board_score": 78.4,
        "discussion_score": 49.0,
        "attention_score": 62.0,
        "growth_score": 44.0,
        "opportunity_score": 78.4,
        "confidence_score": 39.0,
        "post_count": 2,
        "comment_count": 18,
        "unique_user_count": 11,
        "is_weak_signal": false,
        "is_low_confidence": true,
        "is_emerging_signal": false,
        "top_subreddits": ["ADHD", "productivity"],
        "highlight_evidence": [
          {
            "evidence_id": "ev_01JVA2XQ6YXEP0J6F5M2S0KB2A",
            "excerpt": "Most planners feel like another job, not support.",
            "subreddit": "ADHD",
            "created_at": "2026-04-24T10:40:00Z",
            "availability_status": "public",
            "source_url": "https://reddit.com/r/ADHD/comments/demo4"
          }
        ]
      }
    ]
  },
  "meta": {
    "next_page_token": null,
    "response_source": "database",
    "warning_count": 0
  },
  "error": null
}
```

## 场景 D：无结果榜单

### 200 成功

```json
{
  "request_id": "req_board_empty_001",
  "data": {
    "board_type": "hot",
    "items": []
  },
  "meta": {
    "next_page_token": null,
    "response_source": "database",
    "warning_count": 0
  },
  "error": null
}
```

---

## 5.3 `GET /api/v1/result-snapshots/{result_snapshot_id}/clusters/{cluster_id}`

## 场景 A：正常详情

### 200 成功

```json
{
  "request_id": "req_cluster_detail_001",
  "data": {
    "cluster_id": "clu_01JVA2G0X9W4N9V6W2JQ1H4A4C",
    "title": "Users still prefer wired earbuds for reliability",
    "summary": "In the last 30 days, users repeatedly discussed stability, lower latency, and no charging overhead.",
    "time_window": {
      "start_at": "2026-04-01T00:00:00Z",
      "end_at": "2026-05-01T00:00:00Z"
    },
    "flags": {
      "is_weak_signal": false,
      "is_low_confidence": false,
      "is_emerging_signal": false
    },
    "scores": {
      "discussion_score": 82.0,
      "attention_score": 79.5,
      "growth_score": 41.0,
      "opportunity_score": 73.0,
      "confidence_score": 88.0
    },
    "metrics": {
      "post_count": 12,
      "comment_count": 143,
      "unique_user_count": 56,
      "community_spread_count": 4
    },
    "scenes": ["commuting", "gaming", "video editing"],
    "pain_points": [
      "bluetooth instability",
      "charging burden",
      "higher latency"
    ],
    "alternatives": ["wireless earbuds", "budget bluetooth headsets"],
    "supporting_evidence": [
      {
        "evidence_id": "ev_01JVA2M3N2X6JYV0T2SR2Y8GF7",
        "excerpt": "Wired just works.",
        "subreddit": "Earbuds",
        "created_at": "2026-04-22T09:00:00Z",
        "availability_status": "public",
        "source_url": "https://reddit.com/r/Earbuds/comments/demo1"
      },
      {
        "evidence_id": "ev_01JVA34FP7VJ0GZ4M7P0P8Q8R3",
        "excerpt": "I don't want another thing to charge.",
        "subreddit": "HeadphoneAdvice",
        "created_at": "2026-04-26T12:15:00Z",
        "availability_status": "public",
        "source_url": "https://reddit.com/r/HeadphoneAdvice/comments/demo5"
      }
    ],
    "opposing_evidence": [
      {
        "evidence_id": "ev_01JVA35QX7Q5Q2FTQG9S6ZWY4S",
        "excerpt": "Cables still fail for me after a few months.",
        "subreddit": "BuyItForLife",
        "created_at": "2026-04-29T08:45:00Z",
        "availability_status": "public",
        "source_url": "https://reddit.com/r/BuyItForLife/comments/demo6"
      }
    ],
    "top_subreddits": ["Earbuds", "HeadphoneAdvice", "BuyItForLife"],
    "coverage_note": "full coverage on candidate sources"
  },
  "meta": {
    "evidence_next_page_token": null,
    "response_source": "database",
    "warning_count": 0
  },
  "error": null
}
```

## 场景 B：详情中存在不可访问证据

### 200 成功

```json
{
  "request_id": "req_cluster_detail_partial_evidence_001",
  "data": {
    "cluster_id": "clu_01JVA2HFQYEXN30A94M4EN2HNB",
    "title": "AI note-taking tools still fail on action-item extraction",
    "summary": "Users describe unreliable follow-up capture and poor context continuity in meeting summaries.",
    "time_window": {
      "start_at": "2026-04-01T00:00:00Z",
      "end_at": "2026-05-01T00:00:00Z"
    },
    "flags": {
      "is_weak_signal": false,
      "is_low_confidence": false,
      "is_emerging_signal": false
    },
    "scores": {
      "discussion_score": 76.5,
      "attention_score": 81.8,
      "growth_score": 52.7,
      "opportunity_score": 78.9,
      "confidence_score": 82.0
    },
    "metrics": {
      "post_count": 9,
      "comment_count": 121,
      "unique_user_count": 43,
      "community_spread_count": 3
    },
    "scenes": ["team meetings", "client calls", "async follow-up"],
    "pain_points": [
      "missing action items",
      "weak context retention",
      "manual cleanup after summary"
    ],
    "alternatives": ["manual notes", "meeting bots", "task apps"],
    "supporting_evidence": [
      {
        "evidence_id": "ev_01JVA2N9KTMT4E6V5H0B7DZT7M",
        "excerpt": "The summary is fine, but it never captures my next steps properly.",
        "subreddit": "productivity",
        "created_at": "2026-04-19T06:30:00Z",
        "availability_status": "public",
        "source_url": "https://reddit.com/r/productivity/comments/demo2"
      },
      {
        "evidence_id": "ev_01JVA38RTJ7XGAPY3E6J2FE6PW",
        "excerpt": "Source content unavailable. Evidence retained as metadata only.",
        "subreddit": "artificial",
        "created_at": "2026-04-21T13:20:00Z",
        "availability_status": "removed",
        "source_url": null
      }
    ],
    "opposing_evidence": [],
    "top_subreddits": ["productivity", "artificial"],
    "coverage_note": "1 evidence item was removed after source sync"
  },
  "meta": {
    "evidence_next_page_token": null,
    "response_source": "database",
    "warning_count": 1
  },
  "error": null
}
```

## 场景 C：详情不存在

### 404 不存在

```json
{
  "request_id": "req_cluster_detail_404_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "NOT_FOUND",
    "message": "cluster detail not found in current result snapshot",
    "details": {
      "result_snapshot_id": "rs_01JVA1T4WM4B3PG5N8W1HEP7QA",
      "cluster_id": "clu_unknown"
    }
  }
}
```

---

## 6. Export Jobs

## 6.1 `POST /api/v1/export-jobs`

## 场景 A：创建成功

### 202 已受理

```json
{
  "request_id": "req_export_create_001",
  "data": {
    "export_job_id": "exp_01JVA3F5BPB6QYH2FAM0X6G8S0",
    "status": "pending",
    "poll_url": "/api/v1/export-jobs/exp_01JVA3F5BPB6QYH2FAM0X6G8S0"
  },
  "meta": {},
  "error": null
}
```

## 场景 B：未登录

### 401 未认证

```json
{
  "request_id": "req_export_create_401_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "authentication is required for export",
    "details": {}
  }
}
```

## 场景 C：导出类型不支持

### 422 不支持

```json
{
  "request_id": "req_export_create_422_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "EXPORT_TYPE_UNSUPPORTED",
    "message": "export type is not supported",
    "details": {
      "export_type": "pdf"
    }
  }
}
```

---

## 6.2 `GET /api/v1/export-jobs/{export_job_id}`

## 场景 A：running

### 200 成功

```json
{
  "request_id": "req_export_status_running_001",
  "data": {
    "export_job_id": "exp_01JVA3F5BPB6QYH2FAM0X6G8S0",
    "status": "running",
    "download_url": null,
    "expires_at": null
  },
  "meta": {},
  "error": null
}
```

## 场景 B：success

### 200 成功

```json
{
  "request_id": "req_export_status_success_001",
  "data": {
    "export_job_id": "exp_01JVA3F5BPB6QYH2FAM0X6G8S0",
    "status": "success",
    "download_url": "https://storage.example.com/exports/2026-05-12/exp_01JVA3F5BPB6QYH2FAM0X6G8S0.md",
    "expires_at": "2026-05-13T09:50:00Z"
  },
  "meta": {},
  "error": null
}
```

## 场景 C：failed

### 200 失败状态返回

```json
{
  "request_id": "req_export_status_failed_001",
  "data": {
    "export_job_id": "exp_01JVA3F5BPB6QYH2FAM0X6G8S0",
    "status": "failed",
    "download_url": null,
    "expires_at": null
  },
  "meta": {},
  "error": {
    "code": "EXPORT_GENERATION_FAILED",
    "message": "failed to generate export file",
    "details": {}
  }
}
```

---

## 7. 通用错误响应示例

## 7.1 400 参数错误

```json
{
  "request_id": "req_error_400_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "INVALID_INPUT",
    "message": "time_window.start_at must be earlier than time_window.end_at",
    "details": {
      "field": "time_window"
    }
  }
}
```

## 7.2 401 未认证

```json
{
  "request_id": "req_error_401_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "authentication required",
    "details": {}
  }
}
```

## 7.3 403 拒绝访问

```json
{
  "request_id": "req_error_403_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "ACCESS_DENIED",
    "message": "you do not have permission to access this resource",
    "details": {}
  }
}
```

## 7.4 404 不存在

```json
{
  "request_id": "req_error_404_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "NOT_FOUND",
    "message": "resource not found",
    "details": {}
  }
}
```

## 7.5 429 限流

```json
{
  "request_id": "req_error_429_001",
  "data": null,
  "meta": {
    "retry_after_ms": 30000
  },
  "error": {
    "code": "RATE_LIMITED",
    "message": "too many requests",
    "details": {}
  }
}
```

## 7.6 500 系统错误

```json
{
  "request_id": "req_error_500_001",
  "data": null,
  "meta": {},
  "error": {
    "code": "SYSTEM_ERROR",
    "message": "unexpected internal error",
    "details": {}
  }
}
```

---

## 8. 前端 Mock 优先级建议

若前端要先做 mock，建议优先准备以下 8 套数据：

1. 一键发现命中缓存
2. 定向发现异步任务 running
3. QueryTask partial_success
4. ResultSnapshot 正常摘要
5. 热门榜正常列表
6. 增长榜新兴信号列表
7. 详情页正常数据
8. 无结果 / 失败 / 权限错误

---

## 9. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/frontend_component_breakdown.md`
2. 正式 `openapi/openapi.yaml`
3. 前端 mock 数据文件

---

## 10. 一句话结论

接口落地材料的关键，不是把字段“写得更多”，而是：

> **把前后端最常遇到的成功、降级、失败和空状态都用稳定示例固定下来。**
