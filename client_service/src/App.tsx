import 'react-toastify/dist/ReactToastify.css';
import './App.css';
import ChatWindow from './components/ChatWindow';
import Navbar from './components/Navbar';
import { ToastContainer } from 'react-toastify';

function App() {
  return (
    <div className="flex flex-col items-center w-full h-screen justify-center">
      <Navbar/>
      <ChatWindow/>
      <ToastContainer
      position="top-right"
      autoClose={5000}
      />
    </div>
  );
}

export default App;