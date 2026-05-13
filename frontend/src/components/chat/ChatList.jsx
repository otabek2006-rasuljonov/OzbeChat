import { useMemo, useState } from 'react'

const StatusDot = ({ isOnline }) => (
  <span className={`inline-block h-2.5 w-2.5 rounded-full ${isOnline ? 'bg-emerald-500' : 'bg-slate-300'}`} />
)

const ChatList = ({
  conversations,
  activeConversationId,
  currentUsername,
  users,
  onOpenConversation,
  onSearch,
  onStartDirect,
  onCreateGroup,
}) => {
  const [query, setQuery] = useState('')
  const [groupName, setGroupName] = useState('')
  const [selectedUsers, setSelectedUsers] = useState([])

  const filteredConversations = useMemo(() => conversations, [conversations])

  const toggleUser = (username) => {
    setSelectedUsers((prev) =>
      prev.includes(username) ? prev.filter((item) => item !== username) : [...prev, username],
    )
  }

  const handleSearch = (event) => {
    const value = event.target.value
    setQuery(value)
    onSearch(value)
  }

  const handleCreateGroup = () => {
    if (!groupName.trim()) return
    onCreateGroup({ name: groupName.trim(), members: selectedUsers })
    setGroupName('')
    setSelectedUsers([])
  }

  return (
    <aside className="flex h-full w-full flex-col border-r border-slate-200 bg-white md:w-80">
      <div className="border-b border-slate-200 p-3">
        <h1 className="mb-2 text-lg font-semibold text-slate-900">OzbeChat</h1>
        <input
          value={query}
          onChange={handleSearch}
          placeholder="Foydalanuvchi qidirish..."
          className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-sky-400"
        />
      </div>

      {query ? (
        <div className="max-h-48 space-y-2 overflow-y-auto border-b border-slate-100 p-3">
          {users.map((user) => (
            <button
              key={user.id}
              type="button"
              className="flex w-full items-center justify-between rounded-xl border border-slate-100 px-3 py-2 text-left text-sm hover:bg-slate-50"
              onClick={() => onStartDirect(user.username)}
            >
              <span>{user.username}</span>
              <StatusDot isOnline={user.is_online} />
            </button>
          ))}
        </div>
      ) : null}

      <div className="border-b border-slate-100 p-3">
        <input
          value={groupName}
          onChange={(event) => setGroupName(event.target.value)}
          placeholder="Group name"
          className="mb-2 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-sky-400"
        />
        <div className="mb-2 max-h-20 space-y-1 overflow-y-auto rounded-xl border border-slate-100 p-2 text-xs">
          {users.map((user) => (
            <label key={`group-${user.id}`} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedUsers.includes(user.username)}
                onChange={() => toggleUser(user.username)}
              />
              <span className="flex-1">{user.username}</span>
              <StatusDot isOnline={user.is_online} />
            </label>
          ))}
        </div>
        <button
          type="button"
          onClick={handleCreateGroup}
          className="w-full rounded-xl bg-indigo-500 py-2 text-sm font-medium text-white"
        >
          Group chat yaratish
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-2">
        {filteredConversations.map((conversation) => {
          const isActive = conversation.id === activeConversationId
          const isGroup = conversation.conversation_type === 'group'
          const peer = conversation.members.find((member) => member.username !== currentUsername)
          const title = isGroup ? conversation.name || `Group #${conversation.id}` : peer?.username || 'Direct chat'
          const isOnline = isGroup
            ? conversation.members.some((member) => member.username !== currentUsername && member.is_online)
            : Boolean(peer?.is_online)

          return (
            <button
              key={conversation.id}
              type="button"
              onClick={() => onOpenConversation(conversation.id)}
              className={`mb-1 w-full rounded-xl px-3 py-2 text-left ${
                isActive ? 'bg-sky-100' : 'hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-800">{title}</p>
                <StatusDot isOnline={isOnline} />
              </div>
              {conversation.last_message ? (
                <p className="truncate text-xs text-slate-500">{conversation.last_message.text}</p>
              ) : (
                <p className="text-xs text-slate-400">Yangi suhbat</p>
              )}
            </button>
          )
        })}
      </div>
    </aside>
  )
}

export default ChatList
