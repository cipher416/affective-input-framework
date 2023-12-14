

type Props = {
    chat?: Chat;
    isLoading?: boolean;
}

export default function ChatBubble({chat, isLoading = false}: Props) {
    return (
        <div className={`chat ${chat?.sender === "bot" && !isLoading ? "chat-start" : "chat-end"}`}>
            <div className="chat-bubble">
            <div className="chat-header">
                <span className="me-2">
                    {chat?.sender === "bot" ? "Chat Bot" : "User"}
                </span>
                <time className="text-xs opacity-50">{chat?.emotion}</time>
            </div>{isLoading ? <span className="loading loading-dots loading-md"></span> : chat!.message}
            </div>
        </div>
    );
}