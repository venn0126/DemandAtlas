export type ApiEnvelope<TData, TError = null, TMeta = Record<string, unknown>> = {
  request_id: string
  data: TData
  meta: TMeta
  error: TError
}

export type SelectMode = 'async' | 'cache-hit' | 'too-broad'
