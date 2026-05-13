import { Navigate } from 'react-router-dom'
import ChatList from '../components/chat/ChatList'
import ChatWindow from '../components/chat/ChatWindow'
import { useAuth } from '../context/AuthContext'
import { ChatProvider, useChat } from '../context/ChatContext'

const ChatLayout = () => {
  const { auth, logout } = useAuth()
  const {
    conversations,
    activeConversation,
    messages,
    users,
    isLoading,
    error,
    openConversation,
    sendMessage,
    runUserSearch,
    startDirectConversation,
    createGroupConversation,
  } = useChat()

  return (
    <main className="h-screen overflow-hidden bg-slate-100 p-2 md:p-4">
      <section className="mx-auto flex h-full max-w-6xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="hidden md:block">
          <ChatList
            conversations={conversations}
            activeConversationId={activeConversation?.id}
            currentUsername={auth.username}
            users={users}
            onOpenConversation={openConversation}
            onSearch={runUserSearch}
            onStartDirect={startDirectConversation}
            onCreateGroup={createGroupConversation}
          />
        </div>

        <div className="flex w-full min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:hidden">
            <p className="text-sm font-semibold text-slate-900">{auth.username}</p>
            <button type="button" onClick={logout} className="text-sm text-slate-500">
              Chiqish
            </button>
          </header>

          <div className="md:hidden">
            <ChatList
              conversations={conversations}
              activeConversationId={activeConversation?.id}
              currentUsername={auth.username}
              users={users}
              onOpenConversation={openConversation}
              onSearch={runUserSearch}
              onStartDirect={startDirectConversation}
              onCreateGroup={createGroupConversation}
            />
          </div>

          <div className="hidden items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:flex">
            <p className="text-sm font-semibold text-slate-900">{auth.username}</p>
            <button
              type="button"
              onClick={logout}
              className="rounded-lg border border-slate-200 px-3 py-1 text-sm text-slate-600"
            >
              Chiqish
            </button>
          </div>

          {isLoading ? <p className="p-4 text-sm text-slate-400">Yuklanmoqda...</p> : null}
          {error ? <p className="px-4 pt-2 text-sm text-red-500">{error}</p> : null}

          <ChatWindow
            conversation={activeConversation}
            messages={messages}
            currentUsername={auth.username}
            onSend={sendMessage}
          />
        </div>
      </section>
    </main>
  )
}

const ChatPage = () => {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <ChatProvider>
      <ChatLayout />
    </ChatProvider>
  )
}

export default ChatPage
