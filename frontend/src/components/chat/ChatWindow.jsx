import { useMemo } from 'react'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'

const ChatWindow = ({ conversation, messages, currentUsername, onSend }) => {
  const title = useMemo(() => {
    if (!conversation) return 'Suhbat tanlang'
    if (conversation.conversation_type === 'group') {
      return conversation.name || `Guruh #${conversation.id}`
    }
    const peer = conversation.members.find((member) => member.username !== currentUsername)
    return peer?.username || 'Direct chat'
  }, [conversation, currentUsername])

  if (!conversation) {
    return (
      <section className="flex flex-1 items-center justify-center bg-slate-50 text-slate-400">
        Chap tomondan suhbat tanlang
      </section>
    )
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white px-4 py-3">
        <h2 className="text-base font-semibold text-slate-800">{title}</h2>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto px-3 py-4">
        {messages.length === 0 ? (
          <p className="text-center text-sm text-slate-400">Hozircha xabarlar yo'q</p>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={`${message.id}-${message.time}`}
              message={message}
              isOwnMessage={message.username === currentUsername}
            />
          ))
        )}
      </div>

      <MessageInput onSend={onSend} />
    </section>
  )
}

export default ChatWindow
