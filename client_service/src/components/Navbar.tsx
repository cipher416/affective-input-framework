import ThemeChanger from "./ThemeChanger";

export default function Navbar() {
    return (
        <div className="navbar bg-base-100 flex flex-row justify-items-end">
            <a className="btn btn-ghost text-xl">Chat with a Chatbot</a>
            <div className="w-full flex flex-row justify-end">
                <ThemeChanger/>
            </div>
        </div>
    );
}