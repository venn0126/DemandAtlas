import { Link } from 'react-router-dom'

import { routeBuilders } from '../../app/routes'
import type { ResultBoardItemViewModel } from '../../types/view-model'
import { Badge } from '../common/badge'
import { InlineGroup } from '../layout/inline-group'
import { MetaRow } from '../layout/meta-row'

type ResultBoardItemProps = {
  resultSnapshotId: string
  item: ResultBoardItemViewModel
  emergingLabel?: string
  lowConfidenceLabel?: string
  weakSignalLabel?: string
}

export function ResultBoardItem({
  emergingLabel,
  item,
  lowConfidenceLabel,
  resultSnapshotId,
  weakSignalLabel,
}: ResultBoardItemProps) {
  return (
    <Link
      to={routeBuilders.clusterDetail(resultSnapshotId, item.clusterId)}
      className="result-link"
    >
      <article className="result-item">
        <MetaRow
          left={
            <div>
              <p className="mono-text">#{item.rank}</p>
              <h3>{item.title}</h3>
            </div>
          }
          right={
            <InlineGroup variant="badges">
              <Badge tone="info">{item.boardScore.toFixed(1)}</Badge>
              {item.isEmergingSignal && emergingLabel ? (
                <Badge tone="info">{emergingLabel}</Badge>
              ) : null}
              {item.isLowConfidence && lowConfidenceLabel ? (
                <Badge tone="warning">{lowConfidenceLabel}</Badge>
              ) : null}
              {item.isWeakSignal && weakSignalLabel ? (
                <Badge tone="warning">{weakSignalLabel}</Badge>
              ) : null}
            </InlineGroup>
          }
        />

        <p>{item.summary}</p>

        <InlineGroup variant="badges">
          {item.topSubreddits.map((subreddit: string) => (
            <Badge key={subreddit}>{subreddit}</Badge>
          ))}
        </InlineGroup>
      </article>
    </Link>
  )
}
