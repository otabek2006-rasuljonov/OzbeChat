const getWebSocketBase = () => {
  if (import.meta.env.VITE_WS_BASE_URL) {
    return import.meta.env.VITE_WS_BASE_URL.replace(/\/$/, '')
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/ws/chat`
}

export const createChatSocket = (conversationId, token) => {
  const base = getWebSocketBase()
  const query = new URLSearchParams({ token })
  return new WebSocket(`${base}/${conversationId}/?${query.toString()}`)
}
