const PREFIX = 'anon_query_session:'

type AnonymousQuerySession = {
  queryTaskId: string
  token: string
  createdAt: string
}

export function saveAnonymousQuerySession(session: AnonymousQuerySession) {
  sessionStorage.setItem(`${PREFIX}${session.queryTaskId}`, JSON.stringify(session))
}

export function getAnonymousQuerySession(queryTaskId: string) {
  const raw = sessionStorage.getItem(`${PREFIX}${queryTaskId}`)

  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw) as AnonymousQuerySession
  } catch {
    return null
  }
}
