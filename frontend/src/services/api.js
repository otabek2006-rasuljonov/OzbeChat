import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const client = axios.create({
  baseURL: API_BASE_URL,
})

export const setAuthToken = (token) => {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`
    return
  }
  delete client.defaults.headers.common.Authorization
}

export const login = async (payload) => {
  const { data } = await client.post('/auth/login/', payload)
  return data
}

export const register = async (payload) => {
  const { data } = await client.post('/auth/register/', payload)
  return data
}

export const fetchConversations = async () => {
  const { data } = await client.get('/conversations/')
  return data
}

export const fetchMessages = async (conversationId) => {
  const { data } = await client.get(`/messages/${conversationId}/`)
  return data
}

export const searchUsers = async (query) => {
  const { data } = await client.get('/users/search/', {
    params: { q: query || '' },
  })
  return data
}

export const startConversation = async (username) => {
  const { data } = await client.post('/conversations/start/', { username })
  return data
}

export const createGroup = async ({ name, members }) => {
  const { data } = await client.post('/groups/create/', { name, members })
  return data
}
