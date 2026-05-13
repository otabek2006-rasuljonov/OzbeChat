import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { useAuth } from './AuthContext'
import {
  createGroup,
  fetchConversations,
  fetchMessages,
  searchUsers,
  startConversation,
} from '../services/api'
import { createChatSocket } from '../services/websocket'

const ChatContext = createContext(null)

const normalizeApiMessage = (message) => ({
  id: message.id,
  type: message.type,
  username: message.sender,
  message: message.text,
  time: new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
})

export const ChatProvider = ({ children }) => {
  const { auth, isAuthenticated } = useAuth()
  const [conversations, setConversations] = useState([])
  const [activeConversationId, setActiveConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const socketRef = useRef(null)

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeConversationId) || null,
    [activeConversationId, conversations],
  )

  const closeSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }
  }, [])

  const loadConversations = useCallback(async () => {
    if (!isAuthenticated) return

    setIsLoading(true)
    setError('')
    try {
      const list = await fetchConversations()
      setConversations(list)
      if (!activeConversationId && list.length > 0) {
        setActiveConversationId(list[0].id)
      }
    } catch {
      setError('Suhbatlarni olishda xatolik yuz berdi')
    } finally {
      setIsLoading(false)
    }
  }, [activeConversationId, isAuthenticated])

  const openConversation = useCallback(
    async (conversationId) => {
      closeSocket()
      setError('')

      try {
        const serverMessages = await fetchMessages(conversationId)
        setMessages(serverMessages.map(normalizeApiMessage))
      } catch {
        setMessages([])
        setError('Xabarlarni olishda xatolik yuz berdi')
      }

      if (!auth?.access) return

      const socket = createChatSocket(conversationId, auth.access)
      socketRef.current = socket

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        setMessages((prev) => {
          if (prev.some((item) => item.id === data.id)) {
            return prev
          }
          return [...prev, data]
        })
      }

      socket.onerror = () => {
        setError('Real-time ulanishda xatolik bor')
      }

      socket.onclose = () => {
        if (socketRef.current === socket) {
          socketRef.current = null
        }
      }
    },
    [auth?.access, closeSocket],
  )

  const selectConversation = useCallback((conversationId) => {
    setActiveConversationId(conversationId)
  }, [])

  const sendMessage = (text) => {
    const payload = text.trim()
    if (!payload || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      return false
    }

    socketRef.current.send(JSON.stringify({ message: payload }))
    return true
  }

  const runUserSearch = useCallback(async (query) => {
    if (!isAuthenticated) return
    try {
      const result = await searchUsers(query)
      setUsers(result)
    } catch {
      setUsers([])
    }
  }, [isAuthenticated])

  const startDirectConversation = useCallback(
    async (username) => {
      const conversation = await startConversation(username)
      setConversations((prev) => {
        const withoutCurrent = prev.filter((item) => item.id !== conversation.id)
        return [conversation, ...withoutCurrent]
      })
      setActiveConversationId(conversation.id)
      return conversation
    },
    [],
  )

  const createGroupConversation = useCallback(
    async ({ name, members }) => {
      const conversation = await createGroup({ name, members })
      setConversations((prev) => [conversation, ...prev])
      setActiveConversationId(conversation.id)
      return conversation
    },
    [],
  )

  useEffect(() => {
    if (!isAuthenticated) {
      closeSocket()
      setConversations([])
      setMessages([])
      setUsers([])
      setActiveConversationId(null)
      return
    }

    loadConversations()
  }, [closeSocket, isAuthenticated, loadConversations])

  useEffect(() => {
    if (activeConversationId && isAuthenticated) {
      openConversation(activeConversationId)
    }
    return () => {
      closeSocket()
    }
  }, [activeConversationId, closeSocket, isAuthenticated, openConversation])

  const value = useMemo(
    () => ({
      conversations,
      activeConversation,
      messages,
      users,
      isLoading,
      error,
      loadConversations,
      openConversation,
      selectConversation,
      sendMessage,
      runUserSearch,
      startDirectConversation,
      createGroupConversation,
    }),
    [activeConversation, conversations, error, isLoading, loadConversations, messages, openConversation, runUserSearch, selectConversation, startDirectConversation, createGroupConversation, users],
  )

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export const useChat = () => {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used inside ChatProvider')
  }
  return context
}
